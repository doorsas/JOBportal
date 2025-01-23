from django.db import models
from django.contrib.auth.models import User
from employee.models import CV  # Import CV model from the employee app

class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User
    company_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.company_name
'''
Įmonės registracija:
Logo (neprivaloma)
Trumpas veiklos aprašymas
Pavadinimas
Registro numeris
PVM numeris
Buveinės adresas
Telefonas
El.paštas
Administratoriaus vardas pavardė (tik jis gali pridėt kitus vartotojus prie įmonės)
Telefonas
El paštas
Sąskaitų siuntimo el paštas + apskaitos telefonas
'''

class JobPost(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    submitted_cvs = models.ManyToManyField(CV, blank=True, related_name="applied_jobs")  # Reference CV

    def __str__(self):
        return self.title
#
# class JobPost(models.Model):
#     employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     location = models.CharField(max_length=255)
#     salary_range = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title
#
#
