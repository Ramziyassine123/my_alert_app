import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from .models import FCMToken
from django.conf import settings
import json


@login_required
def connection_type_view(request):
    if request.method == 'POST':
        connection_type = request.POST.get('connection_type')

        # Save the connection type to the user's profile
        # user_profile, created = UserProfile.objects.get_or_create(name=request.user)
        # user_profile.connection_type = connection_type
        # user_profile.save()

        if connection_type == "websocket":
            return redirect('alerts_websocket')  # Redirect to the alerts view after selection

        elif connection_type == "long_polling":
            return redirect('alerts_longpolling')  # Redirect to the alerts view after selection

        elif connection_type == "push":
            return redirect('alerts_push')  # Redirect to the alerts view after selection

    return render(request, 'connection_type.html')


def index(request):
    return render(request, 'alerts/index.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Validate the input
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'alerts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'alerts/register.html')

        # Create the user
        user = User.objects.create_user(username=username, password=password)
        user.save()

        # Automatically log in the user after registration
        login(request, user)
        return redirect('alerts/connection_type.html')  # Redirect to conn type after registration

    return render(request, 'alerts/register.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('connection_type')  # Redirect to connection type selection
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


def alerts_websocket_view(request):
    return render(request, 'alerts/alerts_websocket.html')


def alerts_longpolling_view(request):
    return render(request, 'alerts/alerts_longpolling.html')


def alerts_push_view(request):
    return render(request, 'alerts/alerts_push.html')
