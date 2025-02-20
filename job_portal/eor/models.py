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

class Contract(models.Model):
    """
    Modelis, apibūdinantis santykį tarp Darbuotojo, Darbdavio ir Menedžerio.
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

    # Darbuotojo tarifas
    employee_tariff_type = models.CharField(max_length=10, choices=TARIFF_CHOICES, default=HOURLY)
    employee_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Darbuotojo valandinis tarifas")
    employee_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Darbuotojo dienos tarifas")

    # Darbdavio tarifas
    employer_tariff_type = models.CharField(max_length=10, choices=TARIFF_CHOICES, default=HOURLY)
    employer_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Darbdavio valandinis tarifas")
    employer_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Darbdavio dienos tarifas")

    # Menedžerio komisinių tarifas (%)
    manager_commission = models.DecimalField(max_digits=5, decimal_places=2, help_text="Menedžerio komisinių procentas", default=0.00)

    # Darbo pradžios ir pabaigos datos
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    # Automatiniai laikai
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Constants for work hours and days
    HOURS_PER_WEEK = 40
    DAYS_PER_WEEK = 5

    def calculate_work_duration(self):
        """Apskaičiuoja, kiek darbuotojas išdirbo valandų ir dienų."""
        if not self.end_date:
            return {"hours_worked": 0, "days_worked": 0}  # Jei nėra pabaigos datos, laikoma, kad nebaigta

        work_days = (self.end_date - self.start_date).days
        work_weeks = work_days / 7

        hours_worked = work_weeks * self.HOURS_PER_WEEK
        days_worked = work_weeks * self.DAYS_PER_WEEK

        return {"hours_worked": round(hours_worked), "days_worked": round(days_worked)}

    def calculate_profit(self):
        """
        Apskaičiuoja darbuotojo pelną, atsižvelgiant į jo tarifą ir menedžerio komisinius.
        """
        work_duration = self.calculate_work_duration()
        hours_worked = work_duration["hours_worked"]
        days_worked = work_duration["days_worked"]

        # Ensure rates are not None by setting default values
        employee_hourly_rate = self.employee_hourly_rate or 0
        employee_daily_rate = self.employee_daily_rate or 0
        employer_hourly_rate = self.employer_hourly_rate or 0
        employer_daily_rate = self.employer_daily_rate or 0

        if self.employee_tariff_type == self.HOURLY:
            employee_earnings = employee_hourly_rate * hours_worked
            employer_payment = employer_hourly_rate * hours_worked
        else:
            employee_earnings = employee_daily_rate * days_worked
            employer_payment = employer_daily_rate * days_worked

        # Menedžerio komisinių atskaitymas
        manager_fee = (self.manager_commission / 100) * employee_earnings if self.manager_commission else 0
        net_profit = employee_earnings - manager_fee

        return {
            "hours_worked": hours_worked,
            "days_worked": days_worked,
            "employee_earnings": employee_earnings,
            "employer_payment": employer_payment,
            "manager_fee": manager_fee,
            "net_profit": net_profit
        }

    def __str__(self):
        return f"Sutartis: {self.employee} - {self.employer} ({self.start_date} - {self.end_date or 'Nežinoma'})"
