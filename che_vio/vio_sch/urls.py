from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^violation/?', views.violation),
    url(r'^test/?', views.nginx_test)
]
