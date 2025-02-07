import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from utils.tmdb_api import fetch_trending_movies, fetch_trending_tv_shows, fetch_trending_person
from user_history.models import UserHistory
from utils.request_handler import request_handler

def home(request):
    # Get data for the main carousel
    movies = fetch_trending_movies()
    tv_shows = fetch_trending_tv_shows()
    persons = fetch_trending_person()  # Fetch persons separately
    
    if request.user.is_authenticated:
        # Get visited TMDb IDs and their media types from user history
        visited_history = UserHistory.objects.filter(user=request.user).values_list('tmdb_id', 'media_type')
        visited_dict = {media_type: [] for media_type in ['movie', 'tv', 'person']}

        # Populate the visited_dict with TMDb IDs by media type
        for tmdb_id, media_type in visited_history:
            if media_type in visited_dict:
                visited_dict[media_type].append(tmdb_id)

        # Reorder movies using visited IDs
        reordered_movies = [
            movie for movie in movies if movie['id'] not in visited_dict['movie']
        ] + [
            movie for movie in movies if movie['id'] in visited_dict['movie']
        ]

        # Reorder TV shows using visited IDs
        reordered_tv_shows = [
            show for show in tv_shows if show['id'] not in visited_dict['tv']
        ] + [
            show for show in tv_shows if show['id'] in visited_dict['tv']
        ]

        # Reorder persons using visited IDs
        reordered_persons = [
            person for person in persons if person['id'] not in visited_dict['person']
        ] + [
            person for person in persons if person['id'] in visited_dict['person']
        ]

    else:
        # Ensure the session is created
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        
        visited_history = UserHistory.objects.filter(session_id=session_id).values_list('tmdb_id', 'media_type')
        visited_dict = {media_type: [] for media_type in ['movie', 'tv', 'person']}

        # Populate the visited_dict with TMDb IDs by media type
        for tmdb_id, media_type in visited_history:
            if media_type in visited_dict:
                visited_dict[media_type].append(tmdb_id)

        # Reorder movies using visited IDs
        reordered_movies = [
            movie for movie in movies if movie['id'] not in visited_dict['movie']
        ] + [
            movie for movie in movies if movie['id'] in visited_dict['movie']
        ]

        # Reorder TV shows using visited IDs
        reordered_tv_shows = [
            show for show in tv_shows if show['id'] not in visited_dict['tv']
        ] + [
            show for show in tv_shows if show['id'] in visited_dict['tv']
        ]

        # Reorder persons using visited IDs
        reordered_persons = [
            person for person in persons if person['id'] not in visited_dict['person']
        ] + [
            person for person in persons if person['id'] in visited_dict['person']
        ]
    
    context = {
        "movies": reordered_movies,
        "tv_shows": reordered_tv_shows,
        "person": reordered_persons,
    }
    return request_handler( request, "home.html", context=context)





def search_movies(request):
    query = request.GET.get('q')
    if query:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={settings.TMDB_API_KEY}&query={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('results', [])
            movies = [
                {
                    'title': movie.get('title') or movie.get('name'),  # 'title' for movies and 'name' for TV shows
                    'poster_path': f"https://image.tmdb.org/t/p/w200{movie['poster_path']}" if movie.get('poster_path') else None,
                    'media_type': movie['media_type'],
                    'tmdb_id': movie['id']
                }
                for movie in data
            ]
            return JsonResponse(movies, safe=False)
    return JsonResponse([], safe=False)

from utils.tmdb_api import fetch_homepage_data
def hompage(request):
    data = fetch_homepage_data()
    return request_handler(request, 'home.html', context=data)