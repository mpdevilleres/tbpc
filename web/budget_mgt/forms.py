from contract_mgt.models import Contractor, Contract

import utils.forms as uforms

from .models import Task


class InvoiceForm(uforms.EnhancedForm):
    model_choices = {
        'contractor_id': Contractor.objects.values_list('id', 'name'),
        'task_id': Task.objects.values_list('id', 'task_no'),
        'contract_id': Contract.objects.values_list('id', 'contract_no'),
    }

    status_choices = [
        'Open',
        'Close'
    ]

    region_choices = [
        'HO',
        'DXB',
        'AUH',
        'NE'
    ]

    invoice_type_choices = [
        'Civil',
        'Cable',
        'Development',
        'Service Provisioning'
    ]

    form_order = [

        ['region','status'],
        ['contractor_id', 'task_id'],
        ['contract_id', 'proj_no'],
        ['invoice_no','cost_center'],
        ['invoice_type', 'expense_code'],
        ['description'],
        ['hr'],
        ['revenue_amount', 'penalty'],
        ['opex_amount', 'blank'],
        ['capex_amount','remarks'],
        ['hr'],
        ['invoice_date', 'start_date'],
        ['invoice_cert_date', 'end_date'],
        ['received_date', 'rfs_date'],
        ['hr'],
        ['signed_date', 'sent_finance_date'],
    ]

    contractor_id = uforms.EnhancedChoiceField(label='Contractor Name')
    task_id = uforms.EnhancedChoiceField(label='Task No')
    contract_id = uforms.EnhancedChoiceField(label='Contract No.')

    region = uforms.EnhancedChoiceField(choices=[(x,x) for x in region_choices])
    invoice_no = uforms.EnhancedCharField()
    invoice_type = uforms.EnhancedChoiceField(choices=[(x,x) for x in invoice_type_choices])
    revenue_amount = uforms.EnhancedDecimalField()
    opex_amount = uforms.EnhancedDecimalField()
    capex_amount = uforms.EnhancedDecimalField()
    invoice_date = uforms.EnhancedDateField()
    invoice_cert_date = uforms.EnhancedDateField()
    received_date = uforms.EnhancedDateField()
    signed_date = uforms.EnhancedDateField()
    start_date = uforms.EnhancedDateField()
    end_date = uforms.EnhancedDateField()
    rfs_date = uforms.EnhancedDateField()
    sent_finance_date = uforms.EnhancedDateField()
    cost_center = uforms.EnhancedCharField()
    expense_code = uforms.EnhancedCharField()
    remarks = uforms.EnhancedTextField()
    description = uforms.EnhancedTextField()
    proj_no = uforms.EnhancedCharField()
    status = uforms.EnhancedChoiceField(choices=[(x,x) for x in status_choices])
    penalty = uforms.EnhancedDecimalField()


class TaskForm(uforms.EnhancedForm):
    model_choices = {
    }

    form_order = [
        ['task_no', 'blank'],
        ['category','status'],
        ['cear_title', 'remarks'],
        ['commitment_value'],

    ]

    task_no = uforms.EnhancedCharField()
    commitment_value = uforms.EnhancedDecimalField()
    cear_title = uforms.EnhancedTextField()
    remarks = uforms.EnhancedTextField()
    category = uforms.EnhancedCharField()
    status = uforms.EnhancedCharField()