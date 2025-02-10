from django.urls import path
from . import views
from .views import EmployeePaymentsView


app_name = 'employee'

urlpatterns = [
    path('', views.login_employee, name='login_employee'),
    path('home/', views.home, name='home'),
    path('register/', views.employee_register, name='employee_register'),
    path('employees_dashboard/',views.employee_dashboard, name='employee_dashboard'),
    path('logout/', views.logout_employee, name='logout'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/', views.employee_list, name='employee_list'),
    path('cv/<int:pk>/', views.cv_detail, name='cv_detail'),
    path('cv/edit/', views.create_or_edit_cv, name='create_or_edit_cv'),
    path('employee/<int:employee_pk>/', views.employee_detail, name='employee_detail'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    # path('calendar/', views.user_calendar, name='user_calendar'),
    path('toggle-day-status/', views.toggle_day_status, name='toggle_day_status'),
    path('submit-cv/<int:job_id>/', views.submit_cv, name='submit_cv'),
    path('calendar/toggle-booking/<str:date_str>/', views.toggle_booking, name='toggle_booking'),
    path('calendar/', views.user_calendar, name='user_calendar'),
    path('confirm-email/<str:token>/', views.confirm_email, name='confirm_email'),
    path('registration-pending/', views.registration_pending, name='registration_pending'),
    path('registration-failed/', views.registration_failed, name='registration_failed'),
    path('my-applications/', views.employee_applications, name='employee_applications'),
    path('payments/', EmployeePaymentsView.as_view(), name='payments'),

]





