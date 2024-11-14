from flask import Flask, redirect, url_for, render_template, session, request
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import os
import requests

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
app.logger.setLevel(logging.DEBUG)
app.logger.debug("Start frontend")

app.secret_key = '12345678910111213141516'  # Replace with a strong random value

def debug_request(request):
    app.logger.debug("Route: " + request.path)
    app.logger.debug("Host: " + request.host)
    app.logger.debug("Url_root: " + request.url_root)


@app.route('/home')
def home():
    debug_request(request)
    app.logger.info(session)

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

    app.logger.info("Buchung erstellt: " + buchung['user'] + ", Zimmer: " + buchung['room'])
    app.logger.debug(buchung)

    try:
        response = requests.post(request.url_root + 'booking', json=buchung)
        app.logger.debug(response)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    except Exception as err:
        app.logger.error("Fehler beim Speichern der Buchung: " + str(err))
        return render_template('error.html', message='Fehler beim Speichern der Buchung.', error=str(err)), 500

    return render_template('bestaetigung.html', buchung=buchung)

@app.route('/room-management')
def get_rooms():
    debug_request(request)
    try:
        response = requests.get(request.url_root + 'room')
        app.logger.debug(response)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
    except Exception as err:
        app.logger.error("Fehler beim Laden der Buchungen: " + str(err))
        data=[]

    return render_template('room-management.html', buchungen=data)

if __name__ == '__main__':
    app.run(debug=True, port=80)
