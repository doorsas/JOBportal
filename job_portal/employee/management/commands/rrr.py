from employee.models import CalendarDay
from django.db.models import Count
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = 'Remove duplicate dates'

    def handle(self, *args, **kwargs):
        duplicates = CalendarDay.objects.values('date').annotate(count=Count('id')).filter(count__gt=1)
        for duplicate in duplicates:
            date = duplicate['date']
            entries = CalendarDay.objects.filter(date=date)
            entries.exclude(id=entries.first().id).delete()  # Keep one entry, delete others