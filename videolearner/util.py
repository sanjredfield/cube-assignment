from django.conf import settings
from itsdangerous import URLSafeTimedSerializer


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='conf_code')


def confirm_token(token):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.loads(token, salt='conf_code')
