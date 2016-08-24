from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models

from .subscription import Subscription


class UserProfile(AbstractUser):
    class Meta:
        unique_together = ('email', )

    email_confirmed = models.BooleanField(default=False)

    chain_address = models.CharField(max_length=100)

    # a null subscription means user has not subscribed yet
    subscription = models.OneToOneField(Subscription, null=True, on_delete=models.SET_NULL)

    @property
    def valid_subscription(self):
        return self.subscription is not None and self.subscription.valid
