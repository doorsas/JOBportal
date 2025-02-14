from .models import JobPost,JobAgreement, Employer
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
User = get_user_model()


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['title', 'description', 'location', 'salary_range']

class JobAgreementStatusForm(forms.ModelForm):
    class Meta:
        model = JobAgreement
        fields = ['status']




class EmployerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=255, required=True)
    contact_name = forms.CharField(max_length=255, required=True)
    logo = forms.ImageField(required=False)
    company_address = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        # Save User first
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.is_employer = True  # Mark as employer

        if commit:
            user.save()

            # Create Employer profile
            Employer.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                contact_name=self.cleaned_data['contact_name'],
                company_address=self.cleaned_data.get('company_address', ''),
                logo=self.cleaned_data.get('logo', None),  # Handle None case
            )

        return user  # Return the user object