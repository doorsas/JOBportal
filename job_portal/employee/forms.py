from django import forms
from .models import CV,Employee
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = ['education', 'experience', 'skills']

class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["employee_name",'email']

class EmployeeRegistrationForm(UserCreationForm):
    employee_name = forms.CharField(max_length=255, required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'employee_name']

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)