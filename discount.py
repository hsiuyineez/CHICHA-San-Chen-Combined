class Voucher:
    def __init__(self, code, discount, description, expiry_date=None):
        self.code = code
        self.discount = discount  # Discount percentage (e.g., 90 for 90%)
        self.description = description
        self.expiry_date = expiry_date

    def is_valid(self):
        if self.expiry_date:
            from datetime import datetime
            return datetime.now() <= self.expiry_date
        return True  # No expiry date means always valid