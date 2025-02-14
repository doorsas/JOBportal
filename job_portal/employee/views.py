from .forms import CVForm, EmployeeRegistrationForm, LoginForm,EmployeeEditForm
from .models import CV, Employee, JobApplication, Payment
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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from .forms import PaymentFilterForm
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect
from .forms import EmployeeRegistrationForm
from .models import Employee

User = get_user_model()



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
    try:
        employee = get_object_or_404(Employee, user=request.user)
        cv = CV.objects.filter(employee=employee).first()
        return render(request, 'employee/home.html', {
            'username': request.user.username,
            'employee': employee,
            'cv': cv
        })
    except Http404:
        return render(request, 'employee/home.html', {
            'username': request.user.username
        })
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return render(request, 'employee/home.html', {
            'username': request.user.username,
            'error': 'An unexpected error occurred.'
        })


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
            user = form.save()  # Creates user but doesn't log them in

            # Generate confirmation token
            token = generate_confirmation_token(user.email)
            confirmation_link = request.build_absolute_uri(
                f"/employee/confirm-email/{token}/"
            )

            # Send email
            send_mail(
                'Confirm Your Email',
                f'Click to confirm: {confirmation_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return redirect('employee:registration_pending')
    else:
        form = EmployeeRegistrationForm()

    return render(request, 'employee/employee_register.html', {'form': form})

def registration_failed(request):
    return render(request, 'employee/registration_failed.html')


def confirm_email(request, token):
    email = confirm_token(token)
    if email:
        try:
            user = User.objects.get(email=email)
            employee = user.employee
            employee.is_email_verified = True
            employee.save()
            messages.success(request, 'Email confirmed! You may now login.')
            return redirect('employee:login_employee')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    else:
        messages.error(request, 'Invalid or expired link.')
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

            user = authenticate(username=username, password=password)

            if user is not None:
                if hasattr(user, 'employee'):
                    if not user.employee.is_email_verified:
                        messages.error(request, 'Verify your email first.')
                        return redirect('employee:login_employee')

                    login(request, user)
                    return redirect('employee:home')

                # Handle other user types
            else:
                messages.error(request, 'Invalid credentials.')
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
    print (job)

    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to apply for a job.")
        return redirect('login')

    try:
        employee = request.user.employee
        cv = employee.cv
        print (cv)
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
        calendar = Calendar.objects.get(user=request.user)
    except ObjectDoesNotExist:
        calendar, created = Calendar.objects.get_or_create(user=request.user)
        if created:
            print('Kalendorius sukurtas')

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




class EmployeePaymentsView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'employee/payments_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Payment.objects.filter(employee=self.request.user.employee).order_by('-invoice_date')
        form = PaymentFilterForm(self.request.GET)

        if form.is_valid():
            min_amount = form.cleaned_data.get('min_amount')
            max_amount = form.cleaned_data.get('max_amount')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if min_amount is not None:
                queryset = queryset.filter(amount__gte=min_amount)
            if max_amount is not None:
                queryset = queryset.filter(amount__lte=max_amount)
            if start_date is not None:
                queryset = queryset.filter(invoice_date__gte=start_date)
            if end_date is not None:
                queryset = queryset.filter(invoice_date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = PaymentFilterForm(self.request.GET)
        return context



