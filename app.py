from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
import psycopg2
from flask_bcrypt import Bcrypt
import qrcode
from io import BytesIO
import os

app = Flask(__name__)
app.secret_key = 'sdfghjklghjkl98765433456yui'
bcrypt = Bcrypt(app)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="tododb",
        user="postgres",
        password="22882288"
    )
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        user_email = session.get('user_email')
        return render_template('index.html', user_email=user_email)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and bcrypt.check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_email'] = user[1]  # Store user email in session
            return redirect(url_for('activity'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (email, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/activity', methods=['GET', 'POST'])
def activity():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_email = session['user_email']
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        if 'delete' in request.form:
            activity_id = request.form['activity_id']
            cur.execute('DELETE FROM activities WHERE id = %s AND user_id = %s', (activity_id, user_id))
            conn.commit()
        else:
            activity = request.form['activity']
            time = request.form['time']
            cur.execute('INSERT INTO activities (user_id, activity, time) VALUES (%s, %s, %s)', (user_id, activity, time))
            conn.commit()

    cur.execute('SELECT id, activity, time FROM activities WHERE user_id = %s', (user_id,))
    activities = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('activity.html', activities=activities, user_email=user_email)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    return redirect(url_for('index'))

@app.route('/generate_qr')
def generate_qr():
    url = url_for('login', _external=True)
    qr = qrcode.make(url)
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
