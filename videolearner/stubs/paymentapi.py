from django.utils import timezone


class PaymentException(Exception):
    def __init__(self, message):
        self.message = message


class PaymentAPI:
    """
    Assume the payment gateway works as follows:
    1) We connect via some API to the PG, sending the payment details, and
       urls to return to upon completion of the payment (success / failure). We
       receive in return a a url to redirect to.
    2) When the return url is called, the GET params contain a token we can
       use to check the status of the payment (now and in the future).
    """
    def create_recurring_payment(self, amount, duration, success_url, fail_url):
        return '%s?TOKEN=12345' % success_url

    def update_recurring_payment(self, token, success_url, fail_url):
        return '%s?TOKEN=12345' % success_url

    def cancel_recurring_payment(self, token):
        pass

    def get_payment_details(self, token):
        return {
            'TOKEN': token,
            'FIRSTPAYMENTDATE': str(timezone.now()),
            'LASTPAYMENTDATE': str(timezone.now())
        }
