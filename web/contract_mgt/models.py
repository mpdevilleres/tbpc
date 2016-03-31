from django.db import models
from utils.models import TimeStampedBaseModel
# Create your models here.


class Contractor(TimeStampedBaseModel):
    name = models.CharField(max_length=100)
    remarks = models.TextField()
    profile = models.TextField()
    short_hand = models.CharField(max_length=100)


class ContractorContact(TimeStampedBaseModel):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    eadd = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=100)
    office_no = models.CharField(max_length=100)
    fax_no = models.CharField(max_length=100)

    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s" % (self.name, self.eadd)

class Contract(TimeStampedBaseModel):
    contract_no = models.CharField(max_length=100)
    remarks = models.TextField()
