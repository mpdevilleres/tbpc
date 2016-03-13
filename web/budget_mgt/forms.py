from django import forms
from user_mgt.models import Employee

import utils.forms as uforms

from contract_mgt.models import Contractor
from .models import Task


class InvoiceForm(uforms.EnhancedForm):
    model_choices = {
        # 'user': Employee.objects.filter(section=False),
        'contractor_id': Contractor.objects.all(),
        'task_id': Task.objects.all()

    }

    form_order = [
        ['contractor_id', 'blank',
         'proj_no', 'task_id'],
        ['invoice_date', 'invoice_cert_date'],
        ['received_date', 'sent_finance_date'],
        ['signed_date', 'rfs_date'],
        ['start_date', 'end_date'],
        ['hr'],
        ['region', 'blank'],
        ['invoice_no', 'contract_no'],
        ['cost_center', 'expense_code'],
        ['hr'],
        ['revenue_amount', 'invoice_amount'],
        ['opex_amount', 'capex_amount'],
        ['description', 'remarks']
    ]

    contractor_id = uforms.EnhancedChoiceField(label='Contractor Name')
    task_id = uforms.EnhancedChoiceField(label='Task No')

    region = uforms.EnhancedCharField()
    invoice_no = uforms.EnhancedCharField()
    contract_no = uforms.EnhancedCharField()
    revenue_amount = uforms.EnhancedDecimalField()
    opex_amount = uforms.EnhancedDecimalField()
    capex_amount = uforms.EnhancedDecimalField()
    invoice_amount = uforms.EnhancedDecimalField()
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