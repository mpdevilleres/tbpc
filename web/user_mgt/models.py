from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.db import models
from utils.models import TimeStampedBaseModel


class Employee(TimeStampedBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employment_status = models.CharField(max_length=100, default='')
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

    @property
    def is_employee(self):
        return not self.section

class Attendance(TimeStampedBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    date_day = models.DateField(blank=True, null=True)
    date_time = models.TimeField(blank=True, null=True)
    in_or_out = models.CharField(max_length=100)
    offset = models.CharField(max_length=100)
    reason_for_excess = models.TextField(blank=True)
    accepted =models.CharField(max_length=100)
    reason_for_rejection = models.TextField(blank=True)

    def is_signed_in(self):
        import datetime as dt
        if self.date_day==dt.datetime.utcnow().date() and self.in_or_out=='in':
            return True
        return False

class AttendanceSummary(TimeStampedBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    date_day = models.DateField(blank=True, null=True)
    date_time_in = models.TimeField(blank=True, null=True)
    date_time_out = models.TimeField(blank=True, null=True)
    total_hours = models.FloatField(blank=True, null=True)
    reason_for_excess = models.TextField(blank=True)
    accepted = models.CharField(max_length=100)
    reason_for_rejection = models.TextField(blank=True)
