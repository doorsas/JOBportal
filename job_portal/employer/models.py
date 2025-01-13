from django.db import models
from django.contrib.auth.models import User

from django.contrib import admin




class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User
    company_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.company_name


class JobPost(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


