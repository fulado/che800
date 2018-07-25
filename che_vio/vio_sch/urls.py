from django.conf.urls import url
from . import views
from . import views_old

urlpatterns = [
    url(r'^violation/?', views.violation),
    url(r'^test/?', views.nginx_test),
    url(r'^login/?', views_old.login_service),
    url(r'^illegal/?', views_old.violation_service),
    url(r'^register/?', views_old.register_service),
]
