from django.core.signing import Signer, TimestampSigner
from django.urls import reverse
from django.conf import settings
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from django.conf import settings
from faker import Faker
from .models import CustomUser, Payment


fake = Faker()

def generate_users(num):
    for _ in range(num):
        user = CustomUser.objects.create_user(
            username = fake.user_name(),
            email = fake.email(),
            phone_number = fake.phone_number(),
            is_employee = True)
        user.save()

def generate_payments(num):
    for _ in range(num):
        user = Payment.objects.create_user(
                    username=fake.user_name(),
                    email=fake.email(),
                    phone_number=fake.phone_number(),
                    is_employee=True)
        user.save()




        #     email=models.EmailField(unique=True)
        # phone_number = PhoneNumberField(blank=True, null=True)
        # is_employer = models.BooleanField(default=False)
        # is_employee = models.BooleanField(default=False)
        # is_manager = models.BooleanField(default=False)
        # )
        # class Employee(models.Model):
        #     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
        #     citizenship = models.CharField(max_length=100, default="Unknown")
        #     national_id = models.BigIntegerField(blank=True, null=True, unique=True)
        #     receive_special_offers = models.BooleanField(default=False)
        #     is_email_verified = models.BooleanField(default=False)

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