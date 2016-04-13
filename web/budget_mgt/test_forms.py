import pytest

from budget_mgt.forms import InvoiceForm, TaskForm, AccrualForm, PccForm
from contract_mgt.factories import ContractFactory
from contract_mgt.models import Contract
from utils.forms import EnhancedForm
from .factories import InvoiceFactory, TaskFactory, AccrualFactory, PccFactory
from .models import Invoice, Task


@pytest.mark.django_db
class TestInvoiceForm:
    """
    1. Test of Form Instance
    2. Test of Functions that manipulate the values of the fields
    """

    status_choices = [
        ('Open','Open'),
        ('Close','Close'),
        ('Reject','Reject')
    ]

    region_choices = [
        ('HO','HO'),
        ('DXB','DXB'),
        ('AUH','AUH'),
        ('NE','NE'),
    ]

    invoice_type_choices = [
        ('Civil','Civil'),
        ('Cable','Cable'),
        ('Development','Development'),
        ('Service Provisioning','Service Provisioning')
    ]

    def test_invoice_form_instance(self):
        invoice = InvoiceFactory.create()
        form1 = InvoiceForm()
        form2 = InvoiceForm(initial=invoice.__dict__)
        assert isinstance(form1, EnhancedForm) == True
        assert isinstance(form2, EnhancedForm) == True

    def test_static_choices(self):
        form = InvoiceForm()

        assert form.fields['status'].choices == self.status_choices
        assert form.fields['region'].choices == self.region_choices
        assert form.fields['invoice_type'].choices == self.invoice_type_choices

    def test_dynamic_choices(self):
        # Scenario 1: Task are already in the database and just need to show in choices
        tasks = Task.objects.all()
        form = InvoiceForm()
        task_choices = [(i.id, i.task_no) for i in tasks]
        sorted_choices = sorted(task_choices, key=lambda x: x[1])
        assert form.fields['task_id'].choices == sorted_choices

        # Scenario 2: Task are already in the database and we want to add in choices
        TaskFactory.create()
        tasks = Task.objects.all()
        form = InvoiceForm()
        task_choices = [(i.id, i.task_no) for i in tasks]
        sorted_choices = sorted(task_choices, key=lambda x: x[1])
        assert form.fields['task_id'].choices == sorted_choices

@pytest.mark.django_db
class TestTaskForm:
    """
    1. Test of Form Instance
    2. Test of Functions that manipulate the values of the fields
    """
    sicet_type_choices = [
        ('Freight', 'Freight'),
        ('Custom Duty', 'Custom Duty'),
        ('Staff Cost', 'Staff Cost')
    ]


    def test_task_form_instance(self):
        task = TaskFactory.create()
        form1 = TaskForm()
        form2 = TaskForm(initial=task.__dict__)
        assert isinstance(form1, EnhancedForm) == True
        assert isinstance(form2, EnhancedForm) == True

    def test_static_choices(self):
        form = TaskForm()
        assert form.fields['sicet_type'].choices == self.sicet_type_choices

    def test_dynamic_contract_choices(self):
        # Scenario 1: Contract are already in the database and just need to show in choices
        ContractFactory.create_batch(10)
        contracts = Contract.objects.all()
        form = TaskForm()
        contract_choices = [(i.id, i.contract_no) for i in contracts]
        sorted_choices = sorted(contract_choices, key=lambda x: x[1])
        assert form.fields['contract_id'].choices == sorted_choices

        # Scenario 2: Task are already in the database and we want to add in choices
        ContractFactory.create()
        contracts = Contract.objects.all()
        form = TaskForm()
        contract_choices = [(i.id, i.contract_no) for i in contracts]
        sorted_choices = sorted(contract_choices, key=lambda x: x[1])
        assert form.fields['contract_id'].choices == sorted_choices

@pytest.mark.django_db
class TestAccrualForm:
    """
    1. Test of Form Instance
    2. Test of Functions that manipulate the values of the fields
    """
    def test_task_form_instance(self):
        accrual = AccrualFactory.create()
        form1 = AccrualForm()
        form2 = AccrualForm(initial=accrual.__dict__)
        assert isinstance(form1, EnhancedForm) == True
        assert isinstance(form2, EnhancedForm) == True

    def test_static_choices(self):
        pass

    def test_dynamic_task_choices(self):
        # Scenario 1: Task are already in the database and just need to show in choices
        tasks = Task.objects.all()
        form = InvoiceForm()
        task_choices = [(i.id, i.task_no) for i in tasks]
        sorted_choices = sorted(task_choices, key=lambda x: x[1])
        assert form.fields['task_id'].choices == sorted_choices

        # Scenario 2: Task are already in the database and we want to add in choices
        TaskFactory.create()
        tasks = Task.objects.all()
        form = InvoiceForm()
        task_choices = [(i.id, i.task_no) for i in tasks]
        sorted_choices = sorted(task_choices, key=lambda x: x[1])
        assert form.fields['task_id'].choices == sorted_choices

@pytest.mark.django_db
class TestPccForm:
    """
    1. Test of Form Instance
    2. Test of Functions that manipulate the values of the fields
    """
    partial_choices = [
        (False, False),
        (True, True)
    ]
    def test_task_form_instance(self):
        accrual = PccFactory.create()
        form1 = PccForm()
        form2 = PccForm(initial=accrual.__dict__)
        assert isinstance(form1, EnhancedForm) == True
        assert isinstance(form2, EnhancedForm) == True

    def test_static_choices(self):
        form = PccForm()
        assert form.fields['partial'].choices == self.partial_choices

    def test_dynamic_task_choices(self):
        # Scenario 1: Task are already in the database and just need to show in choices
        tasks = Task.objects.all()
        form = InvoiceForm()
        task_choices = [(i.id, i.task_no) for i in tasks]
        sorted_choices = sorted(task_choices, key=lambda x: x[1])
        assert form.fields['task_id'].choices == sorted_choices

        # Scenario 2: Task are already in the database and we want to add in choices
        TaskFactory.create()
        tasks = Task.objects.all()
        form = InvoiceForm()
        task_choices = [(i.id, i.task_no) for i in tasks]
        sorted_choices = sorted(task_choices, key=lambda x: x[1])
        assert form.fields['task_id'].choices == sorted_choices