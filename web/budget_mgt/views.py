# -*- coding: utf-8 -*-

# Create your views here.
import mimetypes

import os
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Sum, Q, F
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_str
from django_fsm import TransitionNotAllowed, has_transition_perm

from budget_mgt.forms import InvoiceForm, TaskForm
from contract_mgt.models import Contractor
from project import settings
from utils.invoice_report_generator import InvoiceReportPrinter
from utils.summarizer import summarize_invoice
from utils.tools import capitalize
from utils.decorators import team_decorators

from .models import Invoice, Task, Workflow, Process, Report
from .tables_ajax import TaskJson, InvoiceJson

from utils.forms import populate_obj
from django.views.generic import View

import pandas as pd
from wsgiref.util import FileWrapper


# Add Edit Views
@method_decorator(team_decorators, name='dispatch')
class AddEditInvoiceView(View):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'default/add_form.html'
    success_redirect_link = 'budget_mgt:table_invoice'

    def get(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)

        if pk is None:
            forms = self.form_class()

        else:
            record = get_object_or_404(self.model, pk=pk)
            forms = self.form_class(initial=record.__dict__)

        return render(request, self.template_name, {'forms': forms})

    def post(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)
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

        return render(request, self.template_name, {'forms': form})

@method_decorator(team_decorators, name='dispatch')
class AddEditTaskView(View):
    model = Task
    form_class = TaskForm
    template_name = 'default/add_form.html'
    success_redirect_link = 'budget_mgt:table_task'

    def get(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        if pk is None:
            forms = self.form_class()

        else:
            record = get_object_or_404(self.model, pk=pk)
            forms = self.form_class(initial=record.__dict__)

        return render(request, self.template_name, {'forms': forms})

    def post(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        if pk is None:
            record = self.model()
        else:
            record = get_object_or_404(self.model, pk=pk)

        form = self.form_class(request.POST)

        if form.is_valid():
            cleaned_data = form.clean()
            populate_obj(cleaned_data, record)
            record.save()

            messages.success(request, "Successfully Updated the Database")
            return redirect(self.success_redirect_link)

        return render(request, self.template_name, {'forms': form})

@method_decorator(team_decorators, name='dispatch')
class InvoiceSummaryView(View):
    model = Task
    template_name = 'budget_mgt/invoices_summary.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.pop('pk',None)
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

        df_invoice = pd.DataFrame.from_records(task.invoice_set.all().values())
        df_contractor = pd.DataFrame.from_records(Contractor.objects.all().values())

        mg = pd.merge(df_invoice, df_contractor, left_on='contractor_id', right_on='id', how='left')

        mg['decimal_str_format'] = mg['capex_amount'].map(lambda x: '{:,.2f}'.format(x))

        mg.rename(columns={'name': 'contractor_name',        # {'old_name': 'new_name'}
                           'id_x': 'id',
                           'decimal_str_format': 'amount'},
                  inplace=True)

        data = mg.to_dict('records')

        actual_total = task.invoice_set.all().aggregate(sum=Sum('capex_amount'))['sum']

        overrun = task.overrun
        context = {
            'data': data,
            'columns': [i for i in capitalize(field_arrangement)],
            'keys': field_arrangement,
            'task_no': task.task_no,
            'commitment_value': task.commitment_value,
            'actual_total': actual_total,
            'overrun': overrun
        }
        return render(request, self.template_name, context)

@method_decorator(team_decorators, name='dispatch')
class InvoiceChangeLogView(View):
    model = Invoice
    template_name = 'budget_mgt/invoices_history.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        invoice = self.model.objects.filter(pk=pk).first()

        if invoice is None:
            raise Http404()

        history = invoice.changelog_set.order_by('pk')

        if len(history) == 0:
            update_by = None
            last_id = None
        else:
            update_by = history.first().modified_by
            last_id = invoice.changelog_set.order_by('-pk').first().pk
        context = {
            'invoice_no': invoice.invoice_no,
            'task_no': invoice.task.task_no,
            'contractor': invoice.contractor.name,
            'update_by': update_by,
            'history': history,
            'pk': pk,
            'last_id': last_id,
            'edit_link': reverse('budget_mgt:add_edit_invoice')
        }
        return render(request, self.template_name, context)

# Tables
@method_decorator(team_decorators, name='dispatch')
class TableTaskView(View):
    add_record_link = reverse_lazy('budget_mgt:add_edit_task')
    columns = getattr(TaskJson,'column_names')
    data_table_url = reverse_lazy('budget_mgt:table_task_json')
    template_name = 'default/datatable.html'
    table_title = 'Expenditure Tasks'

    def get(self, request, *args, **kwargs):

        pk = kwargs.pop('pk', None)
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

        closed = Invoice.objects.filter(current_process='Completed').count()
        ongoing = Invoice.objects.filter(~Q(current_process='Completed')).count()

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
class TableWorkflowView(View):
    model = Workflow
    template_name = 'default/static_table.html'
    table_title = 'Workflow'
    columns = ['process_owner', 'status', 'process_name', 'action']
    column_names = ['Owner', 'Status', 'Description', 'Option']
    def get(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        if pk is None:
            raise Http404()

        processes = Process.objects.all()
        invoice = Invoice.objects.filter(pk=pk).first()

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
            if invoice.state == process.name:
                status = 'New'

        context = {
            'table_title': self.table_title,
            'columns': self.columns,
            'column_names': self.column_names,
            'table_data': temp_list,
            'pk': pk
        }
        return render(request, self.template_name, context)

@method_decorator(team_decorators, name='dispatch')
class EditWorkflowView(View):
    model = Workflow

    def get(self, request, *args, **kwargs):
        action = request.GET.get('action', None)
        pk = request.GET.get('pk', None)

        if pk is None or action is None:
           raise Http404()

        invoice = Invoice.objects.filter(pk=pk).first()
        action = getattr(invoice, 'set_' + action)

        # check if user has permission to execute the method
        if not has_transition_perm(action, request.user):
            messages.warning(request, "Permission Denied")

        else:
            # try to transition and catchese if not allowed
            try:
                action(by=request.user)
                invoice.save()

            except TransitionNotAllowed:
                messages.warning(request, "Transition Not Allowed")

        return redirect(reverse('budget_mgt:invoice_workflow') + '%s' % pk)

@method_decorator(team_decorators, name='dispatch')
class ForCertificationSummaryView(View):
    model = Invoice

    def get(self, request, *args, **kwargs):
        invoices = Invoice.objects.filter(Q(state='Print Summary') &
                                          Q(task__overrun=False)).all()
        if len(invoices) == 0:
            raise Http404()

        for invoice in invoices:
            invoice.set_under_certification()
            invoice.save()

        invoice_ids = [str(i) for i in invoices.values_list('id', flat=True)]
        report = Report(invoice_ids='; '.join(invoice_ids))
        report.counter = F('counter') + 1
        report.save()

        printer = InvoiceReportPrinter(records=invoices, reference=report.reference_no)
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
