import datetime

import factory
import factory.fuzzy
from decimal import Decimal

from pytz import UTC

from . import models

class ContractorFactory(factory.Factory):
    class Meta:
        model = models.Contractor

    name = factory.fuzzy.FuzzyText(length=12)
    remarks = factory.fuzzy.FuzzyText(length=12)
    profile = factory.fuzzy.FuzzyText(length=12)
    short_hand = factory.fuzzy.FuzzyText(length=12)

    def __str__(self):
        return "%s" % (self.name)

    @property
    def choice_alias(self):
        return (self.id, self.name)