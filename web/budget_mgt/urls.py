from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = "budget_mgt"

urlpatterns = [

    url(r'^invoice/$', views.AddEditInvoiceView.as_view(), name='add_edit_invoice'),
    url(r'^invoice/table/$', views.TableInvoiceView.as_view(), name='table_invoice'),
    url(r'^invoice-workflow/$', views.TableInvoiceWorkflowView.as_view(), name='invoice_workflow'),
    url(r'^invoice-workflow/close/$', views.EditInvoiceWorkflowView.as_view(), name='invoice_workflow_close'),

    url(r'^task/$', views.AddEditTaskView.as_view(), name='add_edit_task'),
    url(r'^task/table/$', views.TableTaskView.as_view(), name='table_task'),

    url(r'^task-invoice/$', views.InvoiceSummaryView.as_view(), name='summary_invoice'),
    url(r'^task-workflow/$', views.TableTaskWorkflowView.as_view(), name='task_workflow'),
    url(r'^task-workflow/close/$', views.EditTaskWorkflowView.as_view(), name='task_workflow_close'),

    url(r'^accrual/$', views.AddEditAccrualView.as_view(), name='add_edit_accrual'),
    url(r'^accrual/table/$', views.TableAccrualView.as_view(), name='table_accrual'),

    url(r'^pcc/$', views.AddEditPccView.as_view(), name='add_edit_pcc'),
    url(r'^pcc/table/$', views.TablePccView.as_view(), name='table_pcc'),

    url(r'^authorization/$', views.AddEditAuthorizationView.as_view(), name='add_edit_authorization'),
    url(r'^authorization/table/$', views.TableAuthorizationView.as_view(), name='table_authorization'),

    url(r'^invoice-summary/print/$', views.ForCertificationSummaryView.as_view(), name='invoice_print'),

    url(r'^dashboard/$', views.DashboardView.as_view(), name='dashboard'),

    # Datatables Ajax Link
    url(r'^task/data/$',
        login_required(views.TaskJson.as_view()),
        name='table_task_json'),
    url(r'^invoice/data/$',
        login_required(views.InvoiceJson.as_view()),
        name='table_invoice_json'),
    url(r'^accrual/data/$',
        login_required(views.AccrualJson.as_view()),
        name='table_accrual_json'),
    url(r'^pcc/data/$',
        login_required(views.PccJson.as_view()),
        name='table_pcc_json'),

    url(r'^authorization/data/$',
        login_required(views.AuthorizationJson.as_view()),
        name='table_authorization_json'),

    # Task Choices
    url(r'^choices/task/$',
        views.TaskChoicesView.as_view(),
        name='task_form_choices'),

    # Generate Reference for PCC
    url(r'^pcc/generate-ref/$',
        views.GeneratePccRefView.as_view(),
        name='generate_pcc_ref'),
]
