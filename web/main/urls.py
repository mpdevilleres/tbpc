from django.conf.urls import url

from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.index, name='index'),
     url(r'^ftp/get/$', views.file_get, name='get_file'),
     url(r'^ftp/get/(?P<model>\w+)/(?P<pk>\d+)/$', views.file_get),
]