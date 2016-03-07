from django.conf.urls import url

from . import views
from django.contrib.auth.decorators import login_required
from user_mgt.tables_ajax import AttendanceJson, AttendanceSummaryJson

app_name = "user_mgt"

urlpatterns = [
     url(r'^login/$', views._login, name='login'),
     url(r'^logout/$', views._logout, name='logout'),
     url(r'^change-password/$', views._change_password, name='change_password'),
     url(r'^attendance/in/$', views.sign_in, name='sign_in'),
     url(r'^attendance/out/$', views.sign_out, name='sign_out'),

     url(r'^attendance/acceptance/$', views.attendance_acceptance, name='acceptance'),
     url(r'^attendance/acceptance/(?P<pk>[0-9]+)/(?P<option>[0-1]+)/$', views.attendance_acceptance),

     url(r'^attendance/table/$', views.table_attendance, name='table_attendance'),
     url(r'^attendance/data/$',
         login_required(AttendanceJson.as_view()),
         name='table_attendance_json'),
     url(r'^attendance/data/(?P<pk>[0-9]+)/$',
         login_required(AttendanceJson.as_view())),

     url(r'^attendance-summary/table/$', views.table_attendance_summary,
         name='table_attendance_summary'),
     url(r'^attendance-summary/data/$',
         login_required(AttendanceSummaryJson.as_view()),
         name='table_attendance_summary_json'),
    url(r'^attendance-summary/data/(?P<pk>[0-9]+)/$',
         login_required(AttendanceSummaryJson.as_view())),

    url(r'^reason/$', views.add_edit_attendance_reason, name='add_edit_attendance_reason'),
    url(r'^reason/(?P<pk>[0-9]+)/$', views.add_edit_attendance_reason)

]
