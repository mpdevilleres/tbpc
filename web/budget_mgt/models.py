from contract_mgt.models import Contractor

from decimal import Decimal
from django.db import models

from utils.models import TimeStampedBaseModel

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

    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    region = models.CharField(max_length=100)
    invoice_no = models.CharField(max_length=100)
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

    invoice_ref = models.CharField(max_length=100) # checks uniqueness of invoice_no over the contractor

    process_list = ['Verify Invoices','Overrun Check', 'Print Summary', 'To be Certified by SD/TBP&C',
                        'To be Certified by SVP/MN', 'To be Certified by CTO', 'Sent to Finance']
    def save(self, *args, **kwargs):
        self.invoice_amount = self.revenue_amount + self.opex_amount + self.capex_amount
        super(Invoice, self).save(*args, **kwargs)

    @property
    def invoiceworkflow__process(self):
        try:
            return self.invoiceworkflow_set.first().process
        except:
            return ''

    @property
    def invoiceworkflow__status(self):
        try:
            return self.invoiceworkflow_set.first().status
        except:
            return ''

class InvoiceChangeLog(TimeStampedBaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    field_name = models.CharField(max_length=100)
    previous_value = models.CharField(max_length=100)
    new_value = models.CharField(max_length=100)

class InvoiceWorkflow(TimeStampedBaseModel):

    class Meta:
        ordering = ['-pk']

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    owner = models.CharField(max_length=100)
    start_date = models.CharField(max_length=100)
    end_date = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    process = models.CharField(max_length=100)