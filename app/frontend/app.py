import os
import random
import re
import pdfplumber
import requests
import smtplib
from factory import create_app, create_db_connection, debug_request
from flask import redirect, render_template, request, session, jsonify, flash
from datetime import datetime
from werkzeug.utils import secure_filename
import psycopg2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import qrcode
import pyotp
import io
import base64

app = create_app("frontend")

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

@app.route('/home')
def home():
    debug_request(request)

    app.logger.debug(f"Session-Daten: {session}")

    if 'user_type' in session:
        user_type = session['user_type'].strip()

        # Berechtigungen definieren
        permissions = {
            'student': ['create-booking', 'room-management','user-details'],
            'provider': ['anbietermgmt', 'user-details'],
            'admin': ['user-details','kundenmanagement', 'studentmgmt']
        }

        # Berechtigungen für den aktuellen Benutzer
        user_permissions = permissions.get(user_type, [])

        session['permissions'] = user_permissions

        app.logger.debug(f"Permissions for user {session['user']}: {user_permissions}")
        
        return render_template('home.html', user=session['user'], permissions=user_permissions)

    app.logger.warning("Benutzer ist nicht eingeloggt. Weiterleitung zur Login-Seite.")
    return render_template('login.html')

@app.route('/login')
def login():
    debug_request(request)
    return

@app.route('/get-session', methods=['GET'])
def get_session():
    """
    Gibt die aktuelle Session-Daten zurück, einschließlich user_id.
    """
    try:
        if 'user_id' in session:
            return jsonify({"user_id": session['user_id']}), 200
        return jsonify({"error": "Nicht eingeloggt"}), 401
    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Session-Daten: {e}")
        return jsonify({"error": "Ein Fehler ist aufgetreten"}), 500


@app.route('/anbietermgmt')
def anbietermgmt():
    try:
        user_id = session.get("user_id")
        if not user_id:
            return render_template('error.html', message="Benutzer ist nicht eingeloggt.")
        
        app.logger.debug(f"Session-Daten: {session}")
        
        conn = create_db_connection()
        with conn.cursor() as cur:
            # Benutzerinformationen abfragen
            query_user = """
                SELECT first_name, last_name, email
                FROM public."user"
                WHERE user_id = %s;
            """
            cur.execute(query_user, (user_id,))
            user_row = cur.fetchone()

            if not user_row:
                return render_template('error.html', message="Benutzerinformationen konnten nicht gefunden werden.")

            # Benutzerinformationen als Wörterbuch speichern
            user = {
                "first_name": user_row[0],
                "last_name": user_row[1],
                "email": user_row[2],
            }

        # Daten von der API abrufen
        response_rooms = requests.get(f'http://anbietermgmt.booking-app-main.svc.cluster.local/anbietermgmt?user_id={user_id}')
        response_summary = requests.get(f'http://anbietermgmt.booking-app-main.svc.cluster.local/room_summary?user_id={user_id}')

        if response_rooms.status_code == 200:
            rooms = response_rooms.json().get("rooms", [])
        else:
            app.logger.warning(f"Fehler beim Abrufen der Zimmerdaten im Frontend: {response_rooms.status_code}")
            rooms = []

        if response_summary.status_code == 200:
            summary = response_summary.json().get("summary", {})
        else:
            app.logger.warning(f"Fehler beim Abrufen der Zusammenfassung: {response_summary.status_code}")
            summary = {
                "available": 0,
                "pending": 0,
                "confirmed": 0,
                "completed": 0,
                "failed": 0
            }

        # Validierung der Room-Daten und Ergänzung fehlender Attribute
        for room in rooms:
            room['state_id'] = room.get('state_id', 1)
            room['state_name'] = room.get('state_name', "Available")
            room['zimmer_id'] = room.get('zimmer_id', None)
            room['date'] = room.get('date', "Unbekannt")
            room['firstname'] = room.get('firstname', "N/A")
            room['lastname'] = room.get('lastname', "N/A")

            # Sicherstellen, dass `state_id` numerisch ist
            if not isinstance(room['state_id'], int):
                room['state_id'] = 0

        app.logger.info(f"Anbietermanagement Line 125: {user}")
        # Weitergabe an das Template
        return render_template('room-management.html', rooms=rooms, summary=summary, user=user)

    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Zimmerdaten im Frontend Line 128: {e}")
        return render_template('error.html', message='Fehler beim Laden der Daten.')


@app.route('/add-room', methods=['POST'])
def add_room():
    try:
        # Hole die JSON-Daten aus der Anfrage
        data = request.json
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({'error': 'Benutzer ist nicht eingeloggt.'}), 401

        # Füge die User-ID zu den Daten hinzu
        data['user_id'] = user_id

        # Log die Daten, die gesendet werden
        app.logger.info(f"Zimmer hinzufügen: Daten, die an das Backend gesendet werden: {data}")

        # Anfrage an anbietermanagement.py weiterleiten
        response = requests.post('http://anbietermgmt.booking-app-main.svc.cluster.local/add-room', json=data, timeout=5)

        if response.status_code == 200:
            return jsonify(response.json())  # Erfolgreiche Rückmeldung vom Backend
        else:
            return jsonify({'error': 'Fehler beim Hinzufügen des Raums.'}), response.status_code
    except Exception as e:
        app.logger.error(f"Fehler beim Hinzufügen eines Raums: {e}")
        return jsonify({'error': 'Ein unerwarteter Fehler ist aufgetreten.', 'details': str(e)}), 500


@app.route('/booked-management')
def booked_management():
    """Zeigt dem Benutzer alle Zimmer, die er gebucht hat."""
    debug_request(request)
    try:
        # Hole die user_id aus der Session
        user_id = session.get('user_id')
        if not user_id:
            app.logger.error("Benutzer ist nicht eingeloggt.")
            return render_template('error.html', message='Benutzer ist nicht eingeloggt.')

        # API-Aufruf mit der user_id als Parameter
        response = requests.get(f'http://booked-management.booking-app-main.svc.cluster.local/booked-rooms?user_id={user_id}', timeout=5)
        if response.status_code == 200:
            rooms = response.json()
            app.logger.debug(f"Buchungen: {rooms}")

            # Datumsteilung
            current_date = datetime.now().date()
            future_bookings = [
                room for room in rooms if datetime.strptime(room['date'], "%Y-%m-%d").date() > current_date
            ]
            past_bookings = [
                room for room in rooms if datetime.strptime(room['date'], "%Y-%m-%d").date() <= current_date
            ]
        else:
            app.logger.error(f"Fehlerhafte API-Antwort: {response.status_code}")
            future_bookings = []
            past_bookings = []

        return render_template(
            'booked-management.html',
            future_bookings=future_bookings,
            past_bookings=past_bookings
        )
    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Buchungsübersicht: {e}")
        return render_template('error.html', message='Fehler beim Laden der Buchungsübersicht.')


@app.route('/rent')
def new_booking():
    debug_request(request)
    return render_template('rent.html')

@app.route('/rent', methods=['POST'])
def create_booking():
    debug_request(request)

    room = request.form['room']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "Benutzer ist nicht eingeloggt."}), 401

    try:
        # Datenbankverbindung herstellen
        conn = create_db_connection()
        cursor = conn.cursor()

        # Verifizierungsstatus des Benutzers abrufen
        cursor.execute("""
            SELECT verification
            FROM public."user"
            WHERE user_id = %s;
        """, (user_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Benutzer nicht gefunden."}), 404

        verification_status = result[0]

        if not verification_status == 't':
            # Benutzer ist nicht verifiziert
            return jsonify({
                "error": "Bitte verifizieren Sie Ihr Profil, bevor Sie eine Buchung vornehmen können.",
                "redirect": "/user-profile"
            }), 403

        # Buchungsdaten erstellen
        buchung = {
            'user': session.get('email', 'guest'),
            'room': room,
            'start_date': start_date,
            'end_date': end_date
        }

        app.logger.info(f"Buchung erstellt: {buchung['user']}, Zimmer: {buchung['room']}")
        app.logger.debug(buchung)

        # Anfrage an das Backend senden
        response_host = 'http://buchungsmanagement.booking-app-main.svc.cluster.local/' if request.host == 'localhost' else request.url_root
        response = requests.post(response_host + 'booking', json=buchung)
        response.raise_for_status()  # Fehler bei 4xx und 5xx auslösen

        return render_template('bestaetigung.html', buchung=buchung)

    except Exception as err:
        app.logger.error(f"Fehler beim Speichern der Buchung: {err}")
        return render_template('error.html', message='Fehler beim Speichern der Buchung.', error=str(err)), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/book-room', methods=['POST'])
def book_room():
    """
    Führt die Buchung in der Datenbank aus.
    """
    try:
        # Room- und Provider-Daten aus dem Request abrufen
        room_id = request.form.get('room_id')
        provider_id = request.form.get('provider_id')
        user_id = session.get('user_id')  # User ID aus der Session holen

        if not all([room_id, provider_id, user_id]):
            return jsonify({"error": "Fehlende Parameter für die Buchung."}), 400

        # Datenbankverbindung herstellen
        conn = create_db_connection()
        cursor = conn.cursor()

        # Nächste freie booking_id bestimmen
        cursor.execute("SELECT COALESCE(MAX(booking_id), 0) + 1 FROM public.booking;")
        booking_id = cursor.fetchone()[0]

        # Buchung in der Datenbank einfügen
        cursor.execute("""
            INSERT INTO public.booking (booking_id, user_id, room_id, state_id)
            VALUES (%s, %s, %s, %s);
        """, (booking_id, user_id, room_id, 2))  # state_id = 2 ("pending")

        # Änderungen speichern
        conn.commit()

        # Debugging: Daten loggen
        app.logger.info(f"Buchung erfolgreich: booking_id={booking_id}, user_id={user_id}, room_id={room_id}, state_id=2")

        return jsonify({"success": f"Buchung erfolgreich angefragt mit ID {booking_id}."}), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()  # Änderungen zurücksetzen, falls ein Fehler auftritt
        app.logger.error(f"Fehler bei der Buchung: {e}")
        return jsonify({"error": "Fehler bei der Buchung.", "details": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

#############################-USER PPROFILE #################################
UPLOAD_FOLDER = '/app/uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Datei-Upload erlauben
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/user-profile', methods=['GET'])
def user_profile():
    """Zeigt das Benutzerprofil basierend auf der user_id und Rolle."""
    debug_request(request)
    try:
        user_id = session.get('user_id')
        role_id = session.get('role_id')  # Rolle aus der Session holen
        if not user_id:
            app.logger.error("Keine user_id in der Session gefunden.")
            return render_template('error.html', message='Benutzer ist nicht eingeloggt.')

        conn = create_db_connection()
        with conn.cursor() as cur:
            # Benutzerinformationen aus der Tabelle "user" abrufen
            query_user = """
                SELECT first_name, last_name, email, verification, verification_date 
                FROM public."user"
                WHERE user_id = %s;
            """
            cur.execute(query_user, (user_id,))
            user_row = cur.fetchone()

            if not user_row:
                app.logger.warning(f"Keine Benutzerdetails für user_id {user_id} gefunden.")
                return render_template('error.html', message='Benutzerdetails nicht gefunden.')

            # Grundlegende Benutzerinformationen speichern
            user_data = {
                "firstname": user_row[0],
                "lastname": user_row[1],
                "email": user_row[2],
                "verification": "Ja" if user_row[3] else "Nein",
                "verification_date": user_row[4].strftime('%d.%m.%Y') if user_row[4] else "Nicht verfügbar",
                "role_id": role_id
            }

            # Adressinformationen aus der Tabelle "contact" abrufen
            query_contact = """
                SELECT address, postal_code, location, phone
                FROM public.contact
                WHERE contact_id = (
                    SELECT contact_id
                    FROM public.student
                    WHERE user_id = %s
                ) OR contact_id = (
                    SELECT contact_id
                    FROM public.accommodation
                    WHERE provider_id = (
                        SELECT provider_id
                        FROM public."user"
                        WHERE user_id = %s
                    )
                );
            """
            cur.execute(query_contact, (user_id, user_id))
            contact_row = cur.fetchone()

            if contact_row:
                user_data.update({
                    "adresse": contact_row[0],
                    "plz": contact_row[1],
                    "location": contact_row[2],
                    "phone": contact_row[3]
                })

            # Zusätzliche Logik basierend auf der Rolle
            if role_id == 3:  # Student
                query_student = """
                    SELECT student_number, university_id, enrollment_end
                    FROM public.student
                    WHERE user_id = %s;
                """
                cur.execute(query_student, (user_id,))
                student_row = cur.fetchone()

                if student_row:
                    user_data.update({
                        "matrikelnummer": student_row[0],
                        "inskription_end": student_row[2].strftime('%d.%m.%Y') if student_row[2] else "Nicht verfügbar"
                    })

                    # Universitätsinformationen abrufen
                    query_university = """
                        SELECT university_name, (SELECT address FROM public.contact WHERE contact_id = public.university.contact_id) AS address
                        FROM public.university
                        WHERE university_id = %s;
                    """
                    cur.execute(query_university, (student_row[1],))
                    university_row = cur.fetchone()

                    if university_row:
                        user_data.update({
                            "university": university_row[0],
                            "university_address": university_row[1]
                        })


            elif role_id == 2:  # Provider
                query_provider = """
                    SELECT company_name
                    FROM public.accommodation
                    WHERE provider_id = (
                        SELECT provider_id
                        FROM public."user"
                        WHERE user_id = %s
                    );
                """
                cur.execute(query_provider, (user_id,))
                provider_row = cur.fetchone()

                if provider_row:
                    user_data.update({
                        "company_name": provider_row[0]
                    })

            elif role_id == 1:  # Admin
                # Admin benötigt keine zusätzlichen Daten
                pass

        return render_template('user-profile.html', user=user_data)
    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen des Benutzerprofils: {e}")
        return render_template('error.html', message='Fehler beim Laden des Benutzerprofils.')
    finally:
        if 'conn' in locals():
            conn.close()



@app.route('/update-profile', methods=['POST'])
def update_profile():
    """Aktualisiert die bearbeitbaren Felder im Benutzerprofil."""
    try:
        user_id = session.get('user_id')
        role_id = session.get('role_id')  # Rolle des Benutzers
        if not user_id:
            return jsonify({'error': 'Benutzer ist nicht eingeloggt.'}), 401

        # Hole die aktualisierten Daten aus der Anfrage
        updated_data = request.json
        adresse = updated_data.get('adresse')
        plz = updated_data.get('plz')
        location = updated_data.get('location')
        email = updated_data.get('email')
        phone = updated_data.get('phone')

        app.logger.debug(f"Updated data received: {updated_data}")

        conn = create_db_connection()

        with conn.cursor() as cur:
            # Rollenbasiertes Update
            if role_id == 3:  # Student
                # Update der Adressinformationen in der Tabelle `contact`
                query_contact = """
                    UPDATE public.contact
                    SET address = %s,
                        postal_code = %s,
                        location = %s,
                        phone = %s
                    WHERE contact_id = (
                        SELECT contact_id
                        FROM public.student
                        WHERE user_id = %s
                    );
                """
                cur.execute(query_contact, (adresse, plz, location, phone, user_id))
                app.logger.debug(f"Contact info updated for Student: user_id={user_id}")

            elif role_id == 2:  # Provider
                # Update der Adressinformationen in der Tabelle `contact`
                query_contact = """
                    UPDATE public.contact
                    SET address = %s,
                        postal_code = %s,
                        location = %s,
                        phone = %s
                    WHERE contact_id = (
                        SELECT contact_id
                        FROM public.accommodation
                        WHERE provider_id = (
                            SELECT provider_id
                            FROM public."user"
                            WHERE user_id = %s
                        )
                    );
                """
                cur.execute(query_contact, (adresse, plz, location, phone, user_id))
                app.logger.debug(f"Contact info updated for Provider: user_id={user_id}")

            # Update der E-Mail-Adresse in der Tabelle `user`
            if email:
                query_email = """
                    UPDATE public."user"
                    SET email = %s
                    WHERE user_id = %s;
                """
                cur.execute(query_email, (email, user_id))
                app.logger.debug(f"Email updated for user_id={user_id}")

                # Überprüfen, ob die Änderung wirklich gespeichert wurde
                cur.execute("SELECT email FROM public.\"user\" WHERE user_id = %s;", (user_id,))
                updated_email = cur.fetchone()
                app.logger.debug(f"Updated email in DB: {updated_email}")

                # Aktualisiere die Session mit der neuen E-Mail
                session['email'] = email
                app.logger.debug(f"Session aktualisiert: {session}")

            conn.commit()
            app.logger.info("Database changes committed successfully.")

        return jsonify({'success': 'Profil erfolgreich aktualisiert.'}), 200

    except Exception as e:
        app.logger.error(f"Error while updating profile: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Profils.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()


def extract_data_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        extracted_data = {
            "name": None,
            "start_date": None,
            "matriculation_number": None,  # Jetzt die zweite 8-stellige Zahl
            "university_name": None
        }

        # Initialisiere die Variable vor der Verwendung
        is_interesting_section = False

        for page in pdf.pages:
            text_lines = page.extract_text().split('\n')

            for line in text_lines:
                # Universitätsname aus der Überschrift
                if not extracted_data["university_name"] and "Studienbestätigung" in line:
                    university_match = re.search(r"Studienbestätigung\s(.+)", line)
                    if university_match:
                        extracted_data["university_name"] = university_match.group(1).strip()

                # Interessante Zeilen beginnen nach "Personenkennzeichen Matrikelnummer"
                if "Personenkennzeichen Matrikelnummer" in line:
                    is_interesting_section = True  # Jetzt setzen
                    continue

                if is_interesting_section:
                    # Name extrahieren
                    if not extracted_data["name"]:
                        name_match = re.search(r"([A-ZÄÖÜ][a-zäöüß\-]+\s[A-ZÄÖÜ][a-zäöüß\-]+(?: BSc)?)", line)
                        if name_match:
                            extracted_data["name"] = name_match.group(1).strip()

                    # Suche die zweite 8-stellige Zahl nach der 10-stelligen Matrikelnummer
                    if not extracted_data["matriculation_number"]:
                        match = re.search(r"2\d{9}\s+(\d{8})", line)
                        if match:
                            extracted_data["matriculation_number"] = match.group(1).strip()

                    # Startdatum
                    if not extracted_data["start_date"]:
                        start_date_match = re.search(r"Beginn (\d{2}\.\d{2}\.\d{4})", line)
                        if start_date_match:
                            extracted_data["start_date"] = datetime.strptime(start_date_match.group(1), '%d.%m.%Y').date()

                if all(extracted_data.values()):
                    break

            if all(extracted_data.values()):
                break

        return extracted_data


def send_verification_email(user_email, extracted_data):
    """
    Sendet eine Bestätigungs-E-Mail nach dem Hochladen der PDF.
    """
    try:
        subject = "Ihre Daten zur Verifizierung wurden hochgeladen"
        body = f"""
        Sehr geehrte Damen und Herren,

        Ihre Inskriptionsbestätigung wurde erfolgreich hochgeladen und befindet sich nun in der Prüfung.

        Ihre hochgeladenen Daten:
        - Name: {extracted_data['name']}
        - Matrikelnummer: {extracted_data['matriculation_number']}
        - Universität: {extracted_data['university_name']}
        - Startdatum: {extracted_data['start_date']}

        Sie werden benachrichtigt, sobald die Prüfung abgeschlossen ist.

        Mit freundlichen Grüßen,
        Ihr Roomify-Team
        """
        send_email(user_email, subject, body)
        app.logger.info(f"Verification E-Mail an {user_email} gesendet.")
    except Exception as e:
        app.logger.error(f"Fehler beim Senden der E-Mail: {e}")



@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Keine Datei hochgeladen"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Keine Datei ausgewählt"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Daten aus der PDF extrahieren
        extracted_data = extract_data_from_pdf(file_path)
        if not all([extracted_data["name"], extracted_data["university_name"], extracted_data["matriculation_number"]]):
            return jsonify({"error": "PDF-Daten konnten nicht vollständig extrahiert werden."}), 400

        app.logger.debug(f"Extracted Data: {extracted_data}")

        try:
            conn = create_db_connection()
            cursor = conn.cursor()
            user_id = session.get('user_id')

            app.logger.debug(f"Session user_id: {user_id}")
            if not user_id:
                return jsonify({"error": "Session user_id fehlt"}), 400
            
            # Hole die E-Mail-Adresse des Benutzers aus der Datenbank
            cursor.execute("""
                SELECT email 
                FROM public."user" 
                WHERE user_id = %s
            """, (user_id,))
            user_email_row = cursor.fetchone()

            if not user_email_row:
                return jsonify({"error": "Benutzer-E-Mail nicht gefunden."}), 404

            user_email = user_email_row[0]
            app.logger.debug(f"Benutzer-E-Mail: {user_email}")

            # Prüfen, ob ein Eintrag existiert
            select_query = """
                SELECT start_date, verified 
                FROM uploaded_student_verification_tbl 
                WHERE user_id = %s
            """
            cursor.execute(select_query, (user_id,))
            existing_entry = cursor.fetchone()

            if existing_entry:
                existing_start_date, verified = existing_entry
                app.logger.debug(f"Vorhandenes Startdatum: {existing_start_date}, Verifiziert: {verified}")

                if extracted_data['start_date'] == existing_start_date:
                    if not verified:
                        return jsonify({"info": "Die Daten wurden bereits zur Verifizierung hochgeladen und sind noch in Prüfung."}), 200
                    else:
                        return jsonify({"info": "Die Daten sind bereits verifiziert und müssen nicht erneut hochgeladen werden."}), 200
                elif extracted_data['start_date'] > existing_start_date:
                    # Aktualisiere die Daten, falls das neue Datum aktueller ist
                    update_query = """
                        UPDATE uploaded_student_verification_tbl
                        SET name = %s, university_name = %s, start_date = %s, matriculation_number = %s, verified = %s
                        WHERE user_id = %s
                    """
                    cursor.execute(update_query, (
                        extracted_data['name'],
                        extracted_data['university_name'],
                        extracted_data['start_date'],
                        extracted_data['matriculation_number'],
                        False,  # Zurücksetzen auf nicht verifiziert
                        user_id,
                    ))
                    conn.commit()
                    send_verification_email(user_email, extracted_data)
                    return jsonify({"success": "Daten wurden erfolgreich aktualisiert.", "data": extracted_data}), 200
                else:
                    return jsonify({"info": "Die vorhandenen Daten sind aktueller. Kein Update notwendig."}), 200
            else:
                # Neuer Eintrag
                insert_query = """
                    INSERT INTO uploaded_student_verification_tbl (user_id, name, university_name, start_date, matriculation_number, verified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    user_id,
                    extracted_data['name'],
                    extracted_data['university_name'],
                    extracted_data['start_date'],
                    extracted_data['matriculation_number'],
                    False
                ))
                conn.commit()
                send_verification_email(user_email, extracted_data)
                return jsonify({"success": "Datei erfolgreich verarbeitet. Die Daten wurden nun zur Prüfung weitergeleitet.", "data": extracted_data}), 200

        except Exception as e:
            app.logger.error(f"Fehler beim Speichern in der Datenbank: {e}")
            return jsonify({"error": f"Fehler beim Speichern in der Datenbank: {e}"}), 500
        finally:
            if 'conn' in locals():
                conn.close()

    else:
        return jsonify({"error": "Ungültiger Dateityp"}), 400






####################-USER DETAILS-#######################################



@app.route('/user-details/<zimmer_id>', methods=['GET'])
def user_details(zimmer_id):
    """Zeigt Details eines Benutzers basierend auf der Zimmer-ID."""
    debug_request(request)
    try:
        conn = create_db_connection()
        with conn.cursor() as cur:
            # Schritt 1: user_id anhand der room_id (zimmer_id) aus der Tabelle "booking" abrufen
            query_user_id = """
                SELECT b.user_id 
                FROM public.booking b
                WHERE b.room_id = %s;
            """
            cur.execute(query_user_id, (zimmer_id,))
            user_id_row = cur.fetchone()
            
            if not user_id_row:
                app.logger.warning(f"Keine Buchung für room_id {zimmer_id} gefunden.")
                return render_template('error.html', message='Keine Buchung gefunden.')

            user_id = user_id_row[0]

            # Schritt 2: Benutzerinformationen aus der Tabelle "user" und "contact" abrufen
            query_user_details = """
                SELECT 
                    u.first_name,
                    u.last_name,
                    c.address,
                    c.postal_code,
                    c.location,
                    u.email,
                    c.phone,
                    u.verification
                FROM 
                    public."user" u
                LEFT JOIN 
                    public.contact c ON c.contact_id = (
                        SELECT contact_id
                        FROM public.student s
                        WHERE s.user_id = u.user_id
                        LIMIT 1
                    )
                WHERE 
                    u.user_id = %s;
            """
            cur.execute(query_user_details, (user_id,))
            user_row = cur.fetchone()

            if not user_row:
                app.logger.warning(f"Keine Benutzerdetails für user_id {user_id} gefunden.")
                return render_template('error.html', message='Benutzerdetails nicht gefunden.')

            # Benutzerinformationen in ein Wörterbuch konvertieren
            user_data = {
                "firstname": user_row[0],
                "lastname": user_row[1],
                "adresse": user_row[2] if user_row[2] else "Nicht verfügbar",
                "plz": user_row[3] if user_row[3] else "Nicht verfügbar",
                "location": user_row[4] if user_row[4] else "Nicht verfügbar",
                "email": user_row[5],
                "phone": user_row[6] if user_row[6] else "Nicht verfügbar",
                "verification": "Verifiziert" if user_row[7] else "Nicht verifiziert",
            }

        return render_template('user-details.html', user=user_data)
    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Benutzerdetails: {e}")
        return render_template('error.html', message='Fehler beim Laden der Benutzerdetails.')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/hotel-details/<int:zimmer_id>', methods=['GET'])
def hotel_details(zimmer_id):
    """
    Gibt Hotelinformationen basierend auf der Zimmer-ID zurück.
    """
    app.logger.debug(f"Empfangene Zimmer-ID: {zimmer_id}")

    try:
        conn = create_db_connection()
        with conn.cursor() as cur:
            # Schritt 1: provider_id aus room-Tabelle abrufen
            query_provider = """
                SELECT provider_id
                FROM public.room
                WHERE room_id = %s;
            """
            cur.execute(query_provider, (zimmer_id,))
            provider_row = cur.fetchone()

            if not provider_row:
                return jsonify({"error": "Zimmer-ID nicht gefunden."}), 404
            
            provider_id = provider_row[0]

            # Schritt 2: Hotelinformationen aus accommodation abrufen
            query_hotel = """
                SELECT 
                    a.company_name,
                    c.address,
                    c.postal_code,
                    c.location,
                    c.phone
                FROM public.accommodation a
                JOIN public.contact c ON a.contact_id = c.contact_id
                WHERE a.provider_id = %s;
            """
            cur.execute(query_hotel, (provider_id,))
            hotel_row = cur.fetchone()

            if not hotel_row:
                return jsonify({"error": "Hotelinformationen nicht gefunden."}), 404
            
            hotel_data = {
                "company_name": hotel_row[0],
                "address": hotel_row[1],
                "postal_code": hotel_row[2],
                "location": hotel_row[3],
                "phone": hotel_row[4],
            }

            # Schritt 3: Zusätzliche Anbieterinformationen aus user-Tabelle abrufen
            query_user = """
                SELECT 
                    email
                FROM public."user"
                WHERE provider_id = %s;
            """
            cur.execute(query_user, (provider_id,))
            user_row = cur.fetchone()

            if user_row:
                hotel_data.update({
                    "email": user_row[0]                    
                })

        return render_template('hotel-details.html', hotel=hotel_data)

    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Hotelinformationen: {e}")
        return jsonify({"error": "Ein Fehler ist aufgetreten.", "details": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()



@app.route('/kundenmanagement', methods=['GET'])
def kundenmanagement():
    """Ruft die Kundenliste über die API auf."""
    try:
        search_query = request.args.get('search', '')
        response = requests.get(f'http://kundenmanagement.booking-app-main.svc.cluster.local//kundenmanagement?search={search_query}')
        response.raise_for_status()

        data = response.json()
        users_list = data.get('users', [])
        search_query = data.get('search_query', '')

        return render_template(
            'kundenmanagement.html',
            users=users_list,
            search_query=search_query
        )
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Fehler beim Abrufen der Kundenmanagement-Daten: {e}")
        return render_template('error.html', message='Fehler beim Laden der Kundenmanagement-Daten.')


@app.route('/add-kunde', methods=['POST'])
def add_kunde():
    """Erfasst Kundendaten und sendet sie an den Backend-Service."""
    try:
        # Formulardaten erfassen
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        company_name = request.form.get('company_name')
        address = request.form.get('address')
        postal_code = request.form.get('postal_code')
        location = request.form.get('location')
        phone = request.form.get('phone')
        parking_available = request.form.get('parking') == "on"  # Checkbox: True/False

        # Validierung der Eingabewerte
        if not all([username, password, first_name, last_name, company_name, address, postal_code, location, phone]):
            return redirect('/kundenmanagement?status=error&message=Ungültige Eingabewerte.')

        # Daten für den Backend-Service vorbereiten
        data = {
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "company_name": company_name,
            "address": address,
            "postal_code": postal_code,
            "location": location,
            "phone": phone,
            "parking": parking_available,  
            "parking_free": False  # Standardwert für kostenlose Parkplätze
        }

        # Anfrage an Backend-Service senden
        response = requests.post(
            'http://kundenmanagement.booking-app-main.svc.cluster.local/add-kunde',
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        return redirect('/kundenmanagement?status=success')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Fehler beim Hinzufügen eines Kunden: {e}")
        return redirect(f'/kundenmanagement?status=error&message={e}')



@app.route('/edit-kunde/<int:user_id>', methods=['POST'])
def edit_kunde(user_id):
    """Sendet bearbeitete Kundendaten an die API."""
    try:
        data = {
            "username": request.form['username'],
            "company_name": request.form['company_name'],
            "adresse": request.form['adresse'],
            "postal_code": request.form['postal_code'],  
            "location": request.form['location'],
            "phone": request.form['phone']
        }

        response = requests.put(f'http://kundenmanagement.booking-app-main.svc.cluster.local/edit-kunde/{user_id}', json=data)
        response.raise_for_status()
        return redirect('/kundenmanagement')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Fehler beim Bearbeiten eines Kunden: {e}")
        return render_template('error.html', message='Fehler beim Bearbeiten des Kunden.')


@app.route('/delete-kunde/<int:user_id>', methods=['POST'])
def delete_kunde(user_id):
    """Sendet Löschanfrage an die API."""
    try:
        response = requests.delete(f'http://kundenmanagement.booking-app-main.svc.cluster.local/delete-kunde/{user_id}')
        response.raise_for_status()
        return redirect('/kundenmanagement')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Fehler beim Löschen eines Kunden: {e}")
        return render_template('error.html', message='Fehler beim Löschen des Kunden.')


###### STUDENT MANAGEMENT ########
@app.route('/studentmgmt', methods=['GET'])
def studentmgmt():
    """Rendert die Studentenmanagement-Seite für den Admin."""
    try:
        response = requests.get('http://kundenmanagement.booking-app-main.svc.cluster.local/student-verifications')
        if response.status_code == 200:
            data = response.json()
            app.logger.info(f"Empfangene Verifizierungsdaten: {data}")  # Debugging
            return render_template(
                'student-management.html',
                pending_students=data.get('pending_students', []),
                verified_students=data.get('verified_students', [])
            )
        else:
            return render_template('error.html', message="Fehler beim Abrufen der Studentenverifizierungen.")
    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Studentenverifizierungen: {e}")
        return render_template('error.html', message="Ein Fehler ist aufgetreten.")

############ FAQ #########################


@app.route('/get-faq', methods=['GET'])
def get_faq():
    # Lade Berechtigungen aus der Session und stelle sicher, dass sie korrekt sind
    user_permissions = session.get('permissions', [])
    app.logger.debug(f"User permissions: {user_permissions}")

    # Die Struktur der FAQs vorbereiten
    faqs = {"Allgemein": [], "Studierende": [], "Anbieter": []}

    try:
        with open('FAQ.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            section = None

            for line in lines:
                line = line.strip()

                # Abschnittswechsel basierend auf den Titeln
                if line == "Allgemein:":
                    section = "Allgemein"
                    continue
                elif line == "Für Studierende:":
                    section = "Studierende"
                    continue
                elif line == "Für Anbieter:innen:":
                    section = "Anbieter"
                    continue

                # Inhalte zu den entsprechenden Abschnitten hinzufügen
                if section == "Allgemein":
                    faqs["Allgemein"].append(line)
                elif section == "Studierende" and 'create-booking' in user_permissions:
                    faqs["Studierende"].append(line)
                elif section == "Anbieter" and 'anbietermgmt' in user_permissions:
                    faqs["Anbieter"].append(line)
                elif 'studentmgmt' in user_permissions:
                    faqs["Studierende"].append(line)
                    faqs["Anbieter"].append(line)

        # Gib die gefilterten FAQs als JSON zurück
        return jsonify({"faqs": faqs})

    except Exception as e:
        app.logger.error(f"Error reading FAQ file: {e}")
        return jsonify({"error": "Failed to load FAQs"}), 500

### Sending EMAIL after booking #######

@app.route('/send-booking-email', methods=['POST'])
def send_booking_email():
    """
    Sendet eine Benachrichtigungs-E-Mail.
    """
    try:
        app.logger.info("E-Mail-Sendefunktion aufgerufen.")
        
        # Buchungsinformationen abrufen
        booking_id = request.form.get('booking_id')
        booking_date = request.form.get('booking_date')
        recipient_email = request.form.get('recipient_email')
        is_user = request.form.get('is_user', False)

        if not all([booking_id, booking_date, recipient_email]):
            return jsonify({"error": "Buchungsdaten fehlen."}), 400

        # Abhängig vom Empfänger unterschiedliche Inhalte erstellen
        if is_user:  # E-Mail an den Bucher
            subject = f"Buchungsanfrage eingegangen: {booking_id}"
            body = f"""
            Sehr geehrter Nutzer,

            Ihre Buchungsanfrage wurde erfolgreich eingereicht.
            Buchungs-ID: {booking_id}
            Datum: {booking_date}

            Sie erhalten in Kürze eine Rückmeldung von dem Anbieter.

            Mit freundlichen Grüßen,
            Ihr Roomify-Team
            """
        else:  # E-Mail an den Anbieter
            subject = f"Buchungsbenachrichtigung: Buchungs-ID {booking_id}"
            body = f"""
            Sehr geehrter Anbieter,

            Sie haben eine neue Buchungsanfrage erhalten.
            Buchungs-ID: {booking_id}
            Buchungsdatum: {booking_date}

            Bitte loggen Sie sich in Ihr Anbieterportal ein, um weitere Details zur Buchung einzusehen.

            Mit freundlichen Grüßen,
            Ihr Roomify-Team
            """

        # E-Mail versenden
        sender_email = "roomify.customerservice@gmail.com"
        sender_password = "dsnhlmmkgnwuksfv"
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        app.logger.info(f"E-Mail erfolgreich an {recipient_email} gesendet.")
        return jsonify({"success": f"E-Mail erfolgreich an {recipient_email} gesendet."}), 200

    except Exception as e:
        app.logger.error(f"Fehler beim Senden der E-Mail: {e}")
        return jsonify({"error": f"Fehler beim Senden der E-Mail: {e}"}), 500

#######REGISTRIERUNGSPROZESS ###############

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Wenn GET, dann die HTML-Seite für die Registrierung rendern
        return render_template('register.html')

    if request.method == 'POST':
        # POST-Logik für die Registrierung
        data = request.json
        role = data.get('role')  # 'student' oder 'anbieter'
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')

        # Standardmäßig ist local_user = False
        local_user = data.get('local_user', False)

        try:
            conn = create_db_connection()
            with conn.cursor() as cur:
                # Neue Benutzer-ID abrufen
                cur.execute("SELECT COALESCE(MAX(user_id), 0) + 1 FROM public.\"user\"")
                new_user_id = cur.fetchone()[0]

                # TOTP-Secret für den Benutzer generieren
                totp_secret = pyotp.random_base32()

                # Benutzer in die Datenbank einfügen
                cur.execute("""
                    INSERT INTO public."user" 
                    (user_id, role_id, username, password, first_name, last_name, email, local_user, verification, verification_date, oauth_token) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    new_user_id,
                    3 if role == 'student' else 2,  # 3 = Student, 2 = Anbieter
                    username,
                    password,
                    first_name,
                    last_name,
                    email,
                    local_user,
                    False,  # verification
                    None,   # verification_date
                    totp_secret
                ))

                conn.commit()
            
            # Registrierungsbestätigungsmail senden
            subject = "Willkommen bei Roomify!"
            body = f"""
            Sehr geehrte, Sehr geehrter {first_name} {last_name},

            Vielen Dank für Ihre Registrierung bei Roomify! Wir freuen uns, Sie als {role} an Bord zu haben.

            Ihr Benutzername: {username}

            Bitte beachten Sie, dass Sie sich bei Ihrem Login mithilfe der Zwei-Faktor-Authentifizierung (2FA) verifizieren müssen.

            Anschließend müssen Sie sich mit Hilfe Ihrer Inskriptionsbestätigung Ihrer Hochschule unter " Mein Profil " als Student verifizieren. 

            Mit freundlichen Grüßen,
            Ihr Roomify-Team
            """
            send_email(email, subject, body)

            # Wenn local_user = True, überspringe 2FA
            if local_user:
                return jsonify({
                    'message': 'Registrierung erfolgreich',
                    'redirect': '/home'
                })

           # Session leeren, um nicht eingeloggt zu sein
            session.clear()

            # Weiterleitung zur Startseite
            return jsonify({
                'message': 'Registrierung erfolgreich',
                'redirect': '/home'
            })


        except Exception as e:
            app.logger.error(f"Fehler bei der Registrierung: {e}")
            return jsonify({'error': 'Interner Serverfehler'}), 500
        finally:
            if 'conn' in locals():
                conn.close()



@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    user_id = session.get('user_id')  # Benutzer-ID aus der Session
    if not user_id:
        return redirect('/login')  # Benutzer nicht eingeloggt -> zurück zum Login

    try:
        conn = create_db_connection()
        with conn.cursor() as cur:
            # Abrufen des TOTP-Secrets (oauth_token) aus der Datenbank
            cur.execute("""
                SELECT oauth_token FROM public."user"
                WHERE user_id = %s
            """, (user_id,))
            user = cur.fetchone()

            if not user or not user[0]:
                app.logger.error("Benutzer oder oauth_token nicht gefunden.")
                return redirect('/login')  # Benutzer nicht gefunden oder kein Token

            totp_secret = user[0]  # TOTP-Secret (oauth_token)
            totp = pyotp.TOTP(totp_secret)

            # POST: Benutzer gibt den 2FA-Code ein
            if request.method == 'POST':
                user_code = request.form.get('code')

                # Überprüfen, ob der eingegebene Code korrekt ist
                if totp.verify(user_code):
                    session.pop('qr_code_url', None)  # QR-Code-URL aus Session löschen
                    return redirect('/home')  # Login erfolgreich

                return render_template('2fa.html', error="Falscher Code.", qr_code_url=session.get('qr_code_url'))

            # GET: QR-Code einmalig generieren, falls nötig
            if 'qr_code_url' not in session:
                provisioning_uri = totp.provisioning_uri(
                    name=session.get('email'),
                    issuer_name="Roomify"
                )
                # QR-Code generieren und als Base64-URL speichern
                qr_image = qrcode.make(provisioning_uri)
                qr_buffer = io.BytesIO()
                qr_image.save(qr_buffer, format="PNG")
                qr_buffer.seek(0)
                qr_code_base64 = base64.b64encode(qr_buffer.read()).decode('utf-8')
                session['qr_code_url'] = f"data:image/png;base64,{qr_code_base64}"

            # QR-Code anzeigen
            return render_template('2fa.html', qr_code_url=session['qr_code_url'])

    except Exception as e:
        app.logger.error(f"Fehler bei der 2FA-Überprüfung: {e}")
        return jsonify({'error': 'Interner Serverfehler'}), 500
    finally:
        if 'conn' in locals():
            conn.close()





if __name__ == '__main__':
    app.run(debug=True, port=80)
