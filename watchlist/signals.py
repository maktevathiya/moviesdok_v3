from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction
from .models import Watchlist

@receiver(post_save, sender=User)
def create_default_watchlists(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():  # Ensure all operations are completed or rolled back if an error occurs
            Watchlist.objects.get_or_create(user=instance, name="Plan to Watch", is_default=True)
            Watchlist.objects.get_or_create(user=instance, name="Already Watched", is_default=True)
