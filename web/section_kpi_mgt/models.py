from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from decimal import Decimal
from django.db import models

from utils.models import TimeStampedBaseModel

from django.db import models
import os
from uuid import uuid4

def path_and_rename(instance, filename):
    upload_to = 'kpi_specs'
    ext = filename.split('.')[-1]
    # get filename
    # if record exist
    if instance.pk:
        filename = '{}.{}'.format(instance.spec_date, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(instance.spec_date, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

# Create your models here.
class SectionRawScore(TimeStampedBaseModel):
    section = models.ForeignKey(User, on_delete=models.CASCADE)

    score_date = models.DateTimeField(blank=True, null=True)
    score_class = models.CharField(max_length=100)
    raw_score = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    bonus_score = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))     # Added to the score but not in the weighted


class SectionWeightedScore(TimeStampedBaseModel):

    section = models.ForeignKey(User, on_delete=models.CASCADE)
    weighted_score_date = models.DateTimeField(blank=True, null=True)
    weighted_score = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    category = models.CharField(max_length=100)

class SpecSectionKpi(TimeStampedBaseModel):

    spec_date = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True)
    data = JSONField()
    filename = models.CharField(max_length=100)
    file = models.FileField(upload_to=path_and_rename)
