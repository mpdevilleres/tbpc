from django.test import TestCase
from django_fsm import TransitionNotAllowed

from budget_mgt.forms import InvoiceForm
from utils.forms import EnhancedForm
from .factories import InvoiceFactory
from .models import Invoice

#Fixtures

status_choices = [
    ('Open','Open'),
    ('Close','Close')
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

class TestInvoiceModels(TestCase):
    """
    1. Test of Form Instance
    2. Test of Functions that manipulate the values of the fields
    3. Test for Transitions
    """
    def setUp(self):
        self.invoice = InvoiceFactory.create_batch(21)

    def tearDown(self):
        pass

    def test_invoice_form_instance(self):
        invoice = InvoiceFactory.create()
        form1 = InvoiceForm()
        form2 = InvoiceForm(initial=invoice.__dict__)
        self.assertEqual(isinstance(form1, EnhancedForm), True)
        self.assertEqual(isinstance(form2, EnhancedForm), True)

    def test_static_choices(self):
        form = InvoiceForm()

        self.assertEqual(form.fields['status'].choices, status_choices)
        self.assertEqual(form.fields['region'].choices, region_choices)
        self.assertEqual(form.fields['invoice_type'].choices, invoice_type_choices)

    def test_dynamic_choices(self):
        
        form = InvoiceForm()