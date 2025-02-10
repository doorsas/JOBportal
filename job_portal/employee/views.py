from .forms import CVForm, EmployeeRegistrationForm, LoginForm,EmployeeEditForm
from .models import CV, Employee, JobApplication
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import CalendarDay
from datetime import date, timedelta
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Calendar, Booking
from django.views.decorators.csrf import csrf_exempt
# from django.utils.dateparse import parse_date
from dateutil.parser import parse as parse_date
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from .utils import generate_confirmation_token, confirm_token
from django.views.decorators.csrf import csrf_protect
from employer.models import JobPost




@login_required
def create_or_edit_cv(request):
    employee = get_object_or_404(Employee, user=request.user)
    cv, created = CV.objects.get_or_create(employee=employee)

    if request.method == 'POST':
        form = CVForm(request.POST,request.FILES, instance=cv)
        if form.is_valid():
            form.save()
            return redirect('employer:employer_dashboard')  # Redirect to the employee dashboard or list
    else:
        form = CVForm(instance=cv)

    return render(request, 'employee/create_or_edit_cv.html', {'form': form})

@login_required
def cv_detail(request, pk):
    cv = get_object_or_404(CV, pk=pk)
    return render(request, 'employee/cv_detail.html', {'cv': cv})


@login_required
def home(request):
    cv = None
    employee = None
    try :
        employee = get_object_or_404(Employee, user=request.user)
        cv = get_object_or_404(CV, employee=employee)
        return render(request, 'employee/home.html', {
        'username': request.user.username, 'employee':employee, 'cv':cv })
    except :
        return render(request, 'employee/home.html', {
        'username': request.user.username} )


@login_required
def employee_detail(request, employee_pk):
    # Get the Employee instance
    employee = get_object_or_404(Employee, pk=employee_pk)

    # Check if a CV exists for the employee
    try:
        cv = CV.objects.get(employee=employee)
    except CV.DoesNotExist:
        cv = None

    # Pass both the employee and CV (if exists) to the template
    return render(request, 'employee/detail.html', {
        'employee': employee,
        'cv': cv,
    })


@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee:home')  # Redirect back to list
    else:
        form = EmployeeEditForm(instance=employee)
    return render(request, 'employee/employee_edit.html', {'form': form})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee:home')  # Redirect back to list




@csrf_protect
def employee_register(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            # Create a new User object
            user = User.objects.create_user(
                username=form.cleaned_data['email'],  # Use email as the username
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']  # Assuming the form has password fields
            )

            # Assign the user to the "Employee" group
            employee_group, created = Group.objects.get_or_create(name='Employee')
            employee_group.user_set.add(user)

            # Create an Employee instance
            employee = Employee.objects.create(
                employee_name=form.cleaned_data['employee_name'],
                email=user.email,
                user=user,
                phone_number = form.cleaned_data['phone_number'],
                is_email_verified=False  # Email is not verified yet
            )

            # Generate a confirmation token
            token = generate_confirmation_token(employee.email)

            # Send confirmation email
            confirmation_link = request.build_absolute_uri(
                f"/employee/confirm-email/{token}/"
            )
            send_mail(
                'Confirm Your Email',
                f'Please click the link below to confirm your email and registration to Drekar:\n\n{confirmation_link}',
                settings.DEFAULT_FROM_EMAIL,
                [form.cleaned_data['email']],
                fail_silently=False,
            )

            # Redirect to a "pending confirmation" page
            return redirect('employee:registration_pending')
    else:
        form = EmployeeRegistrationForm()

    return render(request, 'employee/employee_register.html', {'form': form})

def registration_failed(request):
    return render(request, 'employee/registration_failed.html')


def confirm_email(request, token):
    print (token)
    email = confirm_token(token)
    if email:
        employee = Employee.objects.get(email=email)
        employee.is_email_verified = True
        employee.save()
        messages.success(request, 'Your email has been confirmed!')
        return redirect('employee:home')  # Redirect to the home page or login page
    else:
        messages.error(request, 'Invalid or expired confirmation link.')
        return redirect('employee:registration_failed')

@login_required
def employee_list(request):
    # Query all Employee objects from the database
    employees = Employee.objects.all()
    return render(request, 'employee/employee_list.html', {'employees': employees})

def registration_pending(request):
    return render(request, 'employee/registration_pending.html')

@login_required
def employee_dashboard(request):
    # Query all Employer objects from the database
    employees = Employee.objects.all()
    return render(request, 'employee/employee_dashboard.html', {'employees': employees})

def login_employee(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'You are now logged in.')

                # Check if the user has an associated Employee profile
                if hasattr(user, 'employee'):
                    return redirect('employer:employer_dashboard')  # Redirect to Employee dashboard

                # Check if the user has an associated Employer profile
                elif hasattr(user, 'employer'):
                    return redirect('employer:create_job_post')  # Redirect to Employer dashboard

                # If neither profile exists, you can add a fallback
                messages.error(request, 'No profile associated with this account.')
                return redirect('employee:home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'employee/login_employee.html', {'form': form})

# Logout view
@login_required
def logout_employee(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('employee:login_employee')


@login_required
def generate_pdf(request):
    # Create the HTTP response with the PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="employee_details.pdf"'
    employee = get_object_or_404(Employee, user=request.user)
    # Create the PDF object using ReportLab
    pdf = canvas.Canvas(response)

    # Add content to the PDF
    pdf.drawString(250, 750, "Sutartis  Vilnius 2025 ")
    pdf.drawString(100, 720, "Employee and CV Details")
    pdf.drawString(100, 700, employee.employee_name)  # Example, replace with actual data
    pdf.drawString(100, 680, employee.email)
    pdf.drawString(100, 660, "Education: BSc in Computer Science")
    pdf.drawString(100, 640, "Skills: Python, Django")

    # Finalize the PDF
    pdf.showPage()
    pdf.save()

    return response

# @login_required
# def user_calendar(request):
#     # Get all calendar entries for the logged-in user
#     today = date.today()
#     start_date = today.replace(day=1)  # Start of the current month
#     end_date = start_date + timedelta(days=32)  # Go slightly beyond the current month to get all days
#     end_date = end_date.replace(day=1) - timedelta(days=1)  # End of the current month
#
#     days = CalendarDay.objects.filter(user=request.user, date__range=(start_date, end_date))
#
#     # Create a dictionary of days for quick lookup
#     day_status = {day.date: day.is_free for day in days}
#
#     # Generate a list of all days in the current month
#     calendar_days = []
#     for day in range(1, end_date.day + 1):
#         current_date = start_date.replace(day=day)
#         is_free = day_status.get(current_date, True)  # Default to free if no entry exists
#         calendar_days.append({'date': current_date, 'is_free': is_free})
#
#     return render(request, 'employee/calendar.html', {'calendar_days': calendar_days})



@login_required
@csrf_exempt
def toggle_day_status(request):
    if request.method == "POST":
        date = request.POST.get('date')
        print (date)

        if not date:
            return JsonResponse({'success': False, 'error': 'Date not provided'})

        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid date format'})

        try:
            # Use `filter()` and handle duplicates if any remain
            day = CalendarDay.objects.get(date=parsed_date)
            print (day)
            day.is_free = not day.is_free
            day.save()
            return JsonResponse({'success': True, 'is_free': day.is_free})
        except CalendarDay.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Day not found'})
        except CalendarDay.MultipleObjectsReturned:
            return JsonResponse({'success': False, 'error': 'Duplicate entries found. Please fix the database.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
def submit_cv(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)

    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to apply for a job.")
        return redirect('login')

    try:
        employee = request.user.employee
        cv = employee.cv
    except Employee.DoesNotExist:
        messages.error(request, "You must be an employee to apply for a job.")
        return redirect('employer:employer_dashboard')
    except CV.DoesNotExist:
        messages.error(request, "You must have a CV to apply for a job.")
        return redirect('employee:create_or_edit_cv')

    # Check if the employee has already applied for this job
    if JobApplication.objects.filter(job_post=job, employee=employee).exists():
        messages.warning(request, "You have already applied for this job.")
    else:
        JobApplication.objects.create(job_post=job, employee=employee, cv=cv)
        messages.success(request, f"You have successfully applied for {job.title}.")

    return redirect('employer:employer_dashboard')


@csrf_exempt
def toggle_booking(request, date_str):
    if request.method == 'POST':
        try:
            # Attempt to parse the date string into a date object
            date_obj = parse_date(date_str).date() if parse_date(date_str) else None
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        if not date_obj:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        calendar = get_object_or_404(Calendar, user=request.user)
        booking, created = Booking.objects.get_or_create(calendar=calendar, date=date_obj)

        # Toggle booking status
        booking.is_booked = not booking.is_booked
        print (booking.is_booked)
        booking.save()

        total_booked = calendar.bookings.filter(is_booked=True).count()

        return JsonResponse({'status': 'success', 'is_booked': booking.is_booked, 'date': date_obj.isoformat(),'total_booked':total_booked})

    return JsonResponse({'error': 'Invalid request method'}, status=405)




@login_required
def user_calendar(request):
    try:
        calendar = get_object_or_404(Calendar, user=request.user)
    except:
        calendar = Calendar.objects.get_or_create(user=request.user, dates=dates)
        print ('Kalendorius_sukurtas')

    # Get all dates from the calendar (convert from ISO string to date objects)
    all_dates = [date.fromisoformat(day) for day in calendar.dates]

    # Create a dictionary of bookings (map date to is_booked)
    bookings = {booking.date: booking.is_booked for booking in calendar.bookings.all()}

    # Group dates into weeks
    calendar_weeks = []
    week = []
    for day in all_dates:
        is_booked = bookings.get(day, False)
        week.append({'date': day, 'is_booked': is_booked})
        if len(week) == 7:  # Week has 7 days
            calendar_weeks.append(week)
            week = []
    if week:  # Add any remaining days as the last week
        calendar_weeks.append(week)

    total_booked = calendar.bookings.filter(is_booked=True).count()

    # Pass weeks to the template
    context = {'calendar_weeks': calendar_weeks, 'total_booked':total_booked}
    return render(request, 'employee/calendar.html', context)


@login_required
def employee_applications(request):
    employee = request.user.employee
    applications = JobApplication.objects.filter(employee=employee).select_related('job_post')

    return render(request, 'employee/job_applications.html', {'applications': applications})
