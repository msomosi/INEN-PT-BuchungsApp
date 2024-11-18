from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import json,os
import logging

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
app.secret_key = os.getenv('SESSION_KEY', default='BAD_SECRET_KEY')
CORS(app)

app.logger.setLevel(logging.DEBUG)
app.logger.debug("Start buchungsmanagement")

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

def debug_request(request):
    app.logger.info(request)
    app.logger.debug(session)

@app.route('/booking')
def get_bookings():
    debug_request(request)

    return jsonify(buchungen)

@app.route('/booking', methods=['POST'])
def add_booking():
    debug_request(request)

    try:
        buchung = request.get_json()
        app.logger.debug(buchung)

        buchung['user'] = session['email'];
        buchung['room'] = buchung['hotel_id'];
        date_format = "%Y-%m-%d"
        buchung['days'] = (datetime.strptime(buchung['start_date'], date_format) - datetime.strptime(buchung['end_date'], date_format)).days



        # Bestimmung des Objektnamens für S3
        object_name = f"booking_{buchung['room']}_{buchung['start_date']}.json"
        test_data = json.dumps(buchung)

        app.logger.info("Speichere Buchung: " + object_name)
        bucket = s3.create_bucket(Bucket=bucket_name);
        app.logger.debug(bucket)
        s3response = s3.put_object(Bucket=bucket_name, Key=object_name, Body=test_data, ContentType='application/json')
        app.logger.debug(s3response)
        return 'OK', 204
    except Exception as err:
        app.logger.error("Fehler beim Speichern der Buchung: " + str(err))
        return jsonify({'error': f'Fehler beim Speichern der Buchung: {str(err)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=80)
