from django.db import models
from django.utils import timezone
from utils.middleware import get_current_user

# Create your models here.
# UTILS FUNCS
def user_value():
    try:
        return get_current_user().username
    except:
        return "System"

# MODELS ABSTRACT
class TimeStampedBaseModel(models.Model):
    created = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.CharField(max_length=100, editable=False, default='System')

    modified = models.DateTimeField(editable=False, default=timezone.now)
    modified_by = models.CharField(max_length=100, editable=False, default='System')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
            self.created_by = user_value()

        self.modified = timezone.now()
        self.modified_by = user_value()

        super(TimeStampedBaseModel, self).save(*args, **kwargs)

    class Meta:
       abstract = True

class ProcessModel(TimeStampedBaseModel):

    class Meta:
        ordering = ['pk']
        abstract = True

    owner = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)

    @property
    def owners(self):
        return 'tests'

class ChangeLogModel(TimeStampedBaseModel):
    # MUST ADD TO MONITORED MODEL
    #invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    class Meta:
        ordering = ['pk']
        abstract = True

    field_name = models.CharField(max_length=100)
    previous_value = models.CharField(max_length=100)
    new_value = models.CharField(max_length=100)


class WorkflowModel(TimeStampedBaseModel):

    class Meta:
        ordering = ['pk']
        abstract = True

    # MUST ADD TO MONITORED MODEL
    #invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    #process = models.ForeignKey(ProcessModel, on_delete=models.CASCADE)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=100)

    def set_done(self):
        self.status = "Done"
        self.save()

# MIXINS
class ManytoManyMixin(models.Model):
    def get_initials(self):
        val_dict = self.__dict__

        for field in self._meta.get_fields():
            if isinstance(field, models.ManyToManyField):
                record = getattr(self, field.name)
                val_list = [i.pk for i in record.all()]
                val_dict[field.name] = val_list

        return val_dict
    class Meta:
       abstract = True