from django.urls import path
from . import views 


urlpatterns = [
    path('genre/', views.fetch_media_view, name= 'genre'),
    path('choosegenre/', views.choose_genre, name='genre-page'),
    path('collection/<int:collection_id>', views.collection, name='collection_info'),
    path('person/<int:id>', views.person_info, name='person')
]
