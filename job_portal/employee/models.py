from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now
import uuid
from datetime import date, timedelta
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

# User = get_user_model()
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(blank=True, null=True)

    is_employer = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="custom_users", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_users_permissions", blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

    def assign_group(self):
        """Automatically assign the user to a group based on role selection."""
        if self.is_employer:
            self.groups.add(Group.objects.get_or_create(name="Employers")[0])
        if self.is_employee:
            self.groups.add(Group.objects.get_or_create(name="Employees")[0])
        if self.is_manager:
            self.groups.add(Group.objects.get_or_create(name="Managers")[0])

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    citizenship = models.CharField(max_length=100, default="Unknown")
    national_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    receive_special_offers = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name or ''} {self.user.last_name or ''}".strip()


class CV(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    education = models.TextField()
    experience = models.TextField()
    skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    date_of_birth = models.DateField(null=True, blank=True,verbose_name="Date of Birth")
    place_of_birth = models.CharField(max_length=255, verbose_name="Place Of Birth")
    place_of_residence = models.CharField(max_length=255, verbose_name="Place of Residence")
    contacts = models.CharField(max_length=255, verbose_name="Contacts of Emergency")
    languages = models.TextField(verbose_name="Languages")
    civil_status = models.CharField(max_length=255, verbose_name="Civil Status")
    professional_experience = models.TextField(verbose_name="Professional Experience")
    other_relevant_information = models.TextField(verbose_name="Other Relevant Information")
    characteristics = models.TextField(verbose_name="Characteristics")
    hobby = models.TextField(verbose_name="Hobby")
    attachment = models.FileField(upload_to='cv_attachments/', blank=True, null=True, verbose_name="Attachment")

    def __str__(self):
        return f"CV of {self.employee}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="applications")
    job_post = models.ForeignKey("employer.JobPost", on_delete=models.CASCADE, related_name="applications")
    cv = models.ForeignKey(CV, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'job_post')

    def __str__(self):
        return f"{self.employee} applied for {self.job_post.title}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('alga', 'Alga'),
        ('avansinis', 'Avansinis'),
        ('atskaitymas', 'Atskaitymas'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="payments")
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="EUR")
    invoice_date = models.DateField(default=now)
    payment_date = models.DateField(null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    mokejimo_tipas = models.CharField(max_length=20, choices=STATUS_CHOICES, default='alga')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    document = models.FileField(upload_to='employee_payments_documents/', blank=True, null=True,
                                verbose_name="Document")

    class Meta:
        ordering = ['-invoice_date']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.mokejimo_tipas} ({self.amount} {self.currency})"

# In the Payment model, automate invoice generation using
# a library like reportlab or weasyprint to generate PDF invoices dynamically.


class CalendarDay(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to the user
    date = models.DateField()  # Represents the day
    is_free = models.BooleanField(default=True)  # True if free, False otherwise

    class Meta:
        unique_together = ('user', 'date')  # Ensure each user can only have one entry per date
        ordering = ['date']  # Sort by date

    def __str__(self):
        status = "Free" if self.is_free else "Not Free"
        return f"{self.date} - {status}"


def get_default_calendar_dates():
    # Generate the next 30 days as default calendar dates
    today = date.today()
    return [(today + timedelta(days=i)).isoformat() for i in range(60)]  # Convert to ISO format strings

class Calendar(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calendar')
    dates = models.JSONField(default=get_default_calendar_dates)

class Booking(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    is_booked = models.BooleanField(default=False)
