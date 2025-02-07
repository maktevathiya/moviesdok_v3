import requests
from homepage.models import MovieCollection, Movie
from django.core.management.base import BaseCommand

# TMDB API Key and Base URL
API_KEY = '576b7f218633cca086cfcd05227957ed'
SEARCH_URL = 'https://api.themoviedb.org/3/search/collection?api_key={}&language=en-US&query={}&page=1'

class Command(BaseCommand):
    help = 'Fetches collections from TMDb by name and stores them in the database'

    def handle(self, *args, **kwargs):
        collection_names = []
        
        # Loop through each collection name
        for collection_name in collection_names:
            collection_data = self.get_collection_data_by_name(collection_name)
            if collection_data:
                # Save the main collection
                movie_collection = MovieCollection.objects.create(
                    name=collection_data['name'],
                    overview=collection_data['overview'],
                    poster_path=collection_data['poster_path'],
                    backdrop_path=collection_data['backdrop_path']
                )

                # Save all parts (movies) in the collection
                for movie_data in collection_data['parts']:
                    Movie.objects.create(
                        collection=movie_collection,
                        title=movie_data['title'],
                        original_title=movie_data['original_title'],
                        overview=movie_data['overview'],
                        poster_path=movie_data['poster_path'],
                        backdrop_path=movie_data['backdrop_path'],
                        media_type=movie_data['media_type'],
                        adult=movie_data['adult'],
                        original_language=movie_data['original_language'],
                        release_date=movie_data['release_date'],
                        genre_ids=movie_data['genre_ids'],
                        popularity=movie_data['popularity'],
                        video=movie_data['video'],
                        vote_average=movie_data['vote_average'],
                        vote_count=movie_data['vote_count']
                    )
                self.stdout.write(self.style.SUCCESS(f"Successfully added collection {collection_data['name']}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to find or fetch data for collection '{collection_name}'"))

    def get_collection_data_by_name(self, collection_name):
        """
        Fetches collection data from TMDb API by collection name and returns it.
        """
        url = SEARCH_URL.format(API_KEY, collection_name)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Check if collections were found
            if data.get('results'):
                collection_data = data['results'][0]  # Assume first result is the correct one
                collection_details = {
                    'name': collection_data.get('name'),
                    'overview': collection_data.get('overview'),
                    'poster_path': collection_data.get('poster_path'),
                    'backdrop_path': collection_data.get('backdrop_path'),
                    'parts': []
                }

                # Fetch the parts (movies) of the collection
                collection_id = collection_data.get('id')
                collection_details['parts'] = self.get_collection_parts(collection_id)
                return collection_details

        return None

    def get_collection_parts(self, collection_id):
        """
        Fetches the parts (movies) of the collection by collection ID and returns the list.
        """
        url = f"https://api.themoviedb.org/3/collection/{collection_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Extract the parts (movies) of the collection
            parts = []
            for part in data.get('parts', []):
                parts.append({
                    'title': part.get('title'),
                    'original_title': part.get('original_title'),
                    'overview': part.get('overview'),
                    'poster_path': part.get('poster_path'),
                    'backdrop_path': part.get('backdrop_path'),
                    'media_type': part.get('media_type'),
                    'adult': part.get('adult'),
                    'original_language': part.get('original_language'),
                    'release_date': part.get('release_date')if part.get('release_date') != "" else None,
                    'genre_ids': part.get('genre_ids'),
                    'popularity': part.get('popularity'),
                    'video': part.get('video'),
                    'vote_average': part.get('vote_average'),
                    'vote_count': part.get('vote_count')
                })
            return parts
        return []

