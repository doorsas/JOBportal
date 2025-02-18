from employer.models import Employer, JobPost, Payment
from employee.models import Employee, CV, Payment
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from decimal import Decimal
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



