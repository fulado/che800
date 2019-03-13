"""
Vehicle class, used to save vehicle info
"""


class Vehicle(object):
    """
    Vehicle class
    """
    def __init__(self, plat_number, plate_type, engine_code):
        """
        :param plat_number: 车牌号
        :param engine_code:  发动机号
        :param request_ip: 请求ip
        :param request_time: 请求时间
        """
        self.plat_number = plat_number
        self.plate_type = plate_type
        self.engine_code = engine_code
        self.request_ip = request_ip
        self.request_time = request_time
        self.response_time = ''
        self.vin = ''
        self.zts = ''
        self.valid_date = ''
        self.status = 0    # 车辆查询状态码
        self.punishes = []

    def check_vehicle_info(self, db):
        """
        :param db: 数据库连接
        :return: True - 车辆信息正确, False - 车辆信息错误
        """
        if len(self.plat_number) < 7:
            self.status = 5
            return
        # If the vehicle does not register in local, do not check engine code
        elif self.plat_number[0] != '津':
            self.set_vehicle_info(self.engine_code)
            return
        else:
            hphm = self.plat_number[1:]

        try:
            # Query the vehicle form database by hphm and hpzl
            result = db.VehicleUp.find_one({'hphm': hphm, 'hpzl': self.plate_type})
        except Exception as e:
            print(e)
            self.status = 99  # 其它错误
            return

        # Get the engine code
        if result:
            fdjh = result.get('fdjh', '000000')
        else:
            self.status = 5
            return

        # Get the last 6 number of the engine code
        # If the length of the engine code is less then 6, put 0 at the last
        len_engine_code = len(fdjh)
        if len_engine_code < 6:
            for i in range(6 - len(fdjh)):
                fdjh += '0'
        else:
            fdjh = fdjh[-6:]

        # Compare engine codes from user and database
        # If engine codes are same, set other information of the vehicle
        if self.engine_code == fdjh:
            self.set_vehicle_info(
                result.get('fdjh', ''),
                result.get('clsbdh', ''),
                result.get('zt', ''),
                result.get('yxqz', '')
            )
        else:
            self.status = 6

    def add_activity_to_violation(self, db):
        """
        Get violations of the vehicle
        :param db: Mongo db object
        :return:
        """
        try:
            # 根据违法代码构造违法数据列表
            for vio in self.punishes:
                print(vio)
                vio_activity = db.v_ViolationCodeDic.find_one({'dm': vio.get('code', '')})

                vio['activity'] = vio_activity.get('wfxw', '')
                vio['point'] = vio_activity.get('jfz', '')
                vio['money'] = vio_activity.get('fke1', '')

        except Exception as e:
            self.status = 99
            print(e)

    def set_vehicle_info(self, engine_code='', vin='', zts='', valid_date=''):
        """
        Set vehicle information
        :return:
        """
        self.engine_code = engine_code
        self.vin = vin
        self.zts = zts
        self.valid_date = valid_date

    def get_violation_without_activity(self, db):
        """
        Get violations without activity information
        :param db:
        :return:
        """
        try:
            vio_list = []

            cursor = db.SurveilUp.find({'hphm': self.plat_number, 'hpzl': self.plate_type})

            # 构造返回数据
            for item in cursor:
                # 已交款或这无需交款数据不返回
                if item.get('jkbj', '') in ['1', '9']:
                    continue

                vio_info = {
                    'code': item.get('wfxw', ''),
                    'time': item.get('wfsj', ''),
                    'position': item.get('wfdz', ''),
                    'location': item.get('cjjgmc', ''),
                    'deal': item.get('clbj', ''),
                    'pay': item.get('jkbj', '')
                }
                vio_list.append(vio_info)

            self.status = 0
            self.punishes = vio_list
        except Exception as e:
            self.status = 99
            print(e)
        finally:
            cursor.close()
