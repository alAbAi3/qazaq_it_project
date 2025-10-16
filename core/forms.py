# core/forms.py (жаңа файл)
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django import forms
from .models import JobApplication


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['applicant_name', 'applicant_email', 'phone_number', 'cover_letter', 'resume']
        widgets = {
            'applicant_name': forms.TextInput(attrs={'placeholder': 'Аты-жөніңізді енгізіңіз'}),
            'applicant_email': forms.EmailInput(attrs={'placeholder': 'example@mail.com'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+7 (700) 123-45-67'}),
            'cover_letter': forms.Textarea(attrs={'placeholder': 'Өзіңіз туралы қысқаша жазыңыз...', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})