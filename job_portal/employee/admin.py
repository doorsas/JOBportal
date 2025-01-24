# employee/admin.py
from django.contrib import admin
from .models import Employee,CV



@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'email')  # Customize fields for employee admin
    search_fields = ('employee_name', 'email')
    list_filter = ('email',)  # Add filtering options

#
# @admin.register(CV)
# class CVAdmin(admin.ModelAdmin):
#     list_display = ('employee', 'experience')  # Customize fields for employee admin
#     search_fields = ('employee',)
#     list_filter = ('experience',)  # Add filtering options
#
@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('employee', 'name_surname', 'date_and_place_of_birth', 'place_of_residence')
    search_fields = ('employee__employee_name', 'name_surname')
    list_filter = ('civil_status',)

