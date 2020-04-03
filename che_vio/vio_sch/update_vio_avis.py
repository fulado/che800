import sys
import os
import django


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(BASE_DIR)
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'che_vio.settings')
django.setup()


from vio_sch.models import VioInfoAvis, VioInfoAvisIn, VehicleInfoAvisIn


# 1. 比较avis原表中和in表中的违章, 如果原表中违章available为True, 且in表中有该条违章, 则用原表中的数据替代in表中的数据
# 2. 删除原表中的违章数据
# 3. 将in表中的违章数据全部写入原表
def compare_vio_data(vehicle_number):
    vio_list_avis = VioInfoAvis.objects.filter(vehicle_number=vehicle_number).exclude(available=False).\
        exclude(vio_code='999999')
    vio_list_in = VioInfoAvisIn.objects.filter(vehicle_number=vehicle_number).exclude(vio_code='999999')

    for vio_info_in in vio_list_in:

        vio_time_in = vio_info_in.vio_time
        vio_time_in = vio_time_in if len(vio_time_in) == 16 else vio_time_in[: -3]

        for vio_info_avis in vio_list_avis:
            vio_time_avis = vio_info_avis.vio_time
            vio_time_avis = vio_time_avis if len(vio_time_avis) == 16 else vio_time_avis[: -3]
            # print(vio_time_in, vio_time_avis)

            if vio_time_in == vio_time_avis:
                vio_info_in.vio_time = vio_info_avis.vio_time
                vio_info_in.vio_position = vio_info_avis.vio_position
                vio_info_in.vio_activity = vio_info_avis.vio_activity
                vio_info_in.vio_code = vio_info_avis.vio_code
                vio_info_in.save()

                break
            else:
                continue


def delete_vio_in_avis(vehicle_number):
    vio_list = VioInfoAvis.objects.filter(vehicle_number=vehicle_number)

    if vio_list:
        vio_list.delete()
    else:
        pass


def insert_vio_into_avis(vehicle_number):
    vio_list_in = VioInfoAvisIn.objects.filter(vehicle_number=vehicle_number)

    for vio_info_in in vio_list_in:
        vio_info_avis = VioInfoAvis()

        vio_info_avis.vehicle_number = vio_info_in.vehicle_number
        vio_info_avis.vehicle_type = vio_info_in.vehicle_type
        vio_info_avis.vio_time = vio_info_in.vio_time
        vio_info_avis.vio_position = vio_info_in.vio_position
        vio_info_avis.vio_activity = vio_info_in.vio_activity
        vio_info_avis.vio_point = vio_info_in.vio_point
        vio_info_avis.vio_money = vio_info_in.vio_money
        vio_info_avis.vio_code = vio_info_in.vio_code
        vio_info_avis.vio_loc = vio_info_in.vio_loc
        vio_info_avis.deal_status = vio_info_in.deal_status
        vio_info_avis.pay_status = vio_info_in.pay_status
        vio_info_avis.available = False if vio_info_in.vio_code == '999999' else True

        vio_info_avis.save()


def update_vio_avis():
    vehicle_list = VehicleInfoAvisIn.objects.all()

    for vehicle_info in vehicle_list:
        vehicle_number = vehicle_info.vehicle_number

        compare_vio_data(vehicle_number)
        delete_vio_in_avis(vehicle_number)
        insert_vio_into_avis(vehicle_number)

        print('%s 更新完成' % vehicle_number)

    print('全部更新完成')


def test():
    vehicle_number = '京Q73GR2'

    compare_vio_data(vehicle_number)
    delete_vio_in_avis(vehicle_number)
    insert_vio_into_avis(vehicle_number)

    print('%s 更新完成' % vehicle_number)


if __name__ == '__main__':
    # test()
    update_vio_avis()


















