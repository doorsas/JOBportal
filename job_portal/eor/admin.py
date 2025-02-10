# employer/admin.py
from django.contrib import admin
from .models import EmployeeAssignment

@admin.register(EmployeeAssignment)
class EmployeeAssignmentAdmin(admin.ModelAdmin):
    list_display = ('employer', 'employee','start_date','status')  # Customize fields for employer admin
    search_fields = ('employer', 'employee')
