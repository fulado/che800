"""
车辆类
"""


class Vehicle(object):
    """
    Vehicle class
    """

    def __init__(self, v_number, v_type, v_owner):
        self.v_number = v_number
        self.v_type = v_type
        self.v_owner = v_owner


    # get vehicle info
    def get_vehicle_info(self):
        