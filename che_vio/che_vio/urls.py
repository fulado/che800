"""che_vio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.conf.urls import url, include
# from apscheduler.schedulers.background import BackgroundScheduler
# from vio_sch.views import query_vio_auto, backup_log, reset_status

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'^', include('vio_sch.urls'))
]

# 定时任务
# Scheduler = BackgroundScheduler()

# 每天00:10开始, 备份并清空违章表和日志表
# Scheduler.add_job(backup_log, 'cron', hour=0, minute=10, second=0)

# 每天00:30, 重置车辆违章查询状态status为0
# Scheduler.add_job(reset_status, 'cron', hour=0, minute=30, second=0)

# 每天01:00, 开始查询违章数据
# Scheduler.add_job(query_vio_auto, 'cron', hour=1, minute=0, second=0)
#
# Scheduler.start()
