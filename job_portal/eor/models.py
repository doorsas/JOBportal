from django.db import models
from employer.models import Employer
from employee.models import Employee

class EmployeeAssignment(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[('active', 'Active'), ('completed', 'Completed')],
        default='active'
    )

    def __str__(self):
        return f"{self.employee} assigned to {self.employer}"