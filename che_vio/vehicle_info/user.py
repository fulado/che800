"""
查询请求类
"""


import time
import hashlib

from .models import UserInfo


class QueryRequest(object):
    """
    QueryRequest class
    """
    def __init__(self, username, timestamp, sign):
        self.username = username
        self.timestamp = timestamp
        self.sign = sign
        self.status = 0
        self.msg = ''
        self.src_status = None
        self.src_msg = None

    # login check
    def check_user(self):

        try:
            user_timestamp = int(self.timestamp)
        except ValueError:
            self.status = 15
            self.msg = '时间戳格式错误'
            return

        if abs(user_timestamp - int(time.time())) > 60 * 5:
            self.status = 16
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


    # save_log
    def save_log(self):









