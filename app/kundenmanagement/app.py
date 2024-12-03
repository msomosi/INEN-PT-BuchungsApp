from flask import Flask, jsonify, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Datenbankverbindung
def create_db_connection():
    return psycopg2.connect(
        dbname="citizix_db",
        user="citizix_user",
        password="S3cret",
        host="db",
        port=5432
    )

@app.route('/kundenmanagement', methods=['GET'])
def get_kunden():
    """API für die Verwaltung der Kunden."""
    search_query = request.args.get('search', '')

    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        # Daten abrufen
        if search_query:
            query = """
            SELECT u.user_id, u.username, a.company_name, c.address, c.postal_code, c.location, c.phone
            FROM "user" u
            JOIN accommodation a ON u.provider_id = a.provider_id
            JOIN contact c ON a.contact_id = c.contact_id
            WHERE u.role_id = 2 AND a.company_name ILIKE %s
            ORDER BY u.user_id
        """
            cursor.execute(query, (f"%{search_query}%",))
        else:
            query = """
                SELECT u.user_id, u.username, a.company_name, c.address, c.postal_code, c.location, c.phone
                FROM "user" u
                JOIN accommodation a ON u.provider_id = a.provider_id
                JOIN contact c ON a.contact_id = c.contact_id
                WHERE u.role_id = 2
                ORDER BY u.user_id
            """

            
            cursor.execute(query)

        users = cursor.fetchall()

        # Ergebnis zurückgeben
        users_list = [
            {
                "user_id": user[0],
                "username": user[1],
                "company_name": user[2],
                "address": user[3],
                "postal_code": user[4], 
                "location": user[5],
                "phone": user[6],
            }
            for user in users
        ]


        return jsonify(users=users_list, search_query=search_query)
    finally:
        conn.close()


@app.route('/add-kunde', methods=['POST'])
def add_kunde():
    username = request.form.get('username')
    password = request.form.get('password')
    company_name = request.form.get('company_name')
    address = request.form.get('address')
    postal_code = request.form.get('postal_code')
    location = request.form.get('location')
    phone = request.form.get('phone')

    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        # Kontakt hinzufügen
        cursor.execute("""
            INSERT INTO contact (address, postal_code, location, phone)
            VALUES (%s, %s, %s, %s) RETURNING contact_id
        """, (address, postal_code, location, phone))


        # Anbieter hinzufügen
        cursor.execute("""
            INSERT INTO accommodation (contact_id, company_name)
            VALUES (%s, %s) RETURNING provider_id
        """, (contact_id, company_name))
        provider_id = cursor.fetchone()[0]

        # Benutzer hinzufügen
        cursor.execute("""
            INSERT INTO "user" (role_id, provider_id, username, password, verification)
            VALUES (2, %s, %s, %s, TRUE)
        """, (provider_id, username, password))

        conn.commit()
        return redirect('/kundenmanagement?status=success')
    except Exception as e:
        conn.rollback()
        return redirect(f'/kundenmanagement?status=error&message={e}')
    finally:
        conn.close()





@app.route('/edit-kunde/<int:user_id>', methods=['PUT'])
def edit_kunde(user_id):
    try:
        data = request.json
        conn = create_db_connection()
        cursor = conn.cursor()

        # Benutzer aktualisieren
        cursor.execute("""
            UPDATE "user"
            SET username = %s
            WHERE user_id = %s
        """, (data['username'], user_id))

        # Anbieter aktualisieren
        cursor.execute("""
            UPDATE accommodation
            SET company_name = %s
            WHERE provider_id = (
                SELECT provider_id FROM "user" WHERE user_id = %s
            )
        """, (data['company_name'], user_id))

        # Kontakt aktualisieren
        cursor.execute("""
            UPDATE contact
            SET address = %s, postal_code = %s, location = %s, phone = %s
            WHERE contact_id = (
                SELECT a.contact_id FROM accommodation a
                JOIN "user" u ON a.provider_id = u.provider_id
                WHERE u.user_id = %s
            )
        """, (data['address'], data['postal_code'], data['location'], data['phone'], user_id))

        conn.commit()
        return jsonify({"success": True, "message": "Kunde erfolgreich bearbeitet"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()




@app.route('/delete-kunde/<int:user_id>', methods=['DELETE'])
def delete_kunde(user_id):
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        # Anbieter-ID ermitteln
        cursor.execute("""
            SELECT provider_id FROM "user" WHERE user_id = %s
        """, (user_id,))
        provider_id = cursor.fetchone()[0]

        # Kontakt-ID ermitteln
        cursor.execute("""
            SELECT contact_id FROM accommodation WHERE provider_id = %s
        """, (provider_id,))
        contact_id = cursor.fetchone()[0]

        # Löschen in der richtigen Reihenfolge
        cursor.execute("DELETE FROM contact WHERE contact_id = %s", (contact_id,))
        cursor.execute("DELETE FROM accommodation WHERE provider_id = %s", (provider_id,))
        cursor.execute("DELETE FROM \"user\" WHERE user_id = %s", (user_id,))

        conn.commit()
        return jsonify({"success": True, "message": "Kunde erfolgreich gelöscht"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)