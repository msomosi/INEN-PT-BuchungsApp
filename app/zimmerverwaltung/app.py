import json
import os

import boto3
from botocore.exceptions import NoCredentialsError
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request
from geopy.distance import geodesic  # Für Radius-Berechnung

app = create_app("zimmerverwaltung")

# S3 Configuration
bucket_name = 'zimmer'
s3 = boto3.client(
    's3',
    endpoint_url = os.environ.get('S3_ENDPOINT', ''),
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID', ''),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
)

# Städte-Koordinaten
cities = {
    "eisenstadt": (47.8454821, 16.5249288),
    "fh burgenland": (47.8294849, 16.5347871),
    "wien": (48.2083537, 16.3725042),
    "graz": (47.0708678, 15.4382786),
}

# Uni-Standard-Position (z. B. FH Burgenland)
university_location = (47.8294849, 16.5347871)  # Lat, Lon


@app.route('/room')
def get_room():
    debug_request(request)
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        app.logger.debug(response)

        bookings = []

        objects = s3.list_objects_v2(Bucket=bucket_name)
        for obj in objects['Contents']:
            app.logger.info(obj['Key'])

        for obj in response.get('Contents', []):
            data = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
            content = data['Body'].read().decode('utf-8')
            try:
                booking = json.loads(content)
                app.logger.info("Loaded booking: " + content)  # Log each loaded booking
                bookings.append(booking)
            except json.JSONDecodeError as err:
                app.logger.error(f"JSON decoding error for {obj['Key']}: {err}")
                continue  # Skip this booking if there's a JSON error
    except Exception as err:
        app.logger.error(f"Error accessing S3: " + str(err))
        return str(err), 500
    return jsonify(bookings)

@app.route('/search-providers', methods=['GET'])
def search_providers():
    debug_request(request)

    user_location = request.args.get('location', '').strip().lower()
    radius = float(request.args.get('radius', 10))  # Standardradius 10 km
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    if not start_date or not end_date:
        msg = f"Start- und Enddatum sind erforderlich: " + str(err)
        app.logger.error(msg)
        return jsonify({'error': msg}), 500

    start_year = int(start_date.split("-")[0])

    # Fallback auf FH Burgenland, falls keine valide Stadt angegeben ist
    center_location = cities.get(user_location, university_location)

    # Verbinden mit der Datenbank
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
        msg = f"Fehler bei der Datenbankabfrage: " + str(err)
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
