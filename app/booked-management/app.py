from datetime import datetime, timedelta
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request

app = create_app("booked-management")

# API zum Abrufen der Zimmerdaten
from flask import session

@app.route('/booked-rooms', methods=['GET'])
def get_booked_rooms():
    """API, um Buchungen ohne Anbieternamen abzurufen."""
    user_id = request.args.get('user_id', None)  # Hole die user_id aus der Anfrage
    if not user_id:
        app.logger.error("Keine user_id in der Anfrage gefunden.")
        return jsonify({'error': 'Keine user_id übergeben'}), 400

    try:
        conn = create_db_connection()
        with conn.cursor() as cur:
            query = """
                SELECT 
                    b.buchung_id, 
                    b.user_id AS buchender_user_id, 
                    b.zimmer_id, 
                    z.date, 
                    z.state_id
                FROM 
                    tbl_buchung b
                JOIN 
                    tbl_zimmer z ON b.zimmer_id = z.zimmer_id
                WHERE 
                    b.user_id = %s
                ORDER BY 
                    z.date;
            """
            cur.execute(query, (user_id,))
            rows = cur.fetchall()

            data = [
                {
                    "buchung_id": row[0],
                    "zimmer_id": row[2],
                    "date": row[3],
                    "state": "Booked" if row[4] == 1 else "Pending"
                }
                for row in rows
            ]

        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Fehler bei der Abfrage: {e}")
        return jsonify({'error': 'Datenbankabfrage fehlgeschlagen'}), 500






if __name__ == '__main__':
    app.run(debug=True, port=80)
