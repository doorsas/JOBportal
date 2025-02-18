from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employee.models import CalendarDay
from datetime import date, timedelta
from django.contrib.auth.models import Group
from employee.utils import generate_users

class Command(BaseCommand):
    help = 'Create Users'

    def handle(self, *args, **kwargs):
        generate_users(20)
        print ('completed')


