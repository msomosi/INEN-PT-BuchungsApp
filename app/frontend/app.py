import requests
from factory import create_app, create_db_connection, debug_request
from flask import redirect, render_template, request, session

app = create_app("frontend")

@app.route('/home')
def home():
    debug_request(request)

    if 'user_type' in session:
        user_type = session['user_type']

        # Berechtigungen definieren
        permissions = {
            'student': ['create-booking', 'room-management', 'user-details'],
            'anbieter': ['room-management', 'anbietermgmt', 'user-details', 'bookingmgmt']
        }

        # Berechtigungen für den aktuellen Benutzer
        user_permissions = permissions.get(user_type, [])

        session['permissions'] = user_permissions

        app.logger.debug(f"Session after login: {session}")
        app.logger.debug(f"Permissions on /home: {session.get('permissions')}")
        
        return render_template('home.html', user=session['user'], permissions=user_permissions)

    # Fallback: Benutzer ist nicht eingeloggt
    return render_template('login.html')


@app.route('/login/<user_type>')
def login():
    debug_request(request)
    return


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

@app.route('/room-management')
def get_rooms():
    debug_request(request)
    try:
        response_host = 'http://zimmerverwaltung/' if request.host == 'localhost' else request.url_root
        app.logger.debug(response_host + 'room')
        response = requests.get(response_host + 'room')
        app.logger.debug(response)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
    except Exception as err:
        app.logger.error(f"Fehler beim Laden der Buchungen: {err}")
        data = []

    return render_template('room-management.html', buchungen=data)

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

if __name__ == '__main__':
    app.run(debug=True, port=80)
