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
    return request_handler( request, "home.html", context)




from utils.tmdb_api import fetch_homepage_data
def hompage(request):
    data = fetch_homepage_data()
    return request_handler(request, 'home.html', data)


TMDB_API_KEY = settings.TMDB_API_KEY


def search_movies(request):
    query = request.GET.get("q", "")
    category = request.GET.get("category", "all") 
    is_fetch = request.headers.get("Accept") == "application/json" 
    category_map = {
        "movies": "movie",
        "tvseries": "tv",
        "people": "person",
        "collection": "collection"
    }

    search_url = f"https://api.themoviedb.org/3/search/{category_map.get(category, 'multi')}"
    
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "en-US",
        "include_adult": False,
        "sort_by": "popularity.desc"
    }
    results = []
    if query:
        response = requests.get(search_url, params=params)
        results = response.json().get("results")

    if is_fetch:
        return JsonResponse({"results": results})
    
    return request_handler(request, "search.html", {"results": results, "query": query, "category": category})