from django.db.models import Q, Sum
from django_fsm_log.decorators import fsm_log_by
from django_fsm import transition, ConcurrentTransitionMixin, FSMKeyField
from contract_mgt.models import Contractor, Contract

from decimal import Decimal
from django.db import models

from utils.models import TimeStampedBaseModel, ProcessModel, ChangeLogModel

import datetime as dt


# Create your models here.

class TaskProcess(ProcessModel):
    """
    Inherit Process Model to Implement Process Table for Task
    """
    pass

class Task(ConcurrentTransitionMixin, TimeStampedBaseModel):
    class Transitions:
            trans_1 = ['New', 'Work in Progress', 'Work Completed']

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)

    state = FSMKeyField(TaskProcess, default="New")

    task_no = models.CharField(max_length=100)
    authorize_commitment = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    authorize_expenditure = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    total_accrual = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    actual_expenditure = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    cear_title = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    overrun = models.BooleanField(default=True)
    sicet_type = models.CharField(max_length=100)

    def sum_accrual(self):
        total = self.accrual_set.all().aggregate(sum=Sum('amount'))
        self.total_accrual = Decimal('0.00') if total['sum'] is None else total['sum']

    def sum_actual_expenditure(self):
        total = self.invoice_set.all().aggregate(sum=Sum('capex_amount'))
        self.actual_expenditure = Decimal('0.00') if total['sum'] is None else total['sum']

    def can_complete(self):
        """
        Return True if Task is not Overrun
        """
        return not self.overrun

    def save(self, *args, **kwargs):
        self.sum_accrual()
        self.sum_actual_expenditure()
        super(Task, self).save(*args, **kwargs)

    @fsm_log_by
    @transition(field=state, source='New', target='Work in Progress')
    def set_work_in_progress(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='Work in Progress', target='Work Completed',
                conditions=[can_complete])
    def set_work_completed(self, by=None):
        pass


class Accrual(ChangeLogModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))

class Pcc(ChangeLogModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    rfs_date = models.DateTimeField(blank=True, null=True)

class TaskChangeLog(ChangeLogModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

class InvoiceProcess(ProcessModel):
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

    state = FSMKeyField(InvoiceProcess, default="New")

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

    def set_invoice_ref(self):
        self.invoice_ref = self.contractor.name + ':' + self.invoice_no

    def set_invoice_amount(self):
        self.invoice_amount = self.revenue_amount + self.opex_amount + self.capex_amount

    def save(self, *args, **kwargs):
        self.set_invoice_ref()
        self.set_invoice_amount()
        super(Invoice, self).save(*args, **kwargs)

class InvoiceChangeLog(ChangeLogModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

class InvoiceReport(TimeStampedBaseModel):
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

        super(InvoiceReport, self).save(*args, **kwargs)