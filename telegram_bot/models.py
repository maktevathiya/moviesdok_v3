from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def validate_word_limit(value):
    word_count = len(value.split())
    if word_count > 100:
        raise ValidationError("Description cannot exceed 100 words.")
    

class MediaInfo(models.Model):
    unique_id = models.CharField(max_length=20, unique=True)
    description = models.TextField(validators=[validate_word_limit])
    from_id = models.BigIntegerField()
    tmdb_id = models.CharField(max_length=50)
    media_type = models.CharField(max_length=10)
    media_content = models.CharField(max_length=50)    
    season = models.CharField(max_length=400, null=True, blank=True)
    no_of_files = models.PositiveIntegerField(null=True, blank=True)  # Can be null initially
    created_at = models.DateTimeField(auto_now_add=True)  # Set when the instance is created
    updated_at = models.DateTimeField(auto_now=True)  # Updated whenever the instance is saved

    def __str__(self):
        return f"{self.description[:50]} ({self.unique_id})"  

class FileInfo(models.Model):
    unique_id = models.ForeignKey(MediaInfo, on_delete=models.CASCADE, to_field="unique_id", db_column="unique_id", related_name='files')
    file_id = models.CharField(max_length=300)
    mime_type = models.CharField(max_length=50, null=True, blank=True)
    file_name = models.TextField(null=True, blank=True)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=10)

    def __str__(self):
        return f"File {self.file_id} for {self.unique_id}"

class LinkedAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField()

    def __str__(self):
        return f" {self.telegram_id}"
    

class SessionInfo(models.Model):
    unique_id = models.CharField(max_length=20, unique=True)
    chat_id = models.BigIntegerField(unique=True)
    description = models.TextField(validators=[validate_word_limit], null=True, blank=True)
    from_id = models.BigIntegerField()
    tmdb_id = models.CharField(max_length=50)
    media_type = models.CharField(max_length=10)
    media_content = models.CharField(max_length=50, null=True, blank=True)
    season = models.CharField(max_length=400, null=True, blank=True)
    available_season = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)  # Set when the instance is created
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description[:50]} ({self.unique_id})"  
    

class TemporaryFileInfo(models.Model):
    unique_id = models.ForeignKey(SessionInfo, on_delete=models.CASCADE,to_field="unique_id", db_column="unique_id")
    file_id = models.CharField(max_length=300)
    mime_type = models.CharField(max_length=50, null=True, blank=True)
    file_name = models.TextField(null=True, blank=True)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=10)

    def __str__(self):
        return f"File {self.file_id} for {self.unique_id}"