from flask import Flask, redirect, url_for, render_template, session, request, jsonify
from geopy.distance import geodesic  # Für Radius-Berechnung
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import os
import requests

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
app.secret_key = os.getenv('SESSION_KEY', default='BAD_SECRET_KEY')

app.logger.setLevel(logging.DEBUG)
app.logger.debug("Start frontend")


def debug_request(request):
    app.logger.info(request)
    app.logger.debug(session)

# Anbieter-Daten (Hotels)
providers = [
    {
        "id": 1,
        "name": "ÖJAB Eisenstadt",
        "type": "Hotel",
        "address": "Eisenstadt, Österreich",
        "location": (47.8299358, 16.5342446),
        "parking": {"available": True, "paid": False},
    },
    {
        "id": 2,
        "name": "Parkhotel Eisenstadt",
        "type": "Hotel",
        "address": "Eisenstadt, Österreich",
        "location": (47.8473218, 16.524945),
        "parking": {"available": True, "paid": True},
    },
    {
        "id": 3,
        "name": "Gasthof OHR",
        "type": "Hotel",
        "address": "Eisenstadt, Österreich",
        "location": (47.83967208862305, 16.52600860595703),
        "parking": {"available": True, "paid": False},
    },
    {
        "id": 4,
        "name": "Weingut Lichtscheidl",
        "type": "Hotel",
        "address": "Eisenstadt, Österreich",
        "location": (47.85456848144531, 16.54975128173828),
        "parking": {"available": True},
        "always_booked_in": 2024,  # Dieses Hotel ist 2024 immer ausgebucht
    },
    {
        "id": 5,
        "name": "B&B Hotel Graz",
        "type": "Hotel",
        "address": "Graz, Österreich",
        "location": (47.0292892, 15.4357059),
        "parking": {"available": True, "paid": False},
    },
    {
        "id": 6,
        "name": "Best Western Plus Plaza Hotel Graz",
        "type": "Hotel",
        "address": "Graz, Österreich",
        "location": (47.0586522, 15.4452269),
        "parking": {"available": True, "paid": False},
    },
    {
        "id": 7,
        "name": "Meininger Hotel Wien",
        "type": "Hotel",
        "address": "Wien, Österreich",
        "location": (48.21917724609375,16.375764846801758),
        "parking": {"available": True, "paid": False},
    },
    {
        "id": 8,
        "name": "H+ Hotel Wien",
        "type": "Hotel",
        "address": "Wien, Österreich",
        "location": (48.2266002,16.3563713),
        "parking": {"available": True, "paid": False},
    },
]

# Städte-Koordinaten
cities = {
    "eisenstadt": (47.8454821, 16.5249288),
    "fh burgenland": (47.8294849, 16.5347871),
    "wien": (48.2083537, 16.3725042),
    "graz": (47.0708678, 15.4382786),
}

# Uni-Standard-Position (z. B. FH Burgenland)
university_location = (47.8294849, 16.5347871)  # Lat, Lon

@app.route('/home')
def home():
    debug_request(request)

    if 'google_token' in session:
        return render_template('home.html', user=session['user'])
    else:
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
        'user': session['email'],
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

@app.route('/search-providers', methods=['GET'])
def search_providers():
    user_location = request.args.get('location', '').strip().lower()
    radius = float(request.args.get('radius', 10))  # Standardradius 10 km
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    if not start_date or not end_date:
        return jsonify({"error": "Start- und Enddatum sind erforderlich"}), 400

    start_year = int(start_date.split("-")[0])

    # Fallback auf FH Burgenland, falls keine valide Stadt angegeben ist
    center_location = cities.get(user_location, university_location)

    results = []
    for provider in providers:
        if "always_booked_in" in provider and provider["always_booked_in"] == start_year:
            continue  # Hotel ist in diesem Jahr ausgebucht

        # Distanz berechnen
        distance = geodesic(center_location, provider["location"]).km
        if distance <= radius:
            provider["distance"] = round(distance, 2)
            results.append(provider)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=80)
