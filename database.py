import shelve

def save_to_shelve(filename, key, data):
    with shelve.open(filename) as db:
        db[key] = data

def load_from_shelve(filename, key):
    with shelve.open(filename) as db:
        return db.get(key, {})
