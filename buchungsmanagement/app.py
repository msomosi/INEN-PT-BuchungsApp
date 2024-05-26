from flask import Flask, jsonify, request, redirect, url_for, render_template, session
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request, create_access_token, set_access_cookies
import datetime

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '161514131211109876543210'  # Same key as in Login-Service
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # False for development, True for production
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF protection for development

jwt = JWTManager(app)

buchungen = []

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
@jwt_required(optional=True)
def home():
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if current_user:
            return render_template('homev2.html', user=current_user)
    except Exception as e:
        return render_template('error.html', message='Kein gültiges Token gefunden.', error=str(e)), 401

@app.route('/rent', methods=['GET', 'POST'])
@jwt_required()
def rent():
    if request.method == 'POST':
        room = request.form['room']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        current_user = get_jwt_identity()

        # Validate and save the booking
        buchung = {
            'id': len(buchungen) + 1,
            'user': current_user,
            'room': room,
            'start_time': start_time,
            'end_time': end_time
        }
        buchungen.append(buchung)
        return redirect(url_for('home'))
    return render_template('rentv2.html')

@app.route('/buchungen', methods=['GET'])
@jwt_required()
def handle_buchungen():
    return jsonify(buchungen)

@app.route('/kundenverwaltung')
def kundenverwaltung():
    email = session.get('email')
    buchungen = [
        {"room": "101", "start_time": "10:00", "end_time": "12:00"},
        {"room": "102", "start_time": "12:00", "end_time": "14:00"},
        {"room": "103", "start_time": "14:00", "end_time": "16:00"}
    ]
    return render_template('kundenverwaltung.html', user=email, buchungen=buchungen)



if __name__ == '__main__':
    app.run(debug=True, port=5002)