"""
    avis 对象：车辆对象、违章对象
"""
import time


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
        self.msg = '数据源异常'

    # 查询违章
    def get_violations(self):
        # 先从本地数据库查询违章
        self.get_violations_from_local_db()

        # 如违章库中没有被查询车辆信息，则从其它api查询
        if self.status:
            self.get_api_info()
            self.get_violations_from_api()

            if self.status != 41:
                self.standardize_vio_data_from_api()

            # 如果查询结果状态为0，保存车辆信息
            if not self.status:
                self.save_vehicle()     # 保存车辆数据
            else:
                self.create_standard_error_data()

            # 如果查询成功插入数据到缓存库
            if not self.status:
                self.save_violations_into_local_db()

        # 保存日志
        self.save_log(False)

        return self.standard_vio_data

    # 自动缓存违章数据
    def auto_query_violations(self):
        # 从接口查询违章数据
        self.get_api_info()

        # print(self.api_id)
        self.get_violations_from_api()
        # print(self.origin_vio_data)
        if self.status != 41:
            self.standardize_vio_data_from_api()

        # 如果查询成功更新本地违章数据表
        if not self.status:
            self.update_violations_in_local_db()
        else:
            self.create_standard_error_data()

        # 保存日志
        self.save_log(True)

        return self.standard_vio_data

    # 从本地查询违章数据
    def get_violations_from_local_db(self):
        vio_info_list = VioInfoAvis.objects.filter(vehicle_number=self.vehicle_number)

        if vio_info_list:
            self.status = 0
            self.api_id = 99
            self.standardize_vio_data_from_local_db(vio_info_list)
        else:
            return

    # 从外部api查询违章
    def get_violations_from_api(self):
        # print('start query user api %d' % self.api_id)
        if self.api_id == 100:
            self.status = 41
            self.msg = '该城市不支持查询'

        elif self.api_id == 6:
            vehicle_type = str(self.vehicle_type)
            vehicle_type = '0' + vehicle_type if len(vehicle_type) < 2 else vehicle_type
            # print(self.vehicle_number, vehicle_type, self.vehicle_code, self.engine_code)
            self.origin_vio_data = get_vio_from_shaoshuai(self.vehicle_number, vehicle_type, self.vehicle_code,
                                                          self.engine_code)
        elif self.api_id == 7:
            self.origin_vio_data = get_vio_from_doyun(self.vehicle_number, self.vehicle_type, self.vehicle_code,
                                                      self.engine_code, '')
        elif self.api_id == 8:
            self.origin_vio_data = get_vio_from_cwb(self.vehicle_number, self.vehicle_type, self.vehicle_code,
                                                    self.engine_code)
        # print(self.origin_vio_data)

    # 确定查询api
    def get_api_info(self):
        # 获得车牌首字
        vehicle_loc = self.vehicle_number[0] if len(self.vehicle_number) > 0 else None
        # print('车牌所在地：%s' % vehicle_loc)
        # 根据车牌首字查询车辆所在地编码
        if vehicle_loc:
            loc_info_list = LocInfo.objects.filter(plate_name=vehicle_loc)
        else:
            self.status = 32    # 车牌或车辆类型错误
            return

        # 根据user_id和车牌所在地编码查询api_id
        if loc_info_list:
            loc_info = loc_info_list[0]
            api_id_list = LocUrlRelation.objects.filter(user_id=self.user_id, location_id=loc_info.loc_id)
        else:
            self.status = 32
            return

        if api_id_list:
            self.api_id = api_id_list[0].url_id
        else:
            self.status = 32
            return

    # 本地查询结果标准化
    def standardize_vio_data_from_local_db(self, vio_info_list):
        vio_list = []
        for vio_info in vio_info_list:
            if vio_info.available:
                vio_dic = {'vio_time': vio_info.vio_time,
                           'vio_position': vio_info.vio_position,
                           'vio_activity': vio_info.vio_activity,
                           'vio_point': str(vio_info.vio_point),
                           'vio_money': str(vio_info.vio_money),
                           'vio_code': str(vio_info.vio_code),
                           'vio_loc': vio_info.vio_loc,
                           'deal_status': str(vio_info.deal_status),
                           'pay_status': str(vio_info.pay_status),
                           }

                vio_list.append(vio_dic)
            else:
                continue

        self.standard_vio_data = {'status': self.status, 'vehicleNumber': self.vehicle_number, 'data': vio_list}

    # api查询结果标准化
    def standardize_vio_data_from_api(self):

        if self.api_id == 6:
            self.standard_vio_data = vio_dic_for_shaoshuai(self.vehicle_number, self.origin_vio_data)
        elif self.api_id == 7:
            self.standard_vio_data = vio_dic_for_ddyc(self.vehicle_number, self.origin_vio_data)
        elif self.api_id == 8:
            self.standard_vio_data = vio_dic_for_cwb(self.vehicle_number, self.origin_vio_data)

        # print(self.status)
        # print()
        self.status = self.standard_vio_data.get('status')
        self.msg = self.standard_vio_data.get('msg')

    # 构造违章返回数据
    def create_standard_error_data(self):
        self.standard_vio_data = {'status': self.status, 'msg': self.msg}

    # 保存查询日志
    def save_log(self, is_cache):
        save_log_avis(self.vehicle_number, self.vehicle_type, self.vehicle_code, self.engine_code, self.origin_vio_data,
                      self.standard_vio_data, self.user_id, self.api_id, self.user_ip, '', is_cache)

    # 保存车辆信息
    def save_vehicle(self):
        # 如果api查询成功，保存车辆信息
        query_status = self.standard_vio_data.get('status')

        if int(query_status) == 0:
            save_vehicle_avis(self.vehicle_number, self.vehicle_type, self.vehicle_code, self.engine_code, self.user_id)
        else:
            return

    # 保存违章数据
    def save_violations_into_local_db(self):
        vio_dic_list = self.standard_vio_data.get('data', None)

        # 如果该车没有违章
        if vio_dic_list is None:
            return
        elif len(vio_dic_list) == 0:
            vio_info = VioInfoAvis()
            vio_info.vehicle_number = self.vehicle_number
            vio_info.vehicle_type = self.vehicle_type
            vio_info.vio_code = '999999'  # 专用代码表示无违章

            vio_info.save()
        else:
            for vio_dic in vio_dic_list:
                self.insert_new_violation(vio_dic, False)

    # 用api违章数据更新本地违章数据
    def update_violations_in_local_db(self):
        vio_info_local_list = VioInfoAvis.objects.filter(vehicle_number=self.vehicle_number)
        vio_info_api_list = self.standard_vio_data.get('data', None)

        # 更新本地违章表中的数据
        for vio_info_local in vio_info_local_list:
            # 判断api查询的违章中是否有与本地数据一致的违章
            is_vio_in_api = False
            for vio_dic in vio_info_api_list:
                # 时间取值到分钟
                vio_time_local = (str(vio_info_local.vio_time))[: -3]
                vio_time_api = (vio_dic.get('time', ''))[: -3]

                # 取违法代码前4位
                vio_code_local = vio_info_local.vio_code[0: 4] if len(vio_info_local.vio_code) > 4 \
                    else vio_info_local.vio_code
                vio_code_api = vio_dic.get('code')[0: 4] if len(vio_dic.get('code', '')) > 4 \
                    else vio_dic.get('code', '')

                # 如果api中查出的数据与表中现有数据一致
                if vio_time_local == vio_time_api and vio_info_local.vio_position == vio_dic.get('position') \
                        and vio_code_local == vio_code_api:
                    is_vio_in_api = True
                    # 中断本次循环
                    break

            # 如果api中查询的违章数据与本地数据一直，则本地数据累计值+1，如果累计值为15，则数据变为可用
            if is_vio_in_api:
                # 更新违法数据
                vio_info_local.accumulation += 1 if vio_info_local.accumulation < 1 else 1
                vio_info_local.available = True if vio_info_local.accumulation >= 1 else False
            else:
                # 数据不一致，本地数据累计值-1，如果累计值为0则数据变为不可用
                vio_info_local.accumulation -= 1 if vio_info_local.accumulation > 0 else 0
                vio_info_local.available = False if vio_info_local.accumulation <= 0 else True

        # 将新获取的违章数据插入本地违章数据表
        for vio_dic in vio_info_api_list:
            is_vio_in_local_db = False
            for vio_info_local in vio_info_local_list:
                if vio_info_local.vehicle_number == vio_info_local.vio_time == vio_dic.get('time') \
                        and vio_info_local.vio_position == vio_dic.get('position') \
                        and vio_info_local.vio_activity == vio_dic.get('activity'):
                    is_vio_in_local_db = True
                    break

            if not is_vio_in_local_db:
                self.insert_new_violation(vio_dic, False)

    # 加入新的违章数据
    def insert_new_violation(self, vio_dic, is_vehicle_exists):
        vio_info = VioInfoAvis()
        vio_info.vehicle_number = self.vehicle_number
        vio_info.vehicle_type = self.vehicle_type
        vio_info.vio_time = vio_dic.get('time')
        vio_info.vio_position = vio_dic.get('position')
        vio_info.vio_activity = vio_dic.get('activity')
        vio_info.vio_point = vio_dic.get('point')
        vio_info.vio_money = vio_dic.get('money')
        vio_info.vio_code = vio_dic.get('code')
        vio_info.vio_loc = vio_dic.get('location')
        vio_info.deal_status = vio_dic.get('deal')
        vio_info.pay_status = vio_dic.get('pay')
        vio_info.update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        # 如果该车是第一次查询违章，则违章直接可用
        if not is_vehicle_exists:
            vio_info.available = True
            vio_info.accumulation = 1
        else:
            pass

        vio_info.save()







