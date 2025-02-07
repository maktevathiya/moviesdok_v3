from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import WatchlistForm, RenameWatchlistForm
from .models import Watchlist, WatchlistItem
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import json

@login_required
@require_POST
def add_to_watchlist_view(request, tmdb_id):
    """View to handle adding or removing a movie from a watchlist via AJAX."""
    # Check if the request is an AJAX request
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request.'})

    user = request.user

    form = WatchlistForm(user, request.POST)
    if form.is_valid():
        selected_watchlist_id = form.cleaned_data['watchlist']
        title = request.POST.get('title')  # New field
        poster_path = request.POST.get('poster_path')  # New field
        rating = request.POST.get('rating')  # New field
        release_date = request.POST.get('release_date')  # New field
        genres = request.POST.get('genres')  # New field
        media_type = request.POST.get('media_type')  # New field

        # Remove the movie from all watchlists if it's already present
        WatchlistItem.objects.filter(watchlist__user=user, movie_id=tmdb_id).delete()

        if selected_watchlist_id != 'none':
            # If a valid watchlist is selected, add the movie to the new watchlist
            selected_watchlist = Watchlist.objects.get(id=selected_watchlist_id)
            WatchlistItem.objects.create(
                watchlist=selected_watchlist,
                movie_id=tmdb_id,
                title=title,  # New field
                poster_path=poster_path,  # New field
                rating=rating,  # New field
                release_date=release_date,  # New field
                genres=genres,  # New field
                media_type=media_type,  # New field

            )

            # Return success response with the watchlist name
            return JsonResponse({'success': True, 'watchlist_name': selected_watchlist.name})
        else:
            # If 'none' was selected, no specific watchlist to return
            return JsonResponse({'success': True, 'watchlist_name': None})

    # If the form is invalid
    return JsonResponse({'success': False, 'message': 'Form is invalid.'})


@login_required
@require_POST
def create_watchlist_view(request):
    watchlist_name = request.POST.get('watchlist_name', '').strip()
    
    if watchlist_name:
        # Create a new watchlist for the user
        watchlist, created = Watchlist.objects.get_or_create(user=request.user, name=watchlist_name)
        if created:
            return JsonResponse({'success': True, 'message': 'Watchlist created successfully!'})
        else:
            return JsonResponse({'success': False, 'message': 'A watchlist with this name already exists.'})
    else:
        return JsonResponse({'success': False, 'message': 'Please enter a valid watchlist name.'})


@login_required
def watchlist_page(request):
    user = request.user
    watchlists = Watchlist.objects.filter(user=user)

    context = {
        'watchlists': watchlists
    }
    return render(request, 'watchlist_page.html', context)

@login_required
def delete_watchlist(request, watchlist_id):
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)

    # Prevent deletion of the default watchlist
    if watchlist.is_default:
        return JsonResponse({'success': False, 'message': 'Default watchlist cannot be deleted.'})

    if request.method == 'POST':
        watchlist.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required
def delete_watchlist_item(request, item_id):
    item = get_object_or_404(WatchlistItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required
def delete_multiple_watchlist_items(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON data from the request body
            item_ids = data.get('item_ids', [])  # Get the list of item IDs
            
            # Perform deletion only if there are item IDs
            if item_ids:
                items_deleted = WatchlistItem.objects.filter(id__in=item_ids, watchlist__user=request.user).delete()
                return JsonResponse({'success': True, 'deleted_count': items_deleted[0]})
            else:
                return JsonResponse({'success': False, 'message': 'No items selected for deletion.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def rename_watchlist(request, watchlist_id):
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    if request.method == 'POST':
        new_name = request.POST.get('name')
        if new_name:
            watchlist.name = new_name
            watchlist.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})