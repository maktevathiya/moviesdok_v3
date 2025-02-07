from django.urls import path
from . import views 


urlpatterns = [
    path('', views.hompage, name= 'home'),
    path('search/', views.search_movies, name='search_movies'),
    
]
