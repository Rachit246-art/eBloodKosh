from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "database.db"

# -------------------- DATABASE INIT --------------------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        # Donors table
        cur.execute('''CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            blood_group TEXT,
            phone TEXT,
            city TEXT,
            email TEXT
        )''')

        # Requests table
        cur.execute('''CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_name TEXT,
            required_group TEXT,
            units INTEGER,
            city TEXT,
            status TEXT DEFAULT 'Pending'
        )''')

        # Admins table
        cur.execute('''CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )''')

        # Queries table
        cur.execute('''CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT
        )''')

        # Insert default admin if not exists
        cur.execute("SELECT * FROM admins WHERE username=?", ("1234",))
        if not cur.fetchone():
            cur.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ("1234", "9758"))

        conn.commit()

# -------------------- ROUTES --------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_group = request.form['blood_group']
        phone = request.form['phone']
        city = request.form['city']
        email = request.form['email']

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO donors (name, age, blood_group, phone, city, email) VALUES (?, ?, ?, ?, ?, ?)",
                (name, age, blood_group, phone, city, email)
            )
            conn.commit()

        flash("Registration successful!", "success")
        return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        group = request.form['blood_group']
        city = request.form['city']
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute("SELECT * FROM donors WHERE blood_group=? AND city=?", (group, city))
            results = cursor.fetchall()
    return render_template('search.html', results=results)

@app.route('/request_blood', methods=['GET', 'POST'])
def request_blood():
    if request.method == 'POST':
        requester_name = request.form['requester_name']
        required_group = request.form['required_group']
        units = request.form['units']
        city = request.form['city']

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO requests (requester_name, required_group, units, city) VALUES (?, ?, ?, ?)",
                (requester_name, required_group, units, city)
            )
            conn.commit()

        flash("Request submitted!", "success")
        return redirect(url_for('request_blood'))
    return render_template('request.html')

@app.route('/query', methods=['POST'])
def query():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO queries (name, email, message) VALUES (?, ?, ?)",
            (name, email, message)
        )
        conn.commit()

    flash("Your query has been submitted!", "success")
    return redirect(url_for('home'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute("SELECT * FROM admins WHERE username=? AND password=?", (user, pwd))
            admin = cursor.fetchone()
        if admin:
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid login", "danger")
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    with sqlite3.connect(DB_NAME) as conn:
        cursor1 = conn.execute("SELECT * FROM donors")
        donors_data = cursor1.fetchall()

        cursor2 = conn.execute("SELECT * FROM requests")
        requests_data = cursor2.fetchall()

        cursor3 = conn.execute("SELECT * FROM queries")
        queries_data = cursor3.fetchall()

    return render_template('admin_dashboard.html', donors=donors_data, requests=requests_data, queries=queries_data)

# -------------------- MAIN --------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
