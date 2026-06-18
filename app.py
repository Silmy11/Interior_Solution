from flask import Flask, render_template, request, redirect, session, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'spr_ultimate_clean_key'
DATABASE = 'spr_final.db'  # Brand new file name to avoid legacy column errors

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS parts (id INTEGER PRIMARY KEY, name TEXT, status TEXT, inspector TEXT)')
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if 'email' not in session:
        return redirect('/login') 
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        status = request.form['status']
        db.execute('INSERT INTO parts (name, status, inspector) VALUES (?, ?, ?)', (name, status, session['email']))
        db.commit()
        return redirect('/')
    parts = db.execute('SELECT * FROM parts').fetchall()#prevents  duplicats
    return render_template('dashboard.html', parts=parts, email=session['email'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if 'register' in request.form:
            if user:
                msg = "Account already exists! Try logging in."
            else:
                db.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, generate_password_hash(password)))
                db.commit()
                msg = "Registered successfully! Now, please log in below."
        elif 'login' in request.form:
            if user and check_password_hash(user['password'], password):
                session['email'] = email
                return redirect('/')
            msg = "Access Denied. Invalid credentials or account not registered."
    return render_template('auth.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
