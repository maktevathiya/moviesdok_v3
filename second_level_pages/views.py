from django.http import JsonResponse
from django.views.decorators.http import require_POST
from user_history.models import UserHistory 
from utils.tmdb_api import fetch_media_by_genres, get_collection_details, get_person_info
from utils.request_handler import request_handler
import json
from django.shortcuts import render

@require_POST  # Ensure this view only accepts POST requests
def fetch_media_view(request):
    """
    View to fetch media by genre and page number.
    Expects JSON data with 'media_type' (str), 'genres' (list), and 'page' (int).
    Returns JSON response with separated visited and unvisited media.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            media_type = data.get('media_type')
            genres = data.get('genres', [])
            page = data.get('page', 1)

            media_results = fetch_media_by_genres(media_type, genres, page)
            visited_ids = get_visited_ids(request)

            # Separate media results into visited and unvisited
            unvisited_media = [item for item in media_results if item['id'] not in visited_ids]
            visited_media = [item for item in media_results if item['id'] in visited_ids]

            return JsonResponse({
                'unvisited_media': unvisited_media,
                'visited_media': visited_media,
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_visited_ids(request):
    """Retrieve visited TMDb IDs based on user authentication."""
    if request.user.is_authenticated:
        return set(UserHistory.objects.filter(user=request.user).values_list('tmdb_id', flat=True))
    else:
        session_id = request.session.session_key
        return set(UserHistory.objects.filter(session_id=session_id).values_list('tmdb_id', flat=True))


def choose_genre(request):
    return render(request, 'genre.html')

def collection(request, collection_id):
    info = get_collection_details(collection_id)
    return render(request, 'collection_detail.html',{
        'collection_info':info,
    })

def person_info(request,id):
    person_info = get_person_info(id)
    movies = person_info.get('combined_credits', {}).get('cast', [])

    # Track user visit
    if request.user.is_authenticated:
        UserHistory.objects.create(user=request.user, tmdb_id=person_info.get('id'), genre=None, release_date=person_info.get('birthday'), media_type='person',  title=person_info.get('name'), poster_path = person_info.get('profile_path'), rating=person_info.get('popularity'))
    else:
        # Ensure the session is created
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        UserHistory.objects.create(session_id=session_id, tmdb_id=person_info.get('id'), genre=None, release_date=person_info.get('birthday'), media_type='person',  title=person_info.get('name'), poster_path = person_info.get('profile_path'), rating=person_info.get('popularity')) 

    visited_ids = get_visited_ids(request)

            # Separate media results into visited and unvisited
    unvisited_movie = [item for item in movies if item['id'] not in visited_ids]
    visited_movie = [item for item in movies if item['id'] in visited_ids]

    return request_handler(request, 'person.html', context=person_info)