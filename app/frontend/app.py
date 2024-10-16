from flask import Flask, redirect, url_for, render_template, session, request
import os

app = Flask(__name__)
app.secret_key = '12345678910111213141516'  # Replace with a strong random value

@app.route('/home')
def home():
    if 'google_token' in session:
        return render_template('homev2.html', user=session['user'])
    else:
        return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
