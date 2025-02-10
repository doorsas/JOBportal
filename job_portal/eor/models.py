from django.db import models
from employer.models import Employer, JobPost
from employee.models import Employee, CV

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

    def __str__(self):
        return f"{self.employee} assigned to {self.employer} for {self.job_post}"
