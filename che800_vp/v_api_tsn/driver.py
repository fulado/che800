class Driver(object):

    def __init__(self, driver_name, file_id):
        self.driver_name = driver_name
        self.file_id = file_id
        self.change_date = None
        self.clear_date = None
        self.vehicle_type = None
        self.points = None
        self.license_status = None
        self.license_info = None

        self.is_exist = False

    def get_driver_info(self, mongo_db):
        driver_info = mongo_db.DriverUp.find_one({'xm': self.driver_name, 'dabh': self.file_id})

        if not driver_info:
            self.license_info = {'status': 20, 'message': '驾驶人信息不正确'}
        else:
            self.is_exist = True
            self.change_date = driver_info.get('yxqz')
            self.clear_date = driver_info.get('qfrq')
            self.vehicle_type = driver_info.get('zjcx')
            self.points = driver_info.get('ljjf')
            self.license_status = driver_info.get('zt')

    def create_driver_info(self):
        self.license_info = {
            'xm': self.driver_name,
            'dabh': self.file_id,
            'yxqz': self.change_date,
            'qfrq': self.clear_date,
            'zjcx': self.vehicle_type,
            'ljjf': self.points,
            'zt': self.license_status,
        }
