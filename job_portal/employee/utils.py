from django.core.signing import Signer, TimestampSigner
from django.urls import reverse
from django.conf import settings

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