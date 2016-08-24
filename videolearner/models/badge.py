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
    class Meta:
        unique_together = ('user', 'award_month')  # only one badge per month

    user = models.ForeignKey(UserProfile)

    badge = models.ForeignKey(Badge)

    created_at = models.DateTimeField(default=timezone.now)

    award_month = models.CharField(max_length=30)

    def __str__(self):
        args = (self.user, self.badge, self.awarded_at)
        return "%s: %s, awarded_at: %s" % args
