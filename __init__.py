from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from Forms import leaveForm, mcForm
import json
from datetime import datetime
import os
from leave import leave
from mc import mc
import shelve as sh
from data import monthly_sales, individual_sales

app = Flask(__name__, static_folder='static')
app.secret_key = "your-secret-key"

# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        password = request.form['password']

        try:
            with sh.open('staff.db', 'c') as db:
                staff_dict = db.get('staff', {})

        except sh.dbm.error:
            flash('Staff database not found. Please contact support.', 'danger')
            return render_template('login.html')

        if staff_id in staff_dict and staff_dict[staff_id]['password'] == password:
            session['staff_id'] = staff_id
            session['position'] = staff_dict[staff_id]['position']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid staff ID or password. Please try again.', 'danger')

    return render_template('login.html')

# Home page route
@app.route('/homepage')
def home():
    if 'staff_id' in session:
        staff_id = session['staff_id']

        # Example: Assuming the position is stored in session or you can query it from your database
        position = session.get('position')  # Make sure 'position' is stored in session when the user logs in
        if not position:
            flash('Position not found, please contact admin.', 'danger')
            return redirect(url_for('login'))

        return render_template('homepage.html', staff_id=staff_id, position=position)
    else:
        flash('Please log in to access the home page.', 'warning')
        return redirect(url_for('login'))


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()  # Get the search query and make it case-insensitive

    if 'leave records' in query:
        return redirect(url_for('retrieve_leave'))  # Redirect to the leave records page
    elif 'mc records' in query:
        return redirect(url_for('retrieve_mc'))  # Redirect to the MC records page
    elif 'submit mc' in query:
        return redirect(url_for('mc_view'))
    elif 'submit leave' in query :
        return redirect(url_for('leave_view'))# Redirect to the submit MC/Leave page
    else:
        # If no matching query, redirect to home or show an error page
        return redirect(url_for('home'))

@app.route('/leave', methods=['GET', 'POST'])
def leave_view():
    leave_form = leaveForm(request.form)
    if request.method == 'POST' and leave_form.validate():
        leave_dict = {}
        db = sh.open("leave.db", "c")
        try:
            leave_dict = db["leave"]
        except KeyError:
            print("Creating a new leave dictionary.")

        l = leave(
            leave_form.staff_id.data,
            leave_form.starting_date.data,
            leave_form.end_date.data,
            leave_form.reason.data
        )
        leave_dict[l.get_staff_id()] = l
        db["leave"] = leave_dict
        db.close()

        print(
            f"{l.get_staff_id()} submitted leave for {l.get_starting_date()} to {l.get_end_date()} due to {l.get_reason()}.")
        return redirect(url_for('home'))
    return render_template('leave.html', form=leave_form)


@app.route('/mc', methods=['GET', 'POST'])
def mc_view():
    mc_form = mcForm(request.form)
    if request.method == 'POST' and mc_form.validate():
        mc_dict = {}
        db = sh.open("mc.db", "c")
        try:
            mc_dict = db["mc"]
        except KeyError:
            print("Creating a new MC dictionary.")

        m = mc(
            mc_form.staff_id.data,
            mc_form.starting_date.data,
            mc_form.end_date.data,
            mc_form.proof.data
        )
        mc_dict[m.get_staff_id()] = m
        db["mc"] = mc_dict
        db.close()

        print(f"{m.get_staff_id()} submitted an MC for {m.get_starting_date()} to {m.get_end_date()},Proof:{m.get_proof()}")
        return redirect(url_for('home'))
    return render_template('mc.html', form=mc_form)

@app.route('/retrieveleave')
def retrieve_leave():
    leave_dict = {}
    db = sh.open('leave.db', 'r')
    try:
        leave_dict = db['leave']
    except KeyError:
        print("No leave records found.")
    db.close()

    leave_list = list(leave_dict.values())  # Convert dictionary values to a list
    return render_template('retrieveleave.html', leave_list=leave_list)


@app.route('/retrievemc')
def retrieve_mc():
    mc_dict = {}
    db = sh.open('mc.db', 'r')
    try:
        mc_dict = db['mc']
    except KeyError:
        print("No MC records found.")
    db.close()

    mc_list = list(mc_dict.values())  # Convert dictionary values to a list for easier rendering
    return render_template('retrievemc.html', mc_list=mc_list)


@app.route('/updateleave/<int:id>/', methods=['GET', 'POST'])
def update_leave(id):
    update_leave_form = leaveForm(request.form)

    db = sh.open('leave.db', 'c')
    leave_dict = db.get('leave', {})
    db.close()

    l = leave_dict.get(str(id))  # Normalize the key to string

    if not l:
        return f"Leave record with ID {id} not found.", 404

    if request.method == 'POST' and update_leave_form.validate():
        db = sh.open('leave.db', 'w')
        leave_dict = db['leave']
        # Update record
        l.set_staff_id(update_leave_form.staff_id.data)
        l.set_starting_date(update_leave_form.starting_date.data)
        l.set_end_date(update_leave_form.end_date.data)
        l.set_reason(update_leave_form.reason.data)
        leave_dict[str(id)] = l  # Ensure key is str
        db['leave'] = leave_dict
        db.close()
        return redirect(url_for('retrieve_leave'))

    # Pre-populate form
    update_leave_form.staff_id.data = l.get_staff_id()
    update_leave_form.starting_date.data = l.get_starting_date()
    update_leave_form.end_date.data = l.get_end_date()
    update_leave_form.reason.data = l.get_reason()
    return render_template('updateleave.html', form=update_leave_form)


@app.route('/deleteleave/<int:id>', methods=['POST'])
def delete_leave(id):
    db = sh.open('leave.db', 'w')
    leave_dict = db.get('leave', {})
    leave_dict.pop(str(id), None)  # Avoid KeyError, normalize key to string
    db['leave'] = leave_dict
    db.close()
    return redirect(url_for('retrieve_leave'))


@app.route('/updatemc/<int:id>/', methods=['GET', 'POST'])
def update_mc(id):
    update_mc_form = mcForm(request.form)

    db = sh.open('mc.db', 'c')
    mc_dict = db.get('mc', {})
    db.close()

    # Debugging output
    print(f"Debug: All keys in mc_dict = {list(mc_dict.keys())}")
    print(f"Debug: Attempting to retrieve record with key = '{str(id)}'")

    m = mc_dict.get(str(id))  # Ensure ID is a string

    if not m:
        return f"MC record with ID {id} not found.", 404

    if request.method == 'POST' and update_mc_form.validate():
        db = sh.open('mc.db', 'w')
        mc_dict = db['mc']
        # Update record
        m.set_staff_id(update_mc_form.staff_id.data)
        m.set_starting_date(update_mc_form.starting_date.data)
        m.set_end_date(update_mc_form.end_date.data)
        m.set_proof(update_mc_form.proof.data)
        mc_dict[str(id)] = m  # Ensure key is str
        db['mc'] = mc_dict
        db.close()
        return redirect(url_for('retrieve_mc'))

    else:
        db = sh.open('mc.db', 'r')
        mc_dict = db['mc']
        db.close()
        m = mc_dict.get(str(id))
        if m:
            # Pre-populate form
            update_mc_form.staff_id.data = m.get_staff_id()
            update_mc_form.starting_date.data = m.get_starting_date()
            update_mc_form.end_date.data = m.get_end_date()
            update_mc_form.proof.data = m.get_proof()
        return render_template('updatemc.html', form=update_mc_form)


@app.route('/deletemc/<int:id>', methods=['POST'])
def delete_mc(id):
    key = str(id)  # Ensure ID is a string
    db = sh.open('mc.db', 'w')
    mc_dict = db.get('mc', {})
    if key in mc_dict:
        mc_dict.pop(key)
        db['mc'] = mc_dict
        db.close()
        return redirect(url_for('retrieve_mc'))
    else:
        db.close()
        return f"MC record with ID {id} not found.", 404


# Break page route
@app.route("/break", methods=["GET", "POST"])
def break_page():
    if 'staff_id' not in session:
        flash('Please log in to access the break page.', 'warning')
        return redirect(url_for('login'))

    staff_id = session['staff_id']
    position = session.get('position')
    invalid_time = False
    current_time = datetime.now().strftime("%H:%M:%S")
    current_hour = datetime.now().hour
    current_date = datetime.now().strftime("%Y-%m-%d")  # Add the current date for logging

    # Open breaks database
    with sh.open("breaks.db", "c") as db:
        if "break_records" not in db:
            db["break_records"] = {}

        records = db["break_records"]

        if staff_id not in records:
            records[staff_id] = {"break_in": None, "break_out": None, "date": current_date}

        if request.method == "POST":
            break_action = request.form.get("break_action")

            if current_hour < 9 or current_hour >= 23:
                invalid_time = True
            else:
                if break_action == "break_in":
                    records[staff_id]["break_in"] = current_time
                    records[staff_id]["date"] = current_date  # Ensure the date is saved
                    flash(f"Break-in recorded at {current_time}!", "success")
                elif break_action == "break_out":
                    records[staff_id]["break_out"] = current_time
                    flash(f"Break-out recorded at {current_time}!", "success")

                db["break_records"] = records  # Save changes

            # Save to break log if both times exist
            with sh.open("break_log.db", "c") as log_db:
                if "break_log" not in log_db:
                    log_db["break_log"] = {}

                break_log = log_db["break_log"]

                if records[staff_id]["break_in"] and records[staff_id]["break_out"]:
                    break_in_time = datetime.strptime(records[staff_id]["break_in"], "%H:%M:%S")
                    break_out_time = datetime.strptime(records[staff_id]["break_out"], "%H:%M:%S")
                    total_break_minutes = round((break_out_time - break_in_time).seconds / 60.0, 2)

                    break_log[staff_id] = {
                        "break_in": records[staff_id]["break_in"],
                        "break_out": records[staff_id]["break_out"],
                        "total_break": total_break_minutes,
                        "date": current_date  # Include the date in the break log entry
                    }

                log_db["break_log"] = break_log

            return redirect(url_for("break_page"))

        # Get user-specific break record
        user_break_record = records.get(staff_id, {"break_in": None, "break_out": None, "date": current_date})

    return render_template("break.html",
                           position=position,
                           invalid_time=invalid_time,
                           user_break_record=user_break_record)


# Register the custom datetime filter
@app.template_filter('datetime')
def datetime_filter(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, str):
        try:
            return datetime.strftime(value, format)
        except ValueError:
            return value  # Return the original value if it can't be parsed
    return value

# Break log route
@app.route("/break_log", methods=["GET", "POST"])
def break_log():
    if 'staff_id' not in session:
        flash('Please log in to access the break logs.', 'warning')
        return redirect(url_for('login'))

    staff_id = session['staff_id']
    position = session.get('position')

    # Fetch break log data from shelve
    with sh.open("break_log.db", writeback=True) as log_db:
        break_data = log_db.get("break_log", {})

    filtered_logs = break_data.copy()

    # Filter logs by selected date range
    if request.method == "POST":
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        if start_date and end_date:
            filtered_logs = {
                sid: details for sid, details in break_data.items()
                if start_date <= details.get("date", "") <= end_date
            }

    # Staff can only view their own logs; Managers can view all logs
    if position != 'manager':
        filtered_logs = {staff_id: filtered_logs.get(staff_id, {})}

    return render_template(
        "break_log.html",
        break_data=filtered_logs,
        position=position,
        start_date=request.form.get("start_date", ""),
        end_date=request.form.get("end_date", "")
    )

# Replace JSON with shelve for staff data
STAFF_FILE = "staff_data.db"

WORK_HOURS_DB = "work_hours.db"  # Database for logging working hours
STAFF_DB = "staff.db"  # Database for authentication

def get_staff_db():
    db = sh.open(STAFF_DB, writeback=True)
    if 'staff' not in db:
        db['staff'] = {}  # Store staff credentials
    return db


def get_work_hours_db():
    db = sh.open(WORK_HOURS_DB, writeback=True)
    if 'work_hours' not in db:
        db['work_hours'] = {}  # Store work hours
    return db

def initialize_file():
    # This function is now just to ensure that the staff file exists
    if not os.path.exists(STAFF_FILE):
        with sh.open(STAFF_FILE) as staff_db:
            staff_db["staff_data"] = {}  # Initialize with an empty dictionary

initialize_file()

@app.template_filter('to_datetime')
def to_datetime(value, format='%Y-%m-%d'):
    try:
        return datetime.strptime(value, format)
    except ValueError:
        return value  # If there's an error, return the original value instead of crashing

# Simulating database access
def get_work_hours_db():
    # This function is assumed to return a dictionary or shelve-based DB.
    # In actual implementation, replace this with code to access your database.
    import shelve
    db = shelve.open("work_hours_db", writeback=True)
    return db

# Create a custom Jinja filter for date formatting
@app.route('/log_working_hours', methods=['GET', 'POST'])
def log_working_hours():
    if 'staff_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    staff_id = session['staff_id']
    db = get_work_hours_db()

    if request.method == 'POST':
        try:
            start_date = request.form['start_date']
            end_date = request.form['end_date']
        except KeyError:
            flash("Missing form fields. Please fill in all fields.", "danger")
            return redirect(url_for('log_working_hours'))

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Please use the correct format.", "danger")
            return redirect(url_for('log_working_hours'))

        work_hours = {}
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            check_in = request.form.get(f'check_in_{day}')
            check_out = request.form.get(f'check_out_{day}')
            not_working = request.form.get(f'not_working_{day}')

            work_hours[day] = {
                'check_in': check_in if not not_working else None,
                'check_out': check_out if not not_working else None,
                'status': 'Pending' if check_in and check_out else 'Not Working'
            }

        db['work_hours'][staff_id] = {
            'start_date': start_date.strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'weekly_hours': work_hours
        }
        db.close()
        flash("Work hours logged successfully!", "success")
        return redirect(url_for('view_working_hours'))  # Redirect to the view_working_hours route

    start_date = ""
    end_date = ""
    return render_template('log_working_hours.html', start_date=start_date, end_date=end_date)


# View working hours (both staff and manager)
@app.route('/view_working_hours')
def view_working_hours():
    if 'staff_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    db = get_work_hours_db()
    staff_data = db.get('work_hours', {})
    db.close()

    return render_template('view_working_hours.html', staff_data=staff_data)

# Delete working hours (manager only)
@app.route('/delete_working_hours', methods=['POST'])
def delete_working_hours():
    if 'staff_id' not in session or session.get('position') != 'manager':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = json.loads(request.data)
    staff_id, day = data['staff_id'], data['day']

    db = get_work_hours_db()
    if staff_id in db['work_hours']:
        del db['work_hours'][staff_id]['weekly_hours'][day]
        db.close()
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Work hours not found'}), 404

# Edit working hours (manager only)
@app.route('/edit_working_hours', methods=['POST'])
def edit_working_hours():
    if 'staff_id' not in session or session.get('position') != 'manager':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = json.loads(request.data)
    staff_id, day = data['staff_id'], data['day']
    check_in, check_out = data['check_in'], data['check_out']

    db = get_work_hours_db()
    if staff_id in db['work_hours']:
        db['work_hours'][staff_id]['weekly_hours'][day] = {
            'check_in': check_in,
            'check_out': check_out,
            'status': 'Edited by Manager'
        }
        db.close()
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Work hours not found'}), 404

# Accept working hours (manager only)
@app.route('/accept_working_hours', methods=['POST'])
def accept_working_hours():
    if 'staff_id' not in session or session.get('position') != 'manager':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = json.loads(request.data)
    staff_id, day = data['staff_id'], data['day']

    db = get_work_hours_db()
    if staff_id in db['work_hours']:
        db['work_hours'][staff_id]['weekly_hours'][day]['status'] = 'Accepted'
        db.close()
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Work hours not found'}), 404

@app.route("/progress_report")
def progress_report():
    # Make sure to pass the data as lists
    return render_template("progress_report.html",
                           monthly_sales=monthly_sales,
                           individual_sales=individual_sales)

@app.route("/export_excel")
def export_excel():
    import pandas as pd
    from io import BytesIO
    from flask import send_file

    data = []
    for month in monthly_sales:
        total_sales = month["Total Sales"]
        revenue = month["Revenue"]
        for item in individual_sales.get(month["Month"], []):
            data.append({
                "Month": month["Month"],
                "Item Name": item["Item Name"],
                "Units Sold": item["Units Sold"],
                "Revenue": item["Revenue"],
                "Total Sales": total_sales,
                "Monthly Revenue": revenue
            })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sales Data")
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="sales_data.xlsx")

# Logout route
@app.route("/logout")
def logout():
    session.pop("staff_id", None)
    session.pop("position", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

@app.route('/normalize_keys')
def normalize_keys():
    db = sh.open('mc.db', 'w')
    mc_dict = db.get('mc', {})
    updated_mc_dict = {str(k): v for k, v in mc_dict.items()}  # Normalize keys to strings
    db['mc'] = updated_mc_dict
    db.close()
    return "Keys in mc.db have been normalized to strings."

if __name__=="__main__":
    app.run(debug=True)