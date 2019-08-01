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
    def __init__(self, username, timestamp, sign, ip, url_id):
        self.username = username
        self.timestamp = timestamp
        self.sign = sign
        self.status = 0
        self.msg = ''
        self.src_status = None
        self.src_msg = None
        self.vehicle = None
        self.user_id = None
        self.ip = ip
        self.url_id = url_id

    # login check
    def check_user(self):

        try:
            user_timestamp = int(self.timestamp)
        except ValueError:
            self.status = 13
            self.msg = '时间戳格式错误'
            return

        if abs(user_timestamp - int(time.time())) > 60 * 5:
            self.status = 14
            self.msg = '时间戳超时'
            return

        try:
            user_info = UserInfo.objects.get(username=self.username)
        except Exception as e:
            print(e)
            self.status = 11
            self.msg = '用户不存在'
            return

        user_sign = hashlib.sha1((self.username + self.timestamp + user_info.password).encode()).hexdigest().upper()

        if self.sign != user_sign:
            self.status = 12
            self.msg = 'sign签名错误'
            return

        self.user_id = user_info.id

    # create log
    def create_log(self):
        self.src_status = self.vehicle.status
        self.src_msg = self.vehicle.msg

        if self.src_status == 200:
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
            self.status = 31
            self.msg = '查询失败'

    # save_log
    def save_log(self):
        log_info = LogInfo()

        log_info.user_id = self.user_id
        log_info.ip = self.ip
        log_info.query_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_info.vehicle_number = self.vehicle.v_number
        log_info.vehicle_type = self.vehicle.v_type
        log_info.vehicle_owner = self.vehicle.v_owner
        log_info.url_id = self.url_id
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
            query_result = {
                'status': self.status,
                'message': self.msg,
                'data': self.vehicle.data
            }
        else:
            query_result = {
                'status': self.status,
                'message': self.msg
            }

        return query_result







