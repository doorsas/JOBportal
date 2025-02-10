from django.contrib.auth.models import User
from datetime import date, timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()



class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User
    employee_name = models.CharField(max_length=255)
    employee_surname = models.CharField(max_length=255, blank=True, null=True,default="Unknown")  # New field
    email = models.EmailField()
    citizenship = models.CharField(max_length=100, blank=True, null=True, default="Unknown")  # New field
    national_id = models.IntegerField( blank=True, null=True, unique=True)
    receive_special_offers = models.BooleanField(default=False,)  # New field
    phone_number = models.CharField(max_length=20, blank=True, null=True, default="Unknown")  # New field
    '''banko saskaita, gyvenamosios vietos adresas, artimo zmogaus kontaktai (tel nr) '''
    is_email_verified = models.BooleanField(default=False)
    # credit_card = EncryptedCharField(max_length=16)

    def __str__(self):
        return f"{self.employee_name} {self.employee_surname or ''}"

class CV(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)  # Ensures one CV per employee
    education = models.TextField()
    experience = models.TextField()
    skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    name_surname = models.CharField(max_length=255, verbose_name="NAME, SURNAME")
    date_and_place_of_birth = models.CharField(max_length=255, verbose_name="DATE AND PLACE OF BIRTH")
    place_of_residence = models.CharField(max_length=255, verbose_name="PLACE OF RESIDENCE")
    contacts = models.CharField(max_length=255, verbose_name="CONTACTS")
    languages = models.TextField(verbose_name="LANGUAGES")
    civil_status = models.CharField(max_length=255, verbose_name="CIVIL STATUS")
    professional_experience = models.TextField(verbose_name="PROFESSIONAL EXPERIENCE")
    other_relevant_information = models.TextField(verbose_name="OTHER RELEVANT INFORMATION")
    characteristics = models.TextField(verbose_name="CHARACTERISTICS")
    hobby = models.TextField(verbose_name="HOBBY")
    attachment = models.FileField(upload_to='cv_attachments/', blank=True, null=True, verbose_name="Attachment")
    applications = models.ManyToManyField("employer.JobPost", through="JobApplication", blank=True)

    """Dominancios darbo vietos """
    def __str__(self):
        return f"CV of {self.employee}"
    # submitted_jobposts = models.ManyToManyField(JobPost, blank=True, related_name="subbmited_jobs")

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey("employee.Employee", on_delete=models.CASCADE, related_name="applications")
    job_post = models.ForeignKey("employer.JobPost", on_delete=models.CASCADE, related_name="applications")  # Lazy reference
    cv = models.ForeignKey("employee.CV", on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

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

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="payments")
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="EUR")
    invoice_date = models.DateField(default=now)
    payment_date = models.DateField(null=True, blank=True)
    mokejimo_tipas = models.CharField(max_length=20, choices=STATUS_CHOICES, default='alga')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    document = models.FileField(upload_to='employee_payments_documents/', blank=True, null=True, verbose_name="Document")

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.mokejimo_tipas} ({self.amount} {self.currency})"

    class Meta:
        ordering = ['-invoice_date']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"





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


def get_default_calendar_dates():
    # Generate the next 30 days as default calendar dates
    today = date.today()
    return [(today + timedelta(days=i)).isoformat() for i in range(60)]  # Convert to ISO format strings

class Calendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='calendar')
    dates = models.JSONField(default=get_default_calendar_dates)

class Booking(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    is_booked = models.BooleanField(default=False)







