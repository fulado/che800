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
from vio_sch.task import reset_status
from vio_sch.task_query import main


# 定时任务
scheduler = BackgroundScheduler()

# # 每天02:00开始, 备份并清空违章表和日志表
# scheduler.add_job(backup_log, 'cron', hour=2, minute=0, second=0)
#
# # 每天21:00, 重置车辆违章查询状态status为0
# scheduler.add_job(reset_status, 'cron', hour=21, minute=0, second=0)
#
# # 每天02:10, 重置车辆违章查询状态status为0
# scheduler.add_job(reset_status, 'cron', hour=2, minute=30, second=0)
#
# # 每天03:00, 开始查询违章数据
# scheduler.add_job(query_vio_auto, 'cron', hour=3, minute=0, second=0)
#
# # 每天10:00, 再查一遍
# scheduler.add_job(query_vio_auto, 'cron', hour=10, minute=0, second=0)
#
# # 每天15:00, 再查一遍
# scheduler.add_job(query_vio_auto, 'cron', hour=15, minute=0, second=0)

scheduler.add_job(main, 'cron', hour=17, minute=20, second=0)

scheduler.start()
