from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User
    employee_name = models.CharField(max_length=255)
    email = models.EmailField()


    def __str__(self):
        return self.employee_name




class CV(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)  # Ensures one CV per employee
    education = models.TextField()
    experience = models.TextField()
    skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CV of {self.employee}"


class CalendarDay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    date = models.DateField()  # Represents the day
    is_free = models.BooleanField(default=True)  # True if free, False otherwise

    class Meta:
        unique_together = ('user', 'date')  # Ensure each user can only have one entry per date
        ordering = ['date']  # Sort by date

    def __str__(self):
        status = "Free" if self.is_free else "Not Free"
        return f"{self.date} - {status}"

"""class EmployerProfile(models.Model):
    company_name = models.CharField(max_length=255, verbose_name="Įmonės pavadinimas")
    contact_name = models.CharField(max_length=255, verbose_name="Kontaktinis asmuo")
    email = models.EmailField(unique=True, verbose_name="El. paštas")
    phone_number = models.CharField(max_length=20, verbose_name="Telefono numeris")
    password = models.CharField(max_length=255, verbose_name="Slaptažodis")  # Slaptažodžiai paprastai šifruojami
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sukurta")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atnaujinta")
    is_active = models.BooleanField(default=False, verbose_name="Aktyvus")  # Aktyvuojama po el. pašto patvirtinimo

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "Darbdavio profilis"
        verbose_name_plural = "Darbdavių profiliai"
        ordering = ['-created_at']"""