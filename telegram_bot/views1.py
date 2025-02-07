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
from .views import send_media, send_telegram_message


@csrf_exempt
def telegram_webhook_downloader(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            

            if "message" in data:
                # Handle regular messages
                message = data.get('message', {})
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                
                if text.startswith('/start'):
                    unique_id = text.split()[-1]
                    if unique_id:
                        return start(chat_id, unique_id)
                    else:
                        return start(chat_id)
                    
            elif "callback_query" in data:
                # Handle button presses
                callback_query = data['callback_query']
                callback_data = callback_query['data']
                chat_id = callback_query['message']['chat']['id']
                from_id = callback_query['from']['id']
                message_id = callback_query['message']['message_id']

                # Parse callback data
                action, tmdb_id, media_type,unique_id, media_content = callback_data.split(":")
                return JsonResponse({"status":"ok", "message":"no callback query function yet implemented"})

            # If no known commands, send an unknown command message
            if 'chat_id' in locals():  # Ensure chat_id is available before sending
                send_telegram_message(chat_id, "Unknown command. Please try again.")
            return JsonResponse({"status": "unknown command"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "invalid method"})
    

def start(chat_id, unique_id = None):
    if unique_id:  
        session= MediaInfo.objects.filter(unique_id = unique_id).first()
        if session: 
            files = FileInfo.objects.filter(unique_id= unique_id)
            if files:
                file_list = [{'file_id': file.file_id, 'file_type': file.file_type} for file in files]
                send_media(chat_id, file_list)
                return JsonResponse({"status":"ok", "message":"files sent"})
            else:
                send_telegram_message(chat_id, f"there is bundle available with description:\n{session.description}\nbut there doesnot seems to be any files inside it.")
                return JsonResponse({"status":"error","message":"no files inside the bundle"})
        else:
            send_telegram_message(chat_id, "there is no bundle availble for the given id")
            return JsonResponse({"status":"error","message":"no media info for the id"})
    else:
        send_telegram_message(chat_id, f"this bot is only for giving bundles, it is nor equiped with to process any other commands")
        return JsonResponse({"status":"error","message":"not had any parameters"})
