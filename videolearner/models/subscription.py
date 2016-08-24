from __future__ import unicode_literals

import dateutil

from django.db import models

from django.contrib.postgres.fields import JSONField
from django.utils import timezone


class SubscriptionType(models.Model):

    active = models.BooleanField(default=True)

    duration = models.IntegerField()  # number of months between payments

    description = models.CharField(max_length=50)

    price_per_month = models.IntegerField()

    def __str__(self):
        return "%s: %s/month for %d months" % (
            self.total, self.price_per_month, self.duration)

    @property
    def total(self):
        return self.price_per_month * self.duration


class Subscription(models.Model):

    subscription_type = models.ForeignKey(SubscriptionType)

    created_at = models.DateTimeField(default=timezone.now)

    active = models.BooleanField(default=True)  # gets set to False when user cancels subscription

    paid_from = models.DateTimeField()

    paid_until = models.DateTimeField()

    payment_data = JSONField()  # PG specific data

    @property
    def valid(self):
        # One day grace, as the script to check payment may run later in the day than paid_until
        one_day = dateutil.relativedelta.relativedelta(days=1)
        return self.paid_until + one_day > timezone.now()
