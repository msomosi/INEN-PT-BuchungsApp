import json
import os

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic  # Für Radius-Berechnung
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    radius = float(request.args.get('radius', 10))  # Radius
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    if not start_date or not end_date:
        return jsonify({'error': 'Start- und Enddatum sind erforderlich.'}), 400

    center_location = cities.get(request.args.get('location', '').strip().lower(), university_location)

    results = []
    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        # SQL für Verfügbarkeit innerhalb der Zeitspanne
        cursor.execute("""
            SELECT 
                r.room_id,
                a.provider_id,
                a.company_name,
                c.address,
                c.postal_code,
                c.location,
                c.phone,
                a.parking AS parking_available,
                a.parking_free AS parking_paid,
                r.date AS available_date
            FROM 
                public.room r
            JOIN 
                public.accommodation a ON r.provider_id = a.provider_id
            JOIN 
                public.contact c ON a.contact_id = c.contact_id
            WHERE 
                r.date BETWEEN %s AND %s
            ORDER BY 
                r.date;
        """, (start_date, end_date))

        providers = cursor.fetchall()

        for provider in providers:
            room_id, provider_id, name, address, postal_code, location, phone, parking_available, parking_paid, available_date = provider

            # Geokodierung der Adresse
            lat, lon = geocode_address(address, postal_code, location)
            if lat is None or lon is None:
                continue

            # Distanz berechnen
            distance = geodesic(center_location, (lat, lon)).km
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
                "available_date": available_date.strftime('%d-%m-%Y'),  # Verfügbarkeitsdatum
                "room_id": room_id  # Die Room-ID für die Buchung
            })
    except Exception as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    return jsonify(results)

@app.route('/create-booking', methods=['POST'])
def create_booking():
    """
    Fügt eine Buchung zur Datenbank hinzu und ruft die E-Mail-Sende-Logik auf.
    """
    try:
        data = request.get_json()
        app.logger.debug(f"Erhaltene Buchungsdaten: {data}")

        user_id = data.get('user_id')
        room_id = data.get('room_id')
        provider_id = data.get('provider_id')
        state_id = data.get('state_id', 2)  # Standard: "Pending"

        if not all([user_id, room_id, provider_id]):
            app.logger.error("Fehlende Buchungsdaten")
            return jsonify({"error": "Fehlende Buchungsdaten"}), 400

        app.logger.debug(f"Verarbeitete Daten: user_id={user_id}, room_id={room_id}, provider_id={provider_id}, state_id={state_id}")

        # Überprüfen, ob der Benutzer verifiziert ist
        conn = create_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT verification 
            FROM public."user" 
            WHERE user_id = %s;
        """, (user_id,))
        verification_status = cursor.fetchone()

        if not verification_status or not verification_status[0]:  # Nicht verifiziert
            app.logger.warning(f"Benutzer mit user_id={user_id} ist nicht verifiziert.")
            return jsonify({
                "error": "Bitte verifizieren Sie Ihr Profil, bevor Sie eine Buchung vornehmen können.",
                "redirect": "/user-profile"
            }), 403

        app.logger.debug(f"Benutzer mit user_id={user_id} ist verifiziert.")

        conn = create_db_connection()
        cursor = conn.cursor()

        # Datum des Zimmers (room.date) abrufen
        cursor.execute("""
            SELECT date FROM public.room WHERE room_id = %s;
        """, (room_id,))
        room_date = cursor.fetchone()

        if not room_date:
            return jsonify({"error": "Zimmer-ID ungültig oder Zimmer nicht gefunden."}), 400

        room_date = room_date[0]

        # Überprüfen, ob der Benutzer bereits an diesem Tag eine Buchung hat
        cursor.execute("""
            SELECT b.booking_id
            FROM public.booking b
            INNER JOIN public.room r ON b.room_id = r.room_id
            WHERE b.user_id = %s AND r.date = %s;
        """, (user_id, room_date))
        existing_booking = cursor.fetchone()

        if existing_booking:
            booking_id = existing_booking[0]
            app.logger.error(f"Buchung existiert bereits an diesem Tag!")
            return jsonify({
                "error": f"Sie haben bereits eine Buchung am {room_date.strftime('%d-%m-%Y')} mit der Buchungs-ID {booking_id}."
            }), 400

        # Nächste freie booking_id ermitteln
        cursor.execute("SELECT COALESCE(MAX(booking_id), 0) + 1 FROM public.booking;")
        next_booking_id = cursor.fetchone()[0]

        # Buchung speichern
        cursor.execute("""
            INSERT INTO public.booking (booking_id, user_id, room_id, state_id)
            VALUES (%s, %s, %s, %s)
        """, (next_booking_id, user_id, room_id, state_id))
        conn.commit()

        # **E-Mails senden**
        # 1. An den Anbieter
        response_provider_email = requests.post(
            'http://frontend.booking-app-main.svc.cluster.local/send-booking-email',
            data={
                "booking_id": next_booking_id,
                "booking_date": room_date.strftime('%d-%m-%Y'),
                "recipient_email": "anbieter@muellmail.com"
            }
        )

        # 2. An den Bucher
        cursor.execute("""
            SELECT email FROM public."user" WHERE user_id = %s;
        """, (user_id,))
        user_email = cursor.fetchone()[0]

        response_user_email = requests.post(
            'http://frontend.booking-app-main.svc.cluster.local/send-booking-email',
            data={
                "booking_id": next_booking_id,
                "booking_date": room_date.strftime('%d-%m-%Y'),
                "recipient_email": user_email,
                "is_user": True
            }
        )

        # Log-Ergebnisse der E-Mails
        app.logger.info(f"Ergebnis Provider-E-Mail: {response_provider_email.json()}")
        app.logger.info(f"Ergebnis User-E-Mail: {response_user_email.json()}")

        return jsonify({"success": f"Buchung erfolgreich erstellt mit ID {next_booking_id}"}), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        app.logger.error(f"Fehler beim Erstellen der Buchung: {e}")
        return jsonify({"error": "Fehler beim Erstellen der Buchung"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
