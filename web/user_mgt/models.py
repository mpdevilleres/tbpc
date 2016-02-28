from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from utils.models import TimeStampedBaseModel


class Employee(TimeStampedBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    position = models.CharField(max_length=100)
    section = models.BooleanField(
        _('staff status'),
        default=False)
    short_section = models.CharField(max_length=100, default=None)

    def __str__(self):              # __unicode__ on Python 2
        return "%s" % (self.user.full_name)

    @property
    def choice_alias(self):
        return (self.user.id, self.user.first_name + " " + self.user.last_name)