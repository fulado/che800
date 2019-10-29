from .models import VehicleInfo
from django.db import connection


# 定时任务, 重置车辆违章查询状态status为0
def reset_status():
    # 判断连接是否可用, 如不可用关闭连接
    try:
        connection.connection.ping()
    except:
        connection.close()
    finally:
        VehicleInfo.objects.all().update(status=0, spider_status=False)



