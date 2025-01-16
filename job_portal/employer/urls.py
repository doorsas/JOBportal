from django.urls import path
from . import views
from .views import employer_list, employer_dashboard,create_job_post
import os

urlpatterns = [
    path('', views.create_job_post, name='homee'),
    path('register/', views.employer_register, name='employer_register'),
    path('employers_list/',employer_list, name='employer_list'),
    path('employers_dashboard/',employer_dashboard, name='employer_dashboard'),
    path('create_job_post/',create_job_post, name='create_job_post'),
    path('employers/job-posts/', views.employer_job_posts, name='employer_job_posts'),


]






