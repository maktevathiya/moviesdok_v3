
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")), #tailwind reload url
    path('accounts/', include('allauth.urls')),  # Include allauth URLs
    path('', include('homepage.urls')),
    path('detail/', include('detail_page.urls')),
    path('watchlist/', include('watchlist.urls')),
    path('', include('second_level_pages.urls')),
    path('', include('links.urls')),
    path('', include('detail_page.urls')),
    path("telegram-bot/", include("telegram_bot.urls")),
    path('user/', include('user_profile.urls')),
]
