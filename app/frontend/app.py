from flask import Flask, redirect, url_for, render_template, session, request
import os
import requests

app = Flask(__name__)
app.secret_key = '12345678910111213141516'  # Replace with a strong random value

@app.route('/home')
def home():
    if 'google_token' in session:
        return render_template('homev2.html', user=session['user'])
    else:
        return render_template('login.html')


@app.route('/rent')
@jwt_required()
def new_booking():
    return render_template('rentv2.html')

@app.route('/rent', methods=['POST'])
@jwt_required()
def create_booking():
    room = request.form['room']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    days = request.form['days']
    current_user = get_jwt_identity()  # Nutzeridentifikation aus dem JWT

    # Erstellen des Buchungsobjekts
    buchung = {
        'user': session['email'],
        'room': room,
        'start_date': start_date,
        'end_date': end_date,
        'days': days
    }

    try:
        response = requests.post(url_for('booking', _external=True), json=buchung)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        print(response.json())
    except Exception as err:
        return render_template('error.html', message='Fehler beim Speichern der Buchung.', error=str(err)), 500

    return render_template('bestaetigung.html', buchung=buchung)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
