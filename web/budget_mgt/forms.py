from django.core.validators import RegexValidator

from contract_mgt.models import Contractor, Contract

import utils.forms as uforms

from .models import Task
from django import forms

class InvoiceForm(uforms.EnhancedForm):
    model_choices = {
        'contractor_id': Contractor.objects.values_list('id', 'name'),
        'task_id': Task.objects.values_list('id', 'task_no'),
        'contract_id': Contract.objects.values_list('id', 'contract_no'),
    }

    status_choices = [
        'Open',
        'Close',
        'Reject'
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


    contract_id = uforms.EnhancedChoiceField(label='Contract No.')
    contractor_id = uforms.EnhancedChoiceField(label='Contractor Name')
    task_id = uforms.EnhancedChoiceField(label='Task No')

    # state not included

    region = uforms.EnhancedChoiceField(choices=[(x,x) for x in region_choices])
    invoice_no = uforms.EnhancedCharField()
    invoice_type = uforms.EnhancedChoiceField(choices=[(x,x) for x in invoice_type_choices])
    revenue_amount = uforms.EnhancedDecimalField()
    opex_amount = uforms.EnhancedDecimalField()
    capex_amount = uforms.EnhancedDecimalField()

    # invoice_amount not included

    penalty = uforms.EnhancedDecimalField()
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

class TaskForm(uforms.EnhancedForm):
    model_choices = {
        'contractor_id': Contractor.objects.values_list('id', 'name'),
        'contract_id': Contract.objects.values_list('id', 'contract_no'),
    }

    form_order = [
        ['contractor_id', 'contract_id'],
        ['task_no'],

        ['sicet_type', 'section'],
        ['authorize_commitment', 'authorize_expenditure'],
        ['cear_title', 'remarks']
    ]
    sicet_type_choices = [
        'Freight',
        'Custom Duty',
        'Staff Cost'
    ]

    status_choices = [
        'Ongoing',
        'Completed',
        'On-Hold'
    ]

    section_choices = [
        'CSE',
        'MP',
        'ND',
        'BP&TE',
        'MN',
        'MAM',
        'O&M',
        'DS&CE',
        'FAN',
        'DT&TI',
        'ES&DC',
        'EOPS'
    ]
    contract_id = uforms.EnhancedChoiceField(label='Contract No.')
    contractor_id = uforms.EnhancedChoiceField(label='Contractor Name')

    # state no included

#    status = uforms.EnhancedChoiceField(choices=[(x,x) for x in status_choices])
    task_no = uforms.EnhancedCharField(validators=[
        RegexValidator('^[A-Z]{2}-[A-Z]{2}-\d*-[A-Z]-\d*-\d{2}$',
                       'Must be in format "HA-HO-1323-D-12312-15"')])
#    other_ref = uforms.EnhancedCharField()
    # region
    # category
    # year

    authorize_commitment = uforms.EnhancedDecimalField()
    authorize_expenditure = uforms.EnhancedDecimalField()

    # total_accrual
    # actual_expenditure
    # wip_amount
    # total_pcc_amount

    sicet_type = uforms.EnhancedChoiceField(choices=[(x,x) for x in sicet_type_choices])
    section = uforms.EnhancedChoiceField(choices=sorted([(x,x) for x in section_choices]))
    cear_title = uforms.EnhancedTextField()
    remarks = uforms.EnhancedTextField()

    # def clean(self):
    #     super(TaskForm, self).clean()
    #     data = self.cleaned_data
    #     # Adds Validation Error Message to field, and halt post
    #     self.add_error('task_no', 'tet')

class AccrualForm(uforms.EnhancedForm):
    model_choices = {
        'task_id': Task.objects.values_list('id', 'task_no'),
    }

    form_order = [
        ['task_id','accrual_date'],
        ['amount', 'blank'],

    ]

    task_id = uforms.EnhancedChoiceField(label='Task No')
    accrual_date = uforms.EnhancedDateField(required=True)
    amount = uforms.EnhancedDecimalField(label='Accrual Amount')

class PccForm(uforms.EnhancedForm):
    model_choices = {
        'task_id': Task.objects.values_list('id', 'task_no'),
    }
    partial_choices = [
        False,
        True
    ]
    form_order = [
        ['task_id','rfs_ref'],
        ['amount','partial'],
        ['pcc_date', 'rfs_date'],

    ]

    task_id = uforms.EnhancedChoiceField(label='Task No')
    amount = uforms.EnhancedDecimalField(label='PCC Amount')
    rfs_ref = uforms.EnhancedCharField()

    # ref_no

    rfs_date = uforms.EnhancedDateField(required=True)
    pcc_date = uforms.EnhancedDateField(required=True)
    partial = uforms.EnhancedChoiceField(choices=[(x,x) for x in partial_choices])