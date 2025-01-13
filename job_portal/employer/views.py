from django.shortcuts import render, redirect
from .forms import JobPostForm, EmployerRegistrationForm
from .models import JobPost
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from .models import Employer  # Import the Employer model

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

            return redirect('employer_dashboard')  # Redirect to login or another page
    else:
        form = EmployerRegistrationForm()
    return render(request, 'employer/employer_register.html', {'form': form})

@login_required
def create_job_post(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.employer = request.user.employerprofile
            job_post.save()
            return redirect('employer_dashboard')
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
    # Query all Employer objects from the database
    employers = Employer.objects.all()
    return render(request, 'employer/employer_dashboard.html', {'employers': employers})