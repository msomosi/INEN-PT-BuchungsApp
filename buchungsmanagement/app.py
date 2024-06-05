from flask import Flask, jsonify, request, redirect, url_for, render_template, session
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request, create_access_token, set_access_cookies
import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import json

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '161514131211109876543210'  # Same key as in Login-Service
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # False for development, True for production
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF protection for development

jwt = JWTManager(app)

# S3 Configuration
bucket_name = 'zimmer'  # Replace with your Exoscale bucket name
s3_endpoint = 'https://sos-de-fra-1.exo.io'
aws_access_key_id = 'EXO5f27ae1ba3685a0d89d9ae58'  # Replace with your Exoscale access key
aws_secret_access_key = 'll1mYK9P5O3xx52P6ftg3vnrFRyNPkdW4PV3oB_NLo8'  # Replace with your Exoscale secret key

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
        return render_template('error.html', message='Kein gÃ¼ltiges Token gefunden.', error=str(e)), 401

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

        # Upload the booking to S3
        object_name = f"booking_{buchung['id']}.json"
        test_data = json.dumps(buchung)
        try:
            s3.put_object(Bucket=bucket_name, Key=object_name, Body=test_data, ContentType='application/json')
            print(f"Booking data successfully uploaded as {object_name} in bucket {bucket_name}.")
        except NoCredentialsError:
            print("Credentials not available.")
            return jsonify(success=False, error="Credentials not available.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify(success=False, error=str(e))

        return jsonify(success=True)
    return jsonify(success=False, error="Invalid request method.")

@app.route('/')
def home():
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
