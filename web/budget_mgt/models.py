from django.db.models import Sum
from django_fsm_log.decorators import fsm_log_by
from django_fsm import transition, ConcurrentTransitionMixin, FSMKeyField


from contract_mgt.models import Contractor, Contract

from decimal import Decimal
from django.db import models

from utils.models import TimeStampedBaseModel, ProcessModel, ChangeLogModel, FsmLogMixin, ManytoManyMixin

import datetime as dt
from taggit.managers import TaggableManager

# Create your models here.

class TaskProcess(ProcessModel):
    """
    Inherit Process Model to Implement Process Table for Task
    """
    pass

class Task(ConcurrentTransitionMixin, FsmLogMixin, ManytoManyMixin, TimeStampedBaseModel):

    class Transitions:
            trans_1 = ['Work in Progress', 'PCC to be Issued', 'PCC Issued', 'Closed']

    contract = models.ForeignKey(Contract, null=True, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, null=True, on_delete=models.CASCADE)

    state = FSMKeyField(TaskProcess, default="Work in Progress")
    state_date = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=100)
    task_no = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)

    sicet_type = models.CharField(max_length=100, blank=True)
    section = models.CharField(max_length=100, blank=True)
    sub_section = models.CharField(max_length=100, blank=True)
    cear_title = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    modernization = models.BooleanField(default=False)

    finance_actual_expenditure = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    transferable = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    finance_remarks = models.TextField(blank=True)

    proj_no = models.CharField(max_length=100)
    year = models.CharField(max_length=100)

    total_authorize_commitment = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    total_authorize_expenditure = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))

    total_accrual = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    actual_expenditure = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    wip_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    total_pcc_amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))

    tags = TaggableManager()

    def __str__(self):
        return self.task_no

    # get initial values for tags
    @property
    def initial_tags(self):
        return [i.name for i in self.tags.all()]

    @property
    def state__name(self):
        return self.state

    @property
    def is_overrun(self):
        return self.actual_expenditure > self.total_accrual

    @property
    def is_overbook(self):
        return self.total_accrual > self.total_authorize_expenditure

    @property
    def is_pcc_issued(self):
        return True if len(self.pcc_set.all()) != 0 else False

    @property
    def is_pcc_amount_ok(self):
        return self.total_pcc_amount <= self.total_authorize_expenditure

    @property
    def is_pcc_complete(self):
            pcc = self.pcc_set.order_by('-pk').first()
            return pcc.is_complete if pcc else False

    @property
    def is_within_work_criteria(self):
        if self.total_authorize_expenditure != 0:
            work_percent = self.total_pcc_amount/ self.total_authorize_expenditure
            return 100 >= work_percent*100 >= 95
        else:
            return False

    @property
    def is_expenditure_within_commitment(self):
            return True if self.total_authorize_expenditure <= self.total_authorize_commitment else False

    def get_wip_amount(self):
        return self.total_authorize_expenditure - self.total_pcc_amount

    def get_year(self):
        string = str(self.task_no)
        string = string.split('-')
        try:
            return string[-1]
        except IndexError:
            return 'invalid Task No'

    def get_region(self):
        string = str(self.task_no)
        string = string.split('-')
        try:
            return string[0]
        except IndexError:
            return 'invalid Task No'

    def get_category(self):
        string = str(self.task_no)
        string = string.split('-')
        try:
            return string[3]
        except IndexError:
            return 'invalid Task No'

    def get_total_authorize_commitment(self):
        total = self.authorizecommitment_set.all().aggregate(sum=Sum('amount'))
        return Decimal('0.00') if total['sum'] is None else total['sum']

    def get_total_authorize_expenditure(self):
        total = self.authorizeexpenditure_set.all().aggregate(sum=Sum('amount'))
        return Decimal('0.00') if total['sum'] is None else total['sum']

    def get_total_pcc(self):
        total = self.pcc_set.all().aggregate(sum=Sum('amount'))
        return Decimal('0.00') if total['sum'] is None else total['sum']

    def get_total_accrual(self):
        total = self.accrual_set.all().aggregate(sum=Sum('amount'))
        return Decimal('0.00') if total['sum'] is None else total['sum']

    def get_actual_expenditure(self):
        total = self.invoice_set.all().aggregate(sum=Sum('capex_amount'))
        return Decimal('0.00') if total['sum'] is None else total['sum']

    def can_complete(self):
        return not self.is_overbook and not self.is_overrun and self.is_pcc_amount_ok and \
               self.is_within_work_criteria

    def can_close(self):
         return self.can_complete() and self.is_expenditure_within_commitment

    def pcc_is_issued(self):
        return self.is_pcc_issued

    def parse_task_no(self):
        self.year = self.get_year()
        self.region = self.get_region()
        self.category = self.get_category()

    def save(self, *args, **kwargs):
        self.wip_amount = self.get_wip_amount()
        self.total_accrual = self.get_total_accrual()
        self.total_pcc_amount = self.get_total_pcc()
        self.total_authorize_commitment = self.get_total_authorize_commitment()
        self.total_authorize_expenditure = self.get_total_authorize_expenditure()
        self.actual_expenditure = self.get_actual_expenditure()
        super(Task, self).save(*args, **kwargs)

    @fsm_log_by
    @transition(field=state, source='*', target='Work in Progress')
    def set_work_in_progress(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='Work in Progress', target='PCC to be Issued',
                conditions=[can_complete])
    def set_pcc_to_be_issued(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source=['Work in Progress', 'PCC to be Issued'],
                target='PCC Issued',
                conditions=[can_complete, pcc_is_issued])
    def set_pcc_issued(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='PCC Issued',
                target='Close',
                conditions=[can_close, pcc_is_issued])
    def set_close(self, by=None):
        pass

class Accrual(TimeStampedBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    accrual_date = models.DateTimeField(blank=True, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    remarks = models.TextField()

    ref_no = models.CharField(max_length=100)

    def generate_reference_no(self):
         return 'ACL-{0}-{1:%m-%d}'.format(self.task.task_no, self.accrual_date)

    def save(self, *args, **kwargs):
        self.ref_no = self.generate_reference_no()
        super(Accrual, self).save(*args, **kwargs)
        self.task.save()

class AuthorizeCommitment(TimeStampedBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    task_child = models.CharField(max_length=100)

    amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super(AuthorizeCommitment, self).save(*args, **kwargs)
        self.task.save()

class AuthorizeExpenditure(TimeStampedBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    task_child = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    date = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField()

    def save(self, *args, **kwargs):
        super(AuthorizeExpenditure, self).save(*args, **kwargs)
        self.task.save()

class Pcc(TimeStampedBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    rfs_ref = models.CharField(max_length=100)
    rfs_date = models.DateTimeField(blank=True, null=True, default=dt.datetime.now())
    pcc_date = models.DateTimeField(blank=True, null=True, default=dt.datetime.now())
    is_complete = models.BooleanField(default=False)

    ref_no = models.CharField(max_length=100)
    counter = models.PositiveIntegerField()

    file = models.FileField(null=True, blank=True,  upload_to='pcc')

    def inc_counter(self):
        if not self.id:
            obj = self.__class__.objects.filter(task__pk=self.task_id).order_by("-counter").first()
            if obj is None:
                self.counter = 1
            else:
                self.counter =  obj.counter + 1

    def generate_reference_no(self):
        self.inc_counter()
        return 'PCC-{0}-{1}'.format(self.task.task_no,
                                             str(self.counter).zfill(3))

    def save(self, *args, **kwargs):
        self.ref_no = self.generate_reference_no()
        super(Pcc, self).save(*args, **kwargs)
        self.task.save()

class TaskChangeLog(ChangeLogModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

class InvoiceProcess(ProcessModel):
    """
    Inherit Process Model to Implement Process Table for Invoices
    """
    pass

class Invoice(ConcurrentTransitionMixin, FsmLogMixin, TimeStampedBaseModel):
    class Transitions:
            trans_1 = ['New', 'Verify Invoices', 'Overrun Check', 'Print Summary',
                             'Under Certification', 'Sent to Finance', 'Completed']

            trans_2 = ['*', 'Verify Invoices']

    contract = models.ForeignKey(Contract, null=True, on_delete=models.CASCADE)
    contractor = models.ForeignKey(Contractor, null=True, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, null=True, on_delete=models.CASCADE)

    state = FSMKeyField(InvoiceProcess, default="New")

    region = models.CharField(max_length=100)
    invoice_no = models.CharField(max_length=100)
    invoice_type = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=100)
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
    reject_date = models.DateTimeField(blank=True, null=True)
    sent_finance_date = models.DateTimeField(blank=True, null=True)
    cost_center = models.CharField(max_length=100)
    expense_code = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    description = models.TextField(blank=True)
    proj_no = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default='Ongoing')

    #current_process = models.CharField(max_length=100)
    invoice_ref = models.CharField(max_length=100, unique=True) # checks uniqueness of invoice_no over the contractor

    @property
    def state__name(self):
        return self.state

    def get_invoice_ref(self):
        return self.contractor.name + ':' + self.invoice_no

    def get_invoice_amount(self):
        return self.revenue_amount + self.opex_amount + self.capex_amount

    def save(self, *args, **kwargs):
        self.invoice_ref = self.get_invoice_ref()
        self.invoice_amount = self.get_invoice_amount()
        super(Invoice, self).save(*args, **kwargs)
        self.task.save()

    def can_print(self):
        """
        Return True if Task is not Overrun
        """
        return not self.task.is_overrun and not self.task.is_overbook

    def can_verify(self):
        allowed_task_state = ['Work in Progress', 'Work Completed without PCC',
                              'Work Completed with PCC']
        return True if self.task.state in allowed_task_state else False

    @fsm_log_by
    @transition(field=state, source='*', target='New',
                permission='budget_mgt.change_workflow')
    def set_new(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state, source='New', target='Verify Invoices',
                permission='budget_mgt.change_workflow',
                conditions=[can_verify])
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

class InvoiceChangeLog(ChangeLogModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

class InvoiceReport(TimeStampedBaseModel):
    ref_no = models.CharField(max_length=100)
    invoice_ids = models.CharField(max_length=100)
    counter = models.PositiveIntegerField(editable=False, unique=True)

    def inc_counter(self):
        if not self.id:
            obj = self.__class__.objects.order_by("-counter").first()
            if obj is None:
                self.counter = 1
            else:
                self.counter =  obj.counter + 1

    def generate_reference_no(self):
        return r'Invoice Management-{0:%y-%m-%d}-{1}'.format(dt.datetime.now(),
                                                  str(self.counter).zfill(3))

    def save(self, *args, **kwargs):
        self.inc_counter()
        self.ref_no = self.generate_reference_no()
        super(InvoiceReport, self).save(*args, **kwargs)
