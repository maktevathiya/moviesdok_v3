# forms.py
from django import forms
from .models import Link

class MovieLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['url', 'quality', 'site', 'size', 'audio', 'subtitles', 'decoder', 'format', 'expiration']
        widgets = {
            'expiration': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(MovieLinkForm, self).__init__(*args, **kwargs)
        # Set the default value for audio
        self.fields['audio'].initial = 'original'


class TVLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['url', 'quality', 'site', 'size', 'audio', 'subtitles', 'decoder', 'format', 'season', 'episode', 'expiration']
        widgets = {
            'expiration': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(TVLinkForm, self).__init__(*args, **kwargs)
        self.fields['audio'].initial = 'original'
