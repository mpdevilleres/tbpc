from django import forms
import utils.forms as uforms

from .models import Contractor

class ContractorForm(uforms.EnhancedForm):
    name = uforms.EnhancedCharField(placeholder='Eg. Alcatel Lucent')
    remarks = uforms.EnhancedTextField()
    profile = uforms.EnhancedTextField()
    short_hand = uforms.EnhancedCharField(label='Alias',
                                          placeholder='Eg. ALU')
    form_order = [
        ['name', 'short_hand'],
        ['profile', 'remarks'],
    ]

class ContractorContactForm(uforms.EnhancedForm):

    model_choices = {
        'contractor_id': Contractor.objects.values_list('id', 'name')
    }

    contractor_id = uforms.EnhancedChoiceField(label='Contractor Name')
    name = uforms.EnhancedCharField()
    position = uforms.EnhancedCharField()
    mobile_no = uforms.EnhancedCharField()
    office_no = uforms.EnhancedCharField()
    fax_no = uforms.EnhancedCharField()
    eadd = forms.EmailField(label="Email Address",
                            widget = forms.EmailInput(
                            attrs={'class': 'form-control',
                            'placeholder': 'Eg. pdevilleres@etisalat.ae'
                            })
    )
