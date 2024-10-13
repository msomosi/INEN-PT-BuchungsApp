from flask import Flask, jsonify, request, redirect, url_for, render_template, session
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request, create_access_token, set_access_cookies

import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import json,os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', '')  # Same key as in Login-Service
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # False for development, True for production
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF protection for development

jwt = JWTManager(app)

# S3 Configuration
bucket_name = 'zimmer'  # Replace with your Exoscale bucket name
s3_endpoint=os.environ.get('S3_ENDPOINT', '')
aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', '')
aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', '')

# Create an S3 client
s3 = boto3.client(
    's3',
    endpoint_url=s3_endpoint,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

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

@app.route('/rent')
@jwt_required()
def rent():
    return render_template('rentv2.html')  # Beispiel für ein Template

@app.route('/rent', methods=[POST'])
@jwt_required()
def add_rent():
    try:
        room = request.form['room']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        days = request.form['days']
        current_user = get_jwt_identity()  # Nutzeridentifikation aus dem JWT

        # Erstellen des Buchungsobjekts
        buchung = {
            'user': current_user,
            'room': room,
            'start_date': start_date,
            'end_date': end_date,
            'days': days
        }

        # Bestimmung des Objektnamens für S3
        object_name = f"booking_{room}_{start_date}.json"
        test_data = json.dumps(buchung)

        # Upload der Buchungsinformationen in S3
        s3.put_object(Bucket=bucket_name, Key=object_name, Body=test_data, ContentType='application/json')
        return render_template('bestaetigung.html', buchung=buchung)
    except Exception as e:
        return render_template('error.html', message='Fehler beim Speichern der Buchung.', error=str(e)), 500

@app.route('/buchungen', methods=['GET'])
@jwt_required()
def handle_buchungen():
    return jsonify(buchungen)

@app.route('/room_management')
def room_management():
    # Redirect to the room management page on port 5003
    return redirect('http://localhost:5003/room_management')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
