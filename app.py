from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = 'secret123'


# ---------------- DATABASE ---------------- #

def init_db():

    conn = sqlite3.connect('expenses.db')

    cursor = conn.cursor()

    # Expense Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        category TEXT,
        description TEXT

    )
    ''')

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT

    )
    ''')

    conn.commit()
    conn.close()


init_db()


# ---------------- REGISTER ---------------- #

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


# ---------------- LOGIN ---------------- #

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

            session['user'] = username

            return redirect('/')

    return render_template('login.html')


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


# ---------------- HOME PAGE ---------------- #

@app.route('/')
def index():

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")

    expenses = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    return render_template(
        'index.html',
        expenses=expenses,
        total=total
    )


# ---------------- ADD EXPENSE ---------------- #

@app.route('/add', methods=['POST'])
def add_expense():

    amount = request.form['amount']
    category = request.form['category']
    description = request.form['description']

    conn = sqlite3.connect('expenses.db')

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)",
        (amount, category, description)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- DELETE EXPENSE ---------------- #

@app.route('/delete/<int:id>')
def delete_expense(id):

    conn = sqlite3.connect('expenses.db')

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- RUN APP ---------------- #

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)