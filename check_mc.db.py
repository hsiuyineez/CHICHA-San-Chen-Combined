import shelve

# Delete all records in mc.db


# Delete all records in leave.db
with shelve.open("leave.db", writeback=True) as db:
    db["leave"] = {}  # Reset leave_dict

print("mc_dict and leave_dict have been cleared.")
