from django import forms
from django.core import validators
from .models import Profile

class BioForm(forms.Form):
    bio_input = forms.CharField(max_length=200, widget=forms.Textarea(attrs={
        'onkeyup': 'countChar(this)',
        'placeholder': "What's good?",
        'class': 'form-control'
    }
    )
)

class ProfileSettingsForm(forms.Form):
    username = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control username-prompt',
        'placeholder': 'Username input...'
    }))
    nickname = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control nickname-prompt',
        'placeholder': 'Nickname input...'
    }))
    bio_input = forms.CharField(max_length=200, required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'onkeyup': 'countChar(this)',
        'placeholder': "What's good?"
    }
    ))
    image = forms.ImageField(required=False)
    image.widget.attrs.update({'class': 'form-control img-prompt'})

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username', None)
        if username is not None:
            qs = Profile.objects.filter(username=username)
            if qs.count() == 1:
                raise forms.ValidationError('User with this username already exists.')
                # self.add_error('username', 'User with this username already exists.')
