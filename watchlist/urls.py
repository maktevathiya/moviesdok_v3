from django.urls import path
from . import views

urlpatterns = [
    path('movie/<int:tmdb_id>/', views.add_to_watchlist_view, name='add_to_watchlist'),
    path('create-watchlist/', views.create_watchlist_view, name='create_watchlist'),
    path('', views.watchlist_page, name='watchlist_page'),
    path('delete/<int:watchlist_id>/', views.delete_watchlist, name='delete_watchlist'),
    path('item/delete/<int:item_id>/', views.delete_watchlist_item, name='delete_watchlist_item'),
    path('items/delete/', views.delete_multiple_watchlist_items, name='delete_multiple_watchlist_items'),  # For multiple items
    path('rename/<int:watchlist_id>/', views.rename_watchlist, name='rename_watchlist'),

]
