# your_project/utils/tmdb_api.py

import requests
from moviesdok.settings import TMDB_API_KEY as API_KEY
from django.core.cache import cache
from django.http import JsonResponse
from time import sleep

API_KEY = API_KEY
BASE_URL = 'https://api.themoviedb.org/3'
MAX_RETRIES = 3
RETRY_DELAY = 2  



def make_api_call(url, params=None):
    for attempt in range(MAX_RETRIES):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Attempt {attempt + 1}: Failed to fetch data, status code {response.status_code}')
            print(f'{url} and {params} ')
            sleep(RETRY_DELAY) 
    return None

def get_movie_details(tmdb_id):
    # Construct the endpoint with relevant data requests appended
    endpoint = f"{BASE_URL}/movie/{tmdb_id}"
    params = {
        'api_key': API_KEY,
        'append_to_response': 'videos,credits,recommendations,external_ids'
    }

    data = make_api_call(endpoint, params)
    if not data:
        return {}
    # Extract all relevant details from the API response
    details = {
        'id': data.get('id'),
        'title': data.get('title'),
        'original_title': data.get('original_title'),
        'tagline': data.get('tagline'),
        'media_type':'movie',
        'poster': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
        'poster_path':data.get('poster_path')  if data.get('poster_path') else None,
        'backdrop': f"https://image.tmdb.org/t/p/original{data.get('backdrop_path')}" if data.get('backdrop_path') else None,
        'rating': data.get('vote_average'),
        'release_date': data.get('release_date'),
        'genres': [genre['name'] for genre in data.get('genres', [])],
        'genres_id': [genre['id'] for genre in data.get('genres', [])],
        'description': data.get('overview'),
        'runtime': data.get('runtime'),
        'status': data.get('status'),
        'homepage': data.get('homepage'),
        'production_countries': [country['name'] for country in data.get('production_countries', [])],
        'original_country':(data.get('production_countries') or [{}])[0].get('name', 'Unknown Country'),
        'spoken_languages': [language['name'] for language in data.get('spoken_languages', [])],
        'budget': data.get('budget'),
        'revenue': data.get('revenue'),
        'external_ids': data.get('external_ids', {}),
        'trailer': None,  # To be set with the trailer video
        'actors': [{
            'name': actor['name'],
            'id':actor['id'],
            'character': actor['character'],
            'profile_path': f"https://image.tmdb.org/t/p/w500{actor['profile_path']}" if actor.get('profile_path') else None
        } for actor in data.get('credits', {}).get('cast', [])],
        'crew': [{
            'name': member['name'],
            'job': member['job'],
            'department': member['department'],
            'profile_path': f"https://image.tmdb.org/t/p/w500{member['profile_path']}" if member.get('profile_path') else None
        } for member in data.get('credits', {}).get('crew', [])],
        'related_movies': [{
            'title': movie['title'],
            'tmdb_id': movie['id'],
            'poster': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else None
        } for movie in data.get('recommendations', {}).get('results', [])]
    }

    # Fetching the trailer
    for video in data.get('videos', {}).get('results', []):
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            details['trailer'] = f"https://www.youtube.com/embed/{video['key']}?modestbranding=1&rel=0"
            break

    return details





def get_tv_show_details(tmdb_id):
   # Construct the endpoint with relevant data requests appended
    endpoint = f"{BASE_URL}/tv/{tmdb_id}"
    params = {
        'api_key': API_KEY,
        'append_to_response': 'videos,credits,recommendations,external_ids,season'
    }

    data = make_api_call(endpoint, params)
    if not data:
        return {}

    # Extract all relevant details from the API response
    details = {
        'id': data.get('id'),
        'title': data.get('name'),
        'original_title': data.get('original_name'),
        'tagline': data.get('tagline'),
        'media_type':'tv',
        'poster': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
        'poster_path':data.get('poster_path')  if data.get('poster_path') else None,
        'backdrop': f"https://image.tmdb.org/t/p/original{data.get('backdrop_path')}" if data.get('backdrop_path') else None,
        'rating': data.get('vote_average'),
        'release_date': data.get('first_air_date'),
        'genres': [genre['name'] for genre in data.get('genres', [])],
        'genres_id': [genre['id'] for genre in data.get('genres', [])],
        'description': data.get('overview'),
        'status': data.get('status'),
        'homepage': data.get('homepage'),
        'production_countries': [country['name'] for country in data.get('production_countries', [])],
        'original_country': data.get('production_countries', [{}])[0].get('name','Unknown Country'),  # Assuming the first country is the original        
        'spoken_languages': [language['name'] for language in data.get('spoken_languages', [])],
        'budget': data.get('budget'),
        'revenue': data.get('revenue'),
        'external_ids': data.get('external_ids', {}),
        'trailer': None,  # To be set with the trailer video
        'seasons': [{
            'season_number': season['season_number'],
            'name': season.get('name'),
            'poster': f"https://image.tmdb.org/t/p/w500{season.get('poster_path')}" if season.get('poster_path') else None,
            'episode_count': season.get('episode_count'),
            'overview': season.get('overview')
        } for season in data.get('seasons', [])],
        'episodes': [{
            'season_number': episode['season_number'],
            'episode_number': episode['episode_number'],
            'name': episode.get('name'),
            'air_date': episode.get('air_date'),
            'overview': episode.get('overview'),
            'poster': f"https://image.tmdb.org/t/p/w500{episode.get('still_path')}" if episode.get('still_path') else None
        } for episode in data.get('episodes', [])],
        'crew': [{
            'name': member['name'],
            'job': member['job'],
            'department': member['department'],
            'profile_path': f"https://image.tmdb.org/t/p/w500{member['profile_path']}" if member.get('profile_path') else None
        } for member in data.get('credits', {}).get('crew', [])],
       'actors': [{
            'name': actor['name'],
            'id':actor['id'],
            'character': actor['character'],
            'profile_path': f"https://image.tmdb.org/t/p/w500{actor['profile_path']}" if actor.get('profile_path') else None
        } for actor in data.get('credits', {}).get('cast', [])],   
        'related_movies': [{
            'title': show['name'],
            'tmdb_id': show['id'],
            'poster': f"https://image.tmdb.org/t/p/w500{show.get('poster_path')}" if show.get('poster_path') else None
        } for show in data.get('recommendations', {}).get('results', [])],
        "season" : data.get('seasons', []),
       
    }

    # Fetching the trailer
    for video in data.get('videos', {}).get('results', []):
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            details['trailer'] = f"https://www.youtube.com/embed/{video['key']}?modestbranding=1&rel=0"
            break

    return details



def fetch_trending_movies():
    # Check if trending movies are in cache
    trending_movies =  cache.get('trending_movies')
    
    if not trending_movies:
        # Call TMDb API for trending movies with retry logic
        url = f'{BASE_URL}/trending/movie/day?api_key={API_KEY}'
        data = make_api_call(url)
        trending_movies =data.get('results', [])
       
        # Store in cache for 6 hours
        cache.set('trending_movies', trending_movies, timeout=21600)  # 6 hours in seconds

    return trending_movies

def fetch_trending_tv_shows():
    # Check if trending TV shows are in cache
    trending_tv_shows = cache.get('trending_tv_shows')
    
    if not trending_tv_shows:
        # Call TMDb API for trending TV shows with retry logic
        url = f'{BASE_URL}/trending/tv/day?api_key={API_KEY}'
        data = make_api_call(url)
        trending_tv_shows =data.get('results', [])
        
        # Store in cache for 6 hours
        cache.set('trending_tv_shows', trending_tv_shows, timeout=21600)  # 6 hours in seconds

    return trending_tv_shows

def fetch_trending_person():
    # Check if trending TV shows are in cache
    trending_person = cache.get('trending_person')
    
    if not trending_person:
        # Call TMDb API for trending TV shows with retry logic
        url = f'{BASE_URL}/trending/person/day?api_key={API_KEY}'
        data = make_api_call(url)
        trending_person =data.get('results', [])
        
        # Store in cache for 6 hours
        cache.set('trending_person', trending_person, timeout=21600)  # 6 hours in seconds

    return trending_person

def fetch_media_by_genres(media_type, genres=[], page=1):
    
    if media_type not in ['movie', 'tv']:
        raise ValueError(f"Invalid media type '{media_type}','{genres}'. Must be 'movie' or 'tv'.")
    
    # Create a genre string to add to the API call (comma-separated)
    genre_string = ','.join(map(str, genres)) if genres else ''
    
    # Build the API URL
    url = f'{BASE_URL}/discover/{media_type}?api_key={API_KEY}&page={page}&sort_by=vote_count.desc'
    
    # If genres are provided, add them to the URL
    if genre_string:
        url += f'&with_genres={genre_string}'
    
    # Make the API call
    data = make_api_call(url)
    return data.get('results', [])

def get_person_info(id):
    endpoint = f"{BASE_URL}/person/{id}"
    params = {
        'api_key':API_KEY,
        'append_to_response': 'movie_credits,tv_credits'
    }

    person_info = make_api_call(endpoint, params)
    return person_info

def discover_movies(**kwargs):
  
    # Construct the discover endpoint
    endpoint = f"{BASE_URL}/discover/movie"
    
    # Set up the parameters, include the API key
    params = {
        'api_key': API_KEY,
        # Include any additional parameters passed through kwargs (like sort, genre, etc.)
        **kwargs
    }

    # Make the API request
    response = requests.get(endpoint, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()  # Parse the JSON response

    return data  # Return the full data, let views decide what to do with it


def discover_tv(**kwargs):
   
    # Construct the discover endpoint
    endpoint = f"{BASE_URL}/discover/tv"
    
    # Set up the parameters, include the API key
    params = {
        'api_key': API_KEY,
        # Include any additional parameters passed through kwargs (like sort, genre, etc.)
        **kwargs
    }

    # Make the API request
    response = requests.get(endpoint, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()  # Parse the JSON response

    return data  # Return the full data, let views decide what to do with it


def get_collection_details(request, collection_id):
    url = f'https://api.themoviedb.org/3/collection/{collection_id}'
    params = {
        'api_key': API_KEY,
        'language': 'en-US'
    }
    
    try:
        response = requests.get(url, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            collection_data = response.json()
            return collection_data
        else:
            return JsonResponse({'error': 'Failed to fetch data from TMDB'}, status=500)
    
    except requests.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    


#new functions

# Genre mappings for movies and TV shows
MOVIE_GENRE_MAPPING = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western"
}

TV_GENRE_MAPPING = {
    10759: "Action & Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    10762: "Kids",
    9648: "Mystery",
    10763: "News",
    10764: "Reality",
    10765: "Sci-Fi & Fantasy",
    10766: "Soap",
    10767: "Talk",
    10768: "War & Politics",
    37: "Western"
}

def fetch_homepage_data_old():
    """
    Fetches all necessary data for the homepage, including:
    - Trending (all categories)
    - Trending movies
    - Trending TV shows
    - Popular persons
    - Trailers and most popular logos for all titles in Trending (all categories)

    :return: A dictionary containing all the fetched data, categorized by endpoint.
    """
    cache_key = "homepage_data"
    #cache.delete(cache_key)
    homepage_data = cache.get(cache_key)

    if not homepage_data:
        homepage_data = {
            "trending_all": [],
            "trending_movies": [],
            "trending_tv": [],
            "popular_persons": [],
        }

        # Fetch trending all categories
        trending_all_url = f"{BASE_URL}/trending/all/week"
        trending_all_params = {"api_key": API_KEY}
        trending_all_data = make_api_call(trending_all_url, trending_all_params)

        if trending_all_data and 'results' in trending_all_data:
            trending_all_data['results'].sort(key=lambda x: x.get('popularity', 0), reverse=True)
            # Filter out results where media_type is 'person'
            filtered_results = [item for item in trending_all_data['results'] if item.get('media_type') != 'person']
            
            homepage_data["trending_all"] = filtered_results
            print('Trending data for all received')
        else:
            print('Failed trending data for all ')

        # Fetch trending movies
        trending_movies_url = f"{BASE_URL}/trending/movie/week"
        trending_movies_params = {"api_key": API_KEY}
        trending_movies_data = make_api_call(trending_movies_url, trending_movies_params)
        if trending_movies_data and 'results' in trending_movies_data:
            trending_movies_data['results'].sort(key=lambda x: x.get('popularity', 0), reverse=True)
            homepage_data["trending_movies"] = trending_movies_data['results']
            print('trending data for movie recived')


        # Fetch trending TV shows
        trending_tv_url = f"{BASE_URL}/trending/tv/week"
        trending_tv_params = {"api_key": API_KEY}
        trending_tv_data = make_api_call(trending_tv_url, trending_tv_params)
        if trending_tv_data and 'results' in trending_tv_data:
            trending_tv_data['results'].sort(key=lambda x: x.get('popularity', 0), reverse=True)
            homepage_data["trending_tv"] = trending_tv_data['results']
            print('trending data for tv recived')

        # Fetch popular persons
        popular_persons_url = f"{BASE_URL}/trending/person/week"
        popular_persons_params = {"api_key": API_KEY}
        popular_persons_data = make_api_call(popular_persons_url, popular_persons_params)
        if popular_persons_data and 'results' in popular_persons_data:
            popular_persons_data['results'].sort(key=lambda x: x.get('popularity', 0), reverse=True)
            filtered_results = [item for item in popular_persons_data['results'] if item.get('known_for_department') == 'Acting']
            homepage_data["popular_persons"] = filtered_results
            print('trending data for person recived')
            
        # Replace genre numbers with names for movies and TV shows
        for category in ["trending_all", "trending_movies", "trending_tv"]:
            for item in homepage_data[category]:
                if 'genre_ids' in item:
                    # Select the correct genre mapping based on the category
                    genre_mapping = MOVIE_GENRE_MAPPING if category == "trending_movies" else TV_GENRE_MAPPING
                    # Replace genre IDs with names or remove invalid genre IDs
                    item['genres'] = [genre_mapping.get(genre_id) for genre_id in item['genre_ids'] if genre_mapping.get(genre_id)]
        

        total_items = len(homepage_data["trending_all"])
        # Fetch detailed information for each title (including videos and images)
        for i, item in enumerate(homepage_data["trending_all"], start=1):
            media_type = item.get("media_type", "")
            if media_type in ["movie", "tv"]:
                title_url = f"{BASE_URL}/{media_type}/{item['id']}"
                title_params = {"api_key": API_KEY, "append_to_response": "videos,images"}
                title_data = make_api_call(title_url, title_params)

                if title_data:
                    if 'videos' in title_data and 'results' in title_data['videos']:
                        trailers = [video for video in title_data['videos']['results'] if video['type'] == 'Trailer']
                        
                        if trailers:
                            # Try to find an English trailer (assuming trailers have a language code like 'iso_639_1')
                            english_trailer = next((trailer for trailer in trailers if trailer.get('iso_639_1') == 'en'), None)
                            
                            if english_trailer:
                                # Set the English trailer if available
                                item['trailer'] = english_trailer
                            else:
                                # Fallback to the first available trailer if no English trailer
                                item['trailer'] = trailers[0]
                        else:
                            # No trailers found, set as empty dictionary
                            item['trailer'] = {}
                    else:
                        # No videos found, set trailer as empty dictionary
                        item['trailer'] = {}

                    # Append image (logo) data
                    if 'images' in title_data and 'logos' in title_data['images']:
                        logos = title_data['images']['logos']
                        if logos:
                            # Filter logos for English language
                            english_logo = next((logo for logo in logos if logo.get('iso_639_1') == 'en'), None)
                            if english_logo:
                                item['logo'] = english_logo['file_path']
                            else:
                                # Fallback to the first available logo if no English logo is found
                                item['logo'] = logos[0]['file_path'] if logos else ""
                        else:
                            item['logo'] = ""  # No logos found, set as empty string
                    else:
                        item['logo'] = ""  # No image data, set as empty string
            
            progress = (i / total_items) * 100
        
            print(f"\rProcessing: {i}/{total_items} items ({progress:.2f}%)", end="")
        print("\nProcessing complete!")
        # Cache the combined data for 3 day
        cache.set(cache_key, homepage_data, timeout=259200)

    return homepage_data

def fetch_homepage_data():
    """
    Fetches necessary data for the homepage, including:
    - Trending movies
    - Trending TV shows
    - Popular persons
    - Trailers for each movie and TV show, embedded in their respective entries
    - Top 20 trailers based on popularity

    :return: A dictionary containing all the fetched data.
    """
    cache_key = "homepage_data"
    #cache.delete(cache_key)
    homepage_data = cache.get(cache_key)

    if not homepage_data:
        homepage_data = {
            "trending_movies": [],
            "trending_tv": [],
            "popular_persons": [],
            "top_20_trailers": []
        }

        def fetch_trending_data(media_type, category_key, genre_mapping):
            """ Fetch trending data and replace genre IDs with names """
            url = f"{BASE_URL}/trending/{media_type}/week"
            params = {"api_key": API_KEY}
            data = make_api_call(url, params)
            if data and 'results' in data:
                sorted_data = sorted(data['results'], key=lambda x: x.get('popularity', 0), reverse=True)
                
                # Replace genre IDs with names
                for item in sorted_data:
                    if 'genre_ids' in item:
                        item['genres'] = [genre_mapping.get(genre_id) for genre_id in item['genre_ids'] if genre_mapping.get(genre_id)]

                homepage_data[category_key] = sorted_data
                print(f"Trending data for {media_type} received.")
            else:
                print(f"Failed to fetch trending data for {media_type}.")

        # Fetch trending movies and TV shows with genre mapping
        fetch_trending_data("movie", "trending_movies", MOVIE_GENRE_MAPPING)
        fetch_trending_data("tv", "trending_tv", TV_GENRE_MAPPING)

        # Fetch popular persons (actors)
        popular_persons_url = f"{BASE_URL}/trending/person/week"
        popular_persons_params = {"api_key": API_KEY}
        popular_persons_data = make_api_call(popular_persons_url, popular_persons_params)

        if popular_persons_data and 'results' in popular_persons_data:
            filtered_results = [item for item in popular_persons_data['results'] if item.get('known_for_department') == 'Acting']
            homepage_data["popular_persons"] = sorted(filtered_results, key=lambda x: x.get('popularity', 0), reverse=True)
            print("Trending data for persons received.")

        top_trailers = []  # Temporary list for sorting top 20 trailers

        def fetch_trailers(category_key, media_type):
            """ Fetch trailers for a given category (movies or TV shows) and embed them in the original entry """
            for item in homepage_data[category_key]:
                title_id = item.get("id")
                if not title_id:
                    continue

                title_url = f"{BASE_URL}/{media_type}/{title_id}"
                title_params = {"api_key": API_KEY, "append_to_response": "videos,images"}
                title_data = make_api_call(title_url, title_params)

                if title_data:
                    # Extract trailers
                    trailers = [video for video in title_data.get('videos', {}).get('results', []) if video.get('type') == 'Trailer']
                    
                    if trailers:
                        english_trailer = next((trailer for trailer in trailers if trailer.get('iso_639_1') == 'en'), None)
                        selected_trailer = english_trailer if english_trailer else trailers[0]
                        
                        # Embed trailer directly into the movie/TV show entry
                        item["trailer"] = selected_trailer

                        # Store trailer for top 20 sorting
                        top_trailers.append({
                            "title": item.get("title") or item.get("name"),
                            "trailer": selected_trailer,
                            "backdrop_path": item.get("backdrop_path"),
                            "poster_path": item.get("poster_path"),
                            "popularity": item.get("popularity", 0)
                        })
                    else:
                        item["trailer"] = None  # No trailer found

                    # Extract logos
                    logos = title_data.get('images', {}).get('logos', [])
                    if logos:
                        english_logo = next((logo for logo in logos if logo.get('iso_639_1') == 'en'), None)
                        item['logo'] = english_logo['file_path'] if english_logo else logos[0]['file_path']
                    else:
                        item['logo'] = ""

        # Fetch trailers and embed them into movies and TV shows
        fetch_trailers("trending_movies", "movie")
        fetch_trailers("trending_tv", "tv")

        # Sort and store the top 20 trailers
        homepage_data["top_20_trailers"] = sorted(top_trailers, key=lambda x: x["popularity"], reverse=True)[:20]

        print("Trailers fetched, embedded, and top 20 list created.")

        # Cache the data for 3 days
        cache.set(cache_key, homepage_data, timeout=259200)

    return homepage_data


def get_title_details(tmdb_id, media_type):
    endpoint = f"{BASE_URL}/{media_type}/{tmdb_id}"
    if media_type == 'tv':
        params = {
            'api_key': API_KEY,
            'append_to_response': 'videos,credits,recommendations,external_ids,season/1,'
        }
    else:
        params = {
            'api_key': API_KEY,
            'append_to_response': 'videos,credits,recommendations,external_ids'
        }
    title_data = make_api_call(endpoint, params)
    if 'season/1' in title_data:
        title_data["season_1"] = title_data.pop("season/1")
    for item in title_data["recommendations"]["results"]:
        category = item["media_type"]
        if 'genre_ids' in item:
            # Select the correct genre mapping based on the category
            genre_mapping = MOVIE_GENRE_MAPPING if category == "movie" else TV_GENRE_MAPPING
            # Replace genre IDs with names or remove invalid genre IDs
            item['genres'] = [genre_mapping.get(genre_id) for genre_id in item['genre_ids'] if genre_mapping.get(genre_id)]
 
    return title_data
