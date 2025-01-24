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
    cv = get_object_or_404(JobPost, pk=pk)
    print (cv)
    return render(request, 'employer/jobpost_detail.html', {'cv': cv})

@login_required
def view_cv(request, cv_id):
    # Fetch the CV using the provided ID
    cv = get_object_or_404(CV, id=cv_id)
    return render(request, "employer/cv_detail.html", {"cv": cv})