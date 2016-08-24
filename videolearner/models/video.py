from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from .user import UserProfile


class Video(models.Model):

    name = models.CharField(max_length=100)

    youtube_id = models.CharField(unique=True, max_length=20)

    credits = models.IntegerField()

    description = models.TextField()

    length = models.IntegerField()  # length in seconds, TODO: get from youtube on video creation

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        args = (self.name, self.credits)
        return "%s for %d credits" % args


class UserVideo(models.Model):
    class Meta:
        unique_together = ('user', 'video')

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    subscribed_at = models.DateTimeField(default=timezone.now)

    length_watched = models.IntegerField(default=0)  # length in seconds

    active = models.BooleanField(default=True)  # videos can be shelved

    credits_awarded = models.IntegerField(default=0)  # kept in sync with multichain

    @property
    def percent_watched(self):
        return int((float(self.length_watched) / float(self.video.length)) * 100)

    def expected_credits(self, percent_watched=None):
        if percent_watched is None:
            percent_watched = self.percent_watched

        if percent_watched == 100:
            return self.video.credits
        elif percent_watched >= 80:
            return int(self.video.credits * 0.8)
        elif percent_watched >= 60:
            return int(self.video.credits * 0.6)

    def should_update_credits(self, new_length_watched):
        ratio = (float(new_length_watched) / float(self.video.length))
        new_percent = int(ratio * 100)
        return self.expected_credits(new_percent) > self.credits_awarded

    def __str__(self):
        args = (self.user, self.video, self.subscribed_at)
        return "%s by %s at %s" % args
