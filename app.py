from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from openpyxl.reader.excel import load_workbook
from werkzeug.security import generate_password_hash, check_password_hash
import openpyxl
from filelock import FileLock
import shelve
import logging
from discount import *
from datetime import datetime, timedelta
import random
import string


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_FILE = 'users.db'
filename = "user_data.xlsx"
lockfile = f"{filename}.lock"

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/login")
def customer_login():
    return render_template("login.html")

@app.route("/staff_login")
def staff_login():
    return render_template("staff_login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form['phone']
        birthdate = request.form['birth']
        channels = request.form.getlist("channels")


        hashed_password = generate_password_hash(password)

        with shelve.open(DB_FILE, writeback=True) as db:
            if email in db:
                flash("Email already registered. Please log in.", "error")
                return redirect(url_for("login"))

            db[email] = {
                "name": name,
                "email": email,
                "password": hashed_password,
                'birthdate':birthdate,
                "points": 0,
                "vouchers":[],
                "channels":channels,
                'phone':phone
            }

            #Add 90% off voucher for new user
            voucher = Voucher(
                code="WELCOME90",
                discount=90,
                description="90% off for new customers",
                expiry_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")  # 7-day expiry
            )
            db[email]["vouchers"].append(voucher.__dict__)  # Store as a dict

        with FileLock(lockfile):
            workbook = load_workbook(filename)
            sheet = workbook.active
            sheet.append([name, email, phone, hashed_password,birthdate, ",".join(channels)])
            workbook.save(filename)

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


def is_weekend(date=None):
    if date is None:
        date = datetime.now()
    return date.weekday() in [5, 6]  # Saturday (5) or Sunday (6)

def remove_expired_vouchers(user):
    current_time = datetime.now()
    user['vouchers'] = [
        v for v in user['vouchers']
        if 'expiry_date' not in v or
        (isinstance(v["expiry_date"], str) and datetime.strptime(v["expiry_date"], "%Y-%m-%d %H:%M:%S") > current_time) or
        (isinstance(v["expiry_date"], datetime) and v["expiry_date"] > current_time)
    ]



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        with shelve.open(DB_FILE) as db:
            user = db.get(email)

            if user:
                if "vouchers" not in user:
                    user["vouchers"] = []
                else:
                    remove_expired_vouchers(user)

                    weekend_voucher_code = "WEEKEND50"
                    user['vouchers'] = [v for v in user['vouchers'] if
                                        not (v["code"] == weekend_voucher_code and not is_weekend())]

                db[email] = user

        if user and check_password_hash(user['password'], password):
            session["user"] = user

            if is_weekend():
                voucher = Voucher(
                    code="WEEKEND50",
                    discount=50,
                    description="50% off during weekends",
                )
                if voucher.__dict__ not in user["vouchers"]:
                    with shelve.open(DB_FILE, writeback=True) as db:
                        db[email]["vouchers"].append(voucher.__dict__)
                        session["user"] = db[email]  # Update session with new data


            flash(f"Welcome, {user['name']}!", 'success')
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.","error")

    return render_template("login.html")



@app.route("/dashboard")
def dashboard():
    user = session.get("user")  # Retrieve user info from the session
    if not user:
        flash("Please log in to access the dashboard.", 'error')
        return redirect(url_for("login"))

    # Pass the user object from the session to the template
    return render_template("dashboard.html", user=user)

@app.route("/account_information")
def account_information():
    user = session.get("user")
    if not user:
        flash("Please log in to access account information.", 'error')
        return redirect(url_for("login"))

    user_email = user['email']  # Use user email as identifier

    # Retrieve user's points from shelve
    with shelve.open('user_data') as db:
        user['points'] = db.get(user_email, {}).get('points', 0)

    return render_template("account_information.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.",'success')
    return redirect(url_for("login"))

@app.route("/about")
def about():
    return render_template("dashboard.html")

def load_workbook(filename):
    try:
        workbook = openpyxl.load_workbook(filename)
    except FileNotFoundError:
        workbook = openpyxl.Workbook()
        workbook.active.append(["Name", "Email", "Phone", "Password", "Birthdate","Channels"])  # Add headers
        workbook.save(filename)
    return workbook

@app.route("/update_details", methods=["GET", "POST"])
def update_details():
    user = session.get("user")
    if not user:
        flash("Please log in to update your details.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        with shelve.open(DB_FILE, writeback=True) as db:
            db_user = db.get(user["email"])
            if not db_user:
                flash("User not found.", "error")
                return redirect(url_for("account_information"))

            db_user["name"] = name
            db_user["email"] = email
            db_user["phone"] = phone
            db[user["email"]] = db_user

            session["user"] = db_user

        with FileLock(lockfile):
            workbook = load_workbook(filename)
            sheet = workbook.active
            for row in sheet.iter_rows():
                if row[1].value == user["email"]:
                    row[0].value = name
                    row[2].value = phone
                    row[1].value = email
                    break
            workbook.save(filename)

        flash("Details updated successfully.", "success")
        return redirect(url_for("account_information"))

    return render_template("update_details.html", user=user)

@app.route("/loading")
def loading():
    return render_template("loading.html")

@app.route("/redeem_voucher", methods=["POST"])
def redeem_voucher():
    user = session.get("user")
    if not user:
        flash("Please log in to redeem a voucher.", "error")
        return redirect(url_for("login"))

    voucher_code = request.form["voucher_code"]
    purchase_amount = float(request.form["purchase_amount"])

    with shelve.open(DB_FILE, writeback=True) as db:
        db_user = db.get(user["email"])
        if not db_user:
            flash("User not found.", "error")
            return redirect(url_for("dashboard"))

        if "vouchers" not in db_user:
            db_user["vouchers"] = []
            db[user["email"]] = db_user

        voucher = next((v for v in db_user["vouchers"] if v["code"] == voucher_code), None)
        if not voucher:
            flash("Voucher not found or already used.", "error")
            return redirect(url_for("dashboard"))

        discount_amount = (purchase_amount * voucher["discount"]) / 100
        final_amount = purchase_amount - discount_amount

        db_user["vouchers"].remove(voucher)
        db[user["email"]] = db_user
        session["user"] = db_user
        session["final_amount"] = final_amount

    flash(f"Voucher applied! You saved {discount_amount:.2f}. Final amount: {final_amount:.2f}.", "success")
    return redirect(url_for("payment"))

# Menu
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    cart_count = len(session.get('cart', []))

    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'POST':
        location = request.form.get('location', '')
        session['location'] = location

        item_name = request.form.get('name', '')
        item_price = float(request.form.get('price', 0.0))

        # Handle missing item_name gracefully
        if item_name:
            base = request.form.get(f'base_{item_name.lower().replace(" ", "_")}', '')
            sugar = request.form.get(f'sugar_{item_name.lower().replace(" ", "_")}', '')
            ice = request.form.get(f'ice_{item_name.lower().replace(" ", "_")}', '')
            size = request.form.get(f'size_{item_name.lower().replace(" ", "_")}', '')
            remark = request.form.get(f'remark_{item_name.lower().replace(" ", "_")}', '')
            quantity = int(request.form.get(f'quantity_{item_name.lower().replace(" ", "_")}', 1))  # Default quantity to 1
        else:
            # Handle missing item name (e.g., display an error message)
            return render_template('menu.html', error="Item name is missing.")

        item = {
            'name': item_name,
            'price': item_price,
            'base': base,
            'sugar': sugar,
            'ice': ice,
            'size': size,
            'remark': remark,
            'quantity': quantity
        }
        session['cart'].append(item)
        session.modified = True
        return redirect(url_for('menu'))

    return render_template('menu.html', cart_count=cart_count)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    item = data.get('item')
    price = data.get('price')
    base = data.get('base')
    sugar = data.get('sugar')
    ice = data.get('ice')
    size = data.get('size')
    remark = data.get('remark')
    quantity = data.get('quantity', 1)

    cart = session.get('cart', [])
    cart.append({
        'name': item,
        'price': float(price),
        'base': base,
        'sugar': sugar,
        'ice': ice,
        'size': size,
        'remark': remark,
        'quantity': int(quantity)
    })
    session['cart'] = cart
    return jsonify(cart_count=len(cart))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    location = session.get('location', '')
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    gst = subtotal * 0.09
    total = subtotal + gst
    return render_template('cart.html', cart=cart, location=location, subtotal=subtotal, gst=gst, total=total)

@app.route('/remove_item/<int:index>', methods=['GET'])
def remove_item(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        del cart[index]
        session['cart'] = cart
    return redirect(url_for('cart'))

#Payment
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # Process the payment details here
        cart = session.get('cart', [])
        subtotal = sum(item['price'] * item['quantity'] for item in cart)
        gst = subtotal * 0.09
        total = subtotal + gst

        # Store the total amount as points in shelve
        user = session.get('user')
        if user:
            user_email = user['email']
            with shelve.open('user_data') as db:
                user_data = db.get(user_email, {'points': 0})
                user_data['points'] += total
                db[user_email] = user_data

        # Store final amount in session
        session['final_amount'] = total

    cart = session.get('cart', [])
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    gst = subtotal * 0.09
    total = subtotal + gst
    final_amount = session.get('final_amount', total)

    return render_template('payment.html', cart=cart, subtotal=subtotal, gst=gst, total=total, final_amount=final_amount)



#Order Summary
@app.route('/order_summary')
def order_summary():
    current_time = datetime.now()
    order_time = session.get('order_time')

    if order_time:
        order_time = datetime.strptime(order_time, '%Y-%m-%d %H:%M')
        if current_time - order_time > timedelta(minutes=10):
            session.pop('order_number', None)
            session.pop('order_time', None)
            session.pop('cart', None)
            return render_template('order_summary.html', order_number=None, location=None, collection_time=None,
                                   cart=[], subtotal=0, gst=0, total=0)

    else:
        order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        session['order_number'] = order_number
        session['order_time'] = current_time.strftime('%Y-%m-%d %H:%M')

    order_number = session.get('order_number')
    location = session.get('location', 'Not selected')
    cart = session.get('cart', [])
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    gst = subtotal * 0.09
    total = subtotal + gst
    collection_time = (current_time + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M')

    user = session.get('user')
    if user is None:
        flash('No user ID found in session. Please log in.', 'error')
        return redirect(url_for('login'))

    user_email = user['email']

    # Store the total amount as points in shelve
    with shelve.open('user_data') as db:
        user_data = db.get(user_email, {'points': 0})
        user_data['points'] += total
        db[user_email] = user_data

    return render_template('order_summary.html', cart=cart, order_number=order_number, location=location,
                           collection_time=collection_time, subtotal=subtotal, gst=gst, total=total)



# Contact Us
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route to handle form submission
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # Retrieve form data
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    nature = request.form['nature']
    outlet = request.form['outlet']
    date = request.form['date']
    time = request.form['time']
    message = request.form['message']

    # Store the form data in Shelve
    with shelve.open('contact_data.db', writeback=True) as db:
        if 'contacts' not in db:
            db['contacts'] = []
        db['contacts'].append({
            'name': name,
            'email': email,
            'phone': phone,
            'nature': nature,
            'outlet': outlet,
            'date': date,
            'time': time,
            'message': message,
        })

    flash("Your message has been submitted successfully!", "success")
    return redirect(url_for('success'))

# Route for success page
@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == "__main__":
    app.run(debug=True)
