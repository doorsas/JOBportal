# employer/admin.py
from django.contrib import admin
from .models import Employer,JobPost,JobAgreement, Payment

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email')  # Customize fields for employer admin
    search_fields = ('company_name', 'email')

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('employer', 'created_at','title')  # Customize fields for employer admin
    search_fields = ('created_at', 'employer','title')

@admin.register(JobAgreement)
class JobAgreementAdmin(admin.ModelAdmin):
    list_display = ('employer', 'created_at')  # Customize fields for employer admin
    search_fields = ('created_at', 'employer')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('employer', 'invoice_date','payment_date','status')  # Customize fields for employer admin
    search_fields = ('invoice_date', 'employer','status')




