from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


from django.db import models

# credit_card = EncryptedCharField(max_length=16)



class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User
    employee_name = models.CharField(max_length=255)
    employee_surname = models.CharField(max_length=255, blank=True, null=True,default="Unknown")  # New field
    email = models.EmailField()
    citizenship = models.CharField(max_length=100, blank=True, null=True, default="Unknown")  # New field
    national_id = models.IntegerField( blank=True, null=True, unique=True)
    receive_special_offers = models.BooleanField(default=False,)  # New field
    phone_number = models.CharField(max_length=20, blank=True, null=True, default="Unknown")  # New field

    def __str__(self):
        return f"{self.employee_name} {self.employee_surname or ''}"





class CV(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)  # Ensures one CV per employee
    education = models.TextField()
    experience = models.TextField()
    skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # additional_documents


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





# Models
def get_default_calendar_dates():
    # Generate the next 30 days as default calendar dates
    today = date.today()
    return [(today + timedelta(days=i)).isoformat() for i in range(30)]  # Convert to ISO format strings

class Calendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='calendar')
    dates = models.JSONField(default=get_default_calendar_dates)

class Booking(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    is_booked = models.BooleanField(default=False)