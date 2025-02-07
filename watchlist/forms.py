from django import forms
from .models import Watchlist, WatchlistItem

class WatchlistForm(forms.Form):
    movie_id = forms.IntegerField(widget=forms.HiddenInput())  # Hidden field for the movie ID

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically load the user's watchlists into the choice field
        watchlists = Watchlist.objects.filter(user=user)
        WATCHLIST_CHOICES = [(watchlist.id, watchlist.name) for watchlist in watchlists]
        WATCHLIST_CHOICES.append(('none', 'None'))  # Add 'None' option to remove the title
        self.fields['watchlist'] = forms.ChoiceField(choices=WATCHLIST_CHOICES, required=False, label="Watchlist")


class RenameWatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ['name']