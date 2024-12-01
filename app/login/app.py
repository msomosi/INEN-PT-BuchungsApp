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
        session['google_token'] = token
        session['user'] = token.get('userinfo').get('name')
        session['email'] = token.get('userinfo').get('email')

        app.logger.debug(f"User logged in: {session['user']} ({session['email']})")
    except Exception as e:
        app.logger.error(f'Fehler bei der Autorisierung: {e}')
        return redirect('/home')

    
    return redirect('/home')


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    app.logger.debug(f"Login-Anfrage erhalten: username={username}, password={password}")

    try:
        conn = create_db_connection()
        cursor = conn.cursor()

        # Prüfen, ob der Benutzer existiert
        cursor.execute("""
            SELECT u.user_id, u.role_id, r.role_name, u.username
            FROM "user" u
            JOIN role r ON u.role_id = r.role_id
            WHERE u.username = %s AND u.password = %s
        """, (username, password))

        user = cursor.fetchone()

        if user:
            session.clear()
            session['user_id'] = user[0]  # Eindeutige Benutzer-ID
            session['role_id'] = user[1]  # Rolle des Benutzers
            session['user_type'] = user[2]  # Name der Rolle (z. B. "admin", "student", "anbieter")
            session['user'] = user[3]  # Benutzername
            
            app.logger.debug(f"Session-Daten nach Login: {session}")


            return jsonify({
                'message': user[3],
                'redirect': '/home'
            })
        else:
            app.logger.warning(f"Ungültige Login-Daten: username={username}")
            return jsonify({'error': "Ungültige Anmeldedaten"}), 401
    except Exception as err:
        app.logger.error(f"Fehler beim Login: {err}")
        return jsonify({'error': 'Interner Serverfehler'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()



@app.route('/logout')
def logout():
    debug_request(request)

    if 'google_token' in session:
        session.pop('google_token', None)
        session.pop('user_type', None)
        app.logger.info("Logout: " + session.pop('user') + " " + session.pop('email'))
        
        app.logger.debug(session)
    session.clear()
    return redirect("/home")

@app.route('/user/<id>')
def user(id):
    debug_request(request)

    db = create_db_connection()
    try:
        with db.cursor() as cur:
            query = """
                SELECT u.user_id, u.first_name, u.last_name, u.email, r.role_name
                FROM "user" u
                JOIN role r ON u.role_id = r.role_id
                WHERE u.user_id = %s;
            """
            cur.execute(query, (id,))

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
