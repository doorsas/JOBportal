from django.db import models
from django.contrib.auth.models import User
from employee.models import CV, Employee # Import CV model from the employee app
from PIL import Image
from django.utils.timezone import now
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User
    company_name = models.CharField(max_length=255, verbose_name="Įmonės pavadinimas")

    contact_name = models.CharField(max_length=255, verbose_name="Kontaktinis asmuo")
    email = models.EmailField(unique=True, verbose_name="El. paštas")
    phone_number = models.CharField(max_length=20, verbose_name="Telefono numeris")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sukurta")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atnaujinta")
    is_active = models.BooleanField(default=False, verbose_name="Aktyvus")  # Aktyvuojama po el. pašto patvirtinimo
    logo = models.ImageField(blank=True, null=True, upload_to='employer_logos/')
    has_agreement = models.BooleanField(default=False, verbose_name="Sutartis")

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

    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name = "Employer"
        verbose_name_plural = "Employers"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Call the parent save method
        super().save(*args, **kwargs)

        # Resize the logo if it exists
        if self.logo:
            logo_path = self.logo.path
            try:
                img = Image.open(logo_path)
                # Resize the image to a fixed size (e.g., 200x200)
                img = img.resize((200, 200), Image.ANTIALIAS)
                img.save(logo_path)  # Save the resized image back to the same path
            except Exception as e:
                print(f"Error resizing logo: {e}")


class JobPost(models.Model):
    EUROPEAN_COUNTRIES = [
        ('Albania', 'Albania'),
        ('Andorra', 'Andorra'),
        ('Austria', 'Austria'),
        ('Belarus', 'Belarus'),
        ('Belgium', 'Belgium'),
        ('Bosnia and Herzegovina', 'Bosnia and Herzegovina'),
        ('Bulgaria', 'Bulgaria'),
        ('Croatia', 'Croatia'),
        ('Cyprus', 'Cyprus'),
        ('Czech Republic', 'Czech Republic'),
        ('Denmark', 'Denmark'),
        ('Estonia', 'Estonia'),
        ('Finland', 'Finland'),
        ('France', 'France'),
        ('Germany', 'Germany'),
        ('Greece', 'Greece'),
        ('Hungary', 'Hungary'),
        ('Iceland', 'Iceland'),
        ('Ireland', 'Ireland'),
        ('Italy', 'Italy'),
        ('Kosovo', 'Kosovo'),
        ('Latvia', 'Latvia'),
        ('Liechtenstein', 'Liechtenstein'),
        ('Lithuania', 'Lithuania'),
        ('Luxembourg', 'Luxembourg'),
        ('Malta', 'Malta'),
        ('Moldova', 'Moldova'),
        ('Monaco', 'Monaco'),
        ('Montenegro', 'Montenegro'),
        ('Netherlands', 'Netherlands'),
        ('North Macedonia', 'North Macedonia'),
        ('Norway', 'Norway'),
        ('Poland', 'Poland'),
        ('Portugal', 'Portugal'),
        ('Romania', 'Romania'),
        ('San Marino', 'San Marino'),
        ('Serbia', 'Serbia'),
        ('Slovakia', 'Slovakia'),
        ('Slovenia', 'Slovenia'),
        ('Spain', 'Spain'),
        ('Sweden', 'Sweden'),
        ('Switzerland', 'Switzerland'),
        ('Ukraine', 'Ukraine'),
        ('United Kingdom', 'United Kingdom'),
        ('Vatican City', 'Vatican City'),
    ]

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, choices=EUROPEAN_COUNTRIES)
    salary_range = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title



class JobAgreement(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('terminated', 'Terminated'),
        ('expired', 'Expired'),
    ]

    job_post = models.ForeignKey(
        JobPost,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agreements'
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='agreements',
        null = True,
        blank = True
    )

    employer = models.ForeignKey(
        Employer,
        on_delete=models.PROTECT,
        related_name='agreements'
    )

    # Core agreement dates
    offer_date = models.DateField(help_text="Date the job was offered")
    acceptance_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the offer was accepted"
    )
    start_date = models.DateField(help_text="Official start date of employment")
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Planned end date for fixed-term contracts"
    )

    # Termination information
    termination_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual termination date if agreement ended early"
    )

    # Modification tracking
    modification_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last agreement modification"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the job agreement"
    )

    # System timestamps
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
        """
        Add custom validation logic here. For example:
        - Ensure acceptance_date is after offer_date
        - Verify start_date is after acceptance_date
        - Check termination_date is after start_date if exists
        - Ensure job_post and employer are correctly suited
        """
        super().clean()

        # Ensure job_post and employer are correctly suited
        if self.job_post and self.employer:
            if self.job_post.employer != self.employer:
                raise ValidationError({
                    'job_post': "The selected job post does not belong to the specified employer.",
                    'employer': "The selected employer does not match the employer of the job post."
                })

        # Ensure acceptance_date is after offer_date
        if self.acceptance_date and self.offer_date:
            if self.acceptance_date < self.offer_date:
                raise ValidationError({
                    'acceptance_date': "Acceptance date must be after the offer date."
                })

        # Verify start_date is after acceptance_date
        if self.start_date and self.acceptance_date:
            if self.start_date < self.acceptance_date:
                raise ValidationError({
                    'start_date': "Start date must be after the acceptance date."
                })

        # Check termination_date is after start_date if exists
        if self.termination_date and self.start_date:
            if self.termination_date < self.start_date:
                raise ValidationError({
                    'termination_date': "Termination date must be after the start date."
                })



class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('failed', 'Failed'),
    ]

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="payments")
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="EUR")
    invoice_date = models.DateField(default=now)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_proof = models.FileField(upload_to='payment_proofs/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_payment_status(self):
        """ Update payment status based on due date and payment date """
        if self.payment_date:
            self.status = 'paid'
        elif self.due_date < now().date():
            self.status = 'overdue'
        self.save()

    def send_invoice_reminder(self):
        """ Send an email reminder to the employer about the upcoming or overdue invoice """
        subject = f"Invoice Reminder: {self.invoice_number}"
        message = f"Dear {self.employer.contact_name},\n\nYour invoice {self.invoice_number} is due on {self.due_date}. Please ensure payment is made on time.\n\nBest regards,\nYour Company"
        recipient_list = [self.employer.email]

        send_mail(subject, message, 'duomenuanalitikas@gmail.com', recipient_list)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.status} ({self.amount} {self.currency})"

    class Meta:
        ordering = ['-invoice_date']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"