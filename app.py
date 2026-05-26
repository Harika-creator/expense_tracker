from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "expense_secret"

# DATABASE
def init_db():

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT

    )
    ''')

    # EXPENSES TABLE
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        description TEXT

    )
    ''')

    conn.commit()
    conn.close()

init_db()

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session['user_id'] = user[0]
            return redirect('/')

    return render_template('login.html')

# LOGOUT
@app.route('/logout')
def logout():

    session.clear()
    return redirect('/login')

# HOME
@app.route('/', methods=['GET', 'POST'])
def index():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    # ADD EXPENSE
    if request.method == 'POST':

        amount = request.form['amount']
        category = request.form['category']
        description = request.form['description']

        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, description) VALUES (?, ?, ?, ?)",
            (session['user_id'], amount, category, description)
        )

        conn.commit()

    # SHOW USER EXPENSES
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (session['user_id'],)
    )

    expenses = cursor.fetchall()

    # TOTAL
    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id=?",
        (session['user_id'],)
    )

    total = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'index.html',
        expenses=expenses,
        total=total
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)