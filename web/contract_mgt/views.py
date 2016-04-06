from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from contract_mgt.models import Contractor, ContractorContact
from utils.forms import populate_obj

from .forms import ContractorForm, ContractorContactForm
from .tables_ajax import ContractorContactJson, ContractorJson

# Create your views here.

@login_required
def add_edit_contractor(request, pk=None):
    _form = ContractorForm
    _model = Contractor
    if pk is None:
        record = _model()
        form = _form(request.POST or None)
    else:
        record = get_object_or_404(_model, pk=pk)
        form = _form(initial=record.__dict__)

    if request.method == 'POST':
        form = _form(request.POST)
        if form.is_valid():

            populate_obj(form.cleaned_data, record)
            record.save()
            messages.info(request, "Successfully Updated the Database")

            return redirect('contract_mgt:table_contractor')

    context = {
        'forms' : form,
        'form_title': 'Contractor'
    }
    return render(request, 'default/add_form.html', context)


@login_required
def add_edit_contact(request, pk=None):
    _form = ContractorContactForm
    _model  = ContractorContact
    if pk is None:
        record  = _model()
        form = _form(request.POST or None)
    else:
        record  = get_object_or_404(_model, pk=pk)
        form = _form(initial=record.__dict__)

    if request.method == 'POST':
        form = _form(request.POST)
        if form.is_valid():
            form.get_cleaned_data('pic')
            populate_obj(form.cleaned_data, record)

            record.save()
            messages.info(request, "Successfully Updated the Database")

            return redirect('contract_mgt:table_contact')

    context = {
        'forms' : form,
        'form_title': 'Contractor Contact'
    }
    return render(request, 'default/add_form.html', context)


@login_required
def table_contact(request, pk=None):

    if pk is None:
        data_table_url = reverse('contract_mgt:table_contact_json')
    else:
        data_table_url = reverse('contract_mgt:table_contact_json') + pk
    context = {
        'table_title': 'Contractor Contact',
        'columns': getattr(ContractorContactJson,'column_names'),
        'data_table_url': data_table_url,
        'add_record_link': reverse('contract_mgt:add_edit_contact'),
    }
    return render(request, 'default/datatable.html', context)


@login_required
def table_contractor(request):

    context = {
        'table_title': 'Contractor Contact',
        'columns': getattr(ContractorJson,'column_names'),
        'data_table_url': reverse('contract_mgt:table_contractor_json'),
        'add_record_link': reverse('contract_mgt:add_edit_contractor'),
    }
    return render(request, 'default/datatable.html', context)

