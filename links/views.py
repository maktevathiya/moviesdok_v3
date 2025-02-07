from django.shortcuts import render, redirect
from .models import Link
from django.contrib.auth.decorators import login_required
from .forms import MovieLinkForm, TVLinkForm
from utils.tmdb_api import get_title_details
from django.utils import timezone
from django.http import JsonResponse



@login_required
def add_link_page(request, media_type, tmdb_id):
    title_info = get_title_details(tmdb_id, media_type)
        
    context = {
        'movie_details': title_info,
    }

    return render(request, 'add_link_page.html', context)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Link
import json
from datetime import datetime

@login_required  
def add_link(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)


            # Extract fields from the incoming data
            quality = data.get('quality')
            media_type = data.get('media_type')
            site = data.get('site')
            audio = data.get('audio', '')
            subtitles = data.get('subtitles', '')
            decoder = data.get('decoder', '')
            format_choice = data.get('format', '')
            size = data.get('size')
            expiration = data.get('expiration')
            urls = data.get('urls')

            # Ensure that expiration is in the correct format
            if expiration:
                expiration = datetime.strptime(expiration, '%Y-%m-%d')

            # Ensure the URLs are in the correct format
            if isinstance(urls, dict):  # Multiple URLs for TV show
                link_entries = []
                for key, url in urls.items():
                    link = Link(
                        user=request.user,
                        tmdb_id=data.get('tmdb_id'),
                        url=url,
                        quality=quality,
                        site=site,
                        size=size + " " + data.get('unit', 'MB'),
                        audio=audio,
                        subtitles=subtitles,
                        decoder=decoder,
                        format=format_choice,
                        media_type=media_type,
                        expiration=expiration,
                    )
                    if 'season' in key and 'episode' in key:
                        parts = key.split('_')
                        season = parts[1].replace('season', '') if parts[1] else None
                        episode = parts[3].replace('episode', '') if parts[2] else None
                        link.season = season
                        link.episode = episode
                    link.save()
                    link_entries.append(link)
                return JsonResponse({"message": "Links added successfully.", "links": [str(link) for link in link_entries]}, status=201)

            elif isinstance(urls, str):  # Single URL for movie
                link = Link(
                    user=request.user,
                    tmdb_id=data.get('tmdb_id'),
                    url=urls,  # Single URL for movies
                    quality=quality,
                    site=site,
                    size=size + " " + data.get('unit', 'MB'),
                    audio=audio,
                    subtitles=subtitles,
                    decoder=decoder,
                    format=format_choice,
                    media_type=media_type,
                    expiration=expiration,
                )
                link.save()
                return JsonResponse({"message": "Link added successfully.", "link": str(link)}, status=201)


            return JsonResponse({"error": "Invalid media type or data format."}, status=400)

        except KeyError as e:
            return JsonResponse({"error": f"Missing required field: {str(e)}"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid HTTP method."}, status=405)



