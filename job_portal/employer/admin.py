# employer/admin.py
from django.contrib import admin
from .models import Employer

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email')  # Customize fields for employer admin
    search_fields = ('company_name', 'email')