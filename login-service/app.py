from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, render_template, session, make_response, request
from flask_jwt_extended import JWTManager, create_access_token
import os

app = Flask(__name__)
app.secret_key = '12345678910111213141516'  # Replace with a strong random value
app.config['JWT_SECRET_KEY'] = '161514131211109876543210'  # Ensure this is secure in production

jwt = JWTManager(app)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='159476032740-lq70m9cthh0iogpcgdcinn0r9ml3o4eg.apps.googleusercontent.com',  # Replace with your Google client ID
    client_secret='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',  # Replace with your Google client secret
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    user_type = request.args.get('user_type', 'student')
    session['user_type'] = user_type
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    try:
        token = oauth.google.authorize_access_token()
        resp = oauth.google.get('userinfo')
        user_info = resp.json()
        session['email'] = user_info['email']
        access_token = create_access_token(identity=user_info['email'])

        user_type = session.get('user_type', 'student')
        if user_type == 'employee':
            redirect_url = os.getenv('ROOM_MANAGEMENT_URL')
        else:
            redirect_url = os.getenv('BOOKINGS_MANAGEMENT_URL')

        response = make_response(redirect(redirect_url))
        response.set_cookie('access_token_cookie', access_token, httponly=True, secure=False, path='/')
        return response
    except Exception as e:
        print(f'Fehler bei der Autorisierung: {e}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
