from .forms import CVForm, EmployeeRegistrationForm, LoginForm,EmployeeEditForm
from .models import CV, Employee
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect,render

@login_required
def create_cv(request):
    if request.method == 'POST':
        form = CVForm(request.POST)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.employee = request.user.employeeprofile
            cv.save()
            return redirect('employee_dashboard')
    else:
        form = CVForm()
    return render(request, 'employee/create_cv.html', {'form': form})


@login_required
def home(request):
    return render(request, 'employee/home.html', {'username': request.user.username})

def employee_detail(request,pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employee/employee_detail.html', {'employee': employee})


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
                return redirect('home')  # Redirect to home page or another view
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
