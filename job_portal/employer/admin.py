# employer/admin.py
from django.contrib import admin
from .models import Employer,JobPost

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email')  # Customize fields for employer admin
    search_fields = ('company_name', 'email')

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('employer', 'created_at')  # Customize fields for employer admin
    search_fields = ('created_at', 'employer')