from datetime import datetime, timedelta
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
                    bs.state_name,
                    a.company_name  -- Hotelname hinzufügen
                FROM 
                    public.booking b
                JOIN 
                    public.room r ON b.room_id = r.room_id
                LEFT JOIN 
                    public.booking_state bs ON b.state_id = bs.state_id
                JOIN 
                    public.accommodation a ON r.provider_id = a.provider_id  -- Verknüpfung mit Unterkunft
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
                    "state": row[3] or "Unbekannt",
                    "hotel_name": row[4]  
                }
                for row in rows
            ]

        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Fehler bei der Abfrage: {e}")
        return jsonify({'error': 'Datenbankabfrage fehlgeschlagen', 'details': str(e)}), 500


@app.route('/cancel-booking', methods=['POST'])
def cancel_booking():
    """
    Storniert eine Buchung, falls die Bedingungen erfüllt sind (mindestens 2 Tage vorher).
    """
    try:
        data = request.json
        booking_id = data.get('booking_id')

        if not booking_id:
            return jsonify({"error": "Buchungs-ID fehlt."}), 400

        conn = create_db_connection()
        with conn.cursor() as cur:
            # Prüfe das Buchungsdatum
            query_date = """
                SELECT r.date
                FROM public.booking b
                JOIN public.room r ON b.room_id = r.room_id
                WHERE b.booking_id = %s;
            """
            cur.execute(query_date, (booking_id,))
            result = cur.fetchone()

            if not result:
                return jsonify({"error": "Buchung nicht gefunden."}), 404

            booking_date = result[0]
            current_date = datetime.now().date()

            # Verhindere Stornierung innerhalb von 2 Tagen
            if booking_date - current_date <= timedelta(days=2):
                return jsonify({"error": "Stornierung nicht mehr möglich. Mindestfrist: 2 Tage vorher."}), 403

            # Buchung löschen und Zimmerstatus aktualisieren
            query_delete_booking = "DELETE FROM public.booking WHERE booking_id = %s;"
            query_update_room = """
                UPDATE public.room
                SET state_id = 1  -- 'available'
                WHERE room_id = (
                    SELECT room_id
                    FROM public.booking
                    WHERE booking_id = %s
                );
            """
            cur.execute(query_update_room, (booking_id,))
            cur.execute(query_delete_booking, (booking_id,))
            conn.commit()

        return jsonify({"success": "Buchung erfolgreich storniert."}), 200
    except Exception as e:
        app.logger.error(f"Fehler beim Stornieren der Buchung: {e}")
        return jsonify({"error": "Fehler beim Stornieren der Buchung.", "details": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    app.run(debug=True, port=80)
