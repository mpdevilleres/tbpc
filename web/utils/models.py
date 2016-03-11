from django.db import models
from django.utils import timezone
from utils.middleware import get_current_user

# Create your models here.

def user_value():
    try:
        return get_current_user().username
    except:
        return "System"

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