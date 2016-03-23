from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = "budget_mgt"

urlpatterns = [

     url(r'^invoice/$', views.AddEditInvoiceView.as_view(), name='add_edit_invoice'),
     url(r'^invoice/(?P<pk>[0-9]+)/$', views.AddEditInvoiceView.as_view()),

     url(r'^invoice-history/$', views.InvoiceChangeLogView.as_view(), name='invoice_history'),
     url(r'^invoice-history/(?P<pk>[0-9]+)/$', views.InvoiceChangeLogView.as_view()),

     url(r'^invoice/table/$', views.TableInvoiceView.as_view(), name='table_invoice'),

     url(r'^task/$', views.AddEditTaskView.as_view(), name='add_edit_task'),
     url(r'^task/(?P<pk>[0-9]+)/$', views.AddEditTaskView.as_view()),

     url(r'^task/table/$', views.TableTaskView.as_view(), name='table_task'),

     url(r'^task-invoice/$', views.InvoiceSummaryView.as_view(), name='summary_invoice'),
     url(r'^task-invoice/(?P<pk>[0-9]+)/$', views.InvoiceSummaryView.as_view()),

     url(r'^invoice-workflow/$', views.TableWorkflowView.as_view(), name='invoice_workflow'),
     url(r'^invoice-workflow/(?P<pk>[0-9]+)/$', views.TableWorkflowView.as_view()),

     url(r'^invoice-workflow/close/$', views.EditWorkflowView.as_view(), name='invoice_workflow_close'),
     url(r'^invoice-workflow/close/(?P<pk>[0-9]+)/$', views.EditWorkflowView.as_view()),

     url(r'^invoice-summary/print/$', views.ForCertificationSummaryView.as_view(), name='invoice_print'),


     # Datatables Ajax Link
     url(r'^task/data/$',
         login_required(views.TaskJson.as_view()),
         name='table_task_json'),
     # url(r'^task/data/(?P<pk>[0-9]+)/$',
     #     login_required(views.TaskJson.as_view())),
     url(r'^invoice/data/$',
         login_required(views.InvoiceJson.as_view()),
         name='table_invoice_json'),
]
