from flask import Flask, redirect, url_for, session, request
from werkzeug.middleware.proxy_fix import ProxyFix
from authlib.integrations.flask_client import OAuth
import os
import logging

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
app.logger.setLevel(logging.DEBUG)
app.logger.debug("Start login")

app.secret_key = '12345678910111213141516'  # Replace with a strong random value
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('OAUTH_CLIENT_ID', '')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('OAUTH_CLIENT_SECRET', '')



CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

app.logger.debug("Register oauth")

@app.route('/authorize')
def authorize():
    app.logger.debug("Route: " + request.path)

    try:
        token = oauth.google.authorize_access_token()
    except Exception as e:
        app.logger.error(f'Fehler bei der Autorisierung: {e}')
        return redirect('/home')

    app.logger.debug(token)

    session['google_token'] = token
    session['user'] = token.get('userinfo').get('name')
    app.logger.debug(session['user'])

    session['email'] = token.get('userinfo').get('email')
    app.logger.debug(session['email'])


    app.logger.info("Login: " + session.get('user') + " " + session.get('email'))


    if session['user_type'] == 'employee':
        redirect_url = "/room-management"
    else:
        redirect_url = "/home"

    return redirect(redirect_url)

@app.route('/login/<user_type>')
def login(user_type):
    app.logger.debug("Route: " + request.path)
    app.logger.debug("user_type: " + user_type)
    app.logger.debug(session)

    if user_type == 'dummy':
        session['user_type'] = 'employee'
        session['user'] = 'John Doe'
        session['email'] = 'john@doe.com'
        session['google_token'] = 'john@doe.com'
        return redirect("/home")

    session['user_type'] = user_type
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    app.logger.debug("Route: " + request.path)
    app.logger.debug(session)

    if 'google_token' in session:
        session.pop('google_token', None)
        session.pop('user_type', None)
        app.logger.info("Logout: " + session.pop('user') + " " + session.pop('email'))
        app.logger.debug(session)

    return redirect("/home")

if __name__ == '__main__':
    app.run(debug=True, port=80)
