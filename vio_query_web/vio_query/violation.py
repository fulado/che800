# 违章类
import time
import hashlib
import json
import urllib.request
import urllib.parse

from .models import VioInfo


class Violation(object):

    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.username = 'test'
        self.password = 'test'
        self.timestamp = int(time.time())
        self.sign = ''
        self.response_data = {'status': 99}

        self.create_sign()

    def create_sign(self):
        password = hashlib.sha1(self.password.encode('utf_8')).hexdigest().upper()
        sign = '%s%d%s' % (self.username, self.timestamp, password)
        self.sign = hashlib.sha1(sign.encode('utf_8')).hexdigest().upper()

    # 从接口查询违章
    def get_violations_from_api(self):
        url = 'http://58.87.123.72/violation'
        request_data = {'username': self.username,
                        'timestamp': self.timestamp,
                        'sign': self.sign,
                        'vehicleNumber': self.vehicle.number,
                        'engineCode': self.vehicle.engine,
                        'vehicleType': self.vehicle.type,
                        'vehicleCode': self.vehicle.vin
                        }

        request_data = urllib.parse.urlencode(request_data)
        request = urllib.request.Request(url, data=request_data.encode())
        response_data = urllib.request.urlopen(request)

        self.response_data = json.loads(response_data.read().decode())
        # print(self.response_data)

    # 保存违章信息
    def save_violations(self):
        # 保存查询结果状态码
        self.vehicle.status = int(self.response_data.get('status', 99))

        if self.vehicle.status == 41:
            self.vehicle.status = -4
            self.vehicle.save()
            return

        if self.vehicle.status in [32, 33, 34, 35, 36]:
            self.vehicle.status = -2
            self.vehicle.save()
            return

        if self.vehicle.status != 0:
            self.vehicle.status = -3
            self.vehicle.save()
            return

        # 解析查询结果
        vio_list = self.response_data.get('data', '')

        if vio_list:
            self.vehicle.status = len(vio_list)

            for vio in vio_list:
                vio_info = VioInfo()
                vio_info.number = self.vehicle.number
                vio_info.type = self.vehicle.type
                vio_info.time = vio.get('time', '')
                vio_info.position = vio.get('position', '')
                vio_info.activity = vio.get('activity', '')
                vio_info.point = vio.get('point', '')
                vio_info.money = vio.get('money', '')
                vio_info.code = vio.get('code', '')
                vio_info.loc = vio.get('loc', '')
                vio_info.deal_status = vio.get('deal', '')
                vio_info.pay_status = vio.get('pay', '')

                vio_info.save()
        else:
            self.vehicle.status = 0

        self.vehicle.save()
