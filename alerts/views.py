# alerts/views.py -

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm


@login_required
def connection_type_view(request):
    if request.method == 'POST':
        connection_type = request.POST.get('connection_type')

        if connection_type == "websocket":
            return redirect('alerts_websocket')
        elif connection_type == "long_polling":
            return redirect('alerts_longpolling')
        elif connection_type == "push":
            return redirect('alerts_push')

    return render(request, 'connection_type.html')


def index(request):
    return render(request, 'alerts/index.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'alerts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'alerts/register.html')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        login(request, user)
        return redirect('connection_type')

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
                return redirect('connection_type')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def alerts_websocket_view(request):
    # WebSocket server runs on port 6789
    context = {
        'websocket_url': 'ws://localhost:6789/ws/alerts/',
        'server_port': '6789'
    }
    return render(request, 'alerts/alerts_websocket.html', context)


def alerts_longpolling_view(request):
    # Long polling server runs on port 8002
    context = {
        'longpolling_url': 'http://localhost:8002/api/poll/',
        'server_port': '8002'
    }
    return render(request, 'alerts/alerts_longpolling.html', context)


def alerts_push_view(request):
    # Push server runs on port 8001
    context = {
        'push_api_url': 'http://localhost:8001/api/',
        'server_port': '8001'
    }
    return render(request, 'alerts/alerts_push.html', context)
