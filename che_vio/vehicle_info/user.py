"""
用户类
"""


import time
import hashlib

from .models import UserInfo


class User(object):
    """
    User class
    """
    def __init__(self, username, timestamp, sign):
        self.username = username
        self.timestamp = timestamp
        self.sign = sign

    # login check
    def check_user(self):

        try:
            user_timestamp = int(self.timestamp)
        except ValueError:
            return 15

        if abs(user_timestamp - int(time.time())) > 60 * 5:
            return 16

        try:
            user_info = UserInfo.objects.get(username=self.username)
        except Exception as e:
            print(e)
            return 11

        password = user_info.password

        user_sign = hashlib.sha1(())












