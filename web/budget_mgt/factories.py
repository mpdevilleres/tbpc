import datetime

import factory
import factory.fuzzy

from decimal import Decimal

from contract_mgt.factories import ContractorFactory, ContractFactory
from pytz import UTC

from . import models

class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Task

    task_no = factory.Iterator(['HO-13778-H,H,HO-HO-13778-H-0049-15','HO-13778-H,H,HO-DX-13778-H-0050-15'])
    commitment_value = factory.Iterator([Decimal('221818.00'), Decimal('351818.00')])
    expenditure_actual = Decimal('1.11')
    cear_title = ''
    remarks = ''
    category = ''
    status = ''
    overrun = factory.Iterator([True, False])

#    choice_alias = (id,)

# Another, different, factory for the same object
class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Invoice

    contract = factory.SubFactory(ContractFactory)
    contractor = factory.SubFactory(ContractorFactory)
    task = factory.SubFactory(TaskFactory)

    state = "New"

    region = factory.Iterator(['HO', 'DXB', 'AUH', 'NE'])
    invoice_no = factory.fuzzy.FuzzyText(length=12)
    invoice_type = factory.Iterator(['Civil', 'Cable', 'Development', 'Service Provisioning'])
    revenue_amount = factory.fuzzy.FuzzyDecimal(1.11,999999999999999.99,2)
    opex_amount = factory.fuzzy.FuzzyDecimal(1.11,999999999999999.99,2)
    capex_amount = factory.fuzzy.FuzzyDecimal(1.11,999999999999999.99,2)
    penalty = factory.fuzzy.FuzzyDecimal(1.11,999999999999999.99,2)
    invoice_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), 
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    invoice_cert_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), 
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    received_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), 
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    signed_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), 
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    start_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), 
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    end_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), 
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    rfs_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), 
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    sent_finance_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), 
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    cost_center = factory.fuzzy.FuzzyText(length=12)
    expense_code = factory.fuzzy.FuzzyText(length=12)
    remarks = factory.fuzzy.FuzzyText(length=12)
    description = factory.fuzzy.FuzzyText(length=12)
    proj_no = factory.fuzzy.FuzzyText(length=12)
    status = factory.fuzzy.FuzzyText(length=12)
    current_process = factory.fuzzy.FuzzyText(length=12)

    invoice_ref = factory.PostGenerationMethodCall('set_invoice_ref')
    invoice_amount = factory.PostGenerationMethodCall('set_invoice_amount')

class ReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Report

    first_name = 'John'
    last_name = 'Doe'
    admin = False

class ProcessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Process

    first_name = 'John'
    last_name = 'Doe'
    admin = False

class WorkflowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Workflow

    first_name = 'John'
    last_name = 'Doe'
    admin = False

class ChangelogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ChangeLog

    first_name = 'John'
    last_name = 'Doe'
    admin = False
