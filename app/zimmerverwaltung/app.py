from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError
import json
import os
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug("Start zimmerverwaltung")

# S3 Configuration
bucket_name = 'zimmer'
s3 = boto3.client(
    's3',
    endpoint_url = os.environ.get('S3_ENDPOINT', ''),
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID', ''),
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
)

@app.route('/room')
def get_room():
    app.logger.debug("Route: " + request.path)
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        app.logger.debug(response)

        bookings = []

        objects = s3.list_objects_v2(Bucket=bucket_name)
        for obj in objects['Contents']:
            app.logger.info(obj['Key'])

        for obj in response.get('Contents', []):
            data = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
            content = data['Body'].read().decode('utf-8')
            try:
                booking = json.loads(content)
                app.logger.info("Loaded booking: " + content)  # Log each loaded booking
                bookings.append(booking)
            except json.JSONDecodeError as err:
                app.logger.error(f"JSON decoding error for {obj['Key']}: {err}")
                continue  # Skip this booking if there's a JSON error
    except Exception as err:
        app.logger.error(f"Error accessing S3: " + str(err))
        return str(err), 500
    return jsonify(bookings)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
