from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect('database/users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------- PRODUCTS ----------------
products = {
    1: {"id": 1, "name": "Brake Pads", "price": 1200},
    2: {"id": 2, "name": "Engine Oil", "price": 800},
    3: {"id": 3, "name": "Car Battery", "price": 5000},
    4: {"id": 4, "name": "Tyres", "price": 3000}
}

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (request.form['username'], request.form['email'], request.form['password']))
        conn.commit()
        conn.close()
        return redirect('/login')

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('database/users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?",
                  (request.form['email'], request.form['password']))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user[1]
            return redirect('/products')
        else:
            return "Invalid credentials"

    return render_template("login.html")

# ---------------- PRODUCTS ----------------
@app.route('/products')
def products_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template("products.html", products=products)

# ---------------- ADD TO CART ----------------
@app.route('/add_to_cart/<int:pid>')
def add_to_cart(pid):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(products[pid])
    session.modified = True

    return redirect('/products')

# ---------------- CART ----------------
@app.route('/cart')
def cart():
    cart_items = session.get("cart", [])
    total = sum(item["price"] for item in cart_items)
    return render_template("cart.html", cart=cart_items, total=total)

# ---------------- REMOVE ITEM ----------------
@app.route('/remove/<int:index>')
def remove(index):
    cart = session.get("cart", [])

    if 0 <= index < len(cart):
        cart.pop(index)

    session["cart"] = cart
    session.modified = True

    return redirect('/cart')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)