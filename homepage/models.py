from django.db import models

class MovieCollection(models.Model):
    name = models.CharField(max_length=255, unique=True)
    overview = models.TextField()
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    backdrop_path = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.name


class Movie(models.Model):
    collection = models.ForeignKey(MovieCollection, related_name='parts', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255)
    overview = models.TextField()
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    backdrop_path = models.CharField(max_length=255, blank=True, null=True)
    media_type = models.CharField(max_length=50, choices=[('movie', 'Movie'), ('tv', 'TV Show')])
    adult = models.BooleanField(default=False)
    original_language = models.CharField(max_length=50)
    release_date = models.DateField(blank=True, null=True)
    genre_ids = models.JSONField()  # Store list of genre IDs
    popularity = models.FloatField()
    video = models.BooleanField(default=False)
    vote_average = models.FloatField()
    vote_count = models.IntegerField()

    def __str__(self):
        return self.title
