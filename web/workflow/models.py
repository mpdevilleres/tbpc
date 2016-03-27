try:
    from utils.models import TimeStampedBaseModel as BaseModel
except ImportError:
    from django.db.models import Model as BaseModel

from django.db import models
# Create your models here.

class ProcessModel(BaseModel):
    owners = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)

    class Meta:
        abstract = True

class WorkflowModel(BaseModel):
    # This should be define in the Model
    # obj is the model name, Foreign Key
    obj = None
    process = None

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    # True is Done
    status = models.BooleanField(default=False)

    class Meta:
        abstract = True

class ChangeLogModel(BaseModel):
    # This should be define in the Model
    # obj is the model name, Foreign Key
    obj = None

    field_name = models.CharField(max_length=100)
    previous_value = models.CharField(max_length=100)
    new_value = models.CharField(max_length=100)

    class Meta:
        abstract = True
