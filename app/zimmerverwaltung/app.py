import json
import os

import boto3
from botocore.exceptions import NoCredentialsError
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request
from geopy.distance import geodesic  # Für Radius-Berechnung

app = create_app("zimmerverwaltung")

# Städte-Koordinaten
cities = {
    "eisenstadt": (47.8454821, 16.5249288),
    "fh burgenland": (47.8294849, 16.5347871),
    "wien": (48.2083537, 16.3725042),
    "graz": (47.0708678, 15.4382786),
}

# Uni-Standard-Position (z. B. FH Burgenland)
university_location = (47.8294849, 16.5347871)  # Lat, Lon

@app.route('/search-providers', methods=['GET'])
def search_providers():
    debug_request(request)

    user_location = request.args.get('location', '').strip().lower()
    radius = float(request.args.get('radius', 10))  # Standardradius 10 km
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    if not start_date or not end_date:
        msg = "Start- und Enddatum sind erforderlich."
        app.logger.error(msg)
        return jsonify({'error': msg}), 400

    start_year = int(start_date.split("-")[0])

    # Fallback auf FH Burgenland, falls keine valide Stadt angegeben ist
    center_location = cities.get(user_location, university_location)

    results = []
    try:
        conn = create_db_connection()
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
    except Exception as err:
        msg = f"Fehler bei der Datenbankabfrage: {err}"
        app.logger.error(msg)
        return jsonify({'error': msg}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
