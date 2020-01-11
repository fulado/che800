import time

from .models import VehicleInfo, VioInfoAvis, VioInfo
from django.db import connection


def save_vehicle(v_number, v_type, v_code, e_code, user_id):
    try:
        vehicle_bakup = VehicleInfo.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)

        # 如果车辆已经存在
        if vehicle_bakup.exists():

            # 判断是否需要更新车辆信息
            if not vehicle_bakup.filter(vehicle_code=v_code).filter(engine_code=e_code).exists():
                vehicle_bakup.update(vehicle_code=v_code, engine_code=e_code,
                                     update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            else:
                vehicle_bakup.update(update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        # 如果不存在, 创建新的车辆信息, 并保存
        else:

            vehicle = VehicleInfo()
            vehicle.vehicle_number = v_number
            vehicle.vehicle_type = v_type
            vehicle.vehicle_code = v_code
            vehicle.engine_code = e_code
            vehicle.user_id = user_id
            vehicle.update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            vehicle.save()
    except Exception as e:
        print(e)


# 定时任务，超过30天未查询车辆，删除该车辆信息
def delete_vehicle():
    vehicle_list = VehicleInfo.objects.all()

    for vehicle in vehicle_list:

        try:
            timestamp_update_time = int(time.mktime(time.strptime(vehicle.update_time, '%Y-%m-%d %H:%M:%S')))

            dif_time = int(time.time()) - timestamp_update_time

            if dif_time >= 60 * 60 * 24 * 30:
                vehicle.delete()
        except Exception as e:
            print(e)


# 定时任务，把安吉的违章数据插入到违章缓存表中
def insert_avis_vio_data_into_loc_db():
    try:
        connection.connection.ping()
    except:
        connection.close()

    avis_vio_list = VioInfoAvis.objects.all()

    for avis_vio_info in avis_vio_list:
        vio_info = VioInfo()

        vio_info.vehicle_number = avis_vio_info.vehicle_number
        vio_info.vehicle_type = '02'
        vio_info.vio_code = avis_vio_info.vio_code

        if vio_info.vio_code != '999999':
            vio_info.vio_time = avis_vio_info.vio_time
            vio_info.vio_position = avis_vio_info.vio_position
            vio_info.vio_activity = avis_vio_info.vio_activity
            vio_info.vio_point = avis_vio_info.vio_point
            vio_info.vio_money = avis_vio_info.vio_money
            vio_info.deal_status = avis_vio_info.deal_status
            vio_info.pay_status = avis_vio_info.pay_status
        else:
            pass

        vio_info.save()





























