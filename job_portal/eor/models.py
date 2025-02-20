from employer.models import Employer, JobPost, Payment
from employee.models import Employee, CV, Payment
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.conf import settings

User = get_user_model()


class EmployeeAssignment(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    job_post = models.ForeignKey(JobPost,null=True, blank=True, on_delete=models.CASCADE)  # Track the job post
    cv = models.ForeignKey(CV,null=True, blank=True,on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[('active', 'Active'), ('completed', 'Completed')],
        default='active'
    )
    employer_payment = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, help_text="Amount employer pays for the assignment")
    employee_salary = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, help_text="Amount paid to the employee")
    manager_commission = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True, help_text="Commission earned by the manager", default=0)

    def calculate_profit(self):
        """
        Profit = Employer Payment - (Employee Salary + Manager Commission)
        """
        return self.employer_payment - (self.employee_salary + self.manager_commission)

    def __str__(self):
        return f"{self.employee} assigned to {self.employer}"


class Manager(models.Model):
    manager  = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    manager_name = models.CharField(max_length=255)
    manager_surname = models.CharField(max_length=255)
    employer = models.ForeignKey(Employer,blank=True, null=True, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, blank=True, null=True, on_delete=models.CASCADE)
    work_start_date = models.DateField(auto_now_add=True)
    work_end_date = models.DateField(blank=True, null=True, )
    document = models.FileField(upload_to='manager_agreements_documents/', blank=True, null=True,
                                verbose_name="manager_document")
    # Commission Rates
    employee_bonus_percentage = models.FloatField(help_text="Percentage of employer payment given to the employee",
                                                  default=50.0)
    employer_bonus_percentage = models.FloatField(help_text="Percentage of employer payment taken as profit",
                                                  default=20.0)

    def calculate_profit(self, assignment):
        """
        Calculates profit based on the manager's commission structure.
        """
        employer_payment = assignment.employer_payment
        employee_salary = employer_payment * Decimal(self.employee_bonus_percentage / 100)
        manager_profit = employer_payment * Decimal(self.employer_bonus_percentage / 100)

        return employer_payment - employee_salary - manager_profit
    class Meta:
        ordering = ['-work_start_date']
        verbose_name = "Manager"
        verbose_name_plural = "Managers"

    def __str__(self):
        return f"{self.manager_name}  {self.manager_surname}"

class DirectAgreements(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    amount = models.FloatField()
    manager = models.ForeignKey(Manager, on_delete = models.CASCADE)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Direct Agreement"
        verbose_name_plural = "Direct Agreements"



from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings
from datetime import timedelta

from django.db import models
from django.conf import settings
from datetime import timedelta

class Contract(models.Model):
    """
    Modelis, apibūdinantis darbo sutartį tarp darbuotojo, darbdavio ir menedžerio.
    """
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="contracts_as_employee")
    employer = models.ForeignKey(Employer, on_delete=models.PROTECT, related_name="contracts_as_employer")
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True, related_name="contracts_as_manager")

    # Tarifo tipai
    HOURLY = "hourly"
    DAILY = "daily"

    TARIFF_CHOICES = [
        (HOURLY, "Už valandą"),
        (DAILY, "Už dieną"),
    ]

    # Darbuotojo tarifai
    employee_tariff_type = models.CharField(max_length=10, choices=TARIFF_CHOICES, default=HOURLY)
    employee_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Darbuotojo valandinis tarifas")
    employee_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Darbuotojo dienos tarifas")

    # Darbdavio tarifai
    employer_tariff_type = models.CharField(max_length=10, choices=TARIFF_CHOICES, default=HOURLY)
    employer_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Darbdavio valandinis tarifas")
    employer_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Darbdavio dienos tarifas")

    # Menedžerio komisinių tarifas (%)
    manager_commission = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Menedžerio komisinių procentas")

    # Dirbtos valandos ir dienos (saugomos rankiniu būdu arba automatiškai skaičiuojamos)
    worked_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Faktiškai išdirbtos valandos")
    worked_days = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Faktiškai išdirbtos dienos")

    # Dirbtos darbo valandos ir darbo dienos (atsižvelgiant į darbo grafiką)
    business_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Faktiškai išdirbtos darbo valandos")
    business_days = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, help_text="Faktiškai išdirbtos darbo dienos")

    # Darbo pradžios ir pabaigos datos
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    # Automatiniai laikai
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_salary_and_expenses(self):
        """
        Apskaičiuoja darbuotojo užmokestį ir darbdavio išlaidas, atsižvelgiant į darbo valandas ir dienas.
        """
        if self.employee_tariff_type == self.HOURLY:
            employee_earnings = self.employee_hourly_rate * self.worked_hours
            employer_expense = self.employer_hourly_rate * self.worked_hours
        else:
            employee_earnings = self.employee_daily_rate * self.worked_days
            employer_expense = self.employer_daily_rate * self.worked_days

        # Menedžerio komisinių atskaitymas
        manager_fee = (self.manager_commission / 100) * employee_earnings
        net_salary = employee_earnings - manager_fee

        # Pelnas
        net_profit = employer_expense - net_salary

        return {
            "worked_hours": self.worked_hours,
            "worked_days": self.worked_days,
            "business_hours": self.business_hours,
            "business_days": self.business_days,
            "employee_earnings": employee_earnings,
            "employer_expense": employer_expense,
            "manager_fee": manager_fee,
            "net_salary": net_salary,
            "net_profit": net_profit
        }

    def __str__(self):
        return f"Sutartis: {self.employee} - {self.employer} ({self.start_date} - {self.end_date or 'Nežinoma'})"

