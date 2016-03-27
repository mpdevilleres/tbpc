from django.db import models

# Create your models here.
from workflow.models import ProcessModel, WorkflowModel, ChangeLogModel

class Process(ProcessModel):
    pass

class Workflow(WorkflowModel):
    pass

class ChangeLog(ChangeLogModel):
    pass
