from flask import Flask, redirect, url_for, render_template, session, request
import logging
import os
import requests

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug("Start frontend")

app.secret_key = '12345678910111213141516'  # Replace with a strong random value

@app.route('/home')
def home():
    app.logger.debug("Route: " + request.path)
    app.logger.info(session)

    if 'google_token' in session:
        return render_template('homev2.html', user=session['user'])
    else:
        return render_template('login.html')

@app.route('/rent')
def new_booking():
    app.logger.debug("Route: " + request.path)
    return render_template('rentv2.html')

@app.route('/rent', methods=['POST'])
def create_booking():
    app.logger.debug("Route: " + request.path)

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
        response = requests.post(url_for('booking', _external=True), json=buchung)
        app.logger.debug(response)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    except Exception as err:
        app.logger.error("Fehler beim Speichern der Buchung: " + str(err))
        return render_template('error.html', message='Fehler beim Speichern der Buchung.', error=str(err)), 500

    return render_template('bestaetigung.html', buchung=buchung)

@app.route('/room-management')
def get_rooms():
    app.logger.debug("Route: " + request.path)
    try:
        response = requests.get(url_for('room', _external=True))
        app.logger.debug(response)
        # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()
        data = response.json()
    except Exception as err:
        app.logger.error("Fehler beim Laden der Buchungen: " + str(err))
        data=[]

    return render_template('room-management.html', buchungen=data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
