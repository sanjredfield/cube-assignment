from django.http import HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import mixins
from rest_framework import serializers, viewsets

from . import check_authenticated_and_confirmed, IsAuthenticatedAndRegistered
from ..models import Badge, UserBadge
from ..multichain import MultichainRPC


class BadgeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Badge
        fields = ('url', 'name', 'description', 'credits_required')


class UserBadgeSerializer(serializers.HyperlinkedModelSerializer):
    badge = BadgeSerializer()

    class Meta:
        model = UserBadge
        fields = ('url', 'user', 'badge', 'award_month')


class BadgeViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Badge.objects.all().order_by('credits_required')
    serializer_class = BadgeSerializer
    permission_classes = (IsAuthenticatedAndRegistered, )


class UserBadgeViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    queryset = UserBadge.objects.all().order_by('-created_at')
    serializer_class = UserBadgeSerializer
    permission_classes = (IsAuthenticatedAndRegistered, )

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user)


class RewardViews(object):
    multichain_rpc = MultichainRPC()

    @method_decorator(ensure_csrf_cookie)
    @check_authenticated_and_confirmed
    def get_credits(self, request):
        if not request.user.subscription or not request.user.subscription.valid:
            return HttpResponseRedirect("/")
        chain_addr = request.user.chain_address
        credits = self.multichain_rpc.get_credits(chain_addr)
        return JsonResponse({'credits': credits})
