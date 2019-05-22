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
from django.contrib import admin
from django.urls import path
from vio_query import views as vio_query_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check_code/', vio_query_views.check_code),
    path('login_handle/', vio_query_views.login_handle),
    path('main/', vio_query_views.main),
    path('vehicle/', vio_query_views.vehicle),
    path('is_vehicle_exist/', vio_query_views.is_vehicle_exist),    # 判断车辆是否已经存在
    path('vehicle_add/', vio_query_views.vehicle_add),              # 添加车辆
    path('vehicle_modify/', vio_query_views.vehicle_modify),        # 修改车辆
    path('vehicle_delete/', vio_query_views.vehicle_delete),        # 修改车辆
    path('query_vio/', vio_query_views.query_vio),                  # 查询违章
    path('', vio_query_views.login)
]
