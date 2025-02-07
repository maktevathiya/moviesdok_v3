from django.dispatch import receiver
from allauth.account.signals import user_signed_up, user_logged_in
from .models import UserHistory


@receiver(user_signed_up)
def handle_user_signup(sender, request, user, **kwargs):
    session_id = request.session.session_key or request.session.create()
    UserHistory.transfer_session_history_to_user(session_id, user)

@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    old_session_key = request.COOKIES.get('sessionid')  # Retrieve old session key from cookies
    if old_session_key:
        UserHistory.transfer_session_history_to_user(old_session_key, user)
