"""
WSGI config for che_vio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "che_vio.settings")

application = get_wsgi_application()


from apscheduler.schedulers.background import BackgroundScheduler
from vio_sch.views import query_vio_auto, backup_log
from vio_sch.task import reset_status, delete_vehicle_over_dead_date
from vio_sch.task_query import main
from vio_sch.views_sz import query_vio_auto_sz, backup_vio, reset_vehicle
from vio_sch.utils_avis import delete_vehicle as delete_vehicle_avis

# from vio_sch.special import get_tj_vio


# 定时任务
scheduler = BackgroundScheduler()

# 每天02:00开始, 备份并清空违章表和日志表
# scheduler.add_job(backup_log, 'cron', hour=2, minute=5, second=0)

# # 每天21:00, 重置车辆违章查询状态status为0
# # scheduler.add_job(reset_status, 'cron', hour=21, minute=0, second=0)
#
# # 每天02:10, 重置车辆违章查询状态status为0
# scheduler.add_job(reset_status, 'cron', hour=2, minute=8, second=0)
#
# # 每天03:00, 开始查询违章数据
# scheduler.add_job(query_vio_auto, 'cron', hour=3, minute=0, second=0)
#
# # 每天10:00, 再查一遍
# scheduler.add_job(query_vio_auto, 'cron', hour=10, minute=23, second=0)
#
# # 每天15:00, 再查一遍
# scheduler.add_job(query_vio_auto, 'cron', hour=15, minute=0, second=0)
#
# # 每天18:00, 爬取重庆高速违章
# scheduler.add_job(main, 'cron', hour=18, minute=0, second=0)
#
# # 每周日、周三2:30开启自动任务
# scheduler.add_job(query_vio_auto_sz, 'cron', day_of_week='wed', hour=2, minute=30, second=0)
# scheduler.add_job(query_vio_auto_sz, 'cron', day_of_week='sun', hour=2, minute=30, second=0)
#
# # 每周日、周三12:30开启自动任务
# scheduler.add_job(query_vio_auto_sz, 'cron', day_of_week='wed', hour=12, minute=30, second=0)
# scheduler.add_job(query_vio_auto_sz, 'cron', day_of_week='sun', hour=12, minute=30, second=0)
#
# # 每周日、周三19:30开启自动任务
# scheduler.add_job(query_vio_auto_sz, 'cron', day_of_week='wed', hour=19, minute=30, second=0)
# scheduler.add_job(query_vio_auto_sz, 'cron', day_of_week='sun', hour=19, minute=30, second=0)
#
# # 每天1:00 删除库中超过30天未查询的车辆
# scheduler.add_job(delete_vehicle_avis, 'cron', hour=1, minute=0, second=0)
# scheduler.add_job(main, 'cron', hour=14, minute=43, second=30)

scheduler.start()
