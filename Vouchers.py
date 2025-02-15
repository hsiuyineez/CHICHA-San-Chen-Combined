import shelve
from datetime import datetime, timedelta

class Vouchers:
    def __init__(self, code, description, collection):
        self.code = code
        self.description = description
        self.collection = collection

    @staticmethod
    def load_vouchers():
        """ Load voucher templates from the database and convert dictionaries to Voucher instances if needed. """
        with shelve.open('vouchers.db') as db:
            raw_vouchers = db.get('vouchers', {})

            vouchers = {}
            for code, data in raw_vouchers.items():
                if isinstance(data, dict):  # Convert dictionary to Voucher instance
                    vouchers[code] = Vouchers(
                        data['code'],
                        data['description'],
                        data['collection']
                    )
                else:  # Already a Voucher instance
                    vouchers[code] = data

            return vouchers

    @staticmethod
    def save_vouchers(vouchers):
        """ Save voucher templates to the database. """
        with shelve.open('vouchers.db', writeback=True) as db:
            db['vouchers'] = vouchers

    @staticmethod
    def load_staff_vouchers(staff_id):
        """ Load staff-specific voucher collection history. """
        with shelve.open('staff_vouchers.db') as db:
            return db.get(staff_id, {})

    @staticmethod
    def save_staff_vouchers(staff_id, collected_vouchers):
        """ Save staff-specific voucher collection history. """
        with shelve.open('staff_vouchers.db', writeback=True) as db:
            db[staff_id] = collected_vouchers


# Initialize sample vouchers (Run only once)
def initialize_vouchers():
    with shelve.open('vouchers.db', writeback=True) as db:
        db['vouchers'] = {}  # Reset the database

    print("⚠️ Vouchers database reset! Now initializing new vouchers...")
    vouchers = Vouchers.load_vouchers()
    if any(isinstance(v, dict) for v in vouchers.values()):
        print("⚠️ Resetting vouchers.db due to incorrect format!")
        vouchers = {}  # Reset dictionary
    if not vouchers:
        sample_vouchers = [
            {"code": "M3MKS1E8", "description": "20% off on food", "collection": "Collection 1"},
            {"code": "J4BZX0G9", "description": "Free drink with any meal", "collection": "Collection 2"},
            {"code": "T7CSP2A4", "description": "10% off on total bill", "collection": "Collection 3"},
            {"code": "L8NDB3Q2", "description": "Buy 1 get 1 free", "collection": "Collection 4"},
            {"code": "Q9VLP5F6", "description": "15% off on selected items", "collection": "Collection 5"},
            {"code": "X7Y2LMK8", "description": "25% off on all drinks", "collection": "Collection 6"},
            {"code": "D3J9CWP4", "description": "50% off one dessert", "collection": "Collection 7"},
            {"code": "R8KZW2T5", "description": "Loyalty points double for a day", "collection": "Collection 8"},
            {"code": "P4NM7VJ6", "description": "1 free upsize on any drink", "collection": "Collection 9"},
            {"code": "Q6XJPT3L", "description": "Buy 2 get 1 free on snacks", "collection": "Collection 10"},
            {"code": "L9WDK2MJ", "description": "10% off for group orders (min. 3 people)",
             "collection": "Collection 11"},
            ]
        for data in sample_vouchers:
            vouchers[data['code']] = Vouchers(data['code'], data['description'], data['collection'])
        Vouchers.save_vouchers(vouchers)


def reset_staff_vouchers():
    """ Reset the staff_vouchers.db database by clearing all staff vouchers. """
    with shelve.open('staff_vouchers.db', writeback=True) as db:
        db.clear()  # This removes all stored staff voucher records.
    print("✅ Staff vouchers have been reset successfully!")
# Run initialization
initialize_vouchers()

