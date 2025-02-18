from django.urls import path
from . import views

from .views import EmployeeRegistrationView




app_name = 'employee'

urlpatterns = [
    # Authentication
    path('', views.index, name="index"),
    path('search/', views.search, name="search"),
    # path('', views.login_employee, name='login_employee'),
    path('logout/', views.logout_employee, name='logout'),

    # Employee Registration & Dashboard
    path('register/', EmployeeRegistrationView.as_view(), name='employee_register'),
    path('registration-pending/', views.registration_pending, name='registration_pending'),
    path('registration-failed/', views.registration_failed, name='registration_failed'),
    path('employees_dashboard/', views.employee_dashboard, name='employee_dashboard'),

    # Employee Management
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employee/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    # CV Management
    path('cv/<int:pk>/', views.cv_detail, name='cv_detail'),
    path('cv/edit/', views.create_or_edit_cv, name='create_or_edit_cv'),
    path('submit-cv/<int:job_id>/', views.submit_cv, name='submit_cv'),

    # Calendar & Bookings
    path('calendar/', views.user_calendar, name='user_calendar'),
    path('calendar/toggle-booking/<str:date_str>/', views.toggle_booking, name='toggle_booking'),
    path('toggle-day-status/', views.toggle_day_status, name='toggle_day_status'),

    # Email Confirmation
    path('confirm-email/<str:token>/', views.confirm_email, name='confirm_email'),

    # Applications & Payments
    path('my-applications/', views.employee_applications, name='employee_applications'),
    path('payments/', views.EmployeePaymentsView.as_view(), name='payments'),

    # PDF Generation
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),

    # Home
    path('home/', views.home, name='home'),
]
