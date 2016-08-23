from django.contrib import admin

from .models import Badge, Subscription, SubscriptionType
from .models import UserBadge, UserProfile
from .models import UserVideo, Video

# Register your models here.
admin.site.register(Badge)
admin.site.register(Subscription)
admin.site.register(SubscriptionType)
admin.site.register(UserBadge)
admin.site.register(UserProfile)
admin.site.register(UserVideo)
admin.site.register(Video)
