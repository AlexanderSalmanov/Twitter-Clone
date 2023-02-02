from django import forms 

from .models import Tweet 


class TweetForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(TweetForm, self).__init__(*args, **kwargs)
        self.fields['text'] = forms.CharField(
            required=False,
            max_length=140,
            widget=forms.Textarea(attrs={
                'placeholder': "What's good?",
                'id': 'tweet-text-box',
                'maxlength': 140,
            })
        )
        
    class Meta:
        model = Tweet
        fields = ('text', 'image')