from django import forms
from .models import CV,Employee
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Employee  # Import Employee model

User = get_user_model()

class EmployeeRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    citizenship = forms.CharField(max_length=100, required=True)
    national_id = forms.IntegerField(required=False)  # Optional
    receive_special_offers = forms.BooleanField(required=False)
    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number', 'citizenship', 'national_id', 'receive_special_offers']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']  # Store first name
        user.last_name = self.cleaned_data['last_name']  # Store last name
        user.is_employee = True

        if commit:
            user.save()
            Employee.objects.create(
                user=user,
                citizenship=self.cleaned_data['citizenship'],
                national_id=self.cleaned_data.get('national_id'),
                receive_special_offers=self.cleaned_data.get('receive_special_offers', False),

            )
        return user


class DateInput(forms.DateInput):
    input_type = 'date'

class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = [
            'education', 'experience', 'skills',
            'date_of_birth', 'place_of_birth', 'place_of_residence',
            'contacts', 'languages', 'civil_status', 'professional_experience',
            'other_relevant_information', 'characteristics', 'hobby', 'attachment'
        ]

        widgets = {
            'attachment': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx,.jpg,.png'},),
            'date_of_birth': DateInput()
        }

class EmployeeEditForm(forms.ModelForm):
    email = forms.EmailField()
    phone_number = forms.CharField()

    class Meta:
        model = Employee
        fields = []  # No fields from Employee model are directly edited

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate the form with initial data from the related CustomUser
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone_number'].initial = self.instance.user.phone_number

    def save(self, commit=True):
        employee = super().save(commit=False)
        # Update the related CustomUser fields
        if employee.user:
            employee.user.email = self.cleaned_data['email']
            employee.user.phone_number = self.cleaned_data['phone_number']
            if commit:
                employee.user.save()
                employee.save()
        return employee

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)




class PaymentFilterForm(forms.Form):
    min_amount = forms.DecimalField(label='Min Amount', required=False, min_value=0)
    max_amount = forms.DecimalField(label='Max Amount', required=False, min_value=0)
    start_date = forms.DateField(label='Start Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
