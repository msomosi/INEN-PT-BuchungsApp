import requests
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, redirect, render_template, request, url_for
from geopy.distance import geodesic  # Für Radius-Berechnung

app = create_app("frontend")

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

    # Verbinden mit der Datenbank
    results = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL-Abfrage für Anbieter
        cursor.execute("""
            SELECT id, name, type, address, ST_X(location::geometry) AS lon, ST_Y(location::geometry) AS lat,
                   parking_available, parking_paid, always_booked_in
            FROM providers
        """)
        providers = cursor.fetchall()

        for provider in providers:
            provider_id, name, p_type, address, lon, lat, parking_available, parking_paid, always_booked_in = provider

            # Verfügbarkeit prüfen
            if always_booked_in == start_year:
                app.logger.debug(f"{name} ist im Jahr {start_year} immer ausgebucht. Überspringen.")
                continue

            # Distanz berechnen
            distance = geodesic(center_location, (lat, lon)).km
            app.logger.debug(f"Berechnete Distanz für {name}: {distance} km")

            if distance <= radius:
                results.append({
                    "id": provider_id,
                    "name": name,
                    "type": p_type,
                    "address": address,
                    "location": (lat, lon),
                    "parking": {
                        "available": parking_available,
                        "paid": parking_paid,
                    },
                    "distance": round(distance, 2),
                })
    except Exception as e:
        app.logger.error(f"Fehler bei der Datenbankabfrage: {e}")
        return jsonify({"error": "Fehler bei der Verarbeitung"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True, port=80)
