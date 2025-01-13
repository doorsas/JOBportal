from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_employee, name='login_employee'),
    path('create_cv', views.create_cv, name='create_cv'),
    path('home', views.home, name='home'),
    path('register/', views.employee_register, name='employee_register'),
    path('employees_dashboard/',views.employee_dashboard, name='employee_dashboard'),
    path('logout/', views.logout_employee, name='logout'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/', views.employee_list, name='employee_list'),
]