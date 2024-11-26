from datetime import datetime, timedelta
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request

app = create_app("anbietermgmt")

# API zum Abrufen der Zimmerdaten
from flask import session

@app.route('/anbietermgmt', methods=['GET'])
def get_rooms():
    """API, um alle Zimmer für den angemeldeten Benutzer zu laden."""
    debug_request(request)
    
    user_id = "1"  # Hier wird der eingeloggte Benutzer gesetzt (z. B. aus Session)

    conn_room = create_db_connection()
    if not conn_room:
        return jsonify({'error': 'Verbindung zur Zimmer-Datenbank fehlgeschlagen'}), 500

    try:
        with conn_room.cursor() as cur:
            # SQL-Abfrage, um nur Zimmer mit user_id = 1 zu laden
            query = """
                SELECT z.zimmer_id, z.user_id, z.date, z.state_id, s.state_name, u."Firstname", u."Lastname"
                FROM tbl_zimmer z
                JOIN tbl_booking_state s ON z.state_id = s.state_id
                LEFT JOIN tbl_buchung b ON z.zimmer_id = b.zimmer_id
                LEFT JOIN tbl_user_details u ON b.user_id = u.user_id
                WHERE z.user_id = %s
                ORDER BY z.date ASC
            """
            cur.execute(query, (user_id,))
            rows = cur.fetchall()

            # Die Ergebnisse in ein JSON-kompatibles Format umwandeln
            data = [
                {
                    "zimmer_id": row[0],
                    "user_id": row[1],
                    "date": row[2].strftime('%Y-%m-%d'),  # Datum als String formatieren
                    "state_id": row[3],
                    "state_name": row[4],
                    "firstname": row[5] or "-",
                    "lastname": row[6] or "-",
                }
                for row in rows
            ]

        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Fehler bei der Abfrage: {e}")
        return jsonify({'error': 'Datenbankabfrage fehlgeschlagen'}), 500
    finally:
        conn_room.close()


# API zum Hinzufügen von Zimmern
@app.route('/add_room', methods=['POST'])
def add_room():
    debug_request(request)
    user_id = "1"  # Angemeldeter Benutzer
    if not user_id:
        return jsonify({'error': 'Kein Benutzer angemeldet'}), 400

    data = request.json
    try:
        num_rooms = int(data['num_rooms'])
        date_from = datetime.strptime(data['date_from'], '%Y-%m-%d')
        date_to = datetime.strptime(data['date_to'], '%Y-%m-%d')
    except (ValueError, KeyError) as e:
        return jsonify({'error': f'Ungültige Eingabewerte: {e}'}), 400

    if date_from > date_to:
        return jsonify({'error': "'Von'-Datum liegt nach 'Bis'-Datum"}), 400

    conn_room = create_db_connection()
    if not conn_room:
        return jsonify({'error': 'Verbindung zur Datenbank fehlgeschlagen'}), 500

    try:
        with conn_room.cursor() as cur:
            current_date = date_from
            while current_date <= date_to:
                for _ in range(num_rooms):
                    query = """
                        INSERT INTO tbl_zimmer (user_id, date)
                        VALUES (%s, %s);
                    """
                    cur.execute(query, (user_id, current_date))
                current_date += timedelta(days=1)

            conn_room.commit()

        return jsonify({'success': 'Zimmer erfolgreich hinzugefügt'})
    except Exception as e:
        app.logger.error(f"Fehler bei der Datenbankoperation: {e}")
        return jsonify({'error': 'Fehler beim Einfügen der Zimmer'}), 500
    finally:
        conn_room.close()

# API für die Zimmerzusammenfassung
@app.route('/room_summary', methods=['GET'])
def get_room_summary():
    """API, um die Zusammenfassung der Zimmer anzuzeigen."""
    debug_request(request)
    user_id = "1"  

    conn_room = create_db_connection()
    if not conn_room:
        return jsonify({'error': 'Verbindung zur Zimmer-Datenbank fehlgeschlagen'}), 500

    try:
        with conn_room.cursor() as cur:
            # Abfrage für die Zähler basierend auf den Status
            query = """
                SELECT 
                    COUNT(*) FILTER (WHERE state_id = 1) AS available,
                    COUNT(*) FILTER (WHERE state_id = 2) AS pending,
                    COUNT(*) FILTER (WHERE state_id = 3) AS booked
                FROM tbl_zimmer
                WHERE user_id = %s
            """
            cur.execute(query, (user_id,))
            summary = cur.fetchone()

            return jsonify({
                "available": summary[0] or 0,
                "pending": summary[1] or 0,
                "booked": summary[2] or 0
            })
    except Exception as e:
        app.logger.error(f"Fehler bei der Abfrage: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Zimmerzusammenfassung'}), 500
    finally:
        conn_room.close()



if __name__ == '__main__':
    app.run(debug=True, port=80)
