# -*- coding: utf-8 -*-

# Create your views here.
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator

from contract_mgt.models import Contractor
from utils.summarizer import summarize_invoice
from utils.tools import capitalize
from utils.decorators import team_decorators, login_required
from .forms import InvoiceForm, TaskForm
from .models import Invoice, Task
from .tables_ajax import TaskJson, InvoiceJson

from utils.forms import populate_obj
from django.views.generic import View

import pandas as pd

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
    template_name = 'default/datatable.html'
    table_title = 'Invoices'

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


#
# def invoices_summary(record_id):
#
#     record = Task.query.filter(Task.id==record_id).first()
#     (data, total) = table_invoices_summary_(record_id)
#
#     _field_arrangement = [
#         'id',
#         'contractor_name',
#         'invoice_no',
#         'contract_no',
#         'region',
#         'invoice_cert_date',
#         'amount',
#     ]
#     _field_dictionary = key_label(_field_arrangement)
#
#     _template = 'budget_mgt/invoices_summary.html'
#
#     meta = {'task_no': record.task_no,
#             'commitment_value': record.commitment_value,
#             'actual_total': total,
#             'overrun': True if total > record.commitment_value else False
#             }
#
#     return render_template(_template,
#                             data=data,
#                             columns=_field_dictionary,
#                             keys=_field_arrangement,
#                             meta = meta
# #                           add_link_func=_add_link_func_name,
# #                           timeline_link_func=_timeline_link_func_name,
# #                           table_title = _table_title
#                            )
#
