from flask import Flask, request, jsonify, render_template
import boto3
from botocore.exceptions import NoCredentialsError
import json

app = Flask(__name__)

# Configuration for Exoscale S3 access
bucket_name = 'zimmer'  # Replace with your Exoscale bucket name
s3_endpoint = 'https://sos-de-fra-1.exo.io'
aws_access_key_id = 'EXO5f27ae1ba3685a0d89d9ae58'
aws_secret_access_key = 'll1mYK9P5O3xx52P6ftg3vnrFRyNPkdW4PV3oB_NLo8'

# Create an S3 client
s3 = boto3.client(
    's3',
    endpoint_url=s3_endpoint,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

@app.route('/room_management')
def room_management():
    try:
        # Fetch data from S3
        response = s3.list_objects_v2(Bucket=bucket_name)
        bookings = []
        for obj in response.get('Contents', []):
            booking_data = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
            booking_content = booking_data['Body'].read().decode('utf-8')
            bookings.append(json.loads(booking_content))

        return render_template('room_management.html', buchungen=bookings)
    except NoCredentialsError:
        return "Credentials not available", 500
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
