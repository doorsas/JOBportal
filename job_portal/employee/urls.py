from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_employee, name='login_employee'),
    path('home/', views.home, name='home'),
    path('register/', views.employee_register, name='employee_register'),
    path('employees_dashboard/',views.employee_dashboard, name='employee_dashboard'),
    path('logout/', views.logout_employee, name='logout'),
    # path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/', views.employee_list, name='employee_list'),
    path('cv/<int:pk>/', views.cv_detail, name='cv_detail'),
    path('cv/edit/', views.create_or_edit_cv, name='create_or_edit_cv'),
    path('employee/<int:employee_pk>/', views.employee_detail, name='employee_detail'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('calendar/', views.user_calendar, name='user_calendar'),
    path('toggle-day-status/', views.toggle_day_status, name='toggle_day_status'),
]