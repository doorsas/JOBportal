from django.db import models
from django.contrib.auth.models import User
from employee.models import CV, Employee
from PIL import Image
from django.utils.timezone import now
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from io import BytesIO
from django.core.files.base import ContentFile
import uuid
from django.conf import settings


class Employer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, unique=True,verbose_name="Įmonės pavadinimas")
    company_registration_number = models.CharField(max_length=100, unique=True, blank=True, null=True,verbose_name="Įmonės registracijos Nr.")
    contact_name = models.CharField(max_length=255, verbose_name="Kontaktinis asmuo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sukurta")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atnaujinta")
    is_active = models.BooleanField(default=False, verbose_name="Aktyvus")
    logo = models.ImageField(blank=True, null=True, upload_to='employer_logos/')
    has_agreement = models.BooleanField(default=False, verbose_name="Sutartis")
    company_address = models.TextField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    receive_special_offers = models.BooleanField(default=False)


    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "Employer"
        verbose_name_plural = "Employers"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.logo:
            try:
                img = Image.open(self.logo)
                img.thumbnail((200, 200))  # Maintain aspect ratio
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                self.logo.save(self.logo.name, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                print(f"Error resizing logo: {e}")


class JobPost(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = CountryField()
    salary_range = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class JobAgreement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('terminated', 'Terminated'),
        ('expired', 'Expired'),
    ]

    job_post = models.ForeignKey(JobPost, on_delete=models.SET_NULL, null=True, blank=True, related_name='agreements')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='agreements', null=True, blank=True)
    employer = models.ForeignKey(Employer, on_delete=models.PROTECT, related_name='agreements')
    offer_date = models.DateField(help_text="Date the job was offered")
    acceptance_date = models.DateField(null=True, blank=True, help_text="Date the offer was accepted")
    start_date = models.DateField(help_text="Official start date of employment")
    end_date = models.DateField(null=True, blank=True, help_text="Planned end date for fixed-term contracts")
    termination_date = models.DateField(null=True, blank=True,
                                        help_text="Actual termination date if agreement ended early")
    modification_date = models.DateField(null=True, blank=True, help_text="Date of last agreement modification")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',
                              help_text="Current status of the job agreement")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Agreement: {self.employee} @ {self.employer} ({self.start_date})"

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Job Agreement"
        verbose_name_plural = "Job Agreements"
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]

    def clean(self):
        super().clean()
        if self.job_post and self.employer:
            if self.job_post.employer != self.employer:
                raise ValidationError("The selected job post does not belong to the specified employer.")
        if self.acceptance_date and self.offer_date and self.acceptance_date < self.offer_date:
            raise ValidationError("Acceptance date must be after the offer date.")
        if self.start_date and self.acceptance_date and self.start_date < self.acceptance_date:
            raise ValidationError("Start date must be after the acceptance date.")
        if self.termination_date and self.start_date and self.termination_date < self.start_date:
            raise ValidationError("Termination date must be after the start date.")

    def save(self, *args, **kwargs):
        if self.end_date and self.end_date < now().date():
            self.status = 'expired'
        super().save(*args, **kwargs)


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('failed', 'Failed'),
    ]

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="payments")
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="EUR")
    invoice_date = models.DateField(default=now)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_proof = models.FileField(upload_to='payment_proofs/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = str(uuid.uuid4().hex[:10]).upper()
        if self.payment_date:
            self.status = 'paid'
        elif self.due_date and self.due_date < now().date():
            self.status = 'overdue'
        super().save(*args, **kwargs)

    def send_invoice_reminder(self):
        subject = f"Invoice Reminder: {self.invoice_number}"
        message = f"Dear {self.employer.contact_name},\n\nYour invoice {self.invoice_number} is due on {self.due_date}. Please ensure payment is made on time.\n\nBest regards,\nYour Company"
        send_mail(subject, message, 'duomenuanalitikas@gmail.com', [self.employer.email])

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.status} ({self.amount} {self.currency})"

    '''
    Įmonės registracija:
    Trumpas veiklos aprašymas
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
