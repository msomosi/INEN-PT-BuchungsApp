import requests
from factory import create_app, create_db_connection, debug_request
from flask import redirect, render_template, request, session, jsonify
from datetime import datetime

app = create_app("frontend")

@app.route('/home')
def home():
    debug_request(request)

    app.logger.debug(f"Session-Daten: {session}")

    if 'user_type' in session:
        user_type = session['user_type'].strip()

        # Berechtigungen definieren
        permissions = {
            'student': ['create-booking', 'room-management','user-details'],
            'anbieter': ['anbietermgmt', 'user-details'],
            'admin': ['user-details','kundenmanagement']
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

@app.route('/anbietermgmt')
def anbietermgmt():
    try:
        # Daten von der API abrufen
        response_rooms = requests.get('http://anbietermgmt/anbietermgmt')
        response_summary = requests.get('http://anbietermgmt/room_summary')

        # Prüfen, ob die API erfolgreich Daten zurückgegeben hat
        rooms = response_rooms.json() if response_rooms.status_code == 200 else []
        summary = response_summary.json() if response_summary.status_code == 200 else {
            "available": 0,
            "pending": 0,
            "booked": 0
        }

        # Weitergabe an das Template
        return render_template('room-management.html', rooms=rooms, summary=summary)
    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Zimmerdaten: {e}")
        return render_template('error.html', message='Fehler beim Laden der Daten.')


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
        response = requests.get(f'http://booked-management/booked-rooms?user_id={user_id}', timeout=5)
        if response.status_code == 200:
            rooms = response.json()
            app.logger.debug(f"Buchungen: {rooms}")

            # Datumsteilung
            current_date = datetime.now().date()
            future_bookings = [
                room for room in rooms if datetime.strptime(room['date'], "%a, %d %b %Y %H:%M:%S %Z").date() > current_date
            ]
            past_bookings = [
                room for room in rooms if datetime.strptime(room['date'], "%a, %d %b %Y %H:%M:%S %Z").date() <= current_date
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
    days = request.form['days']

    # Erstellen des Buchungsobjekts
    buchung = {
        'user': session.get('email', 'guest'),
        'room': room,
        'start_date': start_date,
        'end_date': end_date,
        'days': days
    }

    app.logger.info(f"Buchung erstellt: {buchung['user']}, Zimmer: {buchung['room']}")
    app.logger.debug(buchung)

    try:
        response_host = 'http://buchungsmanagement/' if request.host == 'localhost' else request.url_root
        app.logger.debug(response_host + 'booking')
        response = requests.post(response_host + 'booking', json=buchung)
        app.logger.debug(response)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    except Exception as err:
        app.logger.error(f"Fehler beim Speichern der Buchung: {err}")
        return render_template('error.html', message='Fehler beim Speichern der Buchung.', error=str(err)), 500

    return render_template('bestaetigung.html', buchung=buchung)


@app.route('/user-profile', methods=['GET'])
def user_profile():
    """Zeigt das Benutzerprofil basierend auf der user_id aus der Session."""
    debug_request(request)
    try:
        user_id = session.get('user_id')
        role_id = session.get('role_id')  # Rolle aus der Session holen
        if not user_id:
            app.logger.error("Keine user_id in der Session gefunden.")
            return render_template('error.html', message='Benutzer ist nicht eingeloggt.')

        conn = create_db_connection()
        with conn.cursor() as cur:
            query = """
                SELECT 
                    user_id, "Firstname", "Lastname", "CompanyName", "Matrikelnummer", 
                    "University", "Inskription_end", "Adresse", "Plz", "Location", 
                    email, phone
                FROM 
                    tbl_user_details
                WHERE 
                    user_id = %s;
            """
            cur.execute(query, (user_id,))
            row = cur.fetchone()

            if not row:
                app.logger.warning(f"Keine Benutzerdetails für user_id {user_id} gefunden.")
                return render_template('error.html', message='Benutzerdetails nicht gefunden.')

            # Benutzerinformationen in ein Wörterbuch konvertieren
            user_data = {
                "user_id": row[0],
                "firstname": row[1],
                "lastname": row[2],
                "company_name": row[3],
                "matrikelnummer": row[4],
                "university": row[5],
                "inskription_end": row[6],
                "adresse": row[7],
                "plz": row[8],
                "location": row[9],
                "email": row[10],
                "phone": row[11],
                "role_id": role_id  # Rolle in die Benutzerdaten einfügen
            }

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
        if not user_id:
            app.logger.error("Keine user_id in der Session gefunden.")
            return jsonify({'error': 'Benutzer ist nicht eingeloggt.'}), 401

        # Hole die aktualisierten Daten aus dem Formular
        updated_data = {
            "adresse": request.form.get('adresse'),
            "plz": request.form.get('plz'),
            "location": request.form.get('location'),
            "email": request.form.get('email'),
            "phone": request.form.get('phone')
        }

        # Verarbeite die Änderungen
        conn = create_db_connection()
        with conn.cursor() as cur:
            query = """
                UPDATE tbl_user_details
                SET 
                    "Adresse" = %s,
                    "Plz" = %s,
                    "Location" = %s,
                    email = %s,
                    phone = %s
                WHERE user_id = %s;
            """
            cur.execute(query, (
                updated_data['adresse'], 
                updated_data['plz'], 
                updated_data['location'], 
                updated_data['email'], 
                updated_data['phone'], 
                user_id
            ))
            conn.commit()

        app.logger.info(f"Benutzerdetails für user_id {user_id} erfolgreich aktualisiert.")
        return jsonify({'success': 'Profil erfolgreich aktualisiert.'}), 200
    except Exception as e:
        app.logger.error(f"Fehler beim Aktualisieren des Profils: {e}")
        return jsonify({'error': 'Fehler beim Aktualisieren des Profils.'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/user-details/<zimmer_id>', methods=['GET'])
def user_details(zimmer_id):
    """Zeigt Details eines Benutzers basierend auf der Zimmer-ID."""
    debug_request(request)
    try:
        conn = create_db_connection()
        with conn.cursor() as cur:
            # Schritt 1: user_id anhand der zimmer_id aus tbl_buchung abrufen
            query_user_id = """
                SELECT user_id 
                FROM tbl_buchung 
                WHERE zimmer_id = %s;
            """
            cur.execute(query_user_id, (zimmer_id,))
            user_id_row = cur.fetchone()
            
            if not user_id_row:
                app.logger.warning(f"Keine Buchung für zimmer_id {zimmer_id} gefunden.")
                return render_template('error.html', message='Keine Buchung gefunden.')

            user_id = user_id_row[0]

            # Schritt 2: Benutzerinformationen aus tbl_user_details und tbl_user abrufen
            query_user_details = """
                SELECT 
                    ud."Firstname", ud."Lastname", ud."Adresse", ud."Plz", 
                    ud."Location", ud.email, ud.phone, u.verification, 
                    u.verification_date
                FROM 
                    tbl_user_details ud
                JOIN 
                    tbl_user u ON ud.user_id = u.user_id
                WHERE 
                    ud.user_id = %s;
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
                "adresse": user_row[2],
                "plz": user_row[3],
                "location": user_row[4],
                "email": user_row[5],
                "phone": user_row[6],
                "verification": "Verifiziert" if user_row[7] else "Nicht verifiziert",
                "verification_date": user_row[8].strftime('%Y-%m-%d') if user_row[8] else "Nicht verfügbar"
            }

        return render_template('user-details.html', user=user_data)
    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Benutzerdetails: {e}")
        return render_template('error.html', message='Fehler beim Laden der Benutzerdetails.')
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/kundenmanagement', methods=['GET'])
def kundenmanagement():
    """Ruft die Kundenliste über die API auf."""
    try:
        search_query = request.args.get('search', '')
        response = requests.get(f'http://kundenmanagement/kundenmanagement?search={search_query}')
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
    """Sendet neue Kundendaten an die API."""
    try:
        data = {
            "username": request.form['username'],
            "password": request.form['password'],
            "company_name": request.form['company_name'],
            "adresse": request.form['adresse'],
            "postal_code": request.form['postal_code'],  
            "location": request.form['location'],
            "phone": request.form['phone']
        }


        # Sende die Daten als JSON und setze den Content-Type korrekt
        response = requests.post(
            'http://kundenmanagement/add-kunde',
            json=data,  # Daten im JSON-Format
            headers={"Content-Type": "application/json"}  # Sicherstellen des Content-Types
        )
        response.raise_for_status()
        return redirect('/kundenmanagement')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Fehler beim Hinzufügen eines Kunden: {e}")
        return render_template('error.html', message='Fehler beim Hinzufügen des Kunden.')




@app.route('/edit-kunde/<int:user_id>', methods=['POST'])
def edit_kunde(user_id):
    """Sendet bearbeitete Kundendaten an die API."""
    try:
        data = {
            "username": request.form['username'],
            "company_name": request.form['company_name'],
            "adresse": request.form['adresse'],
            "postal_code": request.form['postal_code'],  # Hinzufügen von postal_code
            "location": request.form['location'],
            "phone": request.form['phone']
        }

        response = requests.put(f'http://kundenmanagement/edit-kunde/{user_id}', json=data)
        response.raise_for_status()
        return redirect('/kundenmanagement')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Fehler beim Bearbeiten eines Kunden: {e}")
        return render_template('error.html', message='Fehler beim Bearbeiten des Kunden.')


@app.route('/delete-kunde/<int:user_id>', methods=['POST'])
def delete_kunde(user_id):
    """Sendet Löschanfrage an die API."""
    try:
        response = requests.delete(f'http://kundenmanagement/delete-kunde/{user_id}')
        response.raise_for_status()
        return redirect('/kundenmanagement')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Fehler beim Löschen eines Kunden: {e}")
        return render_template('error.html', message='Fehler beim Löschen des Kunden.')





if __name__ == '__main__':
    app.run(debug=True, port=80)
