from django import forms 


class ProfileSettingsForm(forms.Form):
    
    nickname = forms.CharField(required=False, max_length=50)
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'bio-input-box form-control',
        'maxlength': 140
    }))
    profile_pic = forms.ImageField(required=False)
    