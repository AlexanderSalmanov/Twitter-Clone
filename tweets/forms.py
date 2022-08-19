from django import forms
from .models import Tweet

class TweetForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    image.widget.attrs.update({'class': 'form-control'})
    class Meta:
        model = Tweet
        fields = ['text', ]
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'onkeyup': 'charCount(this)',
                'placeholder': 'What\'s good?'
            })
        }

class ResponseForm(forms.Form):
    text = forms.CharField(max_length=140, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'onkeyup': 'charCount(this)',
        'placeholder': 'Whatcha say?'
    }))
    image = forms.ImageField(required=False)
