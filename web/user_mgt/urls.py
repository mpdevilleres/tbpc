from django.conf.urls import url

from . import views
from django.contrib.auth.decorators import login_required
from user_mgt.tables_ajax import AttendanceJson

app_name = "user_mgt"

urlpatterns = [
     url(r'^login/$', views._login, name='login'),
     url(r'^logout/$', views._logout, name='logout'),
     url(r'^change-password/$', views._change_password, name='change_password'),
     url(r'^attendance/in/$', views.sign_in, name='sign_in'),
     url(r'^attendance/out/$', views.sign_out, name='sign_out'),

     url(r'^attendance/table/$', views.table_attendance, name='table_attendance'),
     url(r'^attendance/data/$',
         login_required(AttendanceJson.as_view()),
         name='table_attendance_json'),
     url(r'^attendance/data/(?P<pk>[0-9]+)/$',
         login_required(AttendanceJson.as_view())),
]
