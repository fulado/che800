"""
特殊任务
"""


from .models import VehicleInfo
from .utils import get_vio_from_cwb, vio_dic_for_cwb, save_to_loc_db


def get_tj_vio():
    vehicle_list = VehicleInfo.objects.filter(user_id=19, vehicle_number__contains='津', status=0)

    for vehicle in vehicle_list:
        print('%s querying' % vehicle.vehicle_number)
        vehicle_type = '0%d' % vehicle.vehicle_type
        origin_data = get_vio_from_cwb(vehicle.vehicle_number, vehicle_type, vehicle.vehicle_code,
                                       vehicle.engine_code)
        vio_data = vio_dic_for_cwb(vehicle.vehicle_number, origin_data)

        # 如果查询成功
        if vio_data['status'] == 0:
            # 保存违章数据到本地数据库
            save_to_loc_db(vio_data, vehicle.vehicle_number, int(vehicle_type))
            vehicle.status = 1
        else:
            vehicle.status = vio_data['status']

        print('%s queried' % vehicle.vehicle_number)
        vehicle.save()
        print('%s saved' % vehicle.vehicle_number)

    print('ok')


if __name__ == '__main__':
    get_tj_vio()


