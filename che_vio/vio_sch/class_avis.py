"""
    avis 对象：车辆对象、违章对象
"""


from .models import VioInfoAvis, LocUrlRelation, LocInfo
from .utils import get_vio_from_doyun, get_vio_from_shaoshuai, get_vio_from_cwb
from .utils import vio_dic_for_ddyc, vio_dic_for_shaoshuai, vio_dic_for_cwb
from .utils import save_log as save_log_avis
from .utils_avis import save_vehicle as save_vehicle_avis


class VehicleAvis(object):
    """
    Vehicle class
    """
    def __init__(self, user_id, user_ip, vehicle_number, vehicle_type, vehicle_code, engine_code):
        self.user_id = user_id
        self.user_ip = user_ip
        self.vehicle_number = vehicle_number
        self.vehicle_type = vehicle_type
        self.vehicle_code = vehicle_code
        self.engine_code = engine_code
        self.status = 51    # 默认查询失败，数据源异常，0-查询成功
        self.api_id = None  # 6-上海接口，7-懂云，8-车务帮
        self.origin_vio_data = ''
        self.standard_vio_data = ''

    # 查询违章
    def get_violations(self):
        # 先从本地数据库查询违章
        self.get_violations_from_local_db()

        # 如违章库中没有被查询车辆信息，则从其它api查询
        if self.status:
            self.get_violations_from_api()
            self.standardize_vio_data_from_api()
            self.save_vehicle()     # 保存车辆数据

        # 如果查询结果状态不为0，构造返回的错误信息，通过api查询已经在函数中构造了错误信息
        if self.status:
            self.create_standard_error_data()

        # 保存日志
        self.save_log()

    # 从本地查询违章数据
    def get_violations_from_local_db(self):
        vio_info_list = VioInfoAvis.objects.filter(vehicle_number=self.vehicle_number).filter(available=True)

        if vio_info_list:
            self.status = 0
            self.standardize_vio_data_from_local_db(vio_info_list)
        else:
            pass

    # 从外部api查询违章
    def get_violations_from_api(self):
        if self.api_id == 100:
            self.status = 41
        elif self.api_id == 6:
            self.origin_vio_data = get_vio_from_shaoshuai(self.vehicle_number, self.vehicle_type, self.vehicle_code,
                                                          self.engine_code)
        elif self.api_id == 7:
            self.origin_vio_data = get_vio_from_doyun(self.vehicle_number, self.vehicle_type, self.vehicle_code,
                                                      self.engine_code, '')
        elif self.api_id == 8:
            self.origin_vio_data = get_vio_from_cwb(self.vehicle_number, self.vehicle_type, self.vehicle_code,
                                                    self.engine_code)

    # 确定查询api
    def get_api_info(self):
        # 获得车牌首字
        vehicle_loc = self.vehicle_number[0] if len(self.vehicle_number) > 0 else None

        # 根据车牌首字查询车辆所在地编码
        if vehicle_loc:
            loc_info_list = LocInfo.objects.filter(plate_name=vehicle_loc)
        else:
            self.status = 32    # 车牌或车辆类型错误
            return

        # 根据user_id和车牌所在地编码查询api_id
        if loc_info_list:
            loc_info = loc_info_list[0]
            api_id_list = LocUrlRelation.objects.filter(user_id=self.user_id, location_id=loc_info.id)
        else:
            self.status = 32
            return

        if api_id_list:
            self.api_id = api_id_list[0]
        else:
            self.status = 32
            return

    # 本地查询结果标准化
    def standardize_vio_data_from_local_db(self, vio_info_list):
        vio_list = []
        for vio_info in vio_info_list:
            vio_dic = {'vio_time': vio_info.vio_time,
                       'vio_position': vio_info.vio_position,
                       'vio_activity': vio_info.vio_activity,
                       'vio_point': vio_info.vio_point,
                       'vio_money': vio_info.vio_money,
                       'vio_code': vio_info.vio_code,
                       'vio_loc': vio_info.vio_loc,
                       'deal_status': vio_info.deal_status,
                       'pay_status': vio_info.pay_status,
                       }

            vio_list.append(vio_dic)

        self.standard_vio_data = {'status': self.status, 'vehicleNumber': self.vehicle_number, 'data': vio_list}

    # api查询结果标准化
    def standardize_vio_data_from_api(self):
        if self.api_id == 6:
            self.standard_vio_data = vio_dic_for_shaoshuai(self.vehicle_number, self.origin_vio_data)
        elif self.api_id == 7:
            self.standard_vio_data = vio_dic_for_ddyc(self.vehicle_number, self.origin_vio_data)
        elif self.api_id == 8:
            self.standard_vio_data = vio_dic_for_cwb(self.vehicle_number, self.origin_vio_data)

    # 构造违章返回数据
    def create_standard_error_data(self):
        self.standard_vio_data = {'status': self.status, 'vehicleNumber': self.vehicle_number}

    # 保存查询日志
    def save_log(self):
        save_log_avis(self.vehicle_number, self.vehicle_type, self.vehicle_code, self.engine_code, self.origin_vio_data,
                      self.standard_vio_data, self.user_id, self.api_id, self.user_ip)

    # 保存车辆信息
    def save_vehicle(self):
        # 如果api查询成功，保存车辆信息
        query_status = self.standard_vio_data.get('status')

        if int(query_status) == 0:
            save_vehicle_avis(self.vehicle_number, self.vehicle_type, self.vehicle_code, self.engine_code)
        else:
            return














