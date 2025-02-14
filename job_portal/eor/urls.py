from django.urls import path
from . import views


app_name = "eor"

urlpatterns = [
    # Pvz., pagrindinis EOR puslapis
    path('', views.eor_dashboard, name='eor_dashboard'),
    path('assignments/', views.employee_assignment_list, name='employee_assignment_list'),
    path('cv/', views.employee_cv_list, name='employee_cv_list'),
]