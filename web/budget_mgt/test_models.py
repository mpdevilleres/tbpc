import random
from decimal import Decimal

from django.db.models import Sum
from django.test import TestCase
from django_fsm import TransitionNotAllowed

from .factories import InvoiceFactory, TaskFactory, AccrualFactory, PccFactory, InvoiceReportFactory
from .models import Invoice, Task, Accrual, Pcc, InvoiceReport

import pytest
import datetime as dt

class TestInvoiceModel(TestCase):
    """
    1. Test of Model Instances
    2. Test of Functions that manipulate the values of the fields
    3. Test for Transitions
    """
    def setUp(self):
        from dump import dump_task_process, dump_invoice_process
        dump_task_process()
        dump_invoice_process()
        tasks = TaskFactory.create_batch(3)
        for i in range(1,50):
            InvoiceFactory.create(task=random.choice(tasks))
            AccrualFactory.create(task=random.choice(tasks))

    def tearDown(self):
        pass

    def test_invoice_model_instance(self):
        invoice = Invoice.objects.first()
        self.assertEqual(isinstance(invoice, Invoice), True)

    def test_invoice_ref(self):
        invoice = Invoice.objects.first()
        self.assertEqual(invoice.invoice_ref, invoice.contractor.name + ':' + invoice.invoice_no)

    def test_invoice_amount(self):
        invoice = Invoice.objects.first()
        self.assertEqual(invoice.invoice_amount,
                         invoice.revenue_amount + invoice.capex_amount + invoice.opex_amount)

    def test_invoice_set_verify_invoices(self):

        # New > Verify Invoices
        # Case 1 with Task New
        task = TaskFactory.create()
        invoice = InvoiceFactory.create(task=task)
        task.state = 'New'
        task.save()
        self.assertRaises(TransitionNotAllowed, invoice.set_overrun_check)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_under_certification)# transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_sent_to_finance)    # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)          # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_verify_invoices)    # transition to verify invoices

        # New > Verify Invoices
        # Case 2 with Task "Work in Progress"
        task = TaskFactory.create()
        invoice = InvoiceFactory.create(task=task)
        self.assertRaises(TransitionNotAllowed, invoice.set_overrun_check)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_under_certification)# transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_sent_to_finance)    # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)          # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_verify_invoices)          # transition not allowed
        task.set_work_in_progress()
        task.save()
        self.assertEqual(None, invoice.set_verify_invoices())                   # transition to verify invoices

        # New > Verify Invoices
        # Case 3 with Task "Work Completed with PCC"
        task = TaskFactory.create()
        invoice = InvoiceFactory.create(task=task)
        task.state = 'Work Completed with PCC'
        task.save()
        self.assertRaises(TransitionNotAllowed, invoice.set_overrun_check)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_under_certification)# transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_sent_to_finance)    # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)          # transition not allowed
        self.assertEqual(None, invoice.set_verify_invoices())                   # transition to verify invoices

        # New > Verify Invoices
        # Case 4 with Task "Work Completed without PCC"
        task = TaskFactory.create()
        invoice = InvoiceFactory.create(task=task)
        task.state = 'Work Completed without PCC'
        task.save()
        self.assertRaises(TransitionNotAllowed, invoice.set_overrun_check)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)      # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_under_certification)# transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_sent_to_finance)    # transition not allowed
        self.assertRaises(TransitionNotAllowed, invoice.set_completed)          # transition not allowed
        self.assertEqual(None, invoice.set_verify_invoices())                   # transition to verify invoices

    def test_invoice_transitions(self):

        invoice = Invoice.objects.first()
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

        # Case 1 is overrun and is overbook must not pass
        # overbook = total_accrual > authorize_expenditure
        # overrun = actual_expenditure > total_accrual
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('1000'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('2000'))
        invoice.state_id='Overrun Check'
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)

        # Case 2 is not overrun and is not overbook must pass
        # not overbook = total_accrual =< authorize_expenditure
        # not overrun = actual_expenditure =< total_accrual
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        invoice.state_id='Overrun Check'
        self.assertEqual(None, invoice.set_print_summary())

        # Case 3 is not overrun and is overbook must not pass
        # overbook = total_accrual > authorize_expenditure
        # not overrun = actual_expenditure =< total_accrual
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('600'))
        invoice.state_id='Overrun Check'
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)

        # Case 4 is overrun and is not overbook must not pass
        # not overbook = total_accrual =< authorize_expenditure
        # overrun = actual_expenditure > total_accrual
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('600'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        invoice.state_id='Overrun Check'
        self.assertRaises(TransitionNotAllowed, invoice.set_print_summary)

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

class TestTaskModel(TestCase):
    """
    1. Test of Model Instances
    2. Test of Functions that manipulate the values of the fields
    3. Test for Transitions
    """
    def setUp(self):
        from dump import dump_task_process, dump_invoice_process
        dump_task_process()
        dump_invoice_process()
        tasks = TaskFactory.create_batch(3)
        for i in range(1,50):
            InvoiceFactory.create(task=random.choice(tasks))
            AccrualFactory.create(task=random.choice(tasks))

    def tearDown(self):
        pass

    def test_task_model_instance(self):
        task = Task.objects.first()
        self.assertEqual(isinstance(task, Task), True)

    def test_is_overrun(self):
        task = Task.objects.first()
        self.assertEqual(task.is_overrun, task.actual_expenditure > task.total_accrual)

    def test_is_overbook(self):
        task = Task.objects.first()
        self.assertEqual(task.is_overbook, task.total_accrual > task.authorize_expenditure)

    def test_is_pcc_issued(self):
        task = TaskFactory.create()
        for i in range(1,random.randint(0, 10)):
            PccFactory.create(task=task)

        self.assertEqual(task.is_pcc_issued, True if len(task.pcc_set.all()) != 0 else False)

    def test_wip_amount(self):
        task = Task.objects.first()
        self.assertEqual(task.wip_amount, task.authorize_expenditure - task.total_pcc_amount)

    def test_year(self):
        task = Task.objects.first()
        string = str(task.task_no)
        string = string.split('-')
        self.assertEqual(string[-1], task.year)

    def test_region(self):
        task = Task.objects.first()
        string = str(task.task_no)
        string = string.split('-')
        self.assertEqual(string[0], task.region)

    def test_category(self):
        task = Task.objects.first()
        string = str(task.task_no)
        string = string.split('-')
        self.assertEqual(string[3], task.category)

    def test_total_accrual(self):
        task = Task.objects.first()
        total_amount = Accrual.objects.filter(task__pk=task.pk).all().\
            aggregate(sum=Sum('amount'))
        self.assertEqual(task.total_accrual,total_amount['sum'])

    def test_actual_expenditure(self):
        task = Task.objects.first()
        total_amount = Invoice.objects.filter(task__pk=task.pk).all().\
            aggregate(sum=Sum('capex_amount'))
        self.assertEqual(task.actual_expenditure,total_amount['sum'])

    def test_task_can_complete(self):
        task = Task.objects.first()
        self.assertEqual(not task.is_overbook and not task.is_overrun,
                         task.can_complete())

    def test_task_pcc_is_issued(self):
        task = Task.objects.first()
        self.assertEqual(task.is_pcc_issued,
                         task.pcc_is_issued())

    def test_task_model_transition_set_work_in_progress(self):
        # from "New" > "Work In Progress"
        task = TaskFactory.create()
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_without_pcc)
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_with_pcc)
        self.assertEqual(None, task.set_work_in_progress())

    def test_task_model_transition_set_work_completed_without_pcc(self):
        # Case 1 can pass
        # overbook, overrun, pcc_issued
        # 0,        0,       1
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        pcc = PccFactory.create(task=task)
        task.state = 'Work in Progress'
        self.assertEqual(None, task.set_work_completed_without_pcc())

        # Case 2 can pass
        # overbook, overrun, pcc_issued
        # 0,        0,       0
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        task.state = 'Work in Progress'
        self.assertEqual(None, task.set_work_completed_without_pcc())

        # Case 3 must not pass
        # overbook, overrun, pcc_issued
        # 0,        1,       0
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('600'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_without_pcc)

        # Case 4 must not pass
        # overbook, overrun, pcc_issued
        # 0,        1,       1
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('600'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        pcc = PccFactory.create(task=task)
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_without_pcc)

        # Case 5 must not pass
        # overbook, overrun, pcc_issued
        # 1,        0,       0
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('600'))
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_without_pcc)

        # Case 6 must not pass
        # overbook, overrun, pcc_issued
        # 1,        0,       1
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('600'))
        pcc = PccFactory.create(task=task)
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_without_pcc)

        # Case 7 must not pass
        # overbook, overrun, pcc_issued
        # 1,        1,       0
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('1000'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('2000'))
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_without_pcc)

        # Case 8 must not pass
        # overbook, overrun, pcc_issued
        # 1,        1,       1
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('1000'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('2000'))
        pcc = PccFactory.create(task=task)
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_without_pcc)

    def test_task_model_transition_set_work_completed_with_pcc(self):
        # Case 1 can pass
        # overbook, overrun, pcc_issued
        # 0,        0,       1
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        pcc = PccFactory.create(task=task)
        task.state = 'Work in Progress'
        self.assertEqual(None, task.set_work_completed_with_pcc())

        # Case 2 must not pass
        # overbook, overrun, pcc_issued
        # 0,        0,       0
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_with_pcc)

        # Case 3 must not pass
        # overbook, overrun, pcc_issued
        # 0,        1,       0
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('600'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_with_pcc)

        # Case 4 must not pass
        # overbook, overrun, pcc_issued
        # 0,        1,       1
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('600'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('400'))
        pcc = PccFactory.create(task=task)
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_with_pcc)

        # Case 5 must not pass
        # overbook, overrun, pcc_issued
        # 1,        0,       0
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('600'))
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_with_pcc)

        # Case 6 must not pass
        # overbook, overrun, pcc_issued
        # 1,        0,       1
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('300'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('600'))
        pcc = PccFactory.create(task=task)
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_with_pcc)

        # Case 7 must not pass
        # overbook, overrun, pcc_issued
        # 1,        1,       0
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('1000'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('2000'))
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_with_pcc)

        # Case 8 must not pass
        # overbook, overrun, pcc_issued
        # 1,        1,       1
        task = TaskFactory.create(authorize_expenditure=Decimal('500'))
        invoice = InvoiceFactory.create(task=task, capex_amount=Decimal('1000'))
        acrrual = AccrualFactory.create(task=task, amount=Decimal('2000'))
        pcc = PccFactory.create(task=task)
        task.state = 'Work in Progress'
        self.assertRaises(TransitionNotAllowed, task.set_work_completed_with_pcc)

@pytest.mark.django_db
class TestAccrualModel:
    """
    1. Test of Model Instances
    2. Test of Functions that manipulate the values of the fields
    """
    def test_model_instance(self):
        accrual = AccrualFactory.create()
        assert isinstance(accrual, Accrual) == True

    def test_generate_reference_no(self):
        task = TaskFactory.create()
        AccrualFactory.create(task=task)
        AccrualFactory.create(task=task)
        accrual = Accrual.objects.filter(task__pk=task.pk).first()
        reference = 'ACL-{0:%y-%m-%d}'.format(accrual.accrual_date)
        assert reference == accrual.ref_no

@pytest.mark.django_db
class TestPccModel:
    """
    1. Test of Model Instances
    2. Test of Functions that manipulate the values of the fields
    """
    def test_model_instance(self):
        pcc = PccFactory.create()
        assert isinstance(pcc, Pcc) == True

    def test_inc_counter(self):
        task = TaskFactory.create()
        PccFactory.create(task=task)
        pcc = Pcc.objects.filter(task__pk=task.pk).order_by("-counter").first()
        assert pcc.counter == 1

        PccFactory.create(task=task)
        PccFactory.create(task=task)
        pcc = Pcc.objects.filter(task__pk=task.pk).order_by("-counter").first()
        assert pcc.counter == 3

    def test_generate_reference_no(self):
        task = TaskFactory.create()
        PccFactory.create(task=task)
        PccFactory.create(task=task)
        pcc = Pcc.objects.filter(task__pk=task.pk).first()
        reference = 'PCC-{0}-{1:%y-%m-%d}-{2}'.format(pcc.task.task_no,
                                             pcc.pcc_date,
                                             str(pcc.counter).zfill(3))
        assert reference == pcc.ref_no

@pytest.mark.django_db
class TestInvoiceReportModel:
    """
    1. Test of Model Instances
    2. Test of Functions that manipulate the values of the fields
    """
    def test_model_instance(self):
        invoice_report = InvoiceReportFactory.create()
        assert isinstance(invoice_report, InvoiceReport) == True

    def test_inc_counter(self):
        invoice_report = InvoiceReportFactory.create()
        assert invoice_report.counter == 1

        InvoiceReportFactory.create()
        InvoiceReportFactory.create()
        invoice_report = InvoiceReport.objects.order_by("-counter").first()
        assert invoice_report.counter == 3

    def test_generate_reference_no(self):
        InvoiceReportFactory.create()
        InvoiceReportFactory.create()
        invoice_report = InvoiceReport.objects.order_by("-counter").first()
        reference = r'Invoice Management-{0:%y-%m-%d}-{1}'.format(dt.datetime.now(),
                                                  str(invoice_report.counter).zfill(3))
        assert reference == invoice_report.ref_no