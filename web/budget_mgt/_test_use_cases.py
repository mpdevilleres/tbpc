# import pytest
#
# from budget_mgt.forms import TaskForm
#
#
# @pytest.mark.django_db
# class TestUseCase1:
#     """
#     Use Case simulate form entries and model/table values not the browser
#     'Work in Progress' > 'PCC to be Issued' > 'PCC Issued' > 'Closed'
#
#     Use Case 1:
#     1. Input Task in formation
#     2. Update Authorize Commitment and Expenditure (once or more)
#     3. Update Accrual (once or more)
#     4. Add Invoices  (once or more)
#     5. Traverse to the workflow
#     6. final Task value close
#     """
#
#     def test_model_instance(self):
#         form = TaskForm()
#         assert isinstance(invoice_report, InvoiceReport) == True
#
#     def test_inc_counter(self):
#         invoice_report = InvoiceReportFactory.create()
#         assert invoice_report.counter == 1
#
#         InvoiceReportFactory.create()
#         InvoiceReportFactory.create()
#         invoice_report = InvoiceReport.objects.order_by("-counter").first()
#         assert invoice_report.counter == 3
#
#     def test_generate_reference_no(self):
#         InvoiceReportFactory.create()
#         InvoiceReportFactory.create()
#         invoice_report = InvoiceReport.objects.order_by("-counter").first()
#         reference = r'Invoice Management-{0:%y-%m-%d}-{1}'.format(dt.datetime.now(),
#                                                   str(invoice_report.counter).zfill(3))
#         assert reference == invoice_report.ref_no