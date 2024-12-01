import json
import os

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic  # Für Radius-Berechnung
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request

app = create_app("zimmerverwaltung")

# Geolocator initialisieren
geolocator = Nominatim(user_agent="zimmerverwaltung")

# Städte-Koordinaten (Fallback)
cities = {
    "eisenstadt": (47.8454821, 16.5249288),
    "fh burgenland": (47.8294849, 16.5347871),
    "wien": (48.2083537, 16.3725042),
    "graz": (47.0708678, 15.4382786),
}

# Uni-Standard-Position (z. B. FH Burgenland)
university_location = (47.8294849, 16.5347871)  # Lat, Lon

def geocode_address(address, postal_code, location):
    """Konvertiere Adresse, Postleitzahl und Ort in Latitude und Longitude."""
    full_address = f"{address}, {postal_code}, {location}, Austria"

    # Sonderfall für Campus 2, Eisenstadt
    if address.strip().lower() == "campus 2" and location.strip().lower() == "eisenstadt":
        app.logger.info("Manuelle Koordinaten für Campus 2, Eisenstadt verwendet.")
        return 47.82955551147461, 16.535341262817383

    try:
        location = geolocator.geocode({
            "street": address,
            "city": location,
            "postalcode": postal_code,
            "country": "Austria"
        }, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            app.logger.warning(f"Geokodierung fehlgeschlagen für Adresse: {full_address}")
            return None, None
    except GeocoderTimedOut as e:
        app.logger.error(f"Geocoder Timeout: {e}")
        return None, None


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

    # Fallback auf FH Burgenland, falls keine valide Stadt angegeben ist
    center_location = cities.get(user_location, university_location)

    results = []
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        # SQL-Abfrage für Anbieter erweitern, um postal_code einzubeziehen
        cursor.execute("""
            SELECT a.provider_id, a.company_name, c.address, c.postal_code, c.location, c.phone, 
                   a.parking AS parking_available, a.parking_free AS parking_paid
            FROM accommodation a
            JOIN contact c ON a.contact_id = c.contact_id
        """)

        providers = cursor.fetchall()

        for provider in providers:
            provider_id, name, address, postal_code, location, phone, parking_available, parking_paid = provider

            # Geokodierung der Adresse
            lat, lon = geocode_address(address, postal_code, location)
            if lat is None or lon is None:
                app.logger.warning(f"Überspringe Anbieter {name}: Keine Koordinaten für Adresse {address}, PLZ {postal_code}, Ort {location}")
                continue

            # Distanz berechnen
            distance = geodesic(center_location, (lat, lon)).km
            app.logger.debug(f"Berechnete Distanz für {name}: {distance} km")

            if distance <= radius:
                results.append({
                    "id": provider_id,
                    "name": name,
                    "address": f"{address}, {postal_code} {location}",
                    "phone": phone,
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
