# employee/admin.py
from django.contrib import admin
from .models import Employee



@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'email')  # Customize fields for employee admin
    search_fields = ('emplyee_name', 'email')
    list_filter = ('email',)  # Add filtering options

