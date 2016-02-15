from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    username = forms.CharField(label= "Username:", widget=forms.TextInput(attrs={'class': 'form-control placeholder-no-fix',
                                                             'autocomplete': 'off',
                                                             'placeholder': 'Username'
                                                             }))
    password = forms.CharField(label= "Password:", widget=forms.PasswordInput(attrs={'class': 'form-control placeholder-no-fix',
                                                             'autocomplete': 'off',
                                                             'placeholder': 'Password'
                                                             }))

    # def clean_username(self):
    #     username = self.cleaned_data.get('username')
    #     if len(username) < 4:
    #         raise forms.ValidationError("ERROR")
    #     return username

class ChangePasswordForm(forms.Form):

    password = forms.CharField(label= "Password:", widget=forms.PasswordInput(attrs={'class': 'form-control placeholder-no-fix',
                                                             'autocomplete': 'off',
                                                             'placeholder': 'Password'
                                                             }))

    old_password = forms.CharField(label= "Old Password:", widget=forms.PasswordInput(attrs={'class': 'form-control placeholder-no-fix',
                                                             'autocomplete': 'off',
                                                             'placeholder': 'Old Password'
                                                             }))

    new_password = forms.CharField(label= "New Password:", widget=forms.PasswordInput(attrs={'class': 'form-control placeholder-no-fix',
                                                             'autocomplete': 'off',
                                                             'placeholder': 'New Password'
                                                             }))
    def __init__(self, request, *args, **kwargs):
        self.current_user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(request, *args, **kwargs)

    def clean_new_password(self):
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        if old_password != new_password:
            raise forms.ValidationError("Password didn't Match")
        return old_password

    def clean_password(self):
        password = self.cleaned_data.get('password')
        user = authenticate(username=self.current_user.username, password=password)
        if user is None:
            raise forms.ValidationError("Wrong Password")
        return password

#
# class Input(Widget):
#     """
#     Base class for all <input> widgets (except type='checkbox' and
#     type='radio', which are special).
#     """
#     input_type = None  # Subclasses must define this.
#
#     def _format_value(self, value):
#         if self.is_localized:
#             return formats.localize_input(value)
#         return value
#
#     def render(self, name, value, attrs=None):
#         if value is None:
#             value = ''
#         final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
#         if value != '':
#             # Only add the 'value' attribute if a value is non-empty.
#             final_attrs['value'] = force_text(self._format_value(value))
#         return format_html('<input{} />', flatatt(final_attrs))
