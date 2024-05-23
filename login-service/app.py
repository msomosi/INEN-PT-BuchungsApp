from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.secret_key = 'random_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

oauth = OAuth(app)
keycloak = oauth.remote_app(
    'keycloak',
    consumer_key='booking-app',  # Client ID
    consumer_secret='client-secret',  # Client Secret
    request_token_params={
        'scope': 'openid email profile'
    },
    base_url='http://keycloak:8080/auth/realms/studentenwohnheim/protocol/openid-connect',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='/token',
    authorize_url='/auth'
)

@app.route('/')
def index():
    if 'keycloak_token' in session:
        return redirect(url_for('protected'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return keycloak.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('keycloak_token')
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = keycloak.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error'], request.args['error_description']
        )

    session['keycloak_token'] = (response['access_token'], '')
    return redirect(url_for('protected'))

@app.route('/protected')
def protected():
    if 'keycloak_token' in session:
        # Successful login, redirect to the booking management service
        return redirect("http://buchungsmanagement-service/buchungen")
    return redirect(url_for('login'))

@keycloak.tokengetter
def get_keycloak_oauth_token():
    return session.get('keycloak_token')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
