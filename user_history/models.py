from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # Import timezone

class UserHistory(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=40, null=True, blank=True)
    genre = models.TextField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=255, default='no title available')  # New field
    poster_path = models.CharField(null=True, blank=True, max_length=255, default='null')
    rating = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)  # New field
    visited_at = models.DateTimeField(auto_now_add=True)  # Auto set when creating
    counter = models.PositiveIntegerField(default=1)
    media_type = models.CharField(max_length=20, null=True, blank=True)
    class Meta:
         constraints = [
            models.UniqueConstraint(fields=['user', 'tmdb_id', 'title'], name='unique_user_tmdb_genre'),
            models.UniqueConstraint(fields=['session_id', 'tmdb_id', 'title'], name='unique_session_tmdb_genre')
        ]

    def __str__(self):
        return f"{self.user or self.session_id} - {self.tmdb_id} - {self.visited_at}"

    
    def save(self, *args, **kwargs):
        # If this is a new record (no primary key yet)
        if not self.pk:
            existing_entry = UserHistory.objects.filter(
                user=self.user, tmdb_id=self.tmdb_id, title=self.title
            ).first() if self.user else UserHistory.objects.filter(
                session_id=self.session_id, tmdb_id=self.tmdb_id, title=self.title
            ).first()

            if existing_entry:
                # Update the existing entry's visited_at and counter
                existing_entry.visited_at = timezone.now()
                existing_entry.counter += 1
                existing_entry.save(update_fields=['visited_at', 'counter'])
                return  # Skip saving a new instance
        # Only set visited_at to now if it hasn't been explicitly set elsewhere (e.g., during transfer)
        if not hasattr(self, '_manual_visited_at'):
            self.visited_at = timezone.now()

        # Save normally if it's a new record or being updated
        super().save(*args, **kwargs)

    @classmethod
    def transfer_session_history_to_user(cls, session_id, user):
        # Retrieve all records associated with the session_id
        session_records = cls.objects.filter(session_id=session_id)

        for record in session_records:
            # Check if there's already a record for this user with the same tmdb_id and genre
            existing_entry = cls.objects.filter(
                user=user,
                tmdb_id=record.tmdb_id,
                title=record.title
            ).first()

            if existing_entry:
                # If the record exists for the user, merge the data
                latest_visited_at = max(existing_entry.visited_at, record.visited_at)
                existing_entry.counter += record.counter  # Add the counters together
                existing_entry.visited_at = latest_visited_at 
                existing_entry._manual_visited_at = True  # Flag the manual setting
                existing_entry.save(update_fields=['visited_at', 'counter'])

                # Delete the session-based record after merging
                record.delete()

            else:
                # If no existing user record, assign the user to the current session-based record
                record.user = user
                record.session_id = None  # Remove the session id
                record.save(update_fields=['user', 'session_id'])

