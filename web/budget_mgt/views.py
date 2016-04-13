# -*- coding: utf-8 -*-

# Create your views here.
import mimetypes
from wsgiref.util import FileWrapper

import os
import datetime as dt
import pandas as pd
import numpy as np
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError

from budget_mgt.forms import InvoiceForm, TaskForm, AccrualForm, PccForm
from budget_mgt.utils import summarize_invoice, summarize_accrual
from budget_mgt.utils.invoice_report_generator import InvoiceReportPrinter

from contract_mgt.models import Contractor

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Sum, Q, F
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_str
from django.views.generic import View

from django_fsm import TransitionNotAllowed, has_transition_perm, can_proceed
from project import settings

from utils.decorators import team_decorators
from utils.forms import populate_obj
from utils.tools import capitalize


from .models import Invoice, Task, InvoiceProcess, InvoiceReport, Accrual, TaskProcess, Pcc
from .tables_ajax import TaskJson, InvoiceJson, AccrualJson, PccJson


# Add Edit Views
@method_decorator(team_decorators, name='dispatch')
class AddEditInvoiceView(View):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'default/add_form.html'
    success_redirect_link = 'budget_mgt:table_invoice'

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)

        if pk is None:
            forms = self.form_class()

        else:
            record = get_object_or_404(self.model, pk=pk)
            forms = self.form_class(initial=record.__dict__)

        return render(request, self.template_name, {'forms': forms, 'form_title': self.model.__name__})

    def post(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            record = self.model()
        else:
            record = get_object_or_404(self.model, pk=pk)

        form = self.form_class(request.POST)

        if form.is_valid():
            cleaned_data = form.clean()
            populate_obj(cleaned_data, record)
            record.save()
            summarize_invoice(task_pk=record.task_id)

            messages.success(request, "Successfully Updated the Database")
            return redirect(self.success_redirect_link)

        return render(request, self.template_name, {'forms': form, 'form_title': self.model.__name__})

@method_decorator(team_decorators, name='dispatch')
class AddEditTaskView(View):
    model = Task
    form_class = TaskForm
    template_name = 'default/add_form.html'
    success_redirect_link = 'budget_mgt:table_task'

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            forms = self.form_class()

        else:
            record = get_object_or_404(self.model, pk=pk)
            forms = self.form_class(initial=record.__dict__)

        return render(request, self.template_name, {'forms': forms})

    def post(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            record = self.model()
        else:
            record = get_object_or_404(self.model, pk=pk)

        form = self.form_class(request.POST)

        if form.is_valid():
            cleaned_data = form.clean()
            populate_obj(cleaned_data, record)
            try:
                record.save()
                messages.success(request, "Successfully Updated the Database")
                return redirect(self.success_redirect_link)
            except IntegrityError:
                messages.error(request, "{} already exist".format(record.task_no))

        return render(request, self.template_name, {'forms': form, 'form_title': self.model.__name__})

@method_decorator(team_decorators, name='dispatch')
class AddEditAccrualView(View):
    model = Accrual
    form_class = AccrualForm
    template_name = 'default/add_form.html'
    success_redirect_link = 'budget_mgt:table_task'

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            forms = self.form_class()

        else:
            record = get_object_or_404(self.model, pk=pk)
            forms = self.form_class(initial=record.__dict__)

        return render(request, self.template_name, {'forms': forms, 'form_title': self.model.__name__})

    def post(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            record = self.model()
        else:
            record = get_object_or_404(self.model, pk=pk)

        form = self.form_class(request.POST)

        if form.is_valid():
            cleaned_data = form.clean()
            populate_obj(cleaned_data, record)
            record.save()
            summarize_accrual(task_pk=record.task_id)

            messages.success(request, "Successfully Updated the Database")
            return redirect(self.success_redirect_link)

        return render(request, self.template_name, {'forms': form})

@method_decorator(team_decorators, name='dispatch')
class AddEditPccView(View):
    model = Pcc
    form_class = PccForm
    template_name = 'default/add_form.html'
    success_redirect_link = 'budget_mgt:table_pcc'

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            forms = self.form_class()

        else:
            record = get_object_or_404(self.model, pk=pk)
            forms = self.form_class(initial=record.__dict__)

        return render(request, self.template_name, {'forms': forms, 'form_title': self.model.__name__})

    def post(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            record = self.model()
        else:
            record = get_object_or_404(self.model, pk=pk)

        form = self.form_class(request.POST)

        if form.is_valid():
            cleaned_data = form.clean()
            populate_obj(cleaned_data, record)
            record.save()
            summarize_accrual(task_pk=record.task_id)

            messages.success(request, "Successfully Updated the Database")
            return redirect(self.success_redirect_link)

        return render(request, self.template_name, {'forms': form})

@method_decorator(team_decorators, name='dispatch')
class InvoiceSummaryView(View):
    model = Task
    template_name = 'budget_mgt/invoices_summary.html'

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        field_arrangement = [
            'id',
            'contractor_name',
            'invoice_no',
            'contract_no',
            'region',
#            'invoice_cert_date',
            'invoice_amount',
        ]
        task = Task.objects.filter(pk=pk).first()

        df_invoice = pd.DataFrame.from_records(Invoice.objects.filter(task__pk=pk).all().values())

        df_contractor = pd.DataFrame.from_records(Contractor.objects.all().values())

        if len(df_invoice) == 0 or len(df_contractor) == 0:

            data = {}

            actual_total = 0

            overrun = False
        
        else:
            mg = pd.merge(df_invoice, df_contractor, left_on='contractor_id', right_on='id', how='left')

            mg['decimal_str_format'] = mg['capex_amount'].map(lambda x: '{:,.2f}'.format(x))

            mg.rename(columns={'name': 'contractor_name',        # {'old_name': 'new_name'}
                               'id_x': 'id',
                               'decimal_str_format': 'amount'},
                      inplace=True)

            data = mg.to_dict('records')

            actual_total = task.invoice_set.all().aggregate(sum=Sum('capex_amount'))['sum']

            overrun = task.is_overrun

        context = {
            'data': data,
            'columns': [i for i in capitalize(field_arrangement)],
            'keys': field_arrangement,
            'task_no': task.task_no,
            'authorize_expenditure': task.authorize_expenditure,
            'total_accrual': task.total_accrual,
            'actual_total': actual_total,
            'overrun': task.is_overrun,
            'overbook': task.is_overbook,
        }
        return render(request, self.template_name, context)

#Tables
@method_decorator(team_decorators, name='dispatch')
class TableAccrualView(View):
    add_record_link = reverse_lazy('budget_mgt:add_edit_accrual')
    columns = getattr(AccrualJson,'column_names')
    data_table_url = reverse_lazy('budget_mgt:table_accrual_json')
    template_name = 'default/datatable.html'
    table_title = 'Expenditure Accrual'

    def get(self, request, *args, **kwargs):

        pk = request.GET.get('pk', None)
        if pk is not None:
            self.data_table_url += '?pk={}'.format(pk)

        context = {
            'table_title': self.table_title,
            'columns': self.columns,
            'data_table_url': self.data_table_url,
            'add_record_link': self.add_record_link,
        }
        return render(request, self.template_name, context)

@method_decorator(team_decorators, name='dispatch')
class TablePccView(View):
    add_record_link = reverse_lazy('budget_mgt:add_edit_pcc')
    columns = getattr(PccJson,'column_names')
    data_table_url = reverse_lazy('budget_mgt:table_pcc_json')
    template_name = 'default/datatable.html'
    table_title = 'Expenditure Pcc'

    def get(self, request, *args, **kwargs):

        pk = request.GET.get('pk', None)
        if pk is not None:
            self.data_table_url += '?pk={}'.format(pk)

        context = {
            'table_title': self.table_title,
            'columns': self.columns,
            'data_table_url': self.data_table_url,
            'add_record_link': self.add_record_link,
        }
        return render(request, self.template_name, context)

@method_decorator(team_decorators, name='dispatch')
class TableTaskView(View):
    add_record_link = reverse_lazy('budget_mgt:add_edit_task')
    columns = getattr(TaskJson,'column_names')
    data_table_url = reverse_lazy('budget_mgt:table_task_json')
    template_name = 'default/datatable.html'
    table_title = 'Expenditure Tasks'

    def get(self, request, *args, **kwargs):

        pk = request.GET.get('pk', None)
        if pk is not None:
            self.data_table_url = self.data_table_url + pk

        context = {
            'table_title': self.table_title,
            'columns': self.columns,
            'data_table_url': self.data_table_url,
            'add_record_link': self.add_record_link,
        }
        return render(request, self.template_name, context)

@method_decorator(team_decorators, name='dispatch')
class TableInvoiceView(View):
    add_record_link = reverse_lazy('budget_mgt:add_edit_invoice')
    columns = getattr(InvoiceJson,'column_names')
    data_table_url = reverse_lazy('budget_mgt:table_invoice_json')
    template_name = 'budget_mgt/report_invoice.html'
    table_title = 'Invoices'

    def get(self, request, *args, **kwargs):
        filter = request.GET.get('filter', None)

        closed = Invoice.objects.filter(state='Completed').count()
        ongoing = Invoice.objects.filter(~Q(state='Completed')).count()

        if filter is not None:
            self.data_table_url += '?{}={}'.format('filter', filter)

        context = {
            'table_title': self.table_title,
            'columns': self.columns,
            'data_table_url': self.data_table_url,
            'add_record_link': self.add_record_link,
            'ongoing': ongoing,
            'close': closed,
        }
        return render(request, self.template_name, context)

# Work Flow and Process
@method_decorator(team_decorators, name='dispatch')
class TableInvoiceWorkflowView(View):
    model = Invoice
    process_model = InvoiceProcess
    url_edit_workflow = 'budget_mgt:invoice_workflow_close'

    template_name = 'default/static_table.html'
    table_title = 'Workflow'
    columns = ['process_owner', 'status', 'process_name', 'action']
    column_names = ['Owner', 'Status', 'Description', 'Option']
    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            raise Http404()

        processes = self.process_model.objects.all()
        record = self.model.objects.filter(pk=pk).first()

        temp_list = []
        status = 'Done'
        for process in processes:
            temp_list.append(
                {
                    'process_owner': process.owners,
                    'status': status,
                    'process_name': process.name,
                    'action': '{0}'.format(process.name.lower().replace(' ', '_')),
                }
            )
            if record.state == process.name:
                status = 'New'

        context = {
            'table_title': self.table_title,
            'columns': self.columns,
            'column_names': self.column_names,
            'table_data': temp_list,
            'pk': pk,
            'url_edit_workflow': reverse_lazy(self.url_edit_workflow)
        }
        return render(request, self.template_name, context)

@method_decorator(team_decorators, name='dispatch')
class EditInvoiceWorkflowView(View):
    model = Invoice
    url_redirect_workflow_table = 'budget_mgt:invoice_workflow'

    def get(self, request, *args, **kwargs):
        action = request.GET.get('action', None)
        pk = request.GET.get('pk', None)

        if pk is None or action is None:
           raise Http404()

        record = self.model.objects.filter(pk=pk).first()
        action = getattr(record, 'set_' + action)

        # check if user has permission to execute the method
        if not can_proceed(action):
            if action.__name__ == 'set_verify_invoices':
                messages.warning(request, "Task Must Be Work in Progress or Higher")
            else:
                messages.warning(request, "Transistion is not Allowed")

        elif not has_transition_perm(action, request.user):
            messages.warning(request, "Permission Denied")

        else:
            action(by=request.user)
            record.save()

        return redirect(reverse(self.url_redirect_workflow_table) + '?pk=%s' % pk)

@method_decorator(team_decorators, name='dispatch')
class TableTaskWorkflowView(View):
#    model = Workflow
    model = Task
    process_model = TaskProcess
    url_edit_workflow = 'budget_mgt:task_workflow_close'

    template_name = 'default/static_table.html'
    table_title = 'Workflow'
    columns = ['process_owner', 'status', 'process_name', 'action']
    column_names = ['Owner', 'Status', 'Description', 'Option']
    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        if pk is None:
            raise Http404()

        processes = self.process_model.objects.all()
        record = self.model.objects.filter(pk=pk).first()

        temp_list = []
        status = 'Done'
        for process in processes:
            users = User.objects.filter(Q(user_permissions__codename='change_taskprocess') |
                                        Q(groups__permissions__codename='change_taskprocess'))\
                .distinct()
            temp_list.append(
                {
                    'process_owner': '; '.join([user.first_name for user in users]),
                    'status': status,
                    'process_name': process.name,
                    'action': '{0}'.format(process.name.lower().replace(' ', '_')),
                }
            )
            if record.state == process.name:
                status = 'New'

        context = {
            'table_title': self.table_title,
            'columns': self.columns,
            'column_names': self.column_names,
            'table_data': temp_list,
            'pk': pk,
            'url_edit_workflow': reverse_lazy(self.url_edit_workflow)
        }
        return render(request, self.template_name, context)

@method_decorator(team_decorators, name='dispatch')
class EditTaskWorkflowView(View):
    model = Task
    url_redirect_workflow_table = 'budget_mgt:task_workflow'

    def get(self, request, *args, **kwargs):
        action = request.GET.get('action', None)
        pk = request.GET.get('pk', None)

        if pk is None or action is None:
           raise Http404()

        record = self.model.objects.filter(pk=pk).first()
        action = getattr(record, 'set_' + action)

        # check if user has permission to execute the method
        if not has_transition_perm(action, request.user):
            messages.warning(request, "Permission Denied")

        else:
            # try to transition and catchese if not allowed
            try:
                action(by=request.user)
                record.state_date = dt.datetime.now()
                record.save()

            except TransitionNotAllowed:
                messages.warning(request, "Transition Not Allowed")

        return redirect(reverse(self.url_redirect_workflow_table) + '?pk=%s' % pk)

@method_decorator(team_decorators, name='dispatch')
class ForCertificationSummaryView(View):
    model = Invoice

    def get(self, request, *args, **kwargs):
        invoices = Invoice.objects.filter(Q(state='Print Summary')).all()
        if len(invoices) == 0:
            raise Http404()

        for invoice in invoices:
            invoice.set_under_certification()
            invoice.save()

        invoice_ids = [str(i) for i in invoices.values_list('id', flat=True)]
        report = InvoiceReport(invoice_ids='; '.join(invoice_ids))
        report.counter = F('counter') + 1
        report.save()

        printer = InvoiceReportPrinter(records=invoices, reference=report.ref_no)
        success = printer.run()

        if success is False:
            report.delete()
            raise Http404()

        full_path = printer.full_path
        path, filename = os.path.split(full_path)
        file_wrapper = FileWrapper( open(full_path, 'rb'))
        content_type = mimetypes.guess_type(full_path)[0]
        response = HttpResponse(file_wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(full_path)
        response['Content-Disposition'] = "attachment; filename=%s" % smart_str(filename)
        response['X-Sendfile']= smart_str(os.path.join(settings.MEDIA_ROOT, path, filename))
        return response

# DASHBOARD REPORTS
@method_decorator(team_decorators, name='dispatch')
class DashboardView(View):
    model = Task
    process_model = TaskProcess

    template_name = 'default/dashboard.html'
    table_title = 'Workflow'

    def get(self, request, *args, **kwargs):
        # for Pie Chart
        series = pd.Series(Task.objects.values_list('state', flat=True))
        series = series.value_counts()
        widgets_data = {}
        for k, v in series.items():
            widgets_data[k]={'value': v, 'title': k}

        # WIDGETS DATA
        df_task = pd.DataFrame.from_records(Task.objects.values('task_no',
                                                                     'actual_expenditure',
                                                                     'total_accrual',
                                                                     'authorize_expenditure'))

        df_task['overrun']=(df_task['actual_expenditure'] > df_task['total_accrual']).astype('int')
        df_task['overbook']=(df_task['total_accrual'] > df_task['authorize_expenditure']).astype('int')
        df_task['good']=(np.logical_not(np.logical_or(df_task['overrun'], df_task['overbook']))).astype('int')
        summary = df_task.sum()
        widgets_data['overrun']={'value': summary['overrun'], 'title': 'overrun'}
        widgets_data['overbook']={'value': summary['overbook'], 'title': 'overbook'}
        widgets_data['good']={'value': summary['good'], 'title': 'good'}
        # END WIDGETS DATA

        
        context = {
            'widgets_data': widgets_data
        }
        return render(request, self.template_name, context)
