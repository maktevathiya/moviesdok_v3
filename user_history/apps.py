from django.apps import AppConfig


class UserHistoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_history'

    def ready(self):
        import user_history.signals