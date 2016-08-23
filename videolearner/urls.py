from django.conf.urls import include, url
from rest_framework import routers

from views import index
from views.rewards import BadgeViewSet, RewardViews, UserBadgeViewSet
from views.user import UserProfileViewSet, UserSessionViews
from views.subscription import SubscriptionTypeViewSet, SubscriptionViews
from views.video import VideoViewSet, UserVideoViewSet


router = routers.DefaultRouter()
router.register(r'badge', BadgeViewSet)
router.register(r'subscriptiontype', SubscriptionTypeViewSet)
router.register(r'userprofile', UserProfileViewSet)
router.register(r'userbadge', UserBadgeViewSet)
router.register(r'video', VideoViewSet)
router.register(r'uservideo', UserVideoViewSet)

usw = UserSessionViews()
sw = SubscriptionViews()
rw = RewardViews()

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^api/', include(router.urls)),
    url(r'^api/add_user', usw.add_user, name='add_user'),
    url(r'^api/login', usw.login, name='login'),
    url(r'^api/logout', usw.logout, name='logout'),
    url(r'^api/confirm/', usw.confirm_email),
    url(r'^api/credits/', rw.get_credits),
    url(r'^api/new_subscription/', sw.new_subscription),
    url(r'^api/update_subscription/', sw.update_subscription),
    url(r'^api/cancel_subscription/', sw.cancel_subscription),
    url(r'^api/payment_complete/(?P<key>-?[0-9]+)', sw.payment_complete),
    url(r'^api/payment_update_complete/(?P<key>-?[0-9]+)',
        sw.payment_update_complete),
    url(r'^api/payment_fail/(?P<key>-?[0-9]+)', sw.payment_fail),
]
