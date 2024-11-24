import logging, os
from logging.config import dictConfig

import psycopg2
from flask import Flask, session
from flask.logging import default_handler
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)-5s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %Z",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
)

db_config = {
  'dbname':   os.environ.get('DB_SID', ''),
  'user':     os.environ.get('DB_USERNAME', ''),
  'password': os.environ.get('DB_PASSWORD', ''),
  'host':     os.environ.get('DB_HOSTNAME', ''),
  'port':     os.environ.get('DB_PORT', '5432')
}

logger = logging.getLogger("root")

def create_app(app_name):
    app = Flask(app_name)
    CORS(app)
    name = app_name
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    app.secret_key = os.getenv('SESSION_KEY', default='BAD_SECRET_KEY')
    logger.info("Start " + app_name)
    return app

def create_db_connection():
    logger.debug("Db Config: " + str(db_config))

    try:
        db_connection = psycopg2.connect(**db_config)
        logger.info(f"Verbindung zur Datenbank {db_config['dbname']} erstellt")
        logger.debug(db_connection)
        return db_connection
    except Exception as err:
        logger.error(f"Fehler bei der Verbindung zur Datenbank {db_config['dbname']}: {err}")
        raise

def debug_request(request):
    logger.info(request)
    logger.debug(session)
