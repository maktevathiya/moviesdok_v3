from django.urls import path
from . import views

urlpatterns = [
    path('add-link/<str:media_type>/<int:tmdb_id>/', views.add_link_page, name='add_link_page'),
    path('addlink/', views.add_link, name='addlink' ),
]
