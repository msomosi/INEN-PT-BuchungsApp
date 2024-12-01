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
                SELECT u.user_id, u.username, d."CompanyName", d."Adresse", d.email, d.phone
                FROM tbl_user u
                JOIN tbl_user_details d ON u.user_id = d.user_id
                WHERE u.role_id = 2 AND d."CompanyName" ILIKE %s
                ORDER BY u.user_id
            """
            cursor.execute(query, (f"%{search_query}%",))
        else:
            query = """
                SELECT u.user_id, u.username, d."CompanyName", d."Adresse", d.email, d.phone
                FROM tbl_user u
                JOIN tbl_user_details d ON u.user_id = d.user_id
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
                "adresse": user[3],
                "email": user[4],
                "phone": user[5],
            }
            for user in users
        ]

        return jsonify(users=users_list, search_query=search_query)
    finally:
        conn.close()

@app.route('/add-kunde', methods=['POST'])
def add_kunde():
    """API zum Hinzufügen eines neuen Kunden."""
    username = request.form.get('username')
    password = request.form.get('password')
    company_name = request.form.get('company_name')
    adresse = request.form.get('adresse')
    email = request.form.get('email')
    phone = request.form.get('phone')

    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        # Nächste freie user_id ermitteln
        cursor.execute("""
            SELECT COALESCE(MAX(user_id), 0) + 1 AS next_user_id
            FROM tbl_user
        """)
        next_user_id = cursor.fetchone()[0]

        # Eintrag in tbl_user_details erstellen
        cursor.execute(
            """
            INSERT INTO tbl_user_details (user_id, "CompanyName", "Adresse", email, phone)
            VALUES (%s, %s, %s, %s, %s)
            """, (next_user_id, company_name, adresse, email, phone)
        )

        # Eintrag in tbl_user erstellen
        cursor.execute(
            """
            INSERT INTO tbl_user (user_id, role_id, username, password, verification)
            VALUES (%s, 2, %s, %s, TRUE)
            """, (next_user_id, username, password)
        )

        # Änderungen speichern
        conn.commit()
        return redirect('/kundenmanagement?status=success')
    except Exception as e:
        conn.rollback()
        return redirect(f'/kundenmanagement?status=error&message={e}')
    finally:
        conn.close()



@app.route('/edit-kunde/<int:user_id>', methods=['PUT'])
def edit_kunde(user_id):
    """API zum Bearbeiten eines Kunden."""
    try:
        data = request.json
        conn = create_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tbl_user
            SET username = %s
            WHERE user_id = %s
            """, (data['username'], user_id)
        )
        cursor.execute(
            """
            UPDATE tbl_user_details
            SET "CompanyName" = %s, "Adresse" = %s, email = %s, phone = %s
            WHERE user_id = %s
            """, (data['company_name'], data['adresse'], data['email'], data['phone'], user_id)
        )
        conn.commit()

        return jsonify({"success": True, "message": "Kunde erfolgreich bearbeitet"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@app.route('/delete-kunde/<int:user_id>', methods=['DELETE'])
def delete_kunde(user_id):
    """API zum Löschen eines Kunden."""
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tbl_user_details WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM tbl_user WHERE user_id = %s", (user_id,))
        conn.commit()

        return jsonify({"success": True, "message": "Kunde erfolgreich gelöscht"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
