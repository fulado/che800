"""
自动任务
"""


from .models import UserInfo, VehicleInfo, VioInfo


# system initialized
def system_init():
    vio_info = VioInfo.objects.all()
    vio_info.delete()

    vehicle_list = VehicleInfo.objects.all().exclude(status__in=[-2, -4])
    for vehicle_info in vehicle_list:
        vehicle_info.status = -1
        vehicle_info.save()

    user_list = UserInfo.object.all()
    for user_info in user_list:
        user_info.queried_number = 0
        user_info.save()
