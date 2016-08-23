import dateutil
import logging

from celery import shared_task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.template.loader import get_template
from django.utils import timezone

from accounting import Accountant
from models import Badge, UserBadge, UserVideo, UserProfile
from multichain import MultichainRPC, MultichainException
from multichain import InsufficientCreditsException
from util import generate_confirmation_token


log = logging.getLogger('Tasks')


@shared_task
def send_registration_email(email):
    token = generate_confirmation_token(email)

    ctx = {'confirm_url': 'http://localhost:8000/api/confirm?token=%s' % token}
    template = get_template('videolearner/confirmation-email.html')
    msg = EmailMessage(
        'Thank you for registering for videos',
        template.render(ctx),
        'donotreply@manjaywedding.com',
        [email]
    )
    msg.content_subtype = "html"
    msg.send()

    return 'Registration email sent to: %s ' % email


# @periodic_task(run_every=(crontab(minute=0, hour=0)))
def check_subscriptions_renewed():
    accountant = Accountant()
    users = UserProfile.objects.all()
    for user in users:
        if user.subscription and user.subscription.active:
            paid_until = user.subscription.paid_until
            if paid_until < timezone.now():
                accountant.update_subscription(user.subscription)


@periodic_task(run_every=(crontab(minute=0, hour=0, day_of_month='1')))
def assign_badges():
    now = timezone.localtime(timezone.now())
    prev_mth = now + dateutil.relativedelta.relativedelta(months=-1)
    begin = timezone.datetime(year=prev_mth.year, month=prev_mth.month, day=1)
    end = timezone.datetime(year=now.year, month=now.month, day=1)
    begin, end = timezone.make_aware(begin), timezone.make_aware(end)

    badges = Badge.objects.all().order_by('-credits_required')
    multichain_rpc = MultichainRPC()
    users = UserProfile.objects.all()

    # we need to assign a badge for lapsed / inactive subscriptions too, in
    # case the user earned points in this month before the subscription lapsed.
    for user in users:
        try:
            chain_addr = user.chain_address
            total_credits = multichain_rpc.get_credits(
                chain_addr, begin, end)
            # TODO: prevent the badge being given twice if task is rerun
            for badge in badges:
                if badge.credits_required <= total_credits:
                    UserBadge.objects.create(user=user, badge=badge)
                    break
        except Exception as e:
            args = (user, e)
            log.error('Failed to update badges for: %s, exception: %s' % args)


@shared_task
@transaction.atomic
def update_credits(uservideoid):
    # select_for_update ensures that the row is locked while this
    # transaction is taking place.
    uservideo = UserVideo.objects.select_for_update().get(id=uservideoid)
    credits_awarded = uservideo.credits_awarded
    expected_credits = uservideo.expected_credits()

    if expected_credits <= credits_awarded:
        return
    credits_to_award = expected_credits - credits_awarded

    multichain_rpc = MultichainRPC()
    try:
        multichain_rpc.award_credits(
            uservideo.user.chain_address, credits_to_award)
    except InsufficientCreditsException:
        multichain_rpc.refresh_credits()
        update_credits.apply_async(
            (uservideoid, ), countdown=settings.MULTICHAIN_WAITTIME)
        log.error("Failed due to insufficient credits, will retry")
        return
    except MultichainException as e:
        log.error("Failed to issue credits, exception: %s" % e)
        return

    # We assume the transaction immediately confirmed because we own the
    # entire blockchain.
    uservideo.credits_awarded = expected_credits
    uservideo.save()
