from django.conf.urls import url
from . import views
from . import views_temp

urlpatterns = [
    url(r'^violation-point/login/?', views_temp.login_service),
    url(r'^violation-point/illgledata/vehicleDate/?', views_temp.violation_service),
    url(r'^violation-point/illgledata/driver?', views_temp.driver_service),
    url(r'^violation/?', views.violation),
]
