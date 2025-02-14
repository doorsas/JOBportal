from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Employee, CV, JobApplication, Payment

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_employer', 'is_employee', 'is_manager', 'is_staff', 'is_superuser')
    list_filter = ('is_employer', 'is_employee', 'is_manager', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets +(
        ('Roles', {'fields': ('is_employer', 'is_employee', 'is_manager')}),
    )

# Register CustomUser in Authentication section
admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user__first_name', 'user__last_name','user', 'citizenship', 'national_id', 'user__phone_number')
    search_fields = ('user__first_name', 'user__last_name', 'national_id')

@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('employee', 'place_of_birth', 'place_of_residence')
    search_fields = ('employee__user__first_name', 'employee__user__last_name')
    list_filter = ('civil_status',)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'status')
    search_fields = ('created_at', 'status')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'mokejimo_tipas', 'amount', 'payment_date')
    search_fields = ('created_at', 'mokejimo_tipas')