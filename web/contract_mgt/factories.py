import datetime

import factory
import factory.fuzzy
from decimal import Decimal

from pytz import UTC

from . import models

class ContractorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Contractor

    name = factory.fuzzy.FuzzyText(length=12)
    remarks = factory.fuzzy.FuzzyText(length=12)
    profile = factory.fuzzy.FuzzyText(length=12)
    short_hand = factory.fuzzy.FuzzyText(length=12)

class ContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Contract

    contract_no =  factory.fuzzy.FuzzyText(length=12)
    remarks =  factory.fuzzy.FuzzyText(length=12)