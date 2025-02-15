import shelve

# Create and populate the staff database
with shelve.open('staff.db', 'c') as db:
    staff_dict = {
        '12345': 'password123',
        '4567': 'mypassword456',
        '78901': 'secure789'
    }
    db['staff'] = staff_dict
    print("Staff database (staff.db) created successfully!")

# Print the staff database
with shelve.open('staff.db', 'r') as db:
    staff_dict = db.get('staff', {})
    for staff_id, password in staff_dict.items():
        print(f"Staff ID: {staff_id}, Password: {password}")
