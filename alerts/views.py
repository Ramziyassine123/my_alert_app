from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Alert, UserPreference
from django.http import JsonResponse
from .forms import AlertForm
import json


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
        return redirect('alerts')  # Redirect to alerts page after registration

    return render(request, 'alerts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('alerts')  # Redirect to alerts page after login
    return render(request, 'alerts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


@login_required
def alerts_view(request):
    if request.method == 'POST':
        form = AlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user  # Set the user
            alert.save()
            return JsonResponse({'alert_id': alert.id})
    else:
        form = AlertForm()

    alerts = Alert.objects.filter(user=request.user)
    alerts_data = [{'id': alert.id, 'title': alert.title, 'message': alert.message, 'period': alert.period} for alert in
                   alerts]
    return render(request, 'alerts/alerts.html', {'form': form, 'alerts': alerts_data})


@login_required
def delete_alert(request, alert_id):
    try:
        alert = Alert.objects.get(id=alert_id, user=request.user)
        alert.delete()
        return JsonResponse({'status': 'success'})
    except Alert.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Alert not found.'}, status=404)


@login_required
def update_user_preference(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        notification_method = data.get('notification_method')
        polling_period = data.get('polling_period', 5)  # Default to 5 if not provided

        user_pref, created = UserPreference.objects.get_or_create(user=request.user)
        user_pref.notification_method = notification_method
        user_pref.polling_period = polling_period
        user_pref.save()

        return JsonResponse({'status': 'success'})
