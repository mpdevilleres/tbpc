import factory
from decimal import Decimal

from . import models

class TaskFactory(factory.Factory):
    class Meta:
        model = models.Task

    task_no = factory.Iterator(['HO-13778-H,H,HO-HO-13778-H-0049-15','HO-13778-H,H,HO-DX-13778-H-0050-15'])
    commitment_value = factory.Iterator([Decimal('221818.00'), Decimal('351818.00')])
    expenditure_actual = Decimal('0.00')
    cear_title = ''
    remarks = ''
    category = ''
    status = ''
    overrun = factory.Iterator([True, False])

#    choice_alias = (id,)

# Another, different, factory for the same object
class InvoiceFactory(factory.Factory):
    class Meta:
        model = models.Invoice

    first_name = 'Admin'
    last_name = 'User'
    admin = True

class ReportFactory(factory.Factory):
    class Meta:
        model = models.Report

    first_name = 'John'
    last_name = 'Doe'
    admin = False

class ProcessFactory(factory.Factory):
    class Meta:
        model = models.Process

    first_name = 'John'
    last_name = 'Doe'
    admin = False

class WorkflowFactory(factory.Factory):
    class Meta:
        model = models.Workflow

    first_name = 'John'
    last_name = 'Doe'
    admin = False

class ChangelogFactory(factory.Factory):
    class Meta:
        model = models.ChangeLog

    first_name = 'John'
    last_name = 'Doe'
    admin = False
