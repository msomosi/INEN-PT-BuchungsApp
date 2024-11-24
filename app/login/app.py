import os

from authlib.integrations.flask_client import OAuth
from factory import create_app, create_db_connection, debug_request
from flask import jsonify, redirect, request, session, url_for

app = create_app("login")

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
    debug_request(request)

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

    if user:
        app.logger.info("Login: " + session.get('user') + " " + session.get('email'))
    else:
        user = User(email=email, name=name, oauth_provider='google', is_verified=True)
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"Neuer Benutzer hinzugefügt: {user.name} ({user.email})")

    session['user_id'] = user.id

    # Weiterleitung basierend auf dem user_type
    if session['user_type'] == 'employee' or session['user_type'] == 'anbieter':
        redirect_url = "/room-management"
    else:
        redirect_url = "/home"

    return redirect(redirect_url)

@app.route('/login/<user_type>')
def login(user_type):
    debug_request(request)
    app.logger.debug("user_type: " + user_type)

    # Dummy-Login für Tests
    if user_type == 'dummy':
        session.clear()
        session['user_type'] = 'employee'
        session['user'] = 'John Doe'
        session['email'] = 'john@doe.com'
        session['google_token'] = 'john@doe.com'
        return redirect("/home")

    # Anbieter-Login ohne OAuth
    if user_type == 'anbieter':
        session.clear()
        session['user_type'] = 'anbieter'
        session['user'] = 'Anbieter Test'
        session['email'] = 'anbieter@test.com'
        return redirect("/room-management")

    # Speichern des user_type in der Session
    session['user_type'] = user_type

    # Google OAuth Weiterleitung
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    debug_request(request)

    if 'google_token' in session:
        session.pop('google_token', None)
        session.pop('user_type', None)
        app.logger.info("Logout: " + session.pop('user') + " " + session.pop('email'))
        session.clear()
        app.logger.debug(session)

    return redirect("/home")

@app.route('/user/<id>')
def user(id):
    debug_request(request)

    db = create_db_connection()
    try:
        with db.cursor() as cur:
            query = """
                SELECT *
                FROM tbl_user_details u
                WHERE u.user_id = %s;
            """
            cur.execute(query, (id))
            user_details = cur.fetchone()
            if not user_details:
                msg = f"User nicht gefunden: " + str(id)
                app.logger.error(msg)
                return jsonify({'error': msg}), 404
                # Status Code 404 – Ressource nicht gefunden: Die angeforderte Seite oder Ressource kann nicht gefunden werden.

            app.logger.debug(user_details)

            columns = [column[0] for column in cur.description]
            app.logger.debug(columns)

            sanitize = lambda s: s.strip() if isinstance(s, str) else s
            data = dict(zip(columns, map( sanitize, user_details)))
            app.logger.debug(data)

            return jsonify(data)
    except Exception as err:
        msg = f"Datenbankabfrage fehlgeschlagen: " + str(err)
        app.logger.error(msg)
        return jsonify({'error': msg}), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True, port=80)
