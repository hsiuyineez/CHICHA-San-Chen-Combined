# leave.py
class leave:
    count_id = 0  # Class variable for unique ID generation

    def __init__(self, staff_id, starting_date, end_date, reason):
        leave.count_id += 1
        self.__leave_id = leave.count_id  # Assign a unique leave ID
        self.__staff_id = staff_id
        self.__starting_date = starting_date
        self.__end_date = end_date
        self.__reason = reason

    # Getters
    def get_leave_id(self):
        return self.__leave_id

    def get_staff_id(self):
        return self.__staff_id

    def get_starting_date(self):
        return self.__starting_date

    def get_end_date(self):
        return self.__end_date

    def get_reason(self):
        return self.__reason

    # Setters
    def set_staff_id(self, staff_id):
        self.__staff_id = staff_id

    def set_starting_date(self, starting_date):
        self.__starting_date = starting_date

    def set_end_date(self, end_date):
        self.__end_date = end_date

    def set_reason(self, reason):
        self.__reason = reason
