import logging, os
from logging.config import dictConfig

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

logger = logging.getLogger("root")

def create_app(app_name):
    app = Flask(app_name)
    CORS(app)
    name = app_name
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    app.secret_key = os.getenv('SESSION_KEY', default='BAD_SECRET_KEY')
    logger.info("Start " + app_name)
    return app

def debug_request(request):
    logger.info(request)
    logger.debug(session)
