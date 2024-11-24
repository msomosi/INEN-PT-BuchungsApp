import json
import os

import boto3
from botocore.exceptions import NoCredentialsError
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request

app = create_app("buchungsmanagement")

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
    debug_request(request)

    return jsonify(buchungen)

@app.route('/booking', methods=['POST'])
def add_booking():
    debug_request(request)

    try:
        buchung = request.get_json()
        app.logger.debug(buchung)

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
