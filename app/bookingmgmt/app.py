from datetime import datetime, timedelta

from factory import create_app, create_db_connection, debug_request
from flask import redirect, render_template_string, request, url_for

app = create_app("bookingmgmt")

@app.route('/book', methods=['POST'])
def book_rooms():
    debug_request(request)

    # id vom studenten nach login
    user_id = 3

    selected_rooms = request.form.getlist("selected_rooms")

    if not selected_rooms:
        return "<h1>Fehler: Keine Zimmer ausgewählt</h1>", 400

    conn_room = create_db_connection()
    if not conn_room:
        return "<h1>Fehler: Verbindung zur Datenbank fehlgeschlagen</h1>", 500

    try:
        with conn_room.cursor() as cur:
            for room in selected_rooms:
                zimmer_id, date = room.split("_")

                # Update tbl_zimmer
                cur.execute("""
                    UPDATE tbl_zimmer
                    SET state_id = 2
                    WHERE zimmer_id = %s AND date = %s
                """, (zimmer_id, date))

                # Insert into tbl_buchung
                cur.execute("""
                    INSERT INTO tbl_buchung (user_id, zimmer_id)
                    VALUES (%s, %s)
                """, (user_id, zimmer_id))

            conn_room.commit()
    except Exception as e:
        print(f"Fehler bei der Buchung: {e}")
        return "<h1>Fehler: Buchung fehlgeschlagen</h1>", 500
    finally:
        conn_room.close()

    return redirect(url_for('filter_rooms'))



@app.route('/', methods=['GET', 'POST'])
def filter_rooms():
    debug_request(request)

    # Studenten ID Übergabe durch Login
    student_user_id = 3

    filters = {
        "parking": None,
        "parking_pay": None,
        "location": "",
        "plz": "",
        "date_from": "",
        "date_to": ""
    }
    filtered_data = []

    conn_room = create_db_connection()
    if not conn_room:
        return "<h1>Fehler: Verbindung zur Zimmer-Datenbank fehlgeschlagen</h1>", 500

    try:
        query = """
            WITH prioritized_rooms AS (
                SELECT
                    z.zimmer_id, z.date, z.state_id,
                    b.user_id AS student_user_id,
                    u.user_id AS provider_user_id,
                    u."CompanyName", u.email, u.phone, u."Location", u."Plz", u."Parking", u.parking_pay,
                    CASE
                        WHEN b.user_id = %s THEN s.state_name
                        ELSE 'available'
                    END AS booking_status,
                    ROW_NUMBER() OVER (
                        PARTITION BY z.date, u.user_id
                        ORDER BY
                            CASE WHEN b.user_id = %s THEN 1 ELSE 2 END,
                            z.zimmer_id
                    ) AS rank
                FROM tbl_zimmer z
                JOIN tbl_booking_state s ON z.state_id = s.state_id
                LEFT JOIN tbl_user_details u ON z.user_id = u.user_id
                LEFT JOIN tbl_user t ON u.user_id = t.user_id
                LEFT JOIN tbl_buchung b ON z.zimmer_id = b.zimmer_id AND b.user_id = %s
                WHERE t.role_id = 2 AND (z.state_id = 1 OR b.user_id = %s)
            )
            SELECT *
            FROM prioritized_rooms
            WHERE rank = 1
            ORDER BY date ASC, provider_user_id;
        """
        conditions = []
        params = [student_user_id, student_user_id, student_user_id, student_user_id]

        if request.method == 'POST':
            # Filterbedingungen
            filters["parking"] = request.form.get("parking")
            filters["parking_pay"] = request.form.get("parking_pay")
            filters["location"] = request.form.get("location")
            filters["plz"] = request.form.get("plz")
            filters["date_from"] = request.form.get("date_from")
            filters["date_to"] = request.form.get("date_to")

            if filters["parking"] is not None and filters["parking"] != "":
                filters["parking"] = True if filters["parking"] == "1" else False
                conditions.append('u."Parking" = %s')
                params.append(filters["parking"])

            if filters["parking_pay"] is not None and filters["parking_pay"] != "":
                filters["parking_pay"] = True if filters["parking_pay"] == "1" else False
                conditions.append('u."Parking_Pay" = %s')
                params.append(filters["parking_pay"])

            if filters["location"].strip() != "":
                conditions.append('u."Location" ILIKE %s')
                params.append(f"%{filters['location']}%")

            if filters["plz"].strip() != "":
                conditions.append('u."Plz" = %s')
                params.append(filters["plz"])

            if filters["date_from"].strip() != "":
                conditions.append('z.date >= %s')
                params.append(filters["date_from"])

            if filters["date_to"].strip() != "":
                conditions.append('z.date <= %s')
                params.append(filters["date_to"])

            if conditions:
                # Dynamische Bedingungen korrekt hinzufügen
                if "WHERE" in query:
                    query += " AND " + " AND ".join(conditions)
                else:
                    query += " WHERE " + " AND ".join(conditions)

            query += """
                    GROUP BY z.zimmer_id, z.date, u.user_id, u."CompanyName", u.email, u.phone,
                     u."Location", u."Plz", u."Parking", u.parking_pay, s.state_name, b.user_id
                    ORDER BY z.date ASC;
                    """

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
        <form method="post" action="book">
        <button type="submit">Buchen</button>
        <table border="1">
            <thead>
                <tr>
                    <th>Auswahl</th>
                    <th>Zimmer-ID</th>
                    <th>Datum</th>
                    <th>Anbieter-ID</th>
                    <th>Firmenname</th>
                    <th>Ort</th>
                    <th>PLZ</th>
                    <th>Parkplatz</th>
                    <th>Kostenlos parken</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for row in filtered_data %}
               <tr>
                   <!-- Checkbox für die Buchung -->
                   <td>
                       <input type="checkbox" name="selected_rooms" value="{{ row[0] }}_{{ row[1] }}">
                   </td>
                   <!-- Darstellung der Felder -->
                   <td>{{ row[0] }}</td> <!-- Zimmer-ID -->
                   <td>{{ row[1] }}</td> <!-- Datum -->
                   <td>{{ row[4] }}</td> <!-- Anbieter-ID -->
                   <td>{{ row[5] }}</td> <!-- Firmenname -->
                   <td>{{ row[8] }}</td> <!-- Ort -->
                   <td>{{ row[9] }}</td> <!-- PLZ -->
                   <td>{{ 'Ja' if row[10] else 'Nein' }}</td> <!-- Parkplatz verfügbar -->
                   <td>{{ 'Ja' if row[11] else 'Nein' }}</td> <!-- Kostenlos parken -->
                   <td>{{ row[12] }}</td> <!-- Status -->
               </tr>
               {% endfor %}
            </tbody>
        </table>
        </form>
    </body>
    </html>
    """
    return render_template_string(html_template, filters=filters, filtered_data=filtered_data)

if __name__ == '__main__':
    app.run(debug=True, port=80)
