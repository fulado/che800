"""
查询请求类
"""


import time
import hashlib

from .models import UserInfo, LogInfo


class User(object):
    """
    QueryRequest class
    """
    def __init__(self, username, timestamp, sign, ip, v_number, v_type, vin):
        self.username = username
        self.timestamp = timestamp
        self.sign = sign
        self.status = None
        self.msg = ''
        self.src_status = None
        self.src_msg = None
        self.vehicle = None
        self.user_info = None
        self.ip = ip
        self.v_number = v_number
        self.v_type = v_type
        self.vin = vin
        self.query_url = None
        self.query_result = None

    # login check
    def check_user(self):

        try:
            user_timestamp = int(self.timestamp)
        except ValueError:
            self.status = 13
            self.msg = '时间戳格式错误'
            return False

        if abs(user_timestamp - int(time.time())) > 60 * 5:
            self.status = 14
            self.msg = '时间戳超时'
            return False

        try:
            user_info = UserInfo.objects.get(username=self.username)
        except Exception as e:
            print(e)
            self.status = 11
            self.msg = '用户不存在'
            return False

        user_sign = hashlib.sha1((self.username + self.timestamp + user_info.password).encode()).hexdigest().upper()

        if self.sign != user_sign:
            self.status = 12
            self.msg = 'sign签名错误'
            return False

        self.user_info = user_info

        return True

    # get_url
    def get_url(self):
        try:
            int(self.v_type)
        except ValueError:
            self.status = 23
            self.msg = '车辆类型错误'
            return False

        if len(self.vin) != 4:
            self.status = 24
            self.msg = '车架号错误'
            return False

        permit_list = self.user_info.permit_province

        if self.v_number[0] not in permit_list:
            self.status = 31
            self.msg = '该地区车辆不支持查询'
            return False
        else:
            self.query_url = 'http://39.98.255.209:3001/vehicle/two'
            return True

    # save log and create query result
    def create_result(self):
        self.create_log()
        self.save_log()
        self.get_query_result()

    # create log
    def create_log(self):
        self.src_status = self.vehicle.status if self.vehicle else None
        self.src_msg = self.vehicle.msg if self.vehicle else None

        if self.src_status is None:
            return

        if self.src_status in (0, 200):
            self.status = 0
            self.msg = '查询成功'
        elif self.src_status > 400:
            self.status = 31
            self.msg = '查询失败'
        elif self.src_status == 201:
            self.status = 21
            self.msg = '车辆所有人不匹配'
        elif self.src_status == 223:
            self.status = 22
            self.msg = '车辆信息错误'
        elif self.src_status == 224:
            self.status = 41
            self.msg = '查询失败'

    # save_log
    def save_log(self):
        log_info = LogInfo()

        log_info.user_id = self.user_info.id if self.user_info else None
        log_info.ip = self.ip if self.ip else None
        log_info.query_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_info.vehicle_number = self.vehicle.v_number if self.vehicle else None
        log_info.vehicle_type = self.vehicle.v_type if self.vehicle else None
        log_info.vin = self.vehicle.vin if self.vehicle else None
        log_info.url_id = 1
        log_info.status = self.status
        log_info.msg = self.msg
        log_info.src_status = self.src_status
        log_info.src_msg = self.src_msg

        try:
            log_info.save()
        except Exception as e:
            print(e)

    # create_query_result
    def get_query_result(self):

        if self.status == 0:
            self.query_result = {
                'status': self.status,
                'message': self.msg,
                'data': self.vehicle.data
            }
        else:
            self.query_result = {
                'status': self.status,
                'message': self.msg
            }







