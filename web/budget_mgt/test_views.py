from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, RequestFactory

from budget_mgt.factories import InvoiceFactory, TaskFactory
from budget_mgt.models import Invoice


class ViewTests(TestCase):

    def setUp(self):
        TaskFactory.create_batch(100)
        InvoiceFactory.create_batch(100)
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username='test', email='test', password='top_secret')

    def test_login_required(self):
        response = self.client.get(reverse('budget_mgt:add_edit_invoice'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('budget_mgt:table_invoice'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('budget_mgt:add_edit_task'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('budget_mgt:table_task'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('budget_mgt:summary_invoice'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('budget_mgt:invoice_workflow'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('budget_mgt:invoice_workflow_close'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('budget_mgt:invoice_print'))
        self.assertEqual(response.status_code, 302)


        self.client.login(username='test', password='test')
        response = self.client.get(reverse('budget_mgt:add_edit_invoice'))
        self.assertEqual(response.status_code, 200)
        invoice = Invoice.objects.first()
        response = self.client.get(reverse('budget_mgt:add_edit_invoice') + '?pk=%s' % invoice.id)
        self.assertEqual(response.status_code, 200)

        # response = self.client.get(reverse('budget_mgt:table_invoice'))
        # self.assertEqual(response.status_code, 200)
        #
        # response = self.client.get(reverse('budget_mgt:add_edit_task'))
        # self.assertEqual(response.status_code, 200)
        #
        # response = self.client.get(reverse('budget_mgt:table_task'))
        # self.assertEqual(response.status_code, 200)
        #
        # response = self.client.get(reverse('budget_mgt:summary_invoice'))
        # self.assertEqual(response.status_code, 200)
        #
        # response = self.client.get(reverse('budget_mgt:invoice_workflow'))
        # self.assertEqual(response.status_code, 200)
        #
        # response = self.client.get(reverse('budget_mgt:invoice_workflow_close'))
        # self.assertEqual(response.status_code, 200)
        #
        # response = self.client.get(reverse('budget_mgt:invoice_print'))
        # self.assertEqual(response.status_code, 200)
