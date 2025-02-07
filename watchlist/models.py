from django.db import models
from django.contrib.auth.models import User

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)  # Field to identify the default watchlist

    class Meta:
        unique_together = ('user', 'name')  # Ensure unique watchlist names per user

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class WatchlistItem(models.Model):
    watchlist = models.ForeignKey(Watchlist, related_name='items', on_delete=models.CASCADE)
    movie_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255, default='no title available')  # New field
    poster_path = models.CharField(max_length=255, default='null')
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)  # New field
    release_date = models.DateField(null=True, blank=True)  # New field for release date
    genres = models.CharField(max_length=255, null=True, blank=True)  # New field for genres
    added_at = models.DateTimeField(auto_now_add=True)
    media_type = models.CharField(max_length=255, default='not available')  # New field

    class Meta:
        unique_together = ('watchlist', 'movie_id')  # Prevent duplicate movie entries in the same watchlist

    def __str__(self):
        return f"Item {self.movie_id} ({self.title}) in {self.watchlist.name}"
