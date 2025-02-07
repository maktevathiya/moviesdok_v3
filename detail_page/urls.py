from django.urls import path
from. import views

urlpatterns = [
    path('tv/<int:tmdb_id>', views.detail_view, {'media_type': 'tv'}, name='tv_show_details'),
    path('movie/<int:tmdb_id>', views.detail_view, {'media_type': 'movie'}, name='movie_details'),
]
