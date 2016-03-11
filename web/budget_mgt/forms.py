from django import forms
from user_mgt.models import Employee

import utils.forms as uforms

from .models import Contractor


class InvoiceForm(uforms.EnhancedForm):
    model_choices = {
        'user': Employee.objects.filter(section=False),
        'contractor_id': Contractor.objects.all()
    }

    form_order = [
        ['contractor_id', 'user'],
        ['contract_no', 'classification'],
        ['hr'],
        ['end_user','remarks'],
        ['description',  'status'],
        ['severity', 'category'],
        ['hr'],
        ['date_expected', 'date_team_task'],
        ['blank', 'date_close'],
    ]

    contractor_id = uforms.EnhancedChoiceField(label='Contractor:')

    description = uforms.EnhancedTextField()
    contract_no = uforms.EnhancedCharField()
    end_user = uforms.EnhancedCharField()
    remarks = uforms.EnhancedTextField()
    date_expected = uforms.EnhancedDateField(label='Expected Date')
    date_team_task = uforms.EnhancedDateField(label='Task Start Date')
    date_close = uforms.EnhancedDateField(label='Task Close Date')

    user = uforms.EnhancedMultipleChoiceField(label="Person/s In Charge")

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