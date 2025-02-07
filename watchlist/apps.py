from django.apps import AppConfig

class WatchlistConfig(AppConfig):
    name = 'watchlist'

    def ready(self):
        import watchlist.signals  # Import the signals module to register the signal handlers
