import random

from django.db.models import Sum
from django.test import TestCase
from django_fsm import TransitionNotAllowed

from .factories import InvoiceFactory, TaskFactory, AccrualFactory
from .models import Invoice, Task, Accrual


class TestInvoiceModels(TestCase):
    """
    1. Test of Model Instances
    2. Test of Functions that manipulate the values of the fields
    3. Test for Transitions
    """
    def setUp(self):
        InvoiceFactory.create_batch(9)

    def tearDown(self):
        pass

    def test_invoice_model_instance(self):
        invoice = Invoice.objects.first()
        self.assertEqual(isinstance(invoice, Invoice), True)

    def test_invoice_amount(self):
        invoice = Invoice.objects.first()
        self.assertEqual(invoice.invoice_amount,
                         invoice.revenue_amount + invoice.capex_amount + invoice.opex_amount)

    def test_invoice_ref(self):
        invoice = Invoice.objects.first()
        self.assertEqual(invoice.invoice_ref, invoice.contractor.name + ':' + invoice.invoice_no)

    def test_invoice_model_transition(self):
        invoice = Invoice.objects.first()
        self.assertRaises(TransitionNotAllowed, invoice.set_overrun_check)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_under_certification)# transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_sent_to_finance)    # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)          # transition not allowed
        self.assertEqual(None, invoice.set_verify_invoices())                   # transition to verify invoices

        invoice.state='Verify Invoices'
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)
        self.assertRaises(TransitionNotAllowed, invoice.set_under_certification)
        self.assertRaises(TransitionNotAllowed, invoice.set_sent_to_finance)
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)
        self.assertEqual(None, invoice.set_overrun_check())

        invoice.state_id='Overrun Check'
        self.assertRaises(TransitionNotAllowed, invoice.set_under_certification)
        self.assertRaises(TransitionNotAllowed, invoice.set_sent_to_finance)
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)

        # Print Summary requires that overrun is False
        invoice.task.overrun = True
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)
        invoice.task.overrun = False
        self.assertEqual(None, invoice.set_print_summary())

        invoice.state_id='Print Summary'
        self.assertRaises(TransitionNotAllowed, invoice.set_sent_to_finance)
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)
        self.assertEqual(None, invoice.set_under_certification())

        invoice.state_id='Under Certification'
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)
        self.assertEqual(None, invoice.set_sent_to_finance())

        invoice.state_id='Sent to Finance'
        self.assertEqual(None, invoice.set_completed())

        # Checks for reverse transition must be false for all except for new
        invoice.state_id='Completed'
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)
        self.assertRaises(TransitionNotAllowed, invoice.set_sent_to_finance)
        self.assertRaises(TransitionNotAllowed, invoice.set_under_certification)
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)
        self.assertRaises(TransitionNotAllowed, invoice.set_verify_invoices)
        self.assertEqual(None, invoice.set_new())


class TestTaskModels(TestCase):
    """
    1. Test of Model Instances
    2. Test of Functions that manipulate the values of the fields
    3. Test for Transitions
    """
    def setUp(self):
        tasks = TaskFactory.create_batch(9)
        invoices = InvoiceFactory.create_batch(9)
        accruals = AccrualFactory.create_batch(9)

    def tearDown(self):
        pass

    def test_task_model_instance(self):
        task = Task.objects.first()
        self.assertEqual(isinstance(task, Task), True)

    def test_task_total_accrual(self):
        task = Task.objects.first()
        total_amount = Accrual.objects.all().\
            aggregate(sum=Sum('amount'))
        self.assertEqual(task.total_accrual,total_amount)

    def test_task_total_expenditure(self):
        task = Task.objects.first()
        total_amount = Invoice.objects.filter(task_id=task.id).all().\
            aggregate(sum=Sum('capex_amount'))
        self.assertEqual(task.total_accrual,total_amount)

    def test_task_model_transition(self):
        task = Task.objects.first()
        self.assertRaises(TransitionNotAllowed, task.set_work_completed)      # transition not allowed
        self.assertEqual(None, task.set_work_in_progress())                   # transition to verify invoices
