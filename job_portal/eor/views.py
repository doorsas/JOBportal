
from django.shortcuts import render
from .models import EmployeeAssignment

def employee_assignment_list(request):
    assignments = EmployeeAssignment.objects.all()
    return render(request, 'eor/employee_assignment_list.html', {'assignments': assignments})

def eor_dashboard(request):
    return render(request, 'eor/dashboard.html')