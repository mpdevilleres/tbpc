from django import forms
from django.contrib.auth.models import User

from user_mgt.models import Employee

import utils.forms as uforms

from .models import Contractor
from .choices import *


class TeamTaskForm(uforms.EnhancedForm):
    model_choices = {
        'user': User.objects.filter(is_staff=True).values_list('id', 'username'),
        'contractor_id': Contractor.objects.values_list('id', 'name')
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

    #team_task_no = uforms.EnhancedCharField(placeholder='Eg. Alama')
    description = uforms.EnhancedTextField()
    contract_no = uforms.EnhancedCharField()
    category = uforms.EnhancedChoiceField(choices=choices_category)
    status = uforms.EnhancedChoiceField(choices=choices_status)
    severity = uforms.EnhancedChoiceField(choices=choices_severity)
    end_user = uforms.EnhancedCharField()
    remarks = uforms.EnhancedTextField()
    date_expected = uforms.EnhancedDateField(label='Expected Date')
    date_team_task = uforms.EnhancedDateField(label='Task Start Date')
    date_close = uforms.EnhancedDateField(label='Task Close Date')
    classification = uforms.EnhancedChoiceField(choices=choices_classification)

    user = uforms.EnhancedMultipleChoiceField(label="Person/s In Charge")

class TeamTaskHistoryEditForm(uforms.EnhancedForm):
    model_choices = {
        'user_id': User.objects.filter(is_staff=True).values_list('id', 'username')
    }

    form_order = [
#        ['document_id'],
        ['user_id', 'status'],
        ['action_taken', 'date_action'],
        ['next_action', 'date_expected'],
        ['remarks'],
    ]

    # document_id = SelectField('Attachment:',
    #                validators=[DataRequired()],
    #                choices=ChoicesDocument(),
    #                coerce=int
    #                )

    action_taken = uforms.EnhancedTextField()
    next_action = uforms.EnhancedTextField()
    remarks = uforms.EnhancedTextField()
    user_id = uforms.EnhancedChoiceField(label='Username:')
    status = uforms.EnhancedChoiceField(choices=choices_status)
    date_expected = uforms.EnhancedDateField(label='Task Expected Date')
    date_action = uforms.EnhancedDateField(label='Task Action Date')

class TeamTaskHistoryAddForm(uforms.EnhancedForm):
    model_choices = {
        'user_id': User.objects.filter(is_staff=True).values_list('id', 'username')
    }

    form_order = [
#        ['document_id'],
        ['user_id', 'status'],
        ['action_taken', 'date_action'],
        ['next_action', 'date_expected'],
        ['remarks', 'file'],
    ]

    # document_id = SelectField('Attachment:',
    #                validators=[DataRequired()],
    #                choices=ChoicesDocument(),
    #                coerce=int
    #                )

    action_taken = uforms.EnhancedTextField()
    next_action = uforms.EnhancedTextField()
    remarks = uforms.EnhancedTextField()
    user_id = uforms.EnhancedChoiceField(label='Username:')
    status = uforms.EnhancedChoiceField(choices=choices_status)
    date_expected = uforms.EnhancedDateField(label='Task Expected Date')
    date_action = uforms.EnhancedDateField(label='Task Action Date')
    file = uforms.EnhancedFileField(label='Attachment', required=False)

class TeamTaskAttachmentForm(uforms.EnhancedForm):
    form_order = [
        ['file']
    ]

    file = uforms.EnhancedFileField()
