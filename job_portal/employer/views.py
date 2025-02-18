from .forms import JobPostForm, EmployerRegistrationForm,JobAgreementStatusForm
from .models import JobPost
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from .models import Employer  # Import the Employer model
from django.shortcuts import get_object_or_404, redirect,render
from django.db.models import Prefetch
from employee.models import CV
from eor.models import EmployeeAssignment
from employer.models import JobAgreement  # Update import based on your structure
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from django.utils import timezone
from django import forms
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from employer.models import JobPost,Payment
from employee.models import JobApplication
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect




def today(request):
    return {'today': date.today()}

@csrf_protect
def employer_register(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            employer_group, created = Group.objects.get_or_create(name='Employer')
            employer_group.user_set.add(user)
        else:
            print(form.errors)
        return redirect('employer:employer_dashboard')  # Redirect to login page after successful registration
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
            return redirect('employer:employer_job_posts1')
    else:
        form = JobPostForm()
    return render(request, 'employer/create_job_post.html', {'form': form})


@login_required
def employer_list(request):
    # Query all Employer objects from the database
    employers = Employer.objects.all()
    return render(request, 'employer/employer_list.html', {'employers': employers})


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
    except AttributeError:
        return render(request, "employer/error.html", {"message": "You are not authorized to view this page."})

    # Fetch all job posts for this employer
    job_posts = JobPost.objects.filter(employer=employer).prefetch_related('applications')

    # Fetch all applications related to the employer's job posts
    job_applications = JobApplication.objects.filter(job_post__in=job_posts).select_related('employee', 'cv')

    context = {
        "employer": employer,
        "job_posts": job_posts,
        "job_applications": job_applications,
    }
    return render(request, "employer/job_posts.html", context)


@login_required
def cv_detail(request, pk):
    cv = get_object_or_404(CV, pk=pk)
    return render(request, 'employer/cv_detail.html', {'cv': cv})


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



class EmployerPaymentsView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'employer/payments_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        # Ensure user is an employer
        if not hasattr(request.user, 'employer'):
            return render(
                request,
                "employer/error.html",
                {
                    "message": "You are not authorized to view this page."
                },
                status=403  # Forbidden status
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Get payments related to the logged-in employer
        return Payment.objects.filter(
            employer=self.request.user.employer
        ).order_by('-invoice_date')


@login_required
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



@login_required
def employer_job_agreements(request):
    if not hasattr(request.user, 'employer'):
        return HttpResponseForbidden("You are not an employer.")

    employer = request.user.employer
    agreements = JobAgreement.objects.filter(employer=employer)
    return render(request, 'employer/job_agreements.html', {
        'agreements': agreements
    })

@login_required
def employee_job_agreements(request):
    if not hasattr(request.user, 'employee'):
        return HttpResponseForbidden("You are not an employee.")

    employee = request.user.employee
    agreements = JobAgreement.objects.filter(employee=employee)

    if request.method == 'POST':
        agreement_id = request.POST.get('agreement_id')
        agreement = get_object_or_404(JobAgreement, id=agreement_id)

        if agreement.employee != employee:
            return HttpResponseForbidden()

        form = JobAgreementStatusForm(request.POST, instance=agreement)
        if form.is_valid():
            updated_agreement = form.save(commit=False)
            updated_agreement.modification_date = timezone.now().date()
            updated_agreement.save()

    # Prepare forms for all agreements
    agreement_forms = []
    for agreement in agreements:
        agreement_forms.append({
            'agreement': agreement,
            'form': JobAgreementStatusForm(instance=agreement)
        })

    return render(request, 'employee/job_agreements.html', {
        'agreement_forms': agreement_forms
    })

@login_required
def cv_detail_accept(request, pk):
    cv = get_object_or_404(CV, pk=pk)
    return render(request, 'employer/cv_detail.html', {'cv': cv})



@login_required
def register_match(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id)
    employee = cv.employee
    employer = get_object_or_404(Employer, user=request.user)

    # Fetch job post that the CV was matched for (if applicable)
    job_post = JobPost.objects.filter(employer=employer).first()  # Adjust logic as needed

    existing_assignment = EmployeeAssignment.objects.filter(
        employer=employer,
        employee=employee,
        job_post=job_post,
        cv = cv,
        status='active'
    ).first()

    context = {
        "employer": employer,
        "employee": employee,
        "cv": cv,
        "job_post": job_post,  # Ensure this is passed to the template
        "existing_assignment": existing_assignment,
    }
    return render(request, "employer/register_match.html", context)


@login_required
def confirm_match(request, cv_id, job_post_id):
    cv = get_object_or_404(CV, id=cv_id)
    employee = cv.employee
    employee_id = cv.employee

    employer = get_object_or_404(Employer, user=request.user)
    job_post = get_object_or_404(JobPost, id=job_post_id)

    # Check if an active assignment already exists
    existing_assignment = EmployeeAssignment.objects.filter(
        employer=employer,
        employee=employee,
        job_post=job_post,
        cv = cv,
        status='active'
    ).first()

    if not existing_assignment:
        # Create a new assignment
        EmployeeAssignment.objects.create(
            employer=employer,
            employee=employee,
            job_post=job_post,
            cv=cv
        )

    if not JobApplication.objects.filter(employee=employee, job_post=job_post,cv=cv).exists():
        JobApplication.objects.create(employee=employee, job_post=job_post, cv=cv)
    else:
        try:
            application = JobApplication.objects.get(employee=employee,cv=cv, job_post=job_post)
            application.status = 'accepted'  # Change to the desired status (e.g., 'reviewed', 'accepted', 'rejected')
            # Step 3: Save the instance
            application.save()

        except:
            print(f"Updated status of {application} to {application.status}")



    return redirect('employer:match_success')


def match_success(request):
    return render(request, "employer/match_success.html")