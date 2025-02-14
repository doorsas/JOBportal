from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employee.models import CalendarDay
from datetime import date, timedelta
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create Groups'

    def handle(self, *args, **kwargs):
        Group.objects.get_or_create(name='Employer')
        Group.objects.get_or_create(name='Employee')
        Group.objects.get_or_create(name='Manager')



