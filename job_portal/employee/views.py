from .forms import CVForm, EmployeeRegistrationForm, LoginForm,EmployeeEditForm
from .models import CV, Employee
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect,render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import CalendarDay
from datetime import date, timedelta
from django.http import JsonResponse
from datetime import datetime

# def create_cv(request):
#     if request.method == 'POST':
#         form = CVForm(request.POST)
#         if form.is_valid():
#             cv = form.save(commit=False)
#             cv.employee = request.user.employeeprofile
#             cv.save()
#             return redirect('employee_dashboard')
#     else:
#         form = CVForm()
#     return render(request, 'employee/create_or_edit_cv.html', {'form': form})

def create_or_edit_cv(request):
    employee = get_object_or_404(Employee, user=request.user)
    cv, created = CV.objects.get_or_create(employee=employee)

    if request.method == 'POST':
        form = CVForm(request.POST, instance=cv)
        if form.is_valid():
            form.save()
            return redirect('employee_dashboard')  # Redirect to the employee dashboard or list
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
        'username': request.user.username, 'employee': employee, 'cv':cv } )
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
            return redirect('employee_list')  # Redirect back to list
    else:
        form = EmployeeEditForm(instance=employee)
    return render(request, 'employee/employee_edit.html', {'form': form})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')  # Redirect back to list

def employee_register(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Assign the user to the "Employer" group
            employee_group, created = Group.objects.get_or_create(name='Employee')
            employee_group.user_set.add(user)

            # Create an Employer instance
            Employee.objects.create(
                employee_name=form.cleaned_data['employee_name'],
                email=user.email,
                user=user
            )

            return redirect('employee_dashboard')  # Redirect to login or another page
    else:
        form = EmployeeRegistrationForm()
    return render(request, 'employee/employee_register.html', {'form': form})

@login_required
def employee_list(request):
    # Query all Employee objects from the database
    employees = Employee.objects.all()
    return render(request, 'employee/employee_list.html', {'employees': employees})


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
                    return redirect('employee_dashboard')  # Redirect to Employee dashboard

                # Check if the user has an associated Employer profile
                elif hasattr(user, 'employer'):
                    return redirect('employer_dashboard')  # Redirect to Employer dashboard

                # If neither profile exists, you can add a fallback
                messages.error(request, 'No profile associated with this account.')
                return redirect('home')
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
    return redirect('login_employee')



def generate_pdf(request):
    # Create the HTTP response with the PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="employee_details.pdf"'
    employee = get_object_or_404(Employee, user=request.user)
    # Create the PDF object using ReportLab
    pdf = canvas.Canvas(response)

    # Add content to the PDF
    pdf.drawString(300, 750, "Sutartis")
    pdf.drawString(100, 750, "Employee and CV Details")
    pdf.drawString(100, 720, "Jonas")  # Example, replace with actual data
    pdf.drawString(100, 700, employee.email)
    pdf.drawString(100, 680, "Education: BSc in Computer Science")
    pdf.drawString(100, 660, "Skills: Python, Django")

    # Finalize the PDF
    pdf.showPage()
    pdf.save()

    return response

@login_required
def user_calendar(request):
    # Get all calendar entries for the logged-in user
    today = date.today()
    start_date = today.replace(day=1)  # Start of the current month
    end_date = start_date + timedelta(days=32)  # Go slightly beyond the current month to get all days
    end_date = end_date.replace(day=1) - timedelta(days=1)  # End of the current month

    days = CalendarDay.objects.filter(user=request.user, date__range=(start_date, end_date))

    # Create a dictionary of days for quick lookup
    day_status = {day.date: day.is_free for day in days}

    # Generate a list of all days in the current month
    calendar_days = []
    for day in range(1, end_date.day + 1):
        current_date = start_date.replace(day=day)
        is_free = day_status.get(current_date, True)  # Default to free if no entry exists
        calendar_days.append({'date': current_date, 'is_free': is_free})

    return render(request, 'employee/calendar.html', {'calendar_days': calendar_days})



@login_required
def toggle_day_status(request):
    if request.method == "POST":
        date = request.POST.get('date')  # Date from the frontend
        try:
            # Ensure the date is in YYYY-MM-DD format
            formatted_date = datetime.strptime(date, "%b. %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid date format.'})

        user = request.user
        calendar_day, created = CalendarDay.objects.get_or_create(user=user, date=formatted_date)

        # Toggle the `is_free` status
        calendar_day.is_free = not calendar_day.is_free
        calendar_day.save()

        return JsonResponse({'success': True, 'is_free': calendar_day.is_free})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})