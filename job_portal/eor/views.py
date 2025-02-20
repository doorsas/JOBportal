
from django.shortcuts import render
from .models import EmployeeAssignment
from employee.models import CV
from .models import Manager
from datetime import date
from django.db.models import Sum

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Contract

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Contract
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Contract

import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64
from django.shortcuts import render
from eor.models import Contract


def net_profit_chart(request):
    contracts = Contract.objects.all()

    contracts_data = [
        {"employer": contract.employer.company_name,
         "net_profit": contract.calculate_salary_and_expenses()["net_profit"]}
        for contract in contracts
    ]

    df = pd.DataFrame(contracts_data)
    net_profit_per_employer = df.groupby("employer")["net_profit"].sum().reset_index()
    net_profit_per_employer = net_profit_per_employer.sort_values(by="net_profit", ascending=False)

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.barh(net_profit_per_employer["employer"], net_profit_per_employer["net_profit"])
    plt.xlabel("Net Profit (€)")
    plt.ylabel("Employer")
    plt.title("Net Profit Per Employer")
    plt.gca().invert_yaxis()
    plt.grid(axis="x", linestyle="--", alpha=0.7)

    # Save plot to a string buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode plot to display in HTML
    graphic = base64.b64encode(image_png).decode("utf-8")
    return render(request, "eor/net_profit_chart.html", {"graphic": graphic})


@login_required
def contract_list(request):
    """
    View to display all contracts with detailed earnings and expenses calculation.
    """
    contracts = Contract.objects.all().order_by("-start_date")

    contract_reports = []
    for contract in contracts:
        report_data = contract.calculate_salary_and_expenses()
        contract_reports.append({"contract": contract, "report": report_data})

    return render(request, "eor/contracts_list.html", {"contract_reports": contract_reports})

def employee_assignment_list(request):
    assignments = EmployeeAssignment.objects.all()
    return render(request, 'eor/employee_assignment_list.html', {'assignments': assignments})

def employee_cv_list(request):
    cvs = CV.objects.all()
    return render(request, 'eor/employee_cv_list.html', {'cvs': cvs})

def eor_dashboard(request):
    return render(request, 'eor/dashboard.html')


def calculate_earnings(self, start_date=None, end_date=None):

    employer_payments = self.employer.employer_payments.filter(date__range=(start_date, end_date)).aggregate(total_employer_payment=Sum('amount'))['total_employer_payment'] or 0
    employee_payments = self.employee.employee_payments.filter(date__range=(start_date, end_date)).aggregate(total_employee_payment=Sum('amount'))['total_employee_payment'] or 0

    employer_bonus = employer_payments * (self.employer_bonus_percentage / 100)
    employee_bonus = employee_payments * (self.employee_bonus_percentage / 100)

    total_earnings = employer_bonus + employee_bonus

    return total_earnings

# manager = Manager.objects.get(pk=1)  # Replace 1 with the actual manager's ID
# start_date = date(2023, 1, 1)
# end_date = date(2023, 12, 31)
# earnings = manager.calculate_earnings(start_date, end_date)
# print(f"Manager {manager.name} earned: {earnings}")

def calculate_manager_earnings(manager, start_date=None, end_date=None):
    """
    Calculate earnings for a manager based on the difference between
    employer payments and employee payments for their managed relationships.

    Args:
        manager: Manager model instance
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering

    Returns:
        Dictionary containing earnings breakdown and total
    """
    # Get all employer-employee relationships for this manager
    relationships = manager.managed_relationships.all()

    earnings_breakdown = []
    total_earnings = Decimal('0.00')

    for relationship in relationships:
        # Get employer payments
        employer_payments = relationship.employer.payments.filter(
            status='paid'
        )
        if start_date:
            employer_payments = employer_payments.filter(date__gte=start_date)
        if end_date:
            employer_payments = employer_payments.filter(date__lte=end_date)

        employer_total = employer_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        # Get employee payments
        employee_payments = relationship.employee.payments.filter(
            status='paid'
        )
        if start_date:
            employee_payments = employee_payments.filter(date__gte=start_date)
        if end_date:
            employee_payments = employee_payments.filter(date__lte=end_date)

        employee_total = employee_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        # Calculate difference (manager earnings)
        difference = employer_total - employee_total

        earnings_breakdown.append({
            'employer': relationship.employer,
            'employee': relationship.employee,
            'employer_payments': employer_total,
            'employee_payments': employee_total,
            'earnings': difference
        })

        total_earnings += difference

    return {
        'breakdown': earnings_breakdown,
        'total_earnings': total_earnings
    }


def calculate_employee_profit(employee, start_date=None, end_date=None):
    """
    Calculate profit generated by an employee based on the difference between
    what employers are charged and what the employee is paid.

    Args:
        employee: Employee model instance
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering

    Returns:
        Dictionary containing profit details
    """
    # Get all payments received from employers for this employee
    employer_payments = employee.employer_set.all().values_list(
        'payments', flat=True
    ).filter(status='paid')

    if start_date:
        employer_payments = employer_payments.filter(date__gte=start_date)
    if end_date:
        employer_payments = employer_payments.filter(date__lte=end_date)

    total_employer_payments = employer_payments.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')

    # Get all payments made to the employee
    employee_payments = employee.payments.filter(status='paid')

    if start_date:
        employee_payments = employee_payments.filter(date__gte=start_date)
    if end_date:
        employee_payments = employee_payments.filter(date__lte=end_date)

    total_employee_payments = employee_payments.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')

    # Calculate profit
    profit = total_employer_payments - total_employee_payments

    return {
        'total_employer_payments': total_employer_payments,
        'total_employee_payments': total_employee_payments,
        'profit': profit,
        'profit_margin': (profit / total_employer_payments * 100) if total_employer_payments else 0
    }