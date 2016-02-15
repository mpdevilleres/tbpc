from django.conf.urls import url

from . import views

app_name = "user_mgt"

urlpatterns = [
     url(r'^login/$', views._login, name='login'),
     url(r'^logout/$', views._logout, name='logout'),
     url(r'^change-password/$', views._change_password, name='change_password'),
]
