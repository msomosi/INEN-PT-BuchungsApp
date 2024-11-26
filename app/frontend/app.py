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
            'student': ['create-booking', 'room-management','bookingmgmt','user-details'],
            'anbieter': ['room-management', 'anbietermgmt', 'user-details', 'bookingmgmt'],
            'admin': ['create-booking', 'room-management', 'anbietermgmt', 'user-details', 'bookingmgmt']
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


@app.route('/user-details/<id>')
def user_details(id = "1"):
    debug_request(request)
    try:
        path = "user/" + id
        response_host = 'http://login/' if request.host == 'localhost' else request.url_root
        app.logger.debug(response_host + path)
        response = requests.get(response_host + path)
        app.logger.debug(response)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
    except Exception as err:
        app.logger.error(f"Fehler beim Laden der Buchungen: {err}")
        data = []

    return render_template('user-details.html', user=data)

@app.route('/get-users', methods=['GET'])
def get_users():
    try:
        app.logger.info("Route /get-users aufgerufen")
        conn = create_db_connection()
        app.logger.info("Datenbankverbindung erfolgreich")

        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.user_id, u.username, ud."Firstname", ud."Lastname", r.role_name
            FROM tbl_user u
            JOIN tbl_user_details ud ON u.user_id = ud.user_id
            JOIN tbl_rolle r ON u.role_id = r.role_id
        """)
        users = cursor.fetchall()
        app.logger.info(f"Abfrage erfolgreich, {len(users)} Benutzer gefunden")

        user_list = []
        for user_id, username, firstname, lastname, role_name in users:
            user_list.append({
                "user_id": user_id,
                "username": username,
                "name": f"{firstname} {lastname}",
                "role": role_name
            })

        return jsonify(user_list)
    except Exception as err:
        app.logger.error(f"Fehler beim Abrufen der Benutzer: {err}")
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()



if __name__ == '__main__':
    app.run(debug=True, port=80)
