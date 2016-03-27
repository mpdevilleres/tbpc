from django.conf.urls import url

from . import views

app_name = "more_testing"

urlpatterns = [
    url(r'^next-process/$', views.NextProcessView.as_view(), name='next_process'),
    url(r'^update-workflow/$', views.NextProcessView.as_view(), name='update_workflow'),
    url(r'^process/$', views.NextProcessView.as_view(), name='process'),
    url(r'^workflow/$', views.NextProcessView.as_view(), name='workflow'),
]
