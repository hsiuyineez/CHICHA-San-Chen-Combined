import shelve

# Open the database and clear it
with shelve.open('staff_vouchers.db', writeback=True) as db:
    db.clear()  # Completely resets the database
    print("Database reset successful!")

# Verify it's empty
with shelve.open('staff_vouchers.db') as db:
    print("Current database contents:", dict(db))  # Should print {}
