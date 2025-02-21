from django.urls import path
from . import views


app_name = "eor"

urlpatterns = [
    # Pvz., pagrindinis EOR puslapis
    path('', views.eor_dashboard, name='eor_dashboard'),
    path('assignments/', views.employee_assignment_list, name='employee_assignment_list'),
    path('cv/', views.employee_cv_list, name='employee_cv_list'),
    path("contracts/", views.contract_list, name="contract_list"),
    path("charts/", views.net_profit_chart, name="net_profit_chart"),
    path('employee/contracts/', views.employee_contracts, name='employee_contracts'),
    path('employer/contracts/', views.employer_contracts, name='employer_contracts'),
    path('manager/contracts/', views.manager_contracts, name='manager_contracts'),


]