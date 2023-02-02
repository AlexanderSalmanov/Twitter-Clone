from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django.contrib.auth import get_user_model

import string

User = get_user_model()

class UserAdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['email','full_name']

    def clean(self):
        """
        Verify both password match
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_2 = cleaned_data.get('password_2')
        if password is not None and password != password_2:
            self.add_error('password_2', 'Your passwords don\'t match.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'full_name', 'is_active', 'is_staff', 'is_superuser']

    def clean_password(self):
        return self.initial['password']
    
    
class SignupForm(forms.ModelForm):
    
    password = forms.CharField(
        max_length=64, 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': ''
        }))
    password_2 = forms.CharField(max_length=64, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': ''
    }), label="Repeat your password")
    
    class Meta:
        model = User 
        fields = ('email', 'full_name', 'password', 'password_2')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'abc123@gmail.com'
            }),
            'full_name': forms.TextInput(attrs={'class': 'form-control'})
        }
        
    def clean(self):
        data = super().clean()
        password = data.get('password')
        password_2 = data.get('password_2')
        if password and password != password_2:
            self.add_error('password_2', "Passwords don't match!")
        return data 
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user 
    
    
class LoginForm(forms.Form):
    
    email = forms.EmailField(max_length=64, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'somemail@gmail.com'
    }))
    password = forms.CharField(max_length=64, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
    }))