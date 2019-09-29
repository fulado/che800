"""
WSGI config for vio_query_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vio_query_web.settings")

application = get_wsgi_application()


from apscheduler.schedulers.background import BackgroundScheduler
from vio_query.auto_job import system_init


# 定时任务
scheduler = BackgroundScheduler()

# 每天02:00开始, 备份并清空违章表和日志表
scheduler.add_job(system_init, 'cron', hour=2, minute=0, second=0)

scheduler.start()
