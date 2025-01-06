from datetime import datetime, timedelta
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        remove_old_rooms() #alte Zimmer enfernen die auf available waren
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

            rooms = []
            for row in rows:
                rooms.append({
                    "zimmer_id": row[0],
                    "date": row[1].strftime('%Y-%m-%d') if row[1] else "Nicht verfügbar",
                    "state_name": row[2],
                    "state_id": row[3],
                    "booking_id": row[4],
                    "firstname": row[5] or "-",
                    "lastname": row[6] or "-",
                })

            return jsonify({"rooms": rooms}), 200

    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Zimmerdaten in Anbietermanagement: {e}")
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



# API zum Hinzufügen von Zimmern
@app.route('/add-room', methods=['POST'])
def add_room():
    """Verarbeitet das Hinzufügen eines neuen Zimmers."""
    try:
        data = request.json
        user_id = data.get("user_id")
        date = data.get("date")
        num_rooms = data.get("num_rooms")  # Anzahl der Zimmer

        # Validierung der Eingabewerte
        if not user_id or not date or not num_rooms:
            return jsonify({'error': 'Ungültige Eingabewerte: User-ID, Datum oder Anzahl der Zimmer fehlt.'}), 400

        # Konvertier num_rooms zu Integer
        try:
            num_rooms = int(num_rooms)
        except ValueError:
            return jsonify({'error': 'Ungültige Anzahl von Zimmern, muss eine Zahl sein.'}), 400

        conn = create_db_connection()
        with conn.cursor() as cur:
            # Provider-ID anhand der User-ID abrufen
            query_provider_id = """
                SELECT provider_id
                FROM public."user"
                WHERE user_id = %s;
            """
            cur.execute(query_provider_id, (user_id,))
            provider_row = cur.fetchone()

            if not provider_row:
                return jsonify({'error': 'Kein Anbieter für diesen Benutzer gefunden.'}), 400

            provider_id = provider_row[0]

            query_next_room_id = """
                SELECT COALESCE(MAX(room_id), 0) + 1 AS next_room_id
                FROM public.room;
            """
            cur.execute(query_next_room_id)
            next_room_id = cur.fetchone()[0]

            # Einfügen des neuen Raums in die Tabelle
            query_insert_room = """
                INSERT INTO public.room (room_id, provider_id, date, state_id)
                VALUES (%s, %s, %s, 1);
            """
            cur.execute(query_insert_room, (next_room_id, provider_id, date))
            conn.commit()

        return jsonify({'success': f'{num_rooms} Zimmer erfolgreich hinzugefügt.'}), 200
    except Exception as e:
        app.logger.error(f"Fehler beim Hinzufügen der Zimmer: {e}")
        return jsonify({'error': 'Fehler beim Hinzufügen der Zimmer.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    """Bestätigt eine Buchung und sendet eine E-Mail-Bestätigung an den Studenten."""
    try:
        booking_id = request.json.get('booking_id')
        if not booking_id:
            return jsonify({'error': 'Buchungs-ID fehlt'}), 400

        conn = create_db_connection()
        with conn.cursor() as cur:
            # Benutzer-E-Mail anhand der Buchungs-ID abrufen
            query = """
                SELECT u.email
                FROM public.booking b
                JOIN public."user" u ON b.user_id = u.user_id
                WHERE b.booking_id = %s;
            """
            cur.execute(query, (booking_id,))
            user_row = cur.fetchone()

            if not user_row:
                return jsonify({'error': 'Benutzer-E-Mail nicht gefunden'}), 404

            user_email = user_row[0]

            # Buchungsstatus aktualisieren
            update_query = """
                UPDATE public.booking
                SET state_id = 3  -- Status "confirmed"
                WHERE booking_id = %s;
            """
            cur.execute(update_query, (booking_id,))
            conn.commit()

        # E-Mail senden
        subject = "Buchungsbestätigung"
        body = f"""
        Sehr geehrte/r Student/in,

        Ihre Buchung mit der ID {booking_id} wurde vom Anbieter bestätigt. Der Anbieter freut sich darauf, Sie willkommen zu heißen.

        Mit freundlichen Grüßen,
        Ihr Roomify-Team
        """
        send_email(user_email, subject, body)

        return jsonify({'success': 'Buchung erfolgreich bestätigt und E-Mail gesendet.'}), 200

    except Exception as e:
        app.logger.error(f"Fehler beim Bestätigen der Buchung: {e}")
        return jsonify({'error': 'Fehler beim Bestätigen der Buchung.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()



@app.route('/reject-booking', methods=['POST'])
def reject_booking():
    """Lehnt eine Buchung ab, fügt die Ablehnung in die Tabelle 'cancelled_bookings' ein und löscht die Buchung."""
    try:
        booking_id = request.json.get('booking_id')
        rejection_message = request.json.get('rejection_message', '')

        if not booking_id:
            return jsonify({'error': 'Buchungs-ID fehlt'}), 400

        if not rejection_message:
            rejection_message = "Ihre Buchung wurde vom Anbieter abgelehnt. Bitte kontaktieren Sie uns für weitere Informationen."

        conn = create_db_connection()
        with conn.cursor() as cur:
            # Hole die Buchungsdetails, um sie in die Cancelled-Log-Tabelle einzufügen
            query_booking_details = """
                SELECT b.room_id, u.first_name, u.last_name, bs.state_name
                FROM public.booking b
                JOIN public."user" u ON b.user_id = u.user_id
                JOIN public.booking_state bs ON b.state_id = bs.state_id
                WHERE b.booking_id = %s;
            """
            cur.execute(query_booking_details, (booking_id,))
            booking_details = cur.fetchone()

            if not booking_details:
                return jsonify({'error': 'Buchungsdetails nicht gefunden'}), 404

            room_id, first_name, last_name, state_name = booking_details

            # Ablehnungsgrund in die Cancelled-Bookings-Tabelle einfügen
            insert_cancelled_booking_query = """
                INSERT INTO public.cancelled_bookings (
                    room_id, rejection_reason, student_first_name, student_last_name, booking_status
                ) VALUES (%s, %s, %s, %s, %s);
            """
            cur.execute(insert_cancelled_booking_query, (
                room_id, rejection_message, first_name, last_name, state_name
            ))

            # Benutzer-E-Mail anhand der Buchungs-ID abrufen
            query = """
                SELECT u.email
                FROM public.booking b
                JOIN public."user" u ON b.user_id = u.user_id
                WHERE b.booking_id = %s;
            """
            cur.execute(query, (booking_id,))
            user_row = cur.fetchone()

            if not user_row:
                return jsonify({'error': 'Benutzer-E-Mail nicht gefunden'}), 404

            user_email = user_row[0]

            # Lösche die Buchung aus der Tabelle 'booking'
            delete_booking_query = """
                DELETE FROM public.booking
                WHERE booking_id = %s;
            """
            cur.execute(delete_booking_query, (booking_id,))

            # Setze den Status des Zimmers auf "available"
            update_room_query = """
                UPDATE public.room
                SET state_id = 1 -- Status "available"
                WHERE room_id = %s;
            """
            cur.execute(update_room_query, (room_id,))

            conn.commit()

        # E-Mail senden
        subject = "Buchungsablehnung"
        body = f"""
        Sehr geehrte/r Student/in,

        Leider wurde Ihre Buchung mit der ID {booking_id} abgelehnt.

        Grund: {rejection_message}

        Mit freundlichen Grüßen,
        Ihr Roomify-Team
        """
        send_email(user_email, subject, body)

        return jsonify({'success': 'Buchung erfolgreich abgelehnt und E-Mail gesendet.'}), 200

    except Exception as e:
        app.logger.error(f"Fehler beim Ablehnen der Buchung: {e}")
        return jsonify({'error': 'Fehler beim Ablehnen der Buchung.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()





def send_email(to_email, subject, body):
    """Hilfsfunktion zum Senden von E-Mails."""
    sender_email = "roomify.customerservice@gmail.com"
    sender_password = "dsnhlmmkgnwuksfv"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())

@app.route('/remove-old-rooms', methods=['POST'])
def remove_old_rooms():
    """Bereinigt alte Buchungen und Zimmer basierend auf ihrem Alter."""
    try:
        conn = create_db_connection()
        with conn.cursor() as cur:
            # Schritt 1: Lösche Buchungen älter als "Heute - 2 Tage"
            delete_old_bookings_query = """
            DELETE FROM public.booking
            WHERE room_id IN (
                SELECT room_id
                FROM public.room
                WHERE date < (CURRENT_DATE - INTERVAL '2 days')
            );
            """
            cur.execute(delete_old_bookings_query)

            # Schritt 2: Markiere Zimmer, die zwischen "Heute - 2 Tage" und "Heute" liegen, als "failed"
            update_failed_rooms_query = """
            UPDATE public.room
            SET state_id = 5 -- Status "failed"
            WHERE state_id = 1 -- Status "available"
            AND date < CURRENT_DATE;
            """
            cur.execute(update_failed_rooms_query)

            # Schritt 3: Lösche Zimmer, die älter sind als "Heute - 2 Tage"
            delete_old_rooms_query = """
            DELETE FROM public.room
            WHERE date < (CURRENT_DATE - INTERVAL '2 days');
            """
            cur.execute(delete_old_rooms_query)

            # Änderungen speichern
            conn.commit()

        return jsonify({'success': 'Veraltete Zimmer und Buchungen erfolgreich bereinigt.'}), 200

    except Exception as e:
        app.logger.error(f"Fehler beim Bereinigen der Zimmerdaten: {e}")
        return jsonify({'error': 'Fehler beim Bereinigen der Zimmerdaten.', 'details': str(e)}), 500

    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/cancelled-bookings', methods=['GET'])
def get_cancelled_bookings():
    """Gibt eine Liste der stornierten Buchungen zurück."""
    try:
        conn = create_db_connection()
        with conn.cursor() as cur:
            query = """
            SELECT room_id, rejection_reason, student_first_name, student_last_name, booking_status, cancellation_date
            FROM public.cancelled_bookings
            ORDER BY cancellation_date DESC;
            """
            cur.execute(query)
            rows = cur.fetchall()

            cancelled_bookings = []
            for row in rows:
                cancelled_bookings.append({
                    "room_id": row[0],
                    "rejection_reason": row[1],
                    "student_first_name": row[2],
                    "student_last_name": row[3],
                    "booking_status": row[4],
                    "cancellation_date": row[5].strftime('%Y-%m-%d %H:%M:%S'),
                })

            return jsonify({"cancelled_bookings": cancelled_bookings}), 200

    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der stornierten Buchungen: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der stornierten Buchungen.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()




if __name__ == '__main__':
    app.run(debug=True, port=80)
