from django.db.models import Q
from django_fsm import FSMField, transition
from contract_mgt.models import Contractor, Contract

from decimal import Decimal
from django.db import models

from utils.models import TimeStampedBaseModel, ProcessModel, WorkflowModel, ChangeLogModel

import datetime as dt

# Create your models here.
class Task(TimeStampedBaseModel):
    task_no = models.CharField(max_length=100)
    commitment_value = models.DecimalField(max_digits=20, decimal_places=2)
    expenditure_actual = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    cear_title = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    overrun = models.BooleanField(default=True)

    @property
    def choice_alias(self):
        return (self.id, self.task_no)

class Invoice(TimeStampedBaseModel):

    flow = ['new', 'drafting', 'for signature', 'sent']

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    state = FSMField(default='new')

    region = models.CharField(max_length=100)
    invoice_no = models.CharField(max_length=100)
    invoice_type = models.CharField(max_length=100)
    contract_no = models.CharField(max_length=100)
    revenue_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    opex_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    capex_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    invoice_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    invoice_date = models.DateTimeField(blank=True, null=True)
    invoice_cert_date = models.DateTimeField(blank=True, null=True)
    received_date = models.DateTimeField(blank=True, null=True)
    signed_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    rfs_date = models.DateTimeField(blank=True, null=True)
    sent_finance_date = models.DateTimeField(blank=True, null=True)
    cost_center = models.CharField(max_length=100)
    expense_code = models.CharField(max_length=100)
    reference = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    description = models.TextField(blank=True)
    proj_no = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    penalty = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    current_process = models.CharField(max_length=100)
    invoice_ref = models.CharField(max_length=100) # checks uniqueness of invoice_no over the contractor

    @transition(field=state, source='new', target='drafting')
    def draft(self):
        pass

    def save(self, *args, **kwargs):

        # Get workflows of id is not exist or the invoice is new entry
        workflows = self.initial_workflow() if not self.id else []

        self.invoice_amount = self.revenue_amount + self.opex_amount + self.capex_amount
        super(Invoice, self).save(*args, **kwargs)

        if len(workflows) != 0:
            """
            Add Workflows to the Invoice
            """
            for i in workflows:
                self.workflow_set.add(i, bulk=False)

    def initial_workflow(self):
        """
        Create a List of Workflow Objects, but not yet saved

        """
        workflow_list = []
        for process in Process.objects.all():
            workflow = Workflow(
                start_date=dt.datetime.now(),
                end_date=None,
                status='New',
                process=process
            )
            workflow_list.append(workflow)

        return workflow_list

    @property
    def workflow__process__name(self):
        try:
            name = self.workflow_set.filter(status='New').first().process.name
            return name
        except:
            return 'Completed' if self.workflow_set.all() !=0 else 'Not Exist'

    @property
    def workflow__status(self):
        try:
            return self.workflow_set.first().status
        except:
            return ''

    def next_process(self):
        obj = Workflow.objects.order_by('pk').filter(Q(invoice__pk=self.pk) &
                                                           Q(status='New')).first()

        self.current_process = obj.process.name
        obj.status = "Done"

        super(Invoice, self).save()
        obj.save()

class Report(TimeStampedBaseModel):
    reference_no = models.CharField(max_length=100)
    invoice_ids = models.CharField(max_length=100)
    counter = models.PositiveIntegerField(editable=False, unique=True)

    def save(self, *args, **kwargs):

        if not self.id:
            obj = self.__class__.objects.order_by("-counter").first()
            if obj is None:
                self.counter = 1
            else:
                self.counter =  obj.counter + 1

            self.reference_no = r'Invoice Management/{}/{}'.format(dt.datetime.now().strftime('%b%Y'),self.counter)

        super(Report, self).save(*args, **kwargs)


class Process(ProcessModel):
    """
    Inherit Process Model to Implement Process Table for Invoices
    """
    pass

class Workflow(WorkflowModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)

class ChangeLog(ChangeLogModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
