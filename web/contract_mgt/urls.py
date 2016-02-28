from django.conf.urls import url

from . import views
from .views import ContractorContactJson, ContractorJson

from django.contrib.auth.decorators import login_required


app_name = "contract_mgt"

urlpatterns = [
     url(r'^contractor/table/$', views.table_contractor, name='table_contractor'),
     url(r'^contractor/$', views.add_edit_contractor, name='add_edit_contractor'),
     url(r'^contractor/(?P<pk>[0-9]+)/$', views.add_edit_contractor),

     url(r'^contact/table/$', views.table_contact, name='table_contact'),
     url(r'^contact/table/(?P<pk>[0-9]+)/$', views.table_contact),
     url(r'^contact/$', views.add_edit_contact, name='add_edit_contact'),
     url(r'^contact/(?P<pk>[0-9]+)/$', views.add_edit_contact),

     # Datatables Ajax Link

     url(r'^contact/data/$',
         login_required(ContractorContactJson.as_view()),
         name='table_contact_json'),
     url(r'^contact/data/(?P<pk>[0-9]+)/$',
         login_required(ContractorContactJson.as_view())),

     url(r'^contractor/data/$', login_required(ContractorJson.as_view()),
         name='table_contractor_json'),
]
