from django.urls import path
from . import views
from .views import employer_list, employer_dashboard,create_job_post, employer_job_posts,jobpost_detail, employer_job_posts1

app_name = "employer"

urlpatterns = [
    path('', views.employer_job_posts, name='homeee'),
    path('register/', views.employer_register, name='employer_register'),
    path('employers_list/',employer_list, name='employer_list'),
    path('employers_dashboard/',employer_dashboard, name='employer_dashboard'),
    path('create_job_post/',create_job_post, name='create_job_post'),
    path('employer/<int:employer_id>/job-posts/', employer_job_posts, name='employer_job_posts'),
    path('employer/job-posts/<int:pk>/', jobpost_detail, name='jobpost_detail'),
    path('job-posts/', views.employer_job_posts1, name='employer_job_posts1'),
    path('cv/<int:cv_id>/', views.view_cv, name='view_cv'),

]











