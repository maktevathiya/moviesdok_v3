import uuid
import string
import requests
import json
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import User
from .models import LinkedAccount, MediaInfo, FileInfo, SessionInfo, TemporaryFileInfo
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from itertools import islice

# Telegram Bot Token and API URL
TELEGRAM_API_URL = "https://api.telegram.org/bot7823912250:AAHoQJtAVxuXMniCR0xe4mn8lSL1zW7Hsq0/"
TMDB_API_URL = "https://api.themoviedb.org/3/"
TMDB_API_KEY = "576b7f218633cca086cfcd05227957ed"


def send_telegram_message(chat_id, text=None, reply_markup=None, media=None):

    if media:
        # Send a single media file (photo) with optional caption
        url = f"{TELEGRAM_API_URL}sendPhoto"
        data = {
            "chat_id": chat_id,
            "photo": media,
            "caption": text if text else None,  # Use the text as a caption if provided
            
        }
    else:
        # Send a text message
        url = f"{TELEGRAM_API_URL}sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text if text else "",  # Send a blank message if no text provided
            
        }

    # Add reply_markup if provided
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    # Send the request to Telegram's API
    response = requests.post(url, json=data)

    # Ensure the response is successful
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.status_code}")
        print(response.json())  # Log the error response for debugging


def send_media(chat_id, file_list):
    # Dictionary to store files grouped by their type
    media_types = {'Video': [], 'Audio': [], 'Document': [], 'Photo': []}

    # Group files by type
    for file in file_list:
        file_type = file['file_type']  # No need to change case as it's already capitalized
        if file_type in media_types:
            media_types[file_type].append(file['file_id'])
        else:
            print(f"Unsupported file type: {file_type}")

    # Handle sending files by type
    for media_type, file_ids in media_types.items():
        if len(file_ids) > 1:
            # Split into chunks of 10 (Telegram limit for sendMediaGroup)
            chunks = [file_ids[i:i + 10] for i in range(0, len(file_ids), 10)]
            for chunk in chunks:
                url = f"{TELEGRAM_API_URL}sendMediaGroup"
                media_chunk = [{"type": media_type.lower(), "media": file_id} for file_id in chunk]
                data = {
                    "chat_id": chat_id,
                    "media": json.dumps(media_chunk)
                }
                response = requests.post(url, data=data)
                if response.status_code == 200:
                    print(f"{media_type} group sent successfully!")
                else:
                    print(f"Failed to send {media_type} group: {response.status_code}")
                    print(response.json())  # Log the error response for debugging
        elif len(file_ids) == 1:
            # Send a single file of that type
            url = f"{TELEGRAM_API_URL}send{media_type}"
            data = {
                "chat_id": chat_id,
                media_type.lower(): file_ids[0]
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print(f"{media_type} sent successfully!")
            else:
                print(f"Failed to send {media_type}: {response.status_code}")
                print(response.json())  # Log the error response for debugging


def delete_message(chat_id, message_id):
    url = f"{TELEGRAM_API_URL}deleteMessage"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Message deleted successfully!")
    else:
        print(f"Failed to delete message: {response.status_code}")
        print(response.json())  # Log the error response for debugging



def edit_message(chat_id, message_id, new_text=None, photo=None, reply_markup=None):
    if photo:
        # If a photo is provided, use the editMessageMedia method
        url = f"{TELEGRAM_API_URL}editMessageMedia"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "media": json.dumps({
                "type": "photo", 
                "media": photo,
                "caption": new_text if new_text else None
            })
        }
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        else:
            # Remove inline keyboard by setting reply_markup to an empty array
            data['reply_markup'] = json.dumps({"inline_keyboard": []})


    else:
        # If no photo, edit the text as before
        url = f"{TELEGRAM_API_URL}editMessageText"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text if new_text else ""
        }
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        else:
            # Remove inline keyboard by setting reply_markup to an empty array
            data['reply_markup'] = json.dumps({"inline_keyboard": []})
    # Sending the request to Telegram API
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("Message updated successfully!")
    else:
        print(f"Failed to update message: {response.status_code}")
        print("Response:", response.json())


def remove_buttons(chat_id, message_id):
    url = f"{TELEGRAM_API_URL}editMessageReplyMarkup"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Buttons removed successfully!")
    else:
        print(f"Failed to remove buttons: {response.status_code}")
        print(response.json())  # Log the error response for debugging

#to delete the session
def delete_session(chat_id, unique_id, tmdb_id, message_id):
    session = SessionInfo.objects.filter(chat_id=chat_id, unique_id=unique_id)
    if session:
        session.delete()
        edit_message(
            chat_id,
            message_id,
            f"your session with tmdb id({tmdb_id}) has been deleted"
        )
        return JsonResponse({"status": "session info deleted"})
    else:
        edit_message(
            chat_id,
            message_id,
            f"you do not have any session"
        )
        return JsonResponse({"status": "session was not found."})
        

#saving session data to the main database
def close_bundle(chat_id, unique_id, tmdb_id):
    try:
        # Fetch the SessionInfo instance based on provided parameters
        session_info = SessionInfo.objects.get(chat_id=chat_id, unique_id=unique_id, tmdb_id=tmdb_id)
        temp_files = TemporaryFileInfo.objects.filter(unique_id = unique_id)
        if temp_files.exists():
            # Start a database transaction
            with transaction.atomic():
                # Create a new MediaInfo instance
                media_info = MediaInfo.objects.create(
                    unique_id=session_info.unique_id,
                    description=session_info.description,
                    from_id=session_info.from_id,
                    tmdb_id=session_info.tmdb_id,
                    media_type=session_info.media_type,
                    media_content=session_info.media_content,
                    season=session_info.season,
                    no_of_files=TemporaryFileInfo.objects.filter(unique_id=session_info).count(),
                )

                # Create corresponding FileInfo records
                file_info_objects = [
                    FileInfo(
                        unique_id=media_info,
                        file_id=temp_file.file_id,
                        mime_type=temp_file.mime_type,
                        file_name=temp_file.file_name,
                        file_size=temp_file.file_size,
                        file_type = temp_file.file_type
                    )
                    for temp_file in temp_files
                ]
                FileInfo.objects.bulk_create(file_info_objects)


                # Delete the SessionInfo record
                session_info.delete()

                send_telegram_message(
                    chat_id,
                    f"your bundle for tmdb id: {tmdb_id} has been closed and saved"
                )

            return JsonResponse({"status":"bundle closed and saved"})
        else:
            send_telegram_message(chat_id, f"you do not have uploaded any files, you first have to upload than press close button.")
            return JsonResponse({"status":"error", "message":"no file uploaded"})
    except SessionInfo.DoesNotExist:
        send_telegram_message(chat_id, "your session doesnot seems to exists.")
        return JsonResponse({"status":"bundle not exists"})
    except Exception as e:
        send_telegram_message(chat_id, "there seems to be a problem with server try again later")
        return JsonResponse({"status": "error", "message": str(e)})

# Function to generate unique ID
def generate_unique_id():
    # Generate a UUID and convert it to a string
    unique_id = str(uuid.uuid4().int)  # Get the UUID as an integer
    # Take the first 10 digits from the UUID integer
    return unique_id[:20]

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            

            if "message" in data:
                # Handle regular messages
                message = data.get('message', {})
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                # Check if any file is sent
                if "photo" in message:
                    largest_photo = message['photo'][-1]
                    # Handle photo file
                    return save_file(chat_id, largest_photo, 'Photo')
                elif "video" in message:
                    # Handle video file
                    return save_file(chat_id, message.get('video'), 'Video')
                elif "audio" in message:
                    # Handle audio file
                    return save_file(chat_id, message.get('audio'), 'Audio')
                elif "document" in message:
                    # Handle document file
                    return save_file(chat_id, message.get('document'), 'Document')
                
                if text.startswith('/start'):
                    params = text.split('_')
                    if len(params) == 4:
                       
                        tmdb_id = params[1]
                        media_type = params[3]

                        if tmdb_id and media_type:
                            return start_function(chat_id, tmdb_id, media_type)
                        else:
                            return start_function(chat_id)  # Default behavior
                    else:
                        return start_function(chat_id)
                    
                if text.lower().startswith('id:'):
                    parts = text.split(':', 1)  # Limit split to one colon
                    if len(parts) == 2:
                        tmdb_id = parts[1].strip()
                        if tmdb_id.isdigit():  # Check if TMDb ID is numeric
                            return tmdb_id_function(chat_id, tmdb_id)
                        else:
                            send_telegram_message(chat_id, "Invalid ID format. TMDb IDs must be numeric.")
                            return JsonResponse({"status": "error", "message": "Non-numeric TMDb ID"})
                    else:
                        send_telegram_message(chat_id, "Please use the correct format: 'id:<TMDb_ID>'.")
                        return JsonResponse({"status": "error", "message": "Invalid ID format"})

                    
                if text.lower().startswith('ds:'):
                    parts = text.split(':', 1)
                    description = parts[1].strip()
                    if description:
                        return save_description_function(chat_id, description)
                    else:
                        send_telegram_message(chat_id, "The description cannot be empty. Please provide a valid description after 'ds:'.")
                        return JsonResponse({"status": "error", "message": "Empty description"})


            elif "callback_query" in data:
                # Handle button presses
                callback_query = data['callback_query']
                callback_data = callback_query['data']
                chat_id = callback_query['message']['chat']['id']
                from_id = callback_query['from']['id']
                message_id = callback_query['message']['message_id']

                # Parse callback data
                action, tmdb_id, media_type,unique_id, media_content = callback_data.split(":")
                
                if action == "create":
                    return create_bundle(chat_id, tmdb_id, media_type, from_id, season=media_content, message_id= message_id)
                elif action == "mediaselection":
                    return search_function(chat_id, tmdb_id, media_type, message_id)
                elif action == "discard":
                    return delete_session(chat_id, unique_id, tmdb_id, message_id)
                elif action == "close":
                    return close_bundle(chat_id, unique_id, tmdb_id)
                elif action == 'contentselection':
                    return content_selection(chat_id, unique_id, media_content, message_id)
                elif action == 'seasonselection':
                    return season_selection(chat_id, unique_id, media_content, message_id)
                elif action == 'continue':
                    return continue_function(chat_id, message_id)
                elif action == 'retry':
                    return start_function(chat_id)
                else:
                    send_telegram_message(chat_id, f"this command or action doesn't seems to exist.")

            # If no known commands, send an unknown command message
            if 'chat_id' in locals():  # Ensure chat_id is available before sending
                send_telegram_message(chat_id, "Unknown command. Please try again.")
            return JsonResponse({"status": "unknown command"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "invalid method"})

def start_function(chat_id, tmdb_id=None, media_type=None):
    # Check if the user with chat_id has any session in the session database
    session = SessionInfo.objects.filter(chat_id=chat_id).first()
    if session: 
        if session.media_content:
            if session.season:  
                if session.description:
                    files = TemporaryFileInfo.objects.filter(unique_id=session.unique_id)    
                    if files.exists():
                        file_list = [{'file_id': file.file_id, 'file_type': file.file_type} for file in files]
                        message =(f"You still have a bundle open for the tmdb id:{session.tmdb_id} \n"
                            f"Description: {session.description}\n"
                            f"media content in the bundle:{session.media_content}\n"
                            f"Related to season:{session.season}\n"
                            "if you want to add more files start uploading them.\n if you want to delete the bundle press discard.\nif you wants to close the bundle press close\n here are all the files you have shared till now")
                        send_telegram_message(
                            chat_id,
                            message,
                            reply_markup={
                                "inline_keyboard": [
                                    [
                                        {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                                        {"text": "Close", "callback_data": f"close:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"}
                                    ]
                                ]
                            }
                        )
                        send_media(chat_id, file_list)
                        return JsonResponse({"status": "ok"})
                    else:
                        message =(f"You still have a bundle open for the tmdb id:{session.tmdb_id} \n"
                            f"Description: {session.description}\n"
                            f"media content in the bundle:{session.media_content}\n"
                            f"Related to season:{session.season}\n"
                            "either start uploading files or discard the bundle")
                        send_telegram_message(
                            chat_id,
                            message,
                            reply_markup={
                                "inline_keyboard": [
                                    [
                                        {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                                    ]
                                ]
                            },
                        )
                        return JsonResponse({"status": "ok"})
                else: #if discription doesnot exit
                    message =(
                        f"You still have a bundle open for the tmdb id :{session.tmdb_id} \n"
                        f"media content in the bundle:{session.media_content}\n"
                        f"Related to season:{session.season}\n"
                        "if you want to continue give the description by starting the message wiht (ds:) or press discard to delete the bundle")
                    send_telegram_message(
                            chat_id,
                            message,
                            reply_markup={
                                "inline_keyboard": [
                                    [
                                        {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                                    ]
                                ]
                            },
                        )
                    return JsonResponse({"status": "ok"})
            else: #if season doesnot exits
                message=(
                    f"You still have a bundle open for the tmdb id:{session.tmdb_id} \n"
                    f"media content in the bundle:{session.media_content}\n"
                    "you are currently on the step of choosing the season related to your bundle. Either you continue or delelte the bundle using discard"
                    
                )
                send_telegram_message(
                    chat_id,
                    message,
                    reply_markup={
                        "inline_keyboard":[[
                            {"text":"Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                        ]]
                    }
                )
                return JsonResponse({"status":"ok"})
        else: #if no media content is choosen like video or poster something
            message=(
                    f"You still have a bundle open for the tmdb id:{session.tmdb_id} \n"
                    "you are currently on the step of choosing the media content for your bundle. Either you continue or delelte the bundle using discard"
                    
                )
            send_telegram_message(
                    chat_id,
                    message,
                    reply_markup={
                        "inline_keyboard":[[
                            {"text":"Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                        ]]
                    }
                )
            return JsonResponse({"status":"ok"})
    else:  # No session exists
        # If TMDB ID and media type are provided, proceed to the search function
        if tmdb_id and media_type:
            return search_function(chat_id, tmdb_id, media_type)
        else:
            send_telegram_message(
                chat_id,
                "Please type the TMDB ID of the title in this format: [id:TMDB_ID]."
            )
            return JsonResponse({"status": "ok"})


def tmdb_id_function(chat_id, tmdb_id):
    session = SessionInfo.objects.filter(chat_id=chat_id).first()
    # Check if a session with the same chat_id already exists
    if session:
        send_telegram_message(chat_id, f"there is already a session that exists for this tmdb id:{session.tmdb_id}", reply_markup={
            "inline_keyboard": [
                [
                    {"text":"Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                    {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                ]
            ]
        })
        return JsonResponse({"status":"ok"})
    
    send_telegram_message(chat_id, "Please choose the media type.", reply_markup={
                "inline_keyboard": [
            [
                {"text": "Movie", "callback_data": f"mediaselection:{tmdb_id}:movie:0:0"},
                {"text": "Series", "callback_data": f"mediaselection:{tmdb_id}:tv:0:0"}
            ]
        ]})
    return JsonResponse({"status":"media selection sent"})

def search_function(chat_id, tmdb_id, media_type, message_id=None):
    try:
        url = f"{TMDB_API_URL}{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # Extract general details
            title = data.get('name') if media_type == 'tv' else data.get('title', 'Unknown Title')
            year = data.get('release_date', 'Unknown')[:4] if media_type == 'movie' else data.get('first_air_date', 'Unknown')[:4]
            description = data.get('overview', 'No description available.')
            genres = ", ".join([genre.get('name', 'Unknown') for genre in data.get('genres', [])])
            popularity = f"{data.get('popularity', 0):.1f}"
            vote_average = f"{data.get('vote_average', 0):.1f}"
            vote_count = data.get('vote_count', 'N/A')
            # Extract cast (limit to 5 and handle cases where fewer cast members are available)
            cast_list = data.get('credits', {}).get('cast', [])
            cast = ", ".join([actor.get('name', 'Unknown') for actor in cast_list[:5]]) if cast_list else "No cast information available."

            # Extract TV-specific details
            seasons = data.get('number_of_seasons', 0) if media_type == 'tv' else 0
            season_message = f"This title has {seasons} season(s)." if seasons else ""

            # Build the message
            message = (
                f"*Title:* {title}\n\n"
                f"*Year:* {year}\n"
                f"*Genres:* {genres}\n"
                f"*Cast:* {cast}\n"
                f"*Vote Average:* {vote_average} ({vote_count} votes)\n\n___________________________\n\n"
                f"*Description:* {description}\n"
                f"{season_message}"
            )


            # Get the poster image URL (assuming the data has the 'poster_path' field)
            image_url = data.get('poster_path')  # Example: '/path/to/image.jpg'
            full_image_url = f"https://image.tmdb.org/t/p/w500{image_url}" if image_url else None
            if message_id:
                edit_message(chat_id, message_id, message, reply_markup={
                    "inline_keyboard": [
                    [
                        {"text":"Retry", "callback_data":f"retry:0:0:0:0"},
                        {"text": "Create Bundle", "callback_data": f"create:{tmdb_id}:{media_type}:0:{seasons}"},
                    ]
                ]
                },  photo=full_image_url)
                return JsonResponse({"status": "search completed"})
            else:
                send_telegram_message(chat_id, message, reply_markup={
                    "inline_keyboard": [
                    [
                        {"text":"Retry", "callback_data":f"retry:0:0:0:0"},
                        {"text": "Create bundle", "callback_data": f"create:{tmdb_id}:{media_type}:0:{seasons}"},
                    ]
                ]
                },  media=full_image_url)
                return JsonResponse({"status": "search completed"})
        else:
            edit_message(chat_id,message_id, f"Either your tmdb id or media type is wrong. please try again")
            return JsonResponse({"status":"ok"})
    except Exception as e:
        send_telegram_message(chat_id, "An error occurred while processing your request. Please try again.")
        return JsonResponse({"status": "error", "message": str(e)})
    
# function to create session 
def create_bundle(chat_id, tmdb_id, media_type, from_id, description=None, media_content=None, season=None, message_id=None):
    session = SessionInfo.objects.filter(chat_id=chat_id).first()
    # Check if a session with the same chat_id already exists
    if session:
        remove_buttons(chat_id, message_id)
        send_telegram_message(chat_id, f"there is already a session that exists for this tmdb id:{session.tmdb_id}", reply_markup={
            "inline_keyboard": [
                [
                    {"text":"Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                    {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                ]
            ]
        })
        return JsonResponse({"status":"ok"})

    unique_id = generate_unique_id()


    try:
        # Create the session instance
        session = SessionInfo.objects.create(
            unique_id=unique_id,
            chat_id=chat_id,
            tmdb_id=tmdb_id,
            media_type=media_type,
            from_id=from_id,
            description=description,
            media_content=media_content,
            available_season=int(season)
        )
        message = (
            f"Your bundle has been created.\n"
            f"Proceeding with TMDB ID: {tmdb_id} and Media Type: {media_type}.\n"
            f"\n_____________________\n\n"
            f"Choose one or more of media content that your bundle will have:\n"
            f"- First time you press a media format, it will be added.\n"
            f"- If you press the same button again, it will be removed.\n"
            "Press 'Selection Complete' when done."
        )    
        remove_buttons(chat_id, message_id)
        send_telegram_message(
            chat_id,
            message,
            reply_markup={
                "inline_keyboard": [
                [
                    {"text": "Video", "callback_data": f"contentselection:{tmdb_id}:{media_type}:{unique_id}:video"},
                    {"text": "Poster", "callback_data": f"contentselection:{tmdb_id}:{media_type}:{unique_id}:poster"},
                    {"text": "Backdrop", "callback_data": f"contentselection:{tmdb_id}:{media_type}:{unique_id}:backdrop"},
                    ],
                    [
                    {"text": "Subtitles", "callback_data": f"contentselection:{tmdb_id}:{media_type}:{unique_id}:subtitles"},
                    {"text": "Soundtrack", "callback_data": f"contentselection:{tmdb_id}:{media_type}:{unique_id}:soundtrack"},
                ],
                [
                    {"text": "Finish Selection", "callback_data": f"contentselection:{tmdb_id}:{media_type}:{unique_id}:finish"},
                ]
            ]
            }
        )
        return JsonResponse({"status":"ok"})
    except ValidationError as e:
        remove_buttons(chat_id, message_id)
        send_telegram_message(chat_id, f"there seems to be a data intergerity error:{str(e)}\n you should start again it might be related to the server or the data you have given.")
        return JsonResponse({"status":"ok"})
    except Exception as e:
        remove_buttons(chat_id, message_id)
        send_telegram_message(chat_id, f"there seems to be a error.\n you should start again or wait sometime it might be related to the server or the data you have given.")
        return JsonResponse({"status":"ok"})

def content_selection(chat_id, unique_id, media_content, message_id):
    try:
        # Fetch the session instance by `unique_id` and `chat_id`
        session = SessionInfo.objects.filter(unique_id=unique_id, chat_id=chat_id).first()
        if not session:
            delete_message(chat_id,message_id)
            # If session does not exist, notify the user
            send_telegram_message(chat_id, "No active session found. Please start a new bundle. to do so you should give the tmdb id as in this format ('id:')")
            return JsonResponse({"status": "ok"})

        if media_content == "finish":
            if session.media_content:
                if session.media_type == "tv" and session.available_season:
                    # Generate buttons for each available season
                    buttons = [
                        {"text": f"Season {i}", "callback_data": f"seasonselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:{i}"}
                        for i in range(1, int(session.available_season) + 1)
                    ]
                    # Send season selection message with buttons
                    message = (
                        f"Proceeding with TMDB ID: {session.tmdb_id} and Media Type: {session.media_type}.\n"
                        f"\n_____________________\n\n"
                        f"your bundle content include:{session.media_content}"
                        f"\n_____________________\n\n"
                        "Select the seasons you want to include in your bundle. Press the same button to deselect.",
                    )  
                    edit_message(
                        chat_id,
                        message_id,
                        message,
                        reply_markup={
                            "inline_keyboard": [
                                *[group for group in [buttons[i:i + 3] for i in range(0, len(buttons), 3)]],
                                [{"text": "Finish Selection", "callback_data": f"seasonselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:finish"}]  # The "finish selection" button
                            ]
                        }
                    )
                    return JsonResponse({"status": "ok"})

                elif session.media_type == "movie":
                    session.season = "movie"
                    session.save()
                    message = (
                        f"Proceeding with TMDB ID: {session.tmdb_id} and Media Type: {session.media_type}.\n"
                        f"\n_____________________\n\n"
                        f"your bundle content include:{session.media_content}"
                        f"\n_____________________\n\n"
                        f"Your content category of your bundle is completed.\nnow please give a short description about your bundle like: what kind of files, qualities of the files, language of files inside the bundle.\n IMPORTANT: your description should start with (ds:)."
                    )  
                    edit_message(
                        chat_id,
                        message_id,
                        message,
                    )
                    return JsonResponse({"status": "ok"})
            else:
                message = (
                    f"Proceeding with TMDB ID: {session.tmdb_id} and Media Type: {session.media_type}.\n"
                    f"\n_____________________\n\n"
                    f"your bundle content include:{updated_content}"
                    f"\nyou cannot leave content catogary empty.\n you have to tell what kind file is in your bundle\n"
                    f"\n_____________________\n\n"
                    f"Choose one or more of media content that your bundle will have:\n"
                    f"- First time you press a media format, it will be added.\n"
                    f"- If you press the same button again, it will be removed.\n"
                    "Press 'Selection Complete' when done."
                )    

                edit_message(
                    chat_id, 
                    message_id,
                    message,
                    reply_markup={
                        "inline_keyboard": [
                        [
                            {"text": "Video", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:video"},
                            {"text": "Poster", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:poster"},
                            {"text": "Backdrop", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:backdrop"},
                            ],
                            [
                            {"text": "Subtitles", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:subtitles"},
                            {"text": "Soundtrack", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:soundtrack"},
                        ],
                        [
                            {"text": "Finish selection", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:finish"},
                        ]
                    ]
                    }
                )
                return JsonResponse({"status":"ok"})
            
        # Check if the media_content already exists
        if session.media_content and media_content in session.media_content.split(","):
            # If present, remove it
            updated_content = ",".join(
                [content for content in session.media_content.split(",") if content != media_content]
            )
            session.media_content = updated_content if updated_content else None
            session.save()
            message = (
                f"Proceeding with TMDB ID: {session.tmdb_id} and Media Type: {session.media_type}.\n"
                f"\n_____________________\n\n"
                f"your bundle content include:{updated_content}"
                f"\n_____________________\n\n"
                f"Choose one or more of media content that your bundle will have:\n"
                f"- First time you press a media format, it will be added.\n"
                f"- If you press the same button again, it will be removed.\n"
                "Press 'Selection Complete' when done."
            )    

            edit_message(
                chat_id, 
                message_id,
                message,
                reply_markup={
                    "inline_keyboard": [
                    [
                        {"text": "Video", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:video"},
                        {"text": "Poster", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:poster"},
                        {"text": "Backdrop", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:backdrop"},
                        ],
                        [
                        {"text": "Subtitles", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:subtitles"},
                        {"text": "Soundtrack", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:soundtrack"},
                    ],
                    [
                        {"text": "Finish selection", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:finish"},
                    ]
                ]
                }
            )
            
        else:
            # If not present, add it
            if session.media_content:
                session.media_content += f",{media_content}"
            else:
                session.media_content = media_content
            session.save()
            message = (
                f"Proceeding with TMDB ID: {session.tmdb_id} and Media Type: {session.media_type}.\n"
                f"\n_____________________\n\n"
                f"your bundle content include:{session.media_content}"
                f"\n_____________________\n\n"
                f"Choose one or more of media content that your bundle will have:\n"
                f"- First time you press a media format, it will be added.\n"
                f"- If you press the same button again, it will be removed.\n"
                "Press 'Selection Complete' when done."
            )    

            edit_message(
                chat_id, 
                message_id,
                message,
                reply_markup={
                    "inline_keyboard": [
                    [
                        {"text": "Video", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:video"},
                        {"text": "Poster", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:poster"},
                        {"text": "Backdrop", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:backdrop"},
                        ],
                        [
                        {"text": "Subtitles", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:subtitles"},
                        {"text": "Soundtrack", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:soundtrack"},
                    ],
                    [
                        {"text": "Finish selection", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{unique_id}:finish"},
                    ]
                ]
                }
            )

        return JsonResponse({"status": "ok"})

    except Exception as e:
        # Handle unexpected errors
        send_telegram_message(chat_id, "An unexpected error occurred. Please try again.")
        return JsonResponse({"status": "ok"})


def season_selection(chat_id, unique_id, season_number, message_id):
    try:
        # Fetch the session instance by `unique_id` and `chat_id`
        session = SessionInfo.objects.filter(unique_id=unique_id, chat_id=chat_id).first()

        if not session:
            # If session does not exist, notify the user
            delete_message(chat_id, message_id)
            send_telegram_message(chat_id, "No active session found. Please start a new bundle.")
            return JsonResponse({"status": "ok"})
        
        buttons = [
            {"text": f"Season {i}", "callback_data": f"seasonselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:{i}"}
            for i in range(1, int(session.available_season) + 1)
        ]     

        if season_number == "finish":
            if session.season:  
                message = (
                    f"Proceeding with TMDB ID: {session.tmdb_id} and Media Type: {session.media_type}.\n"
                    f"\n_____________________\n\n"
                    f"your bundle content include:{session.media_content}"
                    f"\n_____________________\n\n"
                    f"season your bundle include:{session.season}"
                    f"\n_____________________\n\n"
                    f"now please give a short description about your bundle like: what kind of files, qualities of the files, language of files inside the bundle.\n IMPORTANT: your description should start with (ds:)."
                )  
                 
                edit_message(chat_id, message_id,message)

                return JsonResponse({"status":"ok"})

            else:
                message = (
                    f"Proceeding with TMDB ID: {session.tmdb_id} and Media Type: {session.media_type}.\n"
                    f"\n_____________________\n\n"
                    f"your bundle content include:{session.media_content}"
                    f"\n_____________________\n\n"
                    f"season your bundle include:{session.season}"
                    f"\nyou have to select atleast one season\n"
                    f"\n_____________________\n\n"
                    "Select the seasons you want to include in your bundle. Press the same button to deselect.",
                )  
                edit_message(
                    chat_id,
                    message_id,
                    message,
                    reply_markup={
                        "inline_keyboard": [
                            *[group for group in [buttons[i:i + 3] for i in range(0, len(buttons), 3)]],
                            [{"text": "Finish selection", "callback_data": f"seasonselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:finish"}]  # The "finish selection" button
                        ]
                    }
                )
                return JsonResponse({"status": "ok"})


    
        # Check if the season is already selected
        if session.season and str(season_number) in session.season.split(","):
            # If present, remove it
            updated_season = ",".join(
                [season for season in session.season.split(",") if season != str(season_number)]
            )
            session.season = updated_season if updated_season else None
            session.save()

            # Send season selection message with buttons
            message = (
                f"Proceeding with TMDB ID: {session.tmdb_id} and Media Type: {session.media_type}.\n"
                f"\n_____________________\n\n"
                f"your bundle content include:{session.media_content}"
                f"\n_____________________\n\n"
                f"season your bundle include:{updated_season}"
                f"\n_____________________\n\n"
                "Select the seasons you want to include in your bundle. Press the same button to deselect.",
            )  
            edit_message(
                chat_id,
                message_id,
                message,
                reply_markup={
                    "inline_keyboard": [
                        *[group for group in [buttons[i:i + 3] for i in range(0, len(buttons), 3)]],
                        [{"text": "Finish Selection", "callback_data": f"seasonselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:finish"}]  # The "finish selection" button
                    ]
                }
            )
        else:
            # If not present, add it
            if session.season:
                session.season += f",{season_number}"
            else:
                session.season = str(season_number)
            session.save()
            message = (
                f"Proceeding with TMDB ID: {session.tmdb_id} and Media Type: {session.media_type}.\n"
                f"\n_____________________\n\n"
                f"your bundle content include:{session.media_content}"
                f"\n_____________________\n\n"
                f"season your bundle include:{session.season}"
                f"\n_____________________\n\n"
                "Select the seasons you want to include in your bundle. Press the same button to deselect.",
            )  
            edit_message(
                chat_id,
                message_id,
                message,
                reply_markup={
                    "inline_keyboard": [
                        *[group for group in [buttons[i:i + 3] for i in range(0, len(buttons), 3)]],
                        [{"text": "Finish Selection", "callback_data": f"seasonselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:finish"}]  # The "finish selection" button
                    ]
                }
            )

        return JsonResponse({"status": "ok"})

    except Exception as e:
        # Handle unexpected errors
        send_telegram_message(chat_id, "An unexpected error occurred. Please try again.")
        return JsonResponse({"status": "ok"})


def save_description_function(chat_id, description):
    # Check if session exists
    session = SessionInfo.objects.filter(chat_id=chat_id).first()
    if not session:
        send_telegram_message(
            chat_id,
            "No active session found! Please create a session before saving a description."
        )
        return JsonResponse({"status": "error", "message": "No active session"})

    # Check if `media_content` and `season` fields are filled
    missing_fields = []
    if not session.media_content:
        missing_fields.append("content")
    if not session.season:
        missing_fields.append("season")

    # Handle missing fields
    if "content" in missing_fields:
        send_telegram_message(
            chat_id,
            f"You currently have a session with TMDB ID: {session.tmdb_id}. "
            "Please update media content before saving a description or discard the session.",
            reply_markup={
                "inline_keyboard": [
                    [
                        {"text": "Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                        {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                    ]
                ]
            }
        )
        return JsonResponse({"status": "error", "message": "Missing fields: content"})

    if "season" in missing_fields:
        if session.media_type == "tv" :
            send_telegram_message(
                chat_id,
                f"You currently have a session with TMDB ID: {session.tmdb_id}. "
                "Please update season before saving a description or discard the session. ",
                reply_markup={
                    "inline_keyboard": [
                        [
                            {"text": "Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                        ]
                    ]
                }
            )
            return JsonResponse({"status": "ok"})

        elif session.media_type == "movie":
            send_telegram_message(
                chat_id,
                f"You currently have a session with TMDB ID: {session.tmdb_id}. "
                "Please update media content before saving a description or discard the session.",
                reply_markup={
                    "inline_keyboard": [
                        [
                            {"text": "Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                        ]
                    ]
                }
            )
            return JsonResponse({"status": "error", "message": "Missing fields: content"})

    # If no fields are missing, save the description
    session.description = description
    session.save()

    # Notify the user
    send_telegram_message(
        chat_id,
        f"Your description:\n**{description}**\nhas been saved for the TMDB ID: {session.tmdb_id}. "
        "Now please upload ALL files for your bundle and then press 'close' to save the bundle.",
        reply_markup={
            "inline_keyboard": [
                [{"text": "Close", "callback_data": f"close:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"}]
            ]
        }
    )
    return JsonResponse({"status": "OK"})


def save_file(chat_id, file_data, file_type):
    try:
        # Retrieve the session info using chat_id
        session = SessionInfo.objects.filter(chat_id=chat_id).first()

        if not session:
            send_telegram_message(
                chat_id,
                "No active session found! Please create a session before saving a file."
            )
            return JsonResponse({"status": "error", "message": "No active session"})

        # Check if `media_content` and `season` fields are filled
        missing_fields = []
        if not session.media_content:
            missing_fields.append("content")
        if not session.season:
            missing_fields.append("season")
        if not session.description:
            missing_fields.append("description")

        # Handle missing fields
        if "content" in missing_fields:
            send_telegram_message(
                chat_id,
                f"You currently have a session with TMDB ID: {session.tmdb_id}. "
                "Please update media content before saving a file or discard the session.",
                reply_markup={
                    "inline_keyboard": [
                        [
                            {"text": "Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                        ]
                    ]
                }
            )
            return JsonResponse({"status": "error", "message": "Missing fields: content"})

        if "season" in missing_fields:
            if session.media_type == "tv":
                                
                send_telegram_message(
                    chat_id,
                    f"You currently have a session with TMDB ID: {session.tmdb_id}. "
                    "Please update season before saving a file to do that press continue or discard the session. ",
                    reply_markup={
                        "inline_keyboard":[
                            [
                                {"text": "Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                                {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            ]
                        ]
                    }
                )
                return JsonResponse({"status": "ok"})

            elif session.media_type == "movie":
                send_telegram_message(
                    chat_id,
                    f"You currently have a session with TMDB ID: {session.tmdb_id}. "
                    "Please finish updating media content before saving a file to do that press continue or discard the session.",
                    reply_markup={
                        "inline_keyboard": [
                           
                            [
                                {"text": "Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                                {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            ]
                        ]
                    }
                )
                return JsonResponse({"status": "error", "message": "Missing fields: content"})
        
        if "description" in missing_fields:
            send_telegram_message(
                chat_id,
                f"you still have a bundle open for the tmdb id: {session.tmdb_id}\nAnd you do not have given description thats needed before the files, so either press continue or discard the bundle",
                reply_markup={
                    "inline_keyboard": [
                        [
                            {"text": "Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                        ]
                    ]
                }
            )
            return JsonResponse({"status": "error", "message":"missing: description"})


        # Extract the necessary file details
        file_id = file_data.get('file_id')
        mime_type = file_data.get('mime_type', '')  # Default to empty string if not available
        file_name = file_data.get('file_name', '')  # Default to empty string if not available
        file_size = file_data.get('file_size', 0)  # Default to 0 if not available
        file_type = file_type
        # Create a new TemporaryFileInfo instance
        TemporaryFileInfo.objects.create(
            unique_id=session,  # ForeignKey to SessionInfo
            file_id=file_id,
            mime_type=mime_type,
            file_name=file_name,
            file_size=file_size,
            file_type = file_type
        )
        send_telegram_message(chat_id, f'added\n{file_data.get('file_name', '')}')
        # Respond with a success message or handle any other necessary actions
        return JsonResponse({"status": "success", "message": "File saved successfully"})
    except Exception as e:
        send_telegram_message(chat_id, f'something went wrong while adding file,\n{file_data.get('file_name', '')}\nplease try again or after some time')
        return JsonResponse({"status": "error", "message": str(e)})


def continue_function(chat_id, message_id):
    session = SessionInfo.objects.filter(chat_id=chat_id).first()
    if session:
        missing_fields = []
        if not session.media_content:
            missing_fields.append("content")
        if not session.season:
            missing_fields.append("season")
        if not session.description:
            missing_fields.append("description")

        # Handle missing fields
        if "content" in missing_fields:
            edit_message(
                chat_id,
                message_id,
                f"You currently have a session with TMDB ID: {session.tmdb_id}. "
                "Please update media content to continue or discard the session.",
                reply_markup={
                    "inline_keyboard": [
                        [
                            {"text": "Video", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:video"},
                            {"text": "Poster", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:poster"},
                            {"text": "Backdrop", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:backdrop"},
                            ],
                            [
                            {"text": "Subtitles", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:subtitles"},
                            {"text": "Soundtrack", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:soundtrack"},
                        ],
                        [
                            {"text": "Finish selection", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:finish"},
                        ],
                        [
                            {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                        ]
                    ]
                }
            )
            return JsonResponse({"status": "error", "message": "Missing fields: content"})

        if "season" in missing_fields:
            if session.media_type == "tv" and session.available_season:
                # Generate buttons for each available season
                buttons = [
                    {"text": f"Season {i}", "callback_data": f"seasonselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:{i}"}
                    for i in range(1, int(session.available_season) + 1)
                ]
                
                edit_message(
                    chat_id,
                    message_id,
                    f"You currently have a session with TMDB ID: {session.tmdb_id}. "
                    "Please update season before saving a file or discard the session. "
                    "Select the seasons you want to include in your bundle. Press the same button to deselect.",
                    reply_markup={
                        "inline_keyboard": [
                             *[group for group in [buttons[i:i + 3] for i in range(0, len(buttons), 3)]], # Break into rows of 3 buttons
                            [{"text": "Finish selection", "callback_data": f"seasonselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:finish"}],
                        ]
                    }
                )
                return JsonResponse({"status": "ok"})

            elif session.media_type == "movie":
                edit_message(
                    chat_id,
                    message_id,
                    f"You currently have a session with TMDB ID: {session.tmdb_id}. "
                    "Please update media content before saving a file or discard the session.",
                    reply_markup={
                        "inline_keyboard": [
                            [
                                {"text": "Video", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:video"},
                                {"text": "Poster", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:poster"},
                                {"text": "Backdrop", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:backdrop"},
                            ],
                            [
                                {"text": "Subtitles", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:subtitles"},
                                {"text": "Soundtrack", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:soundtrack"},
                            ],
                            [
                                {"text": "Finish selection", "callback_data": f"contentselection:{session.tmdb_id}:{session.media_type}:{session.unique_id}:finish"},
                            ],
                            [
                                {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            ]
                        ]
                    }
                )
                return JsonResponse({"status": "error", "message": "Missing fields: content"})
        
        if "description" in missing_fields:
            edit_message(
                chat_id,
                message_id,
                f"you still have a bundle open for the tmdb id: {session.tmdb_id}\nEither you discard the bundle before saving files or continue",
                reply_markup={
                    "inline_keyboard": [
                        [
                            {"text": "Continue", "callback_data": f"continue:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                            {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                        ]
                    ]
                }
            )
            return JsonResponse({"status": "error", "message":"missing: description"})

        if not missing_fields:
            files = TemporaryFileInfo.objects.filter(unique_id=session.unique_id)    
            if files.exists():
                file_list = [{'file_id': file.file_id, 'file_type': file.file_type} for file in files]
                message =(f"You still have a bundle open for the tmdb id:{session.tmdb_id} \n"
                    f"Description: {session.description}\n"
                    f"media content in the bundle:{session.media_content}\n"
                    f"Related to season:{session.season}\n"
                    f"if you want to add more files start uploading them.\n if you want to delete the bundle press discard.\nif you wants to close the bundle press close\n here are all the files you have shared till now")
                edit_message(
                    chat_id,
                    message_id,
                    message,
                    reply_markup={
                        "inline_keyboard": [
                            [
                                {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                                {"text": "Close", "callback_data": f"close:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"}
                            ]
                        ]
                    }
                )
                send_media(chat_id, file_list)
                return JsonResponse({"status": "ok"})
            else:
                message = "start uploading files and then press close button or discard the bundle"
                edit_message(
                    chat_id,
                    message_id,
                    message,
                    reply_markup={
                        "inline_keyboard": [
                            [
                                {"text": "Close", "callback_data": f"close:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"},
                                {"text": "Discard", "callback_data": f"discard:{session.tmdb_id}:{session.media_type}:{session.unique_id}:0"}
                            ]
                        ]
                    }
                )
                return JsonResponse({"status": "ok"})
    else:
        edit_message(
            chat_id,
            message_id,
            f"you currently don't have any session so please start one to make a bundle/session, by sending the tmdb id in the format 'id:(tmdb id)'."
        )
        return JsonResponse({"status":"error","message":"no session found"})