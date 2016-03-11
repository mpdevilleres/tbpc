# -*- coding: utf-8 -*-

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from .forms import InvoiceForm, TaskForm
from .models import Invoice, Task
from .tables_ajax import TaskJson

from utils.forms import populate_obj
from django.views.generic import View


# Add Edit Views
class AddEditInvoiceView(View):
    model = Invoice
    form_class = InvoiceForm

    initial = {'key': 'value'}
    template_name = 'default/add_form.html'

    def get(self, request, *args, **kwargs):

        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'forms': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            pass
            # <process form cleaned data>
            #return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'forms': form})

class AddEditTaskView(View):
    model = Task
    form_class = TaskForm
    template_name = 'default/add_form.html'
    success_redirect_link = redirect('budget_mgt:table_task')

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
            return self.success_redirect_link

        return render(request, self.template_name, {'forms': form})


# Tables
class TableTaskView(View):
    add_record_link = reverse_lazy('budget_mgt:add_edit_task')
    columns = getattr(TaskJson,'column_names')
    data_table_url = reverse_lazy('budget_mgt:table_task_json')
    form_class = TaskForm
    model = Task
    template_name = 'default/datatable.html'
    table_title = 'Tasks'

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

class TableInvoiceView(View):
    add_record_link = reverse_lazy('budget_mgt:add_edit_invoice')
    columns = getattr(TaskJson,'column_names')
    data_table_url = reverse_lazy('budget_mgt:table_invoice_json')
    form_class = TaskForm
    model = Task
    template_name = 'default/datatable.html'
    table_title = 'Tasks'

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
