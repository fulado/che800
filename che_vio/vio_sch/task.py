from .models import VehicleInfo
from django.db import connection

import datetime


# 定时任务, 重置车辆违章查询状态status为0
def reset_status():
    # 判断连接是否可用, 如不可用关闭连接
    try:
        connection.connection.ping()
    except:
        connection.close()
    finally:
        VehicleInfo.objects.all().update(status=0, spider_status=False)


# 定时任务，清楚10天未查询的车辆信息
def delete_vehicle_over_dead_date():
    dead_date = datetime.datetime.today() - datetime.timedelta(days=10)

    try:
        VehicleInfo.objects.filter(update_time__lt=dead_date).delete()
    except Exception as e:
        print(e)

