from django.conf.urls import url
from . import views
from . import views_old

urlpatterns = [
    url(r'^violation/?', views.violation),
    url(r'^test/?', views.nginx_test),
    url(r'^login/?', views_old.login_service)
]
