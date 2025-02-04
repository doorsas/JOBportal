from django.db import models
from django.contrib.auth.models import User
from employee.models import CV, Employee # Import CV model from the employee app
from PIL import Image

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




'''
Įmonės registracija:
Logo (neprivaloma)
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




class JobPost(models.Model):

    EUROPEAN_COUNTRIES = [
    ('AL', 'Albania'),
    ('AD', 'Andorra'),
    ('AT', 'Austria'),
    ('BY', 'Belarus'),
    ('BE', 'Belgium'),
    ('BA', 'Bosnia and Herzegovina'),
    ('BG', 'Bulgaria'),
    ('HR', 'Croatia'),
    ('CY', 'Cyprus'),
    ('CZ', 'Czech Republic'),
    ('DK', 'Denmark'),
    ('EE', 'Estonia'),
    ('FI', 'Finland'),
    ('FR', 'France'),
    ('DE', 'Germany'),
    ('GR', 'Greece'),
    ('HU', 'Hungary'),
    ('IS', 'Iceland'),
    ('IE', 'Ireland'),
    ('IT', 'Italy'),
    ('XK', 'Kosovo'),
    ('LV', 'Latvia'),
    ('LI', 'Liechtenstein'),
    ('LT', 'Lithuania'),
    ('LU', 'Luxembourg'),
    ('MT', 'Malta'),
    ('MD', 'Moldova'),
    ('MC', 'Monaco'),
    ('ME', 'Montenegro'),
    ('NL', 'Netherlands'),
    ('MK', 'North Macedonia'),
    ('NO', 'Norway'),
    ('PL', 'Poland'),
    ('PT', 'Portugal'),
    ('RO', 'Romania'),
    ('RU', 'Russia'),
    ('SM', 'San Marino'),
    ('RS', 'Serbia'),
    ('SK', 'Slovakia'),
    ('SI', 'Slovenia'),
    ('ES', 'Spain'),
    ('SE', 'Sweden'),
    ('CH', 'Switzerland'),
    ('UA', 'Ukraine'),
    ('GB', 'United Kingdom'),
    ('VA', 'Vatican City'),
]

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255,choices=EUROPEAN_COUNTRIES)
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
        """
        super().clean()

