from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee

#
# @receiver(post_save, sender=Employee)
# def update_user_names(sender, instance, **kwargs):
#     user = instance.user
#     user.first_name = instance.first_name
#     user.last_name = instance.last_name
#     user.save()