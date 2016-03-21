from contract_mgt.models import Contractor

import utils.forms as uforms

from .models import Task


class InvoiceForm(uforms.EnhancedForm):
    model_choices = {
        # 'user': Employee.objects.filter(section=False),
        'contractor_id': Contractor.objects.all(),
        'task_id': Task.objects.filter().all()

    }

    penalty_choices = [
        'Yes',
        'No'
    ]
    status_choices = [
        'Under Process',
        'Sent for Certification',
        'Under Verification',
        'Management Approval',
        'Sent to Finance',
        'Rejected'
    ]

    region_choices = [
        'HO',
        'DXB',
        'AUH',
        'NE'
    ]

    form_order = [
        ['contractor_id', 'status',
         'proj_no', 'task_id'],
        ['invoice_date', 'invoice_cert_date'],
        ['received_date', 'sent_finance_date'],
        ['signed_date', 'rfs_date'],
        ['start_date', 'end_date'],
        ['hr'],
        ['region', 'contract_no'],
        ['invoice_no', 'description'],
        ['cost_center', 'expense_code'],
        ['hr'],
        ['revenue_amount', 'penalty'],
        ['opex_amount', ],
        ['capex_amount','remarks']
    ]

    contractor_id = uforms.EnhancedChoiceField(label='Contractor Name')
    task_id = uforms.EnhancedChoiceField(label='Task No')

    region = uforms.EnhancedChoiceField(choices=[(x,x) for x in region_choices])
    invoice_no = uforms.EnhancedCharField()
    contract_no = uforms.EnhancedCharField()
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