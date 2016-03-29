from itertools import chain

import os
from decimal import Decimal
from django import forms
import datetime as dt

# Forms
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


# Fields
class EnhancedCharField(forms.CharField):
    def __init__(self, placeholder='', *args, **kwargs):
        self.widget = forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '%s' % placeholder
                   })
        super(EnhancedCharField, self).__init__(*args, **kwargs)

class EnhancedChoiceField(forms.ChoiceField):
    def __init__(self, placeholder='', *args, **kwargs):
        self.widget = forms.Select(
            attrs={'class': 'form-control select2',
                   'placeholder': '%s' % placeholder
                   })
        super(EnhancedChoiceField, self).__init__(*args, **kwargs)

class EnhancedDateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        self.input_formats=['%Y-%m-%d']
        self.widget = forms.DateInput(
            attrs={'class': 'form-control',
                   'readonly': True
                   })
        super(EnhancedDateField, self).__init__(initial=dt.datetime(1990,1,1),
                                                *args, **kwargs)

class EnhancedDecimalField(forms.DecimalField):
    def __init__(self, placeholder='', *args, **kwargs):
        self.widget = forms.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': '%s' % placeholder
                   })
        super(EnhancedDecimalField, self).__init__(initial=Decimal('0.00'),
                                                   decimal_places=2,
                                                   max_digits=20,
                                                   *args, **kwargs)

    class Meta:
        default_initial_values = {"command":"make", "arguments":"test"}

class EnhancedFileField(forms.FileField):
    def __init__(self, placeholder='', *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist", ['.pdf'])
        self.ext_whitelist = [i.lower() for i in ext_whitelist]

        self.widget = forms.ClearableFileInput(
            attrs={'multiple': True,
                   'placeholder': '%s' % placeholder,
                   'onChange': "makeFileList();"})
        super(EnhancedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(EnhancedFileField, self).clean(*args, **kwargs)
        if data:
            filename = data.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()
            if ext not in self.ext_whitelist:
                raise forms.ValidationError("Filetype not allowed! Filetypes allowed: " + ', '.join(self.ext_whitelist))
        return data

class EnhancedMultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, placeholder='', *args, **kwargs):
        self.widget = forms.SelectMultiple(
            attrs={'class': 'multi-select',
                   'multiple': True,
                   'placeholder': '%s' % placeholder
                   })
        super(EnhancedMultipleChoiceField, self).__init__(*args, **kwargs)

class EnhancedTextField(forms.CharField):
    def __init__(self, placeholder='', *args, **kwargs):
        self.widget = forms.Textarea(
            attrs={'class': 'form-control',
                   'rows': 3,
                   'placeholder': '%s' % placeholder
                   })
        super(EnhancedTextField, self).__init__(*args, **kwargs)


# MISC /TOOLS
def populate_obj(cleaned_data, obj):
    """
    Populates `obj.<name>` with the field's data.
    :note: This is a destructive operation. If `obj.<name>` already exists,
           it will be overridden. Use with caution.
    """
    for key, value in cleaned_data.items():
        setattr(obj, key, value)
