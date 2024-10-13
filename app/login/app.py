from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, session, request
import os
import logging

app = Flask(__name__)
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

@app.route('/login/<user_type>')
def login(user_type):
    app.logger.debug("Route: " + request.path)
    app.logger.debug("user_type: " + user_type)
    app.logger.debug(session)

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

@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    session['user'] = token['userinfo']

    user_type = session.get('user_type', 'student')
    if user_type == 'employee':
        redirect_url = "/room_management"
    else:
        redirect_url = "/home"

    session['google_token'] = oauth.google.authorize_access_token()
    me = google.get('userinfo')

    return redirect(redirect_url)

@app.route('/authorize1')
def authorize1():
    try:
        token = oauth.google.authorize_access_token()
        resp = oauth.google.get('userinfo')
        user_info = resp.json()
        session['email'] = user_info['email']
        access_token = create_access_token(identity=user_info['email'])

        user_type = session.get('user_type', 'student')
        if user_type == 'employee':
            redirect_url = "/room-management"
        else:
            redirect_url = "/home"

        return response
    except Exception as e:
        print(f'Fehler bei der Autorisierung: {e}')
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
