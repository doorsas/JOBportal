from django.contrib import admin

from .models import EmployeeAssignment, Manager, DirectAgreements, Contract


@admin.register(EmployeeAssignment)
class EmployeeAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'employer',
        'employee',
        'job_post',
        'cv',
        'start_date',
        'end_date',
        'status',
        'employer_payment',
        'employee_salary',
        'manager_commission',
    )
    list_filter = (
        'employer',
        'employee',
        'job_post',
        'cv',
        'start_date',
        'end_date',
    )


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'manager',
        'manager_name',
        'manager_surname',
        'employer',
        'employee',
        'work_start_date',
        'work_end_date',
        'document',
        'employee_bonus_percentage',
        'employer_bonus_percentage',
    )
    list_filter = (
        'manager',
        'employer',
        'employee',
        'work_start_date',
        'work_end_date',
    )


@admin.register(DirectAgreements)
class DirectAgreementsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'employer',
        'employee',
        'start_date',
        'amount',
        'manager',
    )
    list_filter = ('employer', 'employee', 'start_date', 'manager')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'employee',
        'employer',
        'manager',
        'employee_tariff_type',
        'employee_hourly_rate',
        'employee_daily_rate',
        'employer_tariff_type',
        'employer_hourly_rate',
        'employer_daily_rate',
        'manager_commission',
        'start_date',
        'end_date',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'employee',
        'employer',
        'manager',
        'start_date',
        'end_date',
        'created_at',
        'updated_at',
    )
    date_hierarchy = 'created_at'
