import json

from django.core.cache import cache
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import mixins, permissions, serializers, viewsets

from . import check_authenticated_and_confirmed
from ..accounting import Accountant
from ..models import SubscriptionType, Subscription, UserProfile
from ..stubs.paymentapi import PaymentAPI, PaymentException


def wrap_payment_exception(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PaymentException as e:
            redirect_url = '/#/paymentexception?message=%s' % e.message
            return HttpResponseRedirect(redirect_url)
    return func_wrapper


class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = ('duration', 'description', 'active', 'price_per_month')


class SubscriptionSerializer(serializers.ModelSerializer):
    subscription_type = SubscriptionTypeSerializer()

    class Meta:
        model = Subscription
        fields = (
            'subscription_type', 'created_at', 'active',
            'paid_from', 'paid_until', 'valid')


class SubscriptionTypeViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    queryset = SubscriptionType.objects.all().order_by('duration')
    serializer_class = SubscriptionTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )


class SubscriptionViews(object):

    accountant = Accountant()
    pg = PaymentAPI()
    monthly_subscription = SubscriptionType.objects.get(duration=1)

    @method_decorator(ensure_csrf_cookie)
    @check_authenticated_and_confirmed
    @wrap_payment_exception
    def new_subscription(self, request):
        if request.user.subscription is not None:
            return HttpResponseRedirect("/")

        data = {}
        data["user"] = request.user.id
        register_key = hash("Initial payment: " + str(request.user.id))
        cache.set(register_key, json.dumps(data), 3600)

        pg_url = self.pg.create_recurring_payment(
            self.monthly_subscription.total,
            self.monthly_subscription.duration,
            '/api/payment_complete/%s/' % register_key,
            '/api/payment_fail/%s/' % register_key)
        return HttpResponseRedirect(pg_url)

    @method_decorator(ensure_csrf_cookie)
    @check_authenticated_and_confirmed
    @wrap_payment_exception
    def update_subscription(self, request):
        if not request.user.subscription:
            return HttpResponseRedirect("/")

        subscription = request.user.subscription
        data = {}
        data['subscription'] = request.user.subscription.id
        register_key = hash('Payment update: ' + str(request.user.id))
        cache.set(register_key, json.dumps(data), 3600)

        # TODO: There is a known bug here. If a subscription has been
        # canceled, but will not expire for some time, we should set the start
        # date of the recurring payment to be the end date of the subscription.
        # However, this requires complicating our pg interface, so we ignore
        # this (the pg is a dummy anyway).
        if not subscription.active:
            pg_url = self.pg.create_recurring_payment(
                self.monthly_subscription.total, self.monthly_subscription.duration,
                '/api/payment_complete/%s/' % register_key,
                '/api/payment_fail/%s/' % register_key)
        else:
            pg_url = self.pg.update_recurring_payment(
                subscription.payment_data['TOKEN'],
                '/api/payment_update_complete/%s/' % register_key,
                '/api/payment_fail/%s/' % register_key)
        return HttpResponseRedirect(pg_url)

    @method_decorator(ensure_csrf_cookie)
    @check_authenticated_and_confirmed
    @wrap_payment_exception
    def cancel_subscription(self, request):
        if not request.user.subscription:
            return HttpResponseRedirect("/")

        self.accountant.cancel_subscription(request.user.subscription)
        return JsonResponse({'result': 'success'})

    @wrap_payment_exception
    def payment_complete(self, request, key):
        pg_token = request.GET.get('TOKEN', None)
        payment_data = self.pg.get_payment_details(pg_token)
        data = json.loads(cache.get(key))
        cache.delete(key)

        if 'subscription' in data:
            subscription = Subscription.objects.get(pk=data['subscription'])
            subscription.active = True
            self.accountant.update_subscription(subscription, payment_data)
        else:
            user = UserProfile.objects.get(pk=data['user'])
            self.accountant.create_subscription(user, self.monthly_subscription, payment_data)
        return HttpResponseRedirect("/#/mysubscription")

    @wrap_payment_exception
    def payment_update_complete(self, request, key):
        pg_token = request.GET.get('TOKEN', None)
        payment_data = self.pg.get_payment_details(pg_token)
        data = json.loads(cache.get(key))
        cache.delete(key)

        subscription = Subscription.objects.get(pk=data['subscription'])
        self.accountant.update_subscription(subscription, payment_data)
        return HttpResponseRedirect("/#/mysubscription")

    # TODO: need to add an angular template for this
    @wrap_payment_exception
    def payment_fail(self, request, key):
        cache.delete(key)
        return HttpResponseRedirect("/#/paymentfail")
