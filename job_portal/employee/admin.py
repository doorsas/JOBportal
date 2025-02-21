from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Employee, CV, JobApplication, Payment,CustomUser



# Register CustomUser in Authentication section

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


# Define a custom admin class for CustomUser
class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ('email', 'username', 'is_employer', 'is_employee', 'is_manager', 'is_staff', 'is_active')
    list_filter = ('is_employer', 'is_employee', 'is_manager', 'is_staff', 'is_active')

    # Fields to include in the edit form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'phone_number')}),
        ('Roles', {'fields': ('is_employer', 'is_employee', 'is_manager')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # Fields to include in the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'email', 'username', 'phone_number', 'password1', 'password2', 'is_employer', 'is_employee', 'is_manager'),
        }),
    )

    # Search and ordering
    search_fields = ('email', 'username')
    ordering = ('email',)

    # Since we're using email as USERNAME_FIELD
    filter_horizontal = ('groups', 'user_permissions',)


# Register the CustomUser model with the custom admin class
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