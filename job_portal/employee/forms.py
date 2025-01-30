from django import forms
from .models import CV,Employee
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

#
# class CVForm(forms.ModelForm):
#     class Meta:
#         model = CV
#         fields = ['education', 'experience', 'skills']
#
class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = [
            'education', 'experience', 'skills', 'name_surname', 'date_and_place_of_birth',
            'place_of_residence', 'contacts', 'languages', 'civil_status', 'professional_experience',
            'other_relevant_information', 'characteristics', 'hobby', 'attachment'
        ]
        widgets = {
            'attachment': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx,.jpg,.png'}),
        }

class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["employee_name",'employee_surname','email','phone_number']

class EmployeeRegistrationForm(UserCreationForm):
    employee_name = forms.CharField(max_length=255, required=True)
    employee_surname = forms.CharField(max_length=255)  # New field
    email = forms.EmailField(required=True)
    citizenship = forms.CharField(max_length=100)  # New field
    national_id = forms.IntegerField()
    receive_special_offers = forms.BooleanField(required=False) # New field
    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'employee_name','employee_surname','citizenship','national_id','receive_special_offers','phone_number']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if Employee.objects.filter(email=email).exists():
    #         raise ValidationError("An employee with this email already exists.")
    #     return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)