from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    position = models.CharField(max_length=100)
    section = models.BooleanField(
        _('staff status'),
        default=False)
    short_section = models.CharField(max_length=100, default=None)
