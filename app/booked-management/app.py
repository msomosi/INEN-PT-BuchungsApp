from datetime import datetime
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request

app = create_app("booked-management")


@app.route('/booked-rooms', methods=['GET'])
def get_booked_rooms():
    """API, um Buchungen für einen Studenten abzurufen."""
    user_id = request.args.get('user_id', None)  # Hole die user_id aus der Anfrage
    if not user_id:
        app.logger.error("Keine user_id in der Anfrage gefunden.")
        return jsonify({'error': 'Keine user_id übergeben'}), 400

    try:
        conn = create_db_connection()
        with conn.cursor() as cur:
            # Buchungsdaten abfragen
            query = """
                SELECT 
                    b.booking_id,
                    b.room_id,
                    r.date,
                    bs.state_name
                FROM 
                    public.booking b
                JOIN 
                    public.room r ON b.room_id = r.room_id
                LEFT JOIN 
                    public.booking_state bs ON b.state_id = bs.state_id
                WHERE 
                    b.user_id = %s
                ORDER BY 
                    r.date;
            """
            cur.execute(query, (user_id,))
            rows = cur.fetchall()

            data = [
                {
                    "buchung_id": row[0],
                    "zimmer_id": row[1],
                    "date": row[2].strftime('%Y-%m-%d') if row[2] else "Unbekannt",
                    "state": row[3] or "Unbekannt"
                }
                for row in rows
            ]

        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Fehler bei der Abfrage: {e}")
        return jsonify({'error': 'Datenbankabfrage fehlgeschlagen', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=80)
