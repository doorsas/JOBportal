from django.urls import path
from . import views
from .views import employer_list, employer_dashboard,create_job_post,\
    create_job_agreement_from_post,employer_job_posts,jobpost_detail,\
    JobAgreementWaitingListView,employer_job_posts1,EmployerAgreementsView

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
    path('agreements/', EmployerAgreementsView.as_view(), name='employer_agreements'),
    path('job-posts/<int:job_post_id>/create-agreement/', create_job_agreement_from_post, name='create_job_agreement'),
    path('agreements/waiting-list/', JobAgreementWaitingListView.as_view(), name='job_agreement_waiting_list'),
    path('agreements/<int:agreement_id>/', views.agreement_detail, name='agreement_detail'),
    path('employer/agreements/', views.employer_job_agreements, name='employer-agreements'),
    path('employee/agreements/', views.employee_job_agreements, name='employee-agreements'),




]












