from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils.decorators import method_decorator
from .models import Subscription
from .stubs.paymentapi import PaymentAPI


class Accountant:
    """ Class for managing new subscriptions, renewals, and cancellations. """

    def __init__(self):
        self.pg = PaymentAPI()

    @method_decorator(transaction.atomic)
    def create_subscription(self, user, subscription_type, payment_data):
        new_subscription = Subscription()

        new_subscription.subscription_type = subscription_type
        new_subscription.paid_from = parse(payment_data['FIRSTPAYMENTDATE'])
        duration = relativedelta(months=subscription_type.duration)
        new_subscription.paid_until = new_subscription.paid_from + duration
        new_subscription.payment_data = payment_data
        new_subscription.save()

        user.subscription = new_subscription
        user.save()

    def update_subscription(self, subscription, payment_data=None):
        if not payment_data:
            token = subscription.payment_data['TOKEN']
            payment_data = self.pg.get_payment_details(token)

        paid_from = parse(payment_data['LASTPAYMENTDATE'])
        if (paid_from == subscription.paid_from):
            return

        duration = relativedelta(months=subscription.subscription_type.duration)
        subscription.paid_from = paid_from
        subscription.paid_until = subscription.paid_from + duration
        subscription.payment_data = payment_data
        subscription.save()

    def cancel_subscription(self, subscription):
        token = subscription.payment_data['TOKEN']
        self.pg.cancel_recurring_payment(token)
        subscription.active = False
        subscription.save()
