from .forms import JobPostForm, EmployerRegistrationForm
from .models import JobPost
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from .models import Employer  # Import the Employer model
from django.shortcuts import get_object_or_404, redirect,render
from django.db.models import Prefetch
from employee.models import CV
from django.views.generic import ListView
from employer.models import JobAgreement  # Update import based on your structure
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from django.utils import timezone



def today(request):
    return {'today': date.today()}

def employer_register(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Assign the user to the "Employer" group
            employer_group, created = Group.objects.get_or_create(name='Employer')
            employer_group.user_set.add(user)

            # Create an Employer instance
            Employer.objects.create(
                company_name=form.cleaned_data['company_name'],
                email=user.email,
                user=user
            )

            return redirect('employer:create_job_post')  # Redirect to login or another page
    else:
        form = EmployerRegistrationForm()
    return render(request, 'employer/employer_register.html', {'form': form})

@login_required
def create_job_post(request):
    employer = get_object_or_404(Employer, user=request.user)

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.employer = employer
            job_post.save()
            return redirect('employer:employer_dashboard')
    else:
        form = JobPostForm()
    return render(request, 'employer/create_job_post.html', {'form': form})

# @login_required
# def employer_job_posts(request):
#     employers = Employer.objects.prefetch_related('jobpost_set').all()
#     return render(request, 'employer/employer_job_posts.html', {'employers': employers})
#


@login_required
def employer_list(request):
    # Query all Employer objects from the database
    employers = Employer.objects.all()
    return render(request, 'employer/employer_list.html', {'employers': employers})

# @login_required
# def employer_dashboard(request):
#     # Query all Employer objects from the database
#     employers = Employer.objects.all()
#     return render(request, 'employer/employer_dashboard.html', {'employers': employers})

@login_required
def employer_dashboard(request):
    # Prefetch job posts for each employer, ordered by created_at
    employers = Employer.objects.prefetch_related(
        Prefetch('jobpost_set', queryset=JobPost.objects.order_by('-created_at'))
    )
    return render(request, 'employer/employer_dashboard1.html', {'employers': employers})

@login_required
def employer_job_posts(request, employer_id):
    employer = get_object_or_404(Employer, id=employer_id)
    print (employer)
    job_posts = JobPost.objects.filter(employer=employer)

    return render(request, 'employer_job_posts.html', {
        'employer': employer,
        'job_posts': job_posts,
    })


@login_required
def employer_job_posts1(request):
    # Ensure the logged-in user is an employer
    try:
        employer = request.user.employer
    except Employer.DoesNotExist:
        return render(request, "employer/error.html", {"message": "You are Employee. You are not authorized to view this page."})

    # Fetch all job posts for this employer
    job_posts = JobPost.objects.filter(employer=employer).prefetch_related('submitted_cvs')

    context = {
        "employer": employer,
        "job_posts": job_posts,
    }
    return render(request, "employer/job_posts.html", context)

@login_required
def jobpost_detail(request, pk):
    print (pk)
    print ('bum')
    job_post = get_object_or_404(JobPost, pk=pk)

    return render(request, 'employer/jobpost_detail.html', {'job_post': job_post})

@login_required
def view_cv(request, cv_id):
    # Fetch the CV using the provided ID
    cv = get_object_or_404(CV, id=cv_id)
    return render(request, "employer/cv_detail.html", {"cv": cv})

@login_required
def agreement_detail(request, agreement_id):
    # Fetch the CV using the provided ID
    agreement = get_object_or_404(JobAgreement, id=agreement_id)
    return render(request, "employer/agreement_detail.html", {"agreement": agreement})




class EmployerAgreementsView(LoginRequiredMixin, ListView):
    model = JobAgreement
    template_name = 'employer/agreements_list.html'
    context_object_name = 'agreements'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        # Check if user has employer profile
        if not hasattr(request.user, 'employer'):
            return render(
                request,
                "employer/error.html",
                {
                    "message": "You are an employee. You are not authorized to view this page."
                },
                status=403  # Forbidden status
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Filter agreements for the current employer
        return JobAgreement.objects.filter(
            employer=self.request.user.employer
        ).select_related('employee').order_by('-start_date')



def create_job_agreement_from_post(request, job_post_id):
    job_post = get_object_or_404(JobPost, id=job_post_id)



    # Ensure the request user is the employer who created the job post
    if request.user != job_post.employer.user:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('employer:job_post_list')  # Redirect to job post list or another appropriate page

    # Check if an agreement already exists for this job post
    if JobAgreement.objects.filter(job_post=job_post).exists():
        messages.warning(request, "An agreement already exists for this job post.")
        return redirect('employer:job_post_list')

    # Create a new JobAgreement
    JobAgreement.objects.create(
        employer=job_post.employer,
        employee=None,  # No employee assigned yet (waiting list)
        job_post=job_post,  # Link to the original job post
        offer_date=timezone.now().date(),
        status='pending',  # Set initial status
    )

    messages.success(request, "Job post moved to agreements waiting list.")
    return redirect('employer:job_agreement_waiting_list')


# def create_job_agreement_from_post(request, job_post_id):
#     job_post = get_object_or_404(JobPost, id=job_post_id)
#
#     if request.user != job_post.employer.user:
#         messages.error(request, "You are not authorized to perform this action.")
#         return redirect('job_post_list')
class JobAgreementWaitingListView(ListView):
    model = JobAgreement
    template_name = 'employer/job_agreement_waiting_list.html'
    context_object_name = 'agreements'

    def get_queryset(self):
        # Filter agreements with no employee assigned (waiting list)
        return JobAgreement.objects.filter(
            employee=None,
            status='pending'
        ).select_related('job_post', 'employer')