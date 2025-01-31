from .models import JobPost,JobAgreement, Employer
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['title', 'description', 'location', 'salary_range']

class JobAgreementStatusForm(forms.ModelForm):
    class Meta:
        model = JobAgreement
        fields = ['status']


# class EmployerRegistrationForm(UserCreationForm):
#     company_name = forms.CharField(max_length=255, required=True)
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2', 'company_name', 'logo']

class EmployerRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True)
    contact_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    logo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'company_name', 'contact_name', 'phone_number', 'logo']

    def save(self, commit=True):
        # Save the User object first
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        # Create the Employer object
        employer = Employer(
            user=user,
            company_name=self.cleaned_data['company_name'],
            contact_name=self.cleaned_data['contact_name'],
            email=self.cleaned_data['email'],
            phone_number=self.cleaned_data['phone_number'],
            logo=self.cleaned_data['logo'],
        )
        if commit:
            employer.save()

        return user  # Return the user object