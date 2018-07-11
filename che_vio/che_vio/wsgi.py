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


# from apscheduler.schedulers.background import BackgroundScheduler
# from vio_sch.views import query_vio_auto, backup_log, reset_status
#
# # 定时任务
# scheduler = BackgroundScheduler()
#
# # 每天00:10开始, 备份并清空违章表和日志表
# scheduler.add_job(backup_log, 'cron', hour=0, minute=10, second=0)
#
# # 每天00:30, 重置车辆违章查询状态status为0
# scheduler.add_job(reset_status, 'cron', hour=0, minute=30, second=0)
#
# # 每天01:00, 开始查询违章数据
# scheduler.add_job(query_vio_auto, 'cron', hour=1, minute=0, second=0)
#
# scheduler.start()
