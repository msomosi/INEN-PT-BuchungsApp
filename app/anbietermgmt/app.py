from datetime import datetime, timedelta
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request

app = create_app("anbietermgmt")

# API zum Abrufen der Zimmerdaten
from flask import session

from datetime import datetime, timedelta
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request, session

app = create_app("anbietermgmt")

# API zum Abrufen der Zimmerdaten
@app.route('/anbietermgmt', methods=['GET'])
def anbietermgmt():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({'error': 'Benutzer-ID fehlt.'}), 401

        conn = create_db_connection()
        with conn.cursor() as cur:
            # Abfrage für Zimmerdetails mit Buchungsstatus
            query_rooms = """
            SELECT 
                r.room_id,
                r.date,
                COALESCE(bs.state_name, 'available') AS state_name,  -- Fallback auf "available"
                COALESCE(b.state_id, 1) AS state_id,                -- Fallback auf state_id 1 (available)
                b.booking_id,
                u.first_name,
                u.last_name
            FROM 
                public.room r
            LEFT JOIN 
                public.booking b ON r.room_id = b.room_id
            LEFT JOIN 
                public.booking_state bs ON b.state_id = bs.state_id
            LEFT JOIN 
                public."user" u ON b.user_id = u.user_id
            WHERE 
                r.provider_id = (
                    SELECT provider_id
                    FROM public.accommodation
                    WHERE provider_id = (
                        SELECT provider_id
                        FROM public."user"
                        WHERE user_id = %s
                    )
                )
            ORDER BY r.date;
        """

            cur.execute(query_rooms, (user_id,))
            rows = cur.fetchall()

            # Datenaufbereitung
            rooms = []
            for row in rows:
                rooms.append({
                    "zimmer_id": row[0],
                    "date": row[1].strftime('%Y-%m-%d') if row[1] else "Nicht verfügbar",
                    "state_name": row[2],
                    "state_id": row[3],
                    "booking_id": row[4],
                    "firstname": row[5] or "N/A",
                    "lastname": row[6] or "N/A",
                })

            return jsonify({"rooms": rooms}), 200

    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Zimmerdaten: {e}")
        return jsonify({'error': 'Fehler beim Laden der Zimmerdaten.', 'details': str(e)}), 500


@app.route('/room_summary', methods=['GET'])
def get_room_summary():
    """API, um die Zusammenfassung der Zimmer anzuzeigen."""
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({'error': 'Benutzer-ID fehlt.'}), 401

        conn = create_db_connection()
        with conn.cursor() as cur:
            # Abfrage für die Zähler basierend auf den Status
            query = """
            SELECT 
            COUNT(*) FILTER (WHERE COALESCE(b.state_id, r.state_id) = 1) AS available,
            COUNT(*) FILTER (WHERE b.state_id = 2) AS pending,
            COUNT(*) FILTER (WHERE b.state_id = 3) AS confirmed,
            COUNT(*) FILTER (WHERE b.state_id = 4) AS completed,
            COUNT(*) FILTER (WHERE b.state_id = 5) AS failed
        FROM public.room r
        LEFT JOIN public.booking b ON r.room_id = b.room_id
        WHERE r.provider_id = (
            SELECT provider_id
            FROM public.accommodation
            WHERE provider_id = (
                SELECT provider_id
                FROM public."user"
                WHERE user_id = %s
    )
);

        """

            cur.execute(query, (user_id,))
            summary = cur.fetchone()

            summary_data = {
                "available": summary[0] or 0,
                "pending": summary[1] or 0,
                "confirmed": summary[2] or 0,
                "completed": summary[3] or 0,
                "failed": summary[4] or 0
            }

            return jsonify({"summary": summary_data}), 200

    except Exception as e:
        app.logger.error(f"Fehler bei der Abfrage: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Zimmerzusammenfassung', 'details': str(e)}), 500



# API für Buchungsstatus-Aktualisierung
@app.route('/update-booking-status', methods=['POST'])
def update_booking_status():
    """Aktualisiert den Buchungsstatus für ein Zimmer."""
    try:
        booking_id = request.json.get('booking_id')
        new_status_id = request.json.get('status_id')

        if not booking_id or not new_status_id:
            return jsonify({'error': 'Buchungs-ID oder neuer Status fehlen'}), 400

        conn = create_db_connection()
        with conn.cursor() as cur:
            # Aktualisiere den Status
            query = """
                UPDATE public.booking
                SET state_id = %s
                WHERE booking_id = %s;
            """
            cur.execute(query, (new_status_id, booking_id))
            conn.commit()

        return jsonify({'success': 'Buchungsstatus erfolgreich aktualisiert'}), 200
    except Exception as e:
        return jsonify({'error': 'Fehler beim Aktualisieren des Buchungsstatus', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    app.run(debug=True, port=80)




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


if __name__ == '__main__':
    app.run(debug=True, port=80)
