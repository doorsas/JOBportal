from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employee.models import CalendarDay
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populate calendar days for all users'

    def handle(self, *args, **kwargs):
        today = date.today()
        start_date = today.replace(day=1)
        end_date = start_date + timedelta(days=32)
        end_date = end_date.replace(day=1) - timedelta(days=1)

        for user in User.objects.all():
            for day in range(1, end_date.day + 1):
                current_date = start_date.replace(day=day)
                CalendarDay.objects.get_or_create(user=user, date=current_date, defaults={'is_free': True})

        self.stdout.write(self.style.SUCCESS('Calendar days populated for all users.'))
