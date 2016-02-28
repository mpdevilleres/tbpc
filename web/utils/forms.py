from collections import OrderedDict
from itertools import chain
from django import forms
import datetime as dt
from project import settings


class EnhancedForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(EnhancedForm, self).__init__(*args, **kwargs)
        self.get_choices()
        try:
            self.field_order = chain.from_iterable(self.form_order)
        except:
            self.field_order = self.form_order
        self.order_fields(field_order=self.field_order)

    def get_choices(self):
        """
        :note: get choices from models
        """
        if hasattr(self, 'model_choices'):
            for k, v in self.model_choices.items():
                choices_value = [x.choice_alias for x in v]
                sorted_choices = sorted(choices_value, key=lambda x: x[1])
                setattr(self.fields[k],'choices', sorted_choices)

class EnhancedCharField(forms.CharField):
    def __init__(self, placeholder='', *args, **kwargs):
        self.widget = forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '%s' % placeholder
                   })
        super(EnhancedCharField, self).__init__(*args, **kwargs)

class EnhancedTextField(forms.CharField):
    def __init__(self, placeholder='', *args, **kwargs):
        self.widget = forms.Textarea(
            attrs={'class': 'form-control',
                   'rows': 3,
                   'placeholder': '%s' % placeholder
                   })
        super(EnhancedTextField, self).__init__(*args, **kwargs)

class EnhancedChoiceField(forms.ChoiceField):
    def __init__(self, placeholder='', *args, **kwargs):
        self.widget = forms.Select(
            attrs={'class': 'form-control select2',
                   'placeholder': '%s' % placeholder
                   })
        super(EnhancedChoiceField, self).__init__(*args, **kwargs)

class EnhancedMultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, placeholder='', *args, **kwargs):
        self.widget = forms.SelectMultiple(
            attrs={'class': 'multi-select',
                   'multiple': True,
                   'placeholder': '%s' % placeholder
                   })
        super(EnhancedMultipleChoiceField, self).__init__(*args, **kwargs)

class EnhancedDateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        self.input_formats=['%Y-%m-%d']
        self.widget = forms.DateInput(
            attrs={'class': 'form-control',
                   'readonly': True
                   })
        super(EnhancedDateField, self).__init__(*args, **kwargs)

def populate_obj(cleaned_data, obj):
    """
    Populates `obj.<name>` with the field's data.
    :note: This is a destructive operation. If `obj.<name>` already exists,
           it will be overridden. Use with caution.
    """
    for key, value in cleaned_data.items():
        setattr(obj, key, value)