from __future__ import unicode_literals

import dateutil

from django.db import models
from django.utils import timezone

from .user import UserProfile


class Badge(models.Model):

    name = models.CharField(unique=True, max_length=30)

    description = models.TextField()

    credits_required = models.IntegerField()

    def __str__(self):
        args = (self.name, self.credits_required)
        return "%s badge, requires %d credits" % args


class UserBadge(models.Model):

    user = models.ForeignKey(UserProfile)

    badge = models.ForeignKey(Badge)

    awarded_at = models.DateTimeField(default=timezone.now)

    @property
    def month_awarded(self):
        awarded_at = timezone.localtime(self.awarded_at)
        prev_mth = awarded_at + dateutil.relativedelta.relativedelta(months=-1)
        return prev_mth.strftime('%B')

    def __str__(self):
        args = (self.user, self.badge, self.awarded_at)
        return "%s: %s, awarded_at: %s" % args
