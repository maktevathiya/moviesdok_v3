from django.shortcuts import render
from django.contrib.auth.models import User
from watchlist.models import Watchlist, WatchlistItem
from utils.tmdb_api import get_movie_details, get_tv_show_details, get_title_details
from django.http import HttpResponseNotFound
from user_history.models import UserHistory
from django.utils import timezone

def movie_detail_view(request, tmdb_id):
    # Fetch movie details from TMDB API
    movie_details = get_movie_details(tmdb_id)
    if not movie_details:
        messsage = 'the server couldnot find the information related to this title'
        return render(request, '404.html', {
            'message': messsage
        })
    genre = movie_details.get('genres_id')
    release_date = movie_details.get('release_date')
    media_type = movie_details.get('media_type')
    title = movie_details.get('title')
    poster_path = movie_details.get('poster_path')
    rating = movie_details.get('rating')

    user_watchlists = None
    movie_in_watchlists = None

    # Track user visit
    if request.user.is_authenticated:
        UserHistory.objects.create(user=request.user, tmdb_id=tmdb_id, genre=genre, release_date=release_date, media_type=media_type, title=title, poster_path = poster_path, rating=rating)
        # Get user's watchlists
        user_watchlists = Watchlist.objects.filter(user=request.user)
        # Check if the movie is already in any of the user's watchlists
        movie_in_watchlists = WatchlistItem.objects.filter(watchlist__user=request.user, movie_id=tmdb_id).select_related('watchlist')
    else:
        # Ensure the session is created
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        UserHistory.objects.create(session_id=session_id, tmdb_id=tmdb_id, genre=genre, release_date=release_date, media_type=media_type,  title=title, poster_path = poster_path, rating=rating)
    # Render the template with the necessary context
    return render(request, 'movie_detail.html', {
        'movie_details': movie_details,
        'user_watchlists': user_watchlists,
        'movie_in_watchlists': movie_in_watchlists
    })

def tv_show_detail_view(request, tmdb_id):
    # Fetch TV show details from TMDB API
    movie_details = get_tv_show_details(tmdb_id)
    if not movie_details:
        messsage = 'the server couldnot find the information related to this title'
        return render(request, '404.html', {
            'message': messsage
        })

    genre = movie_details.get('genres_id')
    release_date = movie_details.get('release_date')
    media_type = movie_details.get('media_type')
    title = movie_details.get('title')
    poster_path = movie_details.get('poster_path')
    rating = movie_details.get('rating')

    user_watchlists = None
    movie_in_watchlists = None

    # Track user visit
    if request.user.is_authenticated:
        UserHistory.objects.create(user=request.user, tmdb_id=tmdb_id, genre=genre, release_date=release_date, media_type=media_type,  title=title, poster_path = poster_path, rating=rating)
        # Get user's watchlists
        user_watchlists = Watchlist.objects.filter(user=request.user)
        # Check if the movie is already in any of the user's watchlists
        movie_in_watchlists = WatchlistItem.objects.filter(watchlist__user=request.user, movie_id=tmdb_id).select_related('watchlist')
    else:
        # Ensure the session is created
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        UserHistory.objects.create(session_id=session_id, tmdb_id=tmdb_id, genre=genre, release_date=release_date, media_type=media_type,  title=title, poster_path = poster_path, rating=rating)
    # Render the template with the necessary context
    return render(request, 'movie_detail.html', {
        'movie_details': movie_details,
        'user_watchlists': user_watchlists,
        'movie_in_watchlists': movie_in_watchlists
    })

from utils.request_handler import request_handler

def detail_view(request, tmdb_id, media_type=None):
    data = get_title_details(tmdb_id, media_type)
    return request_handler(request, "details.html", data)