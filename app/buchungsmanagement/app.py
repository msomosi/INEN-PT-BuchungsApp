import json
import os

import boto3
from botocore.exceptions import NoCredentialsError
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, request

app = create_app("buchungsmanagement")

#OLD