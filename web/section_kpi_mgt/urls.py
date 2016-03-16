from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = "section_kpi_mgt"

urlpatterns = [

     url(r'^specification/$', views.AddSpecView.as_view(), name='add_specification'),
     url(r'^specification/(?P<pk>[0-9]+)/$', views.AddSpecView.as_view()),

     url(r'^kpi-score/$', views.AddKpiView.as_view(), name='add_kpi'),
     url(r'^kpi-score/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<section_id>[0-9]+)/$', views.AddKpiView.as_view()),

     url(r'^select-kpi/$', views.SelectAddKpiView.as_view(), name='select_add_kpi'),
     url(r'^select-kpi/(?P<parameter>\w+)/$', views.SelectAddKpiView.as_view()),

     url(r'^specification/table/$', views.TableSpecView.as_view(), name='table_specification'),

     url(r'^kpi-dashboard-overall/$', views.DashboardKpiAllView.as_view(), name='dashboard_kpi_overall'),
     url(r'^kpi-dashboard-overall/(?P<pk>[0-9]+)/$', views.DashboardKpiAllView.as_view()),

     url(r'^kpi-dashboard/$', views.DashboardKpiView.as_view(), name='dashboard_kpi'),
     url(r'^kpi-dashboard/(?P<pk>[0-9]+)/$', views.DashboardKpiView.as_view()),

     url(r'^kpi-review/$', views.ReviewKpiView.as_view(), name='review_kpi'),
     url(r'^kpi-review/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', views.ReviewKpiView.as_view()),


     # Datatables Ajax Link
     url(r'^task/data/$', views.SpecJson.as_view(), name='table_specification_json'),
]
