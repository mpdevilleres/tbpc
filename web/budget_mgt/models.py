from django.db.models import Q
from django_fsm_log.decorators import fsm_log_by
from django_fsm import FSMField, transition, ConcurrentTransitionMixin, FSMKeyField
from contract_mgt.models import Contractor, Contract

from decimal import Decimal
from django.db import models

from utils.models import TimeStampedBaseModel, ProcessModel, WorkflowModel, ChangeLogModel

import datetime as dt
from utils.middleware import get_current_user

# Create your models here.
# UTILS FUNCS
def user_value():
    try:
        return get_current_user().username
    except:
        return "System"

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

class Process(ProcessModel):
    """
    Inherit Process Model to Implement Process Table for Invoices
    """
    pass

class Invoice(ConcurrentTransitionMixin, TimeStampedBaseModel):
    class Transitions:
            trans_1 = ['New', 'Verify Invoices', 'Overrun Check', 'Print Summary',
                             'Under Certification', 'Sent to Finance', 'Completed']

            trans_2 = ['*', 'Verify Invoices']

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    state = FSMKeyField(Process, default="New")

    region = models.CharField(max_length=100)
    invoice_no = models.CharField(max_length=100)
    invoice_type = models.CharField(max_length=100)
    revenue_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    opex_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    capex_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    invoice_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    penalty = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
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
    remarks = models.TextField(blank=True)
    description = models.TextField(blank=True)
    proj_no = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default='Ongoing')
    current_process = models.CharField(max_length=100)
    invoice_ref = models.CharField(max_length=100, unique=True) # checks uniqueness of invoice_no over the contractor

    def can_print(self):
        """
        Return True if Task is not Overrun
        """
        return not self.task.overrun

    @fsm_log_by
    @transition(field=state, source='*', target='New',
                permission='budget_mgt.change_workflow')
    def set_new(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='New', target='Verify Invoices',
                permission='budget_mgt.change_workflow')
    def set_verify_invoices(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='Verify Invoices', target='Overrun Check',
                permission='budget_mgt.change_workflow')
    def set_overrun_check(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='Overrun Check', target='Print Summary',
                permission='budget_mgt.change_workflow',
                conditions=[can_print])
    def set_print_summary(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='Print Summary', target='Under Certification',
                permission='budget_mgt.change_workflow')
    def set_under_certification(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='Under Certification', target='Sent to Finance',
                permission='budget_mgt.change_workflow')
    def set_sent_to_finance(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='Sent to Finance', target='Completed',
                permission='budget_mgt.change_workflow')
    def set_completed(self, by=None):
        pass

    def save(self, *args, **kwargs):
        self.invoice_ref = self.contractor.name + ':' + self.invoice_no
        self.invoice_amount = self.revenue_amount + self.opex_amount + self.capex_amount
        super(Invoice, self).save(*args, **kwargs)

class Workflow(WorkflowModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)

class ChangeLog(ChangeLogModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

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

