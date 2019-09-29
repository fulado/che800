"""
自动任务
"""


from .models import VehicleInfo, VioInfo


# system initialized
def system_init():
    print('system init start')
    vio_info = VioInfo.objects.all()
    vio_info.delete()

    vehicle_list = VehicleInfo.objects.all().exclude(status__in=[-2, -4])
    for vehicle_info in vehicle_list:
        vehicle_info.status = -1
        vehicle_info.save()

    print('system init end')
