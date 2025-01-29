from django.db import models
from django.contrib.auth.models import User
from employee.models import CV, Employee # Import CV model from the employee app


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
        null = True,  # Add this
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

