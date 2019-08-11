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
    url(r'^query_all/?', views.query_all),                  # 查询违章
    url(r'^vio_display/?', views.vio_display),              # 违章显示
    url(r'^vio_export/?', views.vio_export),                # 违章导出

    url(r'^delete_all_vehicle/?', views.delete_all_vehicle),                  # 删除账号内全部车辆
    url(r'^delete_all_violation/?', views.delete_all_violation),                  # 删除账号内的全部违章
    url(r'^delete_all/?', views.delete_all),              # 删除账号内的全部车辆和违章

    url(r'^is_user_exist/?', views.is_user_exist),  # 判断用户是否已经存在
    url(r'^user_show/?', views.user_show),  # 显示用户管理界面
    url(r'^user_add/?', views.user_add),    # 保存新增用户信息
    url(r'^is_exceed_limitation/?', views.is_exceed_limitation),  # 判断查询量是否超限
    url(r'^can_query_all/?', views.can_query_all),  # 判断是否可以查询全部车辆
    # url(r'^user_modify/?', views.user_modify),  # 保存用户信息

    url(r'^', views.login),
]
