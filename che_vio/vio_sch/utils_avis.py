import time

from .models import VehicleInfo


def save_vehicle(v_number, v_type, v_code, e_code, user_id):
    try:
        vehicle_bakup = VehicleInfo.objects.filter(vehicle_number=v_number).filter(vehicle_type=v_type)

        # 如果车辆已经存在
        if vehicle_bakup.exists():

            # 判断是否需要更新车辆信息
            if not vehicle_bakup.filter(vehicle_code=v_code).filter(engine_code=e_code).exists():
                vehicle_bakup.update(vehicle_code=v_code, engine_code=e_code,
                                     update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        # 如果不存在, 创建新的车辆信息, 并保存
        else:

            vehicle = VehicleInfo()
            vehicle.vehicle_number = v_number
            vehicle.vehicle_type = v_type
            vehicle.vehicle_code = v_code
            vehicle.engine_code = e_code
            vehicle.user_id = user_id

            vehicle.save()
    except Exception as e:
        print(e)
