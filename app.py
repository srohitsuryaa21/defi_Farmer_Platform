import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from blockchain.blockchain_utils import (
    create_product_on_blockchain,
    get_product_count,
    update_product_status_on_blockchain,
    get_product_from_blockchain
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"

DB_PATH = "database/app.db"


# --------------------------
# Database Connection
# --------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------
# Create Tables
# --------------------------
def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        crop_name TEXT NOT NULL,
        quantity TEXT NOT NULL,
        location TEXT NOT NULL,
        harvest_date TEXT NOT NULL,
        price TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Available',
        blockchain_status TEXT NOT NULL DEFAULT 'Not Synced',
        blockchain_product_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        buyer_id INTEGER NOT NULL,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (buyer_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()


create_tables()


# --------------------------
# Home
# --------------------------
@app.route("/")
def home():
    return render_template("index.html")


# --------------------------
# Register
# --------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form["role"]

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (full_name, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (full_name, email, hashed_password, role))

            conn.commit()
            conn.close()

            flash("Registration successful. Please login.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email already exists.")

    return render_template("register.html")


# --------------------------
# Login
# --------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["role"] = user["role"]

            if user["role"] == "Farmer":
                return redirect(url_for("farmer_dashboard"))
            elif user["role"] == "Buyer":
                return redirect(url_for("buyer_dashboard"))
        else:
            flash("Invalid login details.")

    return render_template("login.html")


# --------------------------
# Farmer Dashboard
# --------------------------
@app.route("/farmer/dashboard")
def farmer_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Farmer":
        flash("Access denied.")
        return redirect(url_for("home"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products
        WHERE farmer_id = ?
        ORDER BY id DESC
    """, (session["user_id"],))
    products = cursor.fetchall()
    conn.close()

    blockchain_count = get_product_count()

    return render_template(
        "farmer_dashboard.html",
        name=session["user_name"],
        products=products,
        blockchain_count=blockchain_count
    )


# --------------------------
# Add Product
# --------------------------
@app.route("/farmer/add-product", methods=["GET", "POST"])
def add_product():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Farmer":
        flash("Access denied.")
        return redirect(url_for("home"))

    if request.method == "POST":
        crop_name = request.form["crop_name"].strip()
        quantity = request.form["quantity"].strip()
        location = request.form["location"].strip()
        harvest_date = request.form["harvest_date"].strip()
        price = request.form["price"].strip()

        blockchain_status = "Synced"
        blockchain_product_id = None

        try:
            result = create_product_on_blockchain(
                crop_name,
                quantity,
                location,
                harvest_date,
                price
            )
            blockchain_product_id = result["blockchain_product_id"]
        except Exception as e:
            blockchain_status = f"Failed: {str(e)}"

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (
                farmer_id, crop_name, quantity, location, harvest_date, price,
                blockchain_status, blockchain_product_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            crop_name,
            quantity,
            location,
            harvest_date,
            price,
            blockchain_status,
            blockchain_product_id
        ))
        conn.commit()
        conn.close()

        if blockchain_status == "Synced":
            flash(f"Product batch added and synced to blockchain. Blockchain ID: {blockchain_product_id}")
        else:
            flash("Product added to database, but blockchain sync failed.")

        return redirect(url_for("farmer_dashboard"))

    return render_template("add_product.html")


# --------------------------
# Buyer Dashboard
# --------------------------
@app.route("/buyer/dashboard")
def buyer_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Buyer":
        flash("Access denied.")
        return redirect(url_for("home"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            products.*,
            users.full_name AS farmer_name
        FROM products
        JOIN users ON products.farmer_id = users.id
        WHERE products.status = 'Available'
        ORDER BY products.id DESC
    """)
    products = cursor.fetchall()

    cursor.execute("""
        SELECT 
            purchases.id AS purchase_id,
            purchases.purchase_date,
            products.id AS product_id,
            products.crop_name,
            products.quantity,
            products.location,
            products.harvest_date,
            products.price,
            products.status,
            products.blockchain_status,
            products.blockchain_product_id,
            users.full_name AS farmer_name
        FROM purchases
        JOIN products ON purchases.product_id = products.id
        JOIN users ON products.farmer_id = users.id
        WHERE purchases.buyer_id = ?
        ORDER BY purchases.id DESC
    """, (session["user_id"],))
    purchased_products = cursor.fetchall()

    conn.close()

    return render_template(
        "buyer_dashboard.html",
        name=session["user_name"],
        products=products,
        purchased_products=purchased_products
    )


# --------------------------
# Buy Product
# --------------------------
@app.route("/buyer/buy/<int:product_id>", methods=["POST"])
def buy_product(product_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Buyer":
        flash("Access denied.")
        return redirect(url_for("home"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE id = ? AND status = 'Available'
    """, (product_id,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        flash("Product is no longer available.")
        return redirect(url_for("buyer_dashboard"))

    new_blockchain_status = product["blockchain_status"]

    if product["blockchain_product_id"]:
        try:
            update_product_status_on_blockchain(product["blockchain_product_id"], "Sold")
            new_blockchain_status = "Sold Synced"
        except Exception as e:
            new_blockchain_status = f"Sold in DB, chain sync failed: {str(e)}"

    cursor.execute("""
        INSERT INTO purchases (product_id, buyer_id)
        VALUES (?, ?)
    """, (product_id, session["user_id"]))

    cursor.execute("""
        UPDATE products
        SET status = 'Sold',
            blockchain_status = ?
        WHERE id = ?
    """, (new_blockchain_status, product_id))

    conn.commit()
    conn.close()

    flash("Product purchased successfully.")
    return redirect(url_for("buyer_dashboard"))


# --------------------------
# Product Traceability / Details
# --------------------------
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            products.*,
            farmer.full_name AS farmer_name
        FROM products
        JOIN users AS farmer ON products.farmer_id = farmer.id
        WHERE products.id = ?
    """, (product_id,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        flash("Product not found.")
        return redirect(url_for("home"))

    cursor.execute("""
        SELECT 
            purchases.purchase_date,
            buyer.full_name AS buyer_name
        FROM purchases
        JOIN users AS buyer ON purchases.buyer_id = buyer.id
        WHERE purchases.product_id = ?
        ORDER BY purchases.id DESC
        LIMIT 1
    """, (product_id,))
    purchase = cursor.fetchone()

    conn.close()

    blockchain_product = None
    if product["blockchain_product_id"]:
        try:
            blockchain_product = get_product_from_blockchain(product["blockchain_product_id"])
        except Exception:
            blockchain_product = None

    return render_template(
        "product_detail.html",
        product=product,
        purchase=purchase,
        blockchain_product=blockchain_product
    )


# --------------------------
# Logout
# --------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)