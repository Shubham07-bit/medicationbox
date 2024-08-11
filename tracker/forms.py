from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Patient

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username',
            'aria-label': 'Username',
            'aria-describedby': 'basic-addon1'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password',
            'aria-label': 'Password',
            'aria-describedby': 'basic-addon1'
        })
    )

class UserRegistrationForm(forms.ModelForm):
    fullname = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Full Name',
            'aria-label': 'Full Name',
            'aria-describedby': 'basic-addon1'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password',
            'aria-label': 'Password',
            'aria-describedby': 'basic-addon1'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'aria-label': 'Confirm Password',
            'aria-describedby': 'basic-addon1'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Username',
                'aria-label': 'Username',
                'aria-describedby': 'basic-addon1'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email',
                'aria-label': 'Email',
                'aria-describedby': 'basic-addon1'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise ValidationError("Passwords do not match")

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        full_name = self.cleaned_data['fullname']
        first_name, last_name = full_name.split(' ', 1)
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user



class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['device_id', 'name', 'age', 'gender', 'disease', 'photo']

    # Customizing the form fields
    device_id = forms.CharField(
        label='Device ID',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Device ID'})
    )

    name = forms.CharField(
        label='Patient Name',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Patient Name'})
    )

    age = forms.IntegerField(
        label='Patient Age',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Patient Age'})
    )

    gender = forms.ChoiceField(
        label='Patient Gender',
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    disease = forms.CharField(
        label='Patient Disease',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Patient Disease'})
    )

    photo = forms.ImageField(
        label='Patient Photo (optional)',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )