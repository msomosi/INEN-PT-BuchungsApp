from flask import Flask, jsonify, request, redirect, url_for, render_template, session

import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import json,os

app = Flask(__name__)

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


@app.route('/booking')
def get_bookings():
    return jsonify(buchungen)

@app.route('/booking', methods=['POST'])
def add_booking():
    try:
        buchung = request.get_json()

        # Bestimmung des Objektnamens für S3
        object_name = f"booking_{buchung['room']}_{buchung['start_date']}.json"
        test_data = json.dumps(buchung)

        # Upload der Buchungsinformationen in S3
        s3.put_object(Bucket=bucket_name, Key=object_name, Body=test_data, ContentType='application/json')
        return render_template('bestaetigung.html', buchung=buchung)
    except Exception as e:
        return render_template('error.html', message='Fehler beim Speichern der Buchung.', error=str(e)), 500

@app.route('/room_management')
def room_management():
    # Redirect to the room management page on port 5003
    return redirect('http://localhost:5003/room_management')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
