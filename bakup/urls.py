from django.conf.urls import url
from . import views
from . import views_old
from . import views_sz

urlpatterns = [
    url(r'^violation/?', views.violation),
    url(r'^test/?', views.nginx_test),
    url(r'^login/shenzhou/?', views_sz.login_service),
    url(r'^login/?', views_old.login_service),
    url(r'^IllegalData-search/login/?', views_old.login_service),
    url(r'^illegal/shenzhou/?', views_sz.violation_service),
    url(r'^illegal/?', views_old.violation_service),
    url(r'^IllegalData-search/vehicle/?', views_old.violation_service),
    url(r'^register/shenzhou/?', views_sz.register_service),
    url(r'^register/?', views_old.register_service),
]