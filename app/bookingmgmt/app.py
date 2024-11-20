#!/usr/bin/env python3

from flask import Flask, request, session, render_template_string, redirect, url_for
from connect import connect_to_db
from datetime import datetime, timedelta


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def filter_rooms():
    filters = {
        "parking": None,
        "parking_pay": None,
        "location": "",
        "plz": "",
        "date_from": "",
        "date_to": ""
    }
    filtered_data = []

    conn_room = connect_to_db("bpf")
    if not conn_room:
        return "<h1>Fehler: Verbindung zur Zimmer-Datenbank fehlgeschlagen</h1>", 500

    try:
        query = """
            SELECT z.zimmer_id, z.date, z.state_id, s.state_name, u."CompanyName", u.email, u.phone, u."Location", u."Plz", u."Parking", u.parking_pay
            FROM tbl_zimmer z
            JOIN tbl_booking_state s ON z.state_id = s.state_id
            LEFT JOIN tbl_user_details u ON z.user_id = u.user_id
            LEFT JOIN tbl_user t ON u.user_id = t.user_id
            WHERE t.role_id = 2 AND z.state_id = 1
        """
        conditions = []
        params = []

        if request.method == 'POST':
            # Filterbedingungen aus dem Formular übernehmen
            filters["parking"] = request.form.get("parking")
            filters["parking_pay"] = request.form.get("parking_pay")
            filters["location"] = request.form.get("location")
            filters["plz"] = request.form.get("plz")
            filters["date_from"] = request.form.get("date_from")
            filters["date_to"] = request.form.get("date_to")

            # Parking Filter
            if filters["parking"] is not None and filters["parking"] != "":
                filters["parking"] = True if filters["parking"] == "1" else False
                conditions.append('u."Parking" = %s')
                params.append(filters["parking"])

            # Parking Pay Filter
            if filters["parking_pay"] is not None and filters["parking_pay"] != "":
                filters["parking_pay"] = True if filters["parking_pay"] == "1" else False
                conditions.append('u."Parking_Pay" = %s')
                params.append(filters["parking_pay"])

            # Location Filter
            if filters["location"].strip() != "":
                conditions.append('u."Location" ILIKE %s')
                params.append(f"%{filters['location']}%")

            # PLZ Filter
            if filters["plz"].strip() != "":
                conditions.append('u."Plz" = %s')
                params.append(filters["plz"])

            # Datum from
            if filters["date_from"].strip() != "":
                conditions.append('z.date >= %s')
                params.append(filters["date_from"])

            # Datum bis
            if filters["date_to"].strip() != "":
               conditions.append('z.date <= %s')
               params.append(filters["date_to"])


            # Bedingungen an die Abfrage anhängen
            if conditions:
                query += " AND " + " AND ".join(conditions)

        query += " ORDER BY z.date ASC;"

        with conn_room.cursor() as cur:
            cur.execute(query, tuple(params))
            filtered_data = cur.fetchall()
    except Exception as e:
        print(f"Fehler bei der Abfrage: {e}")
        return "<h1>Fehler: Datenbankabfrage fehlgeschlagen</h1>", 500
    finally:
        conn_room.close()

    html_template = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Zimmerfilter</title>
    </head>
    <body>
        <h1>Zimmerfilter</h1>
        <form method="post">
            <label for="parking">Parkplatz:</label>
            <select name="parking" id="parking">
                <option value="">-- Alle --</option>
                <option value="1" {% if filters.parking == True %}selected{% endif %}>Ja</option>
                <option value="0" {% if filters.parking == False %}selected{% endif %}>Nein</option>
            </select>
            <br><br>

            <label for="parking_pay">Parkplatz kostenpflichtig:</label>
            <select name="parking_pay" id="parking_pay">
                <option value="">-- Alle --</option>
                <option value="1" {% if filters.parking_pay == True %}selected{% endif %}>Ja</option>
                <option value="0" {% if filters.parking_pay == False %}selected{% endif %}>Nein</option>
            </select>
            <br><br>

            <label for="location">Ort:</label>
            <input type="text" name="location" id="location" value="{{ filters.location }}">
            <br><br>

            <label for="plz">PLZ:</label>
            <input type="text" name="plz" id="plz" value="{{ filters.plz }}">
            <br><br>

            <label for="date_from">Datum von:</label>
            <input type="date" name="date_from" id="date_from" value="{{ filters.date_from }}">
            <br><br>

            <label for="date_to">Datum bis:</label>
            <input type="date" name="date_to" id="date_to" value="{{ filters.date_to }}">
            <br><br>

            <button type="submit">Filtern</button>
            <button type="button" onclick="window.location.href=''">Zurücksetzen</button>
        </form>
        <br>
        <h2>Verfügbare Zimmer:</h2>
        <table border="1">
            <thead>
                <tr>
                    <th>Zimmer-ID</th>
                    <th>Datum</th>
                    <th>CompanyName</th>
                    <th>E-Mail</th>
                    <th>Phone</th>
                    <th>Ort</th>
                    <th>PLZ</th>
                    <th>Parkplatz</th>
                    <th>Kostenlos parken</th>
                </tr>
            </thead>
            <tbody>
                {% for row in filtered_data %}
                <tr>
                    <td>{{ row[0] }}</td>
                    <td>{{ row[1] }}</td>
                    <td>{{ row[4] }}</td>
                    <td>{{ row[5] }}</td>
                    <td>{{ row[6] }}</td>
                    <td>{{ row[7] }}</td>
                    <td>{{ row[8] }}</td>
                    <td>{{ 'Ja' if row[9] else 'Nein' }}</td>
                    <td>{{ 'Ja' if row[10] else 'Nein' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, filters=filters, filtered_data=filtered_data)





# Flask unter CGI ausführen
if __name__ == '__main__':
    from wsgiref.handlers import CGIHandler
    CGIHandler().run(app)
