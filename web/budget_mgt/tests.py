from django.test import TestCase
from . import factories
from . import models
# Create your tests here.
class TestTask(TestCase):
    obj = factories.TaskFactory.build()

    def test_model(self):
        self.assertTrue(isinstance(self.obj, models.Task))

class TestInvoice(TestCase):
    pass

class TestReport(TestCase):
    pass

class TestProcess(TestCase):
    pass

class TestWorkflow(TestCase):
    pass

class TestChangelog(TestCase):
    pass
