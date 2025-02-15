import shelve
class mc:
    count_id = 0  # Class variable for unique ID generation

    def __init__(self, staff_id,starting_date, end_date, proof):
        mc.count_id += 1
        self.__staff_id = staff_id # Auto-generate unique staff ID
        self.__starting_date = starting_date
        self.__end_date = end_date
        self.__proof = proof

    # Getters

    def get_staff_id(self):
        return self.__staff_id

    def get_starting_date(self):
        return self.__starting_date

    def get_end_date(self):
        return self.__end_date


    def get_proof(self):
        return self.__proof

    # Setters
    def set_staff_id(self,staff_id):
        self.__staff_id=staff_id

    def set_starting_date(self, starting_date):
        self.__starting_date = starting_date

    def set_end_date(self, end_date):
        self.__end_date = end_date

    def set_proof(self, proof):
        self.__proof = proof


def get_mc_records(staff_id):
    db = shelve.open('mc.db', 'r')  # Open the MC database in read mode
    mc_dict = db.get('mc', {})
    db.close()

    # Filter MC records for the given staff_id
    staff_mc_records = [record for record in mc_dict.values() if record.get_staff_id() == staff_id]

    # Return the first record or modify this to suit your needs
    return staff_mc_records[0] if staff_mc_records else None
