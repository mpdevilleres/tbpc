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

    contract = factory.SubFactory(ContractFactory)
    contractor = factory.SubFactory(ContractorFactory)

    state = "New"

    task_no = factory.Iterator(['AU-HO-13742-C-0394-15', 'DX-DX-13281-C-0069-13', 'HO-HO-13691-H-0005-14'])
    authorize_commitment = factory.fuzzy.FuzzyDecimal(1.11,9999999999.99,2)
    authorize_expenditure = factory.fuzzy.FuzzyDecimal(1.11,9999999999.99,2)
    cear_title = factory.fuzzy.FuzzyText(length=12)
    remarks = factory.fuzzy.FuzzyText(length=12)
    category = factory.fuzzy.FuzzyText(length=12)
    sicet_type = factory.Iterator(['Freight', 'Customs Duty', 'Staff Cost'])
    section = factory.fuzzy.FuzzyText(length=12)


class AccrualFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Accrual

    task = factory.SubFactory(TaskFactory)
    amount = factory.fuzzy.FuzzyDecimal(1.11,9999999999.99,2)
    accrual_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC),
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))

class PccFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Pcc

    task = factory.SubFactory(TaskFactory)
    amount = factory.fuzzy.FuzzyDecimal(1.11,9999999999.99,2)

    rfs_ref = factory.fuzzy.FuzzyText(length=12)
    rfs_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC),
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    pcc_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC),
                                               datetime.datetime(2009, 1, 1, tzinfo=UTC))
    partial = factory.Iterator([True, False])

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

class InvoiceReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InvoiceReport

    invoice_ids = factory.fuzzy.FuzzyText(length=12)

class ProcessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InvoiceProcess

    first_name = 'John'
    last_name = 'Doe'
    admin = False

class ChangelogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InvoiceChangeLog

    first_name = 'John'
    last_name = 'Doe'
    admin = False
