from django.urls import path
from .views import telegram_webhook
from .views1 import telegram_webhook_downloader

urlpatterns = [
    path("webhook/", telegram_webhook, name="telegram_webhook"),
]
