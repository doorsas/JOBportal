from django.contrib import admin

from .models import EmployeeAssignment, Manager, DirectAgreements




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
        'employer',
        'employee',
        'work_start_date',
        'work_end_date',
        'document',
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

