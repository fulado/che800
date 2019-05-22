# 违章类
import time
import hashlib
import urllib
import json

from .models import VioInfo


class Violation(object):

    def __init__(self, number, v_type, engine, vin):
        self.number = number
        self.type = v_type
        self.engine = engine
        self.vin = vin
        self.username = 'test'
        self.password = 'test'
        self.timestamp = int(time.time())
        self.sign = ''
        self.response_data = ''
        self.status = 99

    def create_sign(self):
        password = hashlib.sha1(self.password.encode('utf_8')).hexdigest().upper()
        sign = '%s%d%s' % (self.username, self.timestamp, password)
        self.sign = hashlib.sha1(sign.encode('utf_8')).hexdigest().upper()

    def get_violations(self):
        url = 'http://58.87.123.72/violation'
        request_data = {'username': self.username,
                        'timestamp': self.timestamp,
                        'sign': self.sign,
                        'vehicleNumber': self.number,
                        'engineCode': self.engine,
                        'vehicleType': self.type,
                        'vehicleCode': self.vin
                        }

        request_data = urllib.parse.urlencode(request_data)
        request = urllib.request.Request(url, data=request_data.encode())
        response_data = urllib.request.urlopen(request)

        self.response_data = json.loads(response_data.read().decode())

    def save_violations(self):

        self.status = self.response_data.get('status', 99)