from django.conf.urls import url

from . import views

from django.contrib.auth.decorators import login_required
from team_mgt.tables_ajax import TeamTaskJson

app_name = "team_mgt"

urlpatterns = [
     url(r'^team-task/table/$', views.table_team_task, name='table_team_task'),
     url(r'^team-task/table/(?P<pk>[0-9]+)/$', views.table_team_task, name='table_team_task'),

     url(r'^team-task/$', views.add_edit_team_task, name='add_edit_team_task'),
     url(r'^team-task/(?P<pk>[0-9]+)/$', views.add_edit_team_task),

     url(r'^team-task/team-task-history-add/$', views.add_team_task_history, name='add_team_task_history'),
     url(r'^team-task/team-task-history-add/(?P<pk>[0-9]+)/$', views.add_team_task_history),

     url(r'^team-task/team-task-history-edit/$', views.edit_team_task_history, name='edit_team_task_history'),
     url(r'^team-task/team-task-history-edit/(?P<pk>[0-9]+)/$', views.edit_team_task_history),

     url(r'^team-task/timeline/$', views.timeline, name='timeline'),
     url(r'^team-task/timeline/(?P<pk>[0-9]+)/$', views.timeline),

     # Dashboards
     url(r'^team-task/dashboard/$', views.index_dashboard, name='index_dashboard'),
     url(r'^team-task/summary/$', views.summary_dashboard, name='summary_dashboard'),


     # Datatables Ajax Link

     url(r'^contact/data/$',
         login_required(TeamTaskJson.as_view()),
         name='table_team_task_json'),
     # url(r'^contact/data/(?P<pk>[0-9]+)/$',
     #     login_required(ContractorContactJson.as_view())),
     #
     # url(r'^contractor/data/$', login_required(ContractorJson.as_view()),
     #     name='table_contractor_json'),
]
