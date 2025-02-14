from django.core.signing import Signer, TimestampSigner
from django.urls import reverse
from django.conf import settings
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from django.conf import settings

def generate_confirmation_token(email):
    signer = TimestampSigner()
    return signer.sign(email)

def confirm_token(token, max_age=86400):  # 86400 seconds = 1 day
    signer = TimestampSigner()
    try:
        email = signer.unsign(token, max_age=max_age)
    except:
        return None
    return email


# def generate_confirmation_token(email, expiration=3600):
#     s = Serializer(settings.SECRET_KEY, expiration)
#     return s.dumps({'email': email}).decode('utf-8')
#
# def confirm_token(token):
#     s = Serializer(settings.SECRET_KEY)
#     try:
#         data = s.loads(token)
#     except:
#         return None
#     return data.get('email')