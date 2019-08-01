"""
车辆类
"""


from .models import VehicleInfo


class Vehicle(object):
    """
    Vehicle class
    """

    def __init__(self, v_number, v_type, v_owner, url):
        self.v_number = v_number
        self.v_type = v_type
        self.v_owner = v_owner
        self.status = None
        self.msg = None
        self.data = None
        self.url = url

    # get vehicle info
    def get_vehicle_info(self):
        url = 'http://39.98.255.209:3001/vehicle/checkName'

        self.status = 200
        self.msg = '查询成功'

    # save vehicle info
    def save_vehicle_info(self):
        vehicle_info = VehicleInfo()

        vehicle_info.hphm = self.data.get('hphm', '')
        vehicle_info.hpzl = self.data.get('hpzl', '')
        vehicle_info.syr = self.data.get('syr', '')
        vehicle_info.clpp1 = self.data.get('clpp1', '')
        vehicle_info.clxh = self.data.get('clxh', '')
        vehicle_info.clsbdh = self.data.get('clsbdh', '')
        vehicle_info.fdjh = self.data.get('fdjh', '')
        vehicle_info.cllx = self.data.get('cllx', '')
        vehicle_info.csys = self.data.get('csys', '')
        vehicle_info.syxz = self.data.get('syxz', '')
        vehicle_info.ccdjrq = self.data.get('ccdjrq', '')
        vehicle_info.yxqz = self.data.get('yxqz', '')
        vehicle_info.qzbfqz = self.data.get('qzbfqz', '')
        vehicle_info.zt = self.data.get('zt', '')
        vehicle_info.fdjxh = self.data.get('fdjxh', '')
        vehicle_info.rlzl = self.data.get('rlzl', '')
        vehicle_info.pl = self.data.get('pl', '')
        vehicle_info.gl = self.data.get('gl', '')
        vehicle_info.zs = self.data.get('zs', '')
        vehicle_info.zj = self.data.get('zj', '')
        vehicle_info.qlj = self.data.get('qlj', '')
        vehicle_info.hlj = self.data.get('hlj', '')
        vehicle_info.zzl = self.data.get('zzl', '')
        vehicle_info.zbzl = self.data.get('zbzl', '')
        vehicle_info.hdzzl = self.data.get('hdzzl', '')
        vehicle_info.hdzk = self.data.get('hdzk', '')
        vehicle_info.ccrq = self.data.get('ccrq', '')

        try:
            vehicle_info.save()
        except Exception as e:
            print(e)


















