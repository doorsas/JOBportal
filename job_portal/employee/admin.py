from django.contrib import admin
from .models import Employee,CV,JobApplication,Payment

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_name','user', 'email')  # Customize fields for employee admin
    search_fields = ('employee_name', 'email')
    list_filter = ('email',)  # Add filtering options

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name_surname', 'date_and_place_of_birth', 'place_of_residence')
    search_fields = ('employee__employee_name', 'name_surname')
    list_filter = ('civil_status',)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'status')  # Customize fields for employer admin
    search_fields = ('created_at', 'status')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'mokejimo_tipas','amount', 'payment_date')  # Customize fields for employer admin
    search_fields = ('created_at', 'mokejimo_tipas')