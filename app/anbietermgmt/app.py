#!/usr/bin/env python3

from flask import Flask, request, session, render_template_string, redirect, url_for
from connect import connect_to_db
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/user_details')
def user_details():
    zimmer_id = request.args.get('zimmer_id')

    if not zimmer_id :
        return "<h1>Fehler: Ungültige Parameter</h1>", 400

    conn_room = connect_to_db("bpf")
    if not conn_room:
        return "<h1>Fehler: Verbindung zur Datenbank fehlgeschlagen</h1>", 500

    try:
        with conn_room.cursor() as cur:
            query = """
                SELECT u."Firstname", u."Lastname", u.email, u.phone, z.zimmer_id, z.date
                FROM tbl_user_details u
                JOIN tbl_buchung b ON u.user_id = b.user_id
                JOIN tbl_zimmer z ON b.zimmer_id = z.zimmer_id
                WHERE z.zimmer_id = %s;
            """
            cur.execute(query, (zimmer_id))
            user_details = cur.fetchone()
            if not user_details:
                return "<h1>Benutzer nicht gefunden</h1>", 404

            user_info = {
                "Firstname": user_details[0],
                "Lastname": user_details[1],
                "email": user_details[2],
                "phone": user_details[3],
                "zimmer_id": user_details[4],
                "date": user_details[5],
            }
    except Exception as e:
        print(f"Fehler bei der Abfrage: {e}")
        return "<h1>Fehler: Datenbankabfrage fehlgeschlagen</h1>", 500
    finally:
        conn_room.close()


    return render_template_string("""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Benutzerdetails</title>
    </head>
    <body>
        <h1>Details zum Benutzer</h1>
        <p><strong>Firstname:</strong> {{ user_info.Firstname }}</p>
        <p><strong>Lastname:</strong> {{ user_info.Lastname }}</p>
        <p><strong>E-Mail:</strong> {{ user_info.email }}</p>
        <p><strong>Telefon:</strong> {{ user_info.phone }}</p>
        <p><strong>Zimmer-ID:</strong> {{ user_info.zimmer_id }}</p>
        <p><strong>Datum:</strong> {{ user_info.date }}</p>
        <a href="#" onclick="window.close();">Fenster schließen</a>
    </body>
    </html>
    """, user_info=user_info)



@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':

        user_id = "1"
        if not user_id:
            return "<h1>Fehler: Kein Benutzer angemeldet</h1>", 400

        try:
            num_rooms = int(request.form['num_rooms'])
            date_from = datetime.strptime(request.form['date_from'], '%Y-%m-%d')
            date_to = datetime.strptime(request.form['date_to'], '%Y-%m-%d')
        except ValueError:
            return "<h1>Fehler: Ungültige Eingabewerte</h1>", 400

        if date_from > date_to:
            return "<h1>Fehler: 'Von'-Datum liegt nach 'Bis'-Datum</h1>", 400

        conn_room = connect_to_db("bpf")
        if not conn_room:
            return "<h1>Fehler: Verbindung zur Datenbank fehlgeschlagen</h1>", 500

        try:
            with conn_room.cursor() as cur:

                current_date = date_from
                while current_date <= date_to:
                    for _ in range(num_rooms):
                        query = """
                            INSERT INTO tbl_zimmer (user_id, date)
                            VALUES (%s, %s);
                        """
                        cur.execute(query, (user_id, current_date))
                    current_date += timedelta(days=1)

                conn_room.commit()
        except Exception as e:
            print(f"Fehler bei der Datenbankoperation: {e}")
            return "<h1>Fehler: Einfügen in die Datenbank fehlgeschlagen</h1>", 500
        finally:
            conn_room.close()

        return redirect(url_for('show_table'))

    html_template = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Zimmer hinzufügen</title>
    </head>
    <body>
        <h1>Zimmer hinzufügen</h1>
        <form method="post">
            <label for="num_rooms">Anzahl Zimmer:</label>
            <input type="number" id="num_rooms" name="num_rooms" min="1" required><br><br>

            <label for="date_from">Datum von:</label>
            <input type="date" id="date_from" name="date_from" required><br><br>

            <label for="date_to">Datum bis:</label>
            <input type="date" id="date_to" name="date_to" required><br><br>

            <button type="submit">Hinzufügen</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(html_template)



@app.route('/')
def show_table():

    # hier kommt die session hin mit der eingeloggen user id
    user_id = "1"

    conn_room = connect_to_db("bpf")
    if not conn_room:
        return "<h1>Fehler: Verbindung zur Zimmer-Datenbank fehlgeschlagen</h1>", 500

    try:
        with conn_room.cursor() as cur:
            query = """
                SELECT z.zimmer_id, z.user_id, z.date, z.state_id, s.state_name, u."Firstname", u."Lastname"
                FROM tbl_zimmer z
                JOIN tbl_booking_state s ON z.state_id = s.state_id
                LEFT JOIN tbl_buchung b ON z.zimmer_id = b.zimmer_id
                LEFT JOIN tbl_user_details u ON b.user_id = u.user_id
                WHERE z.user_id = %s
                ORDER BY z.date ASC
                """
            cur.execute(query, (user_id,))
            rows = cur.fetchall()

            data = [
                {"zimmer_id": row[0], "user_id": row[1], "date": row[2], "state_id": row[3], "state_name": row[4],"firstname": row[5] if row[5] else "-", "lastname": row[6] if row[6] else "-",}
                for row in rows
            ]
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
        <title>Zimmerübersicht</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    </head>
    <body>
        <h1 style="text-align: center;">Meine Zimmerübersicht</h1>
        <div style="text-align: center; margin-bottom: 20px;">
        <a href="add_room">
            <button style="padding: 10px 20px; font-size: 16px;">Zimmer hinzufügen</button>
        </a>
       </div>
        <table>
            <thead>
                <tr>
                    <th>Zimmer-ID</th>
                    <th>Datum</th>
                    <th>Buchungsstatus</th>
                    <th>Info Student:in</th>
                    <th>Student:in</th>
                </tr>
            </thead>
            <tbody>
                {% for row in data %}
                <tr>
                    <td>{{ row.zimmer_id }}</td>
                    <td>{{ row.date }}</td>
                    <td>{{ row.state_name }}</td>
                    <td>
                    {% if row.state_id in [2, 3, 4] %}
                        <a href="user_details?zimmer_id={{ row.zimmer_id }}" target="_blank">
                            <button>Benutzerdetails</button>
                    {% else %}
                        -
                    {% endif %}
                    <td>{{ row.firstname }} {{ row.lastname }}</td>
                </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, data=data)

# Flask unter CGI ausführen
if __name__ == '__main__':
    from wsgiref.handlers import CGIHandler
    CGIHandler().run(app)


