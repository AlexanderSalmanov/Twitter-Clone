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
        fields = ['email', 'full_name', 'active', 'staff', 'admin']

    def clean_password(self):
        return self.initial['password']

class LoginForm(forms.Form):
    email = forms.EmailField(label='Your Email Address')
    password = forms.CharField(widget=forms.PasswordInput())

class RegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(widget=forms.PasswordInput, label='Verify your password')

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password_2']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_2 = cleaned_data.get('password_2')
        if password is not None and password != password_2:
            self.add_error('password_2', 'Passwords don\'t match!')

    def clean_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        digits = string.digits
        chars = string.ascii_lowercase
        if all([char in digits for char in password]) or all([char in chars for char in password]):
            self.add_error('password', 'Your password should consist of both letters and digits.')
        elif len(password) < 8:
            self.add_error('password', 'Your password must be at least 8 characters long.')


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
