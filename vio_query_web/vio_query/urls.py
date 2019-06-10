"""vehicle_business URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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

from django.conf.urls import url
from vio_query import views

urlpatterns = [
    url(r'^check_code/?', views.check_code),
    url(r'^login_handle/?', views.login_handle),
    url(r'^logout/?', views.logout),
    url(r'^main/?', views.main),

    url(r'^is_vehicle_exist/?', views.is_vehicle_exist),    # 判断车辆是否已经存在
    url(r'^vehicle_add/?', views.vehicle_add),              # 添加车辆
    url(r'^vehicle_modify/?', views.vehicle_modify),        # 修改车辆
    url(r'^vehicle_delete/?', views.vehicle_delete),        # 修改车辆
    url(r'^vehicle_import/?', views.vehicle_import),        # 导入车辆信息
    url(r'^vehicle/?', views.vehicle_management),

    url(r'^query_vio/?', views.query_vio),                  # 查询违章
    url(r'^vio_display/?', views.vio_display),              # 违章显示
    url(r'^', views.login),
]
