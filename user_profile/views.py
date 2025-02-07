from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Prefetch
from .forms import UpdateEmailForm
from django.utils.http import urlencode
from django.urls import reverse

@login_required
def profile_view(request):
    # Get the logged-in user
    user = request.user

    # Handle email update
    if request.method == "POST" and "update_email" in request.POST:
        email_form = UpdateEmailForm(request.POST, instance=user)
        if email_form.is_valid():
            email_form.save()
            messages.success(request, "Email updated successfully.")
            return redirect("profile:profile_view")
    else:
        email_form = UpdateEmailForm(instance=user)

    # Handle password update
    if request.method == "POST" and "change_password" in request.POST:
        password_form = PasswordChangeForm(user=user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            next_url = f"{reverse('account_login')}?{urlencode({'next': reverse('profile:profile_view')})}" 
            messages.success(request, "Password changed successfully. Please log in again.")
            return redirect(next_url)  # Redirect to logout to force re-login
    else:
        password_form = PasswordChangeForm(user=user)

    context = {
        "user": user,
        "email_form": email_form,
        "password_form": password_form,
    }

    return render(request, "profile.html", context)
