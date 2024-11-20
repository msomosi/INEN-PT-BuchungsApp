#!/usr/bin/env python3

from flask import Flask, request, session, render_template_string, redirect, url_for
from connect import connect_to_db
from datetime import datetime, timedelta

app = Flask(__name__)

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

        # Verbindung zur Datenbank herstellen
        conn_room = connect_to_db("bpf")
        if not conn_room:
            return "<h1>Fehler: Verbindung zur Datenbank fehlgeschlagen</h1>", 500

        try:
            with conn_room.cursor() as cur:
                # Über alle Tage im Zeitraum iterieren
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

        # Erfolgreiche Eingabe -> Zurück zur Übersicht
        return redirect(url_for('show_table'))

    # HTML für die Maske (GET-Methode)
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
                SELECT zimmer_id, user_id, date
                FROM tbl_zimmer WHERE user_id = %s;
            """
            cur.execute(query, (user_id,))
            rows = cur.fetchall()

            data = [
                {"zimmer_id": row[0], "user_id": row[1], "date": row[2]}
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
                    <th>Firma</th>
                    <th>Datum</th>
                </tr>
            </thead>
            <tbody>
                {% for row in data %}
                <tr>
                    <td>{{ row.zimmer_id }}</td>
                    <td>{{ row.user_id }}</td>
                    <td>{{ row.date }}</td>
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


