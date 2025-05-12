import time
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Alert, UserProfile
from django.http import JsonResponse
from .forms import AlertForm
from django.contrib.auth.forms import AuthenticationForm


@login_required
def connection_type_view(request):
    if request.method == 'POST':
        connection_type = request.POST.get('connection_type')

        # Save the connection type to the user's profile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.connection_type = connection_type
        user_profile.save()

        return redirect('alerts')  # Redirect to the alerts view after selection

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
        return redirect('alerts')  # Redirect to alerts page after registration

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


@login_required
def alerts_view(request):
    user_profile = UserProfile.objects.get(user=request.user)  # Get the user's profile
    connection_type = user_profile.connection_type  # Get the connection type

    if request.method == 'POST':
        form = AlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.notification_type = connection_type  # Set the notification type based on user profile
            alert.save()

            # Logic for sending notifications based on the selected technology
            if connection_type == 'websocket':
                # Send via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "alerts",
                    {
                        'type': 'send_alert',
                        'title': alert.title,
                        'message': alert.message,
                        'period': alert.period,
                    }
                )
            elif connection_type == 'push':
                # Send via push notification
                send_push_notification(alert.title, alert.message, alert.period)
            elif connection_type == 'long_polling':
                # Handle long polling
                return long_poll_alert(alert.title, alert.message, alert.period)

            return JsonResponse({'alert_id': alert.id})

    else:
        form = AlertForm()

    # Render the appropriate template based on the connection type
    if connection_type == 'websocket':
        return render(request, 'alerts/alerts_websocket.html', {'form': form})
    elif connection_type == 'push':
        return render(request, 'alerts/alerts_push.html', {'form': form})
    elif connection_type == 'long_polling':
        return render(request, 'alerts/alerts_long_polling.html', {'form': form})


def long_poll_alert(title, message, period):
    # Simulate long polling by waiting for a certain period
    time.sleep(period)  # Wait for the specified period before responding

    # Send the alert data back as a response
    return JsonResponse({
        'status': 'success',
        'title': title,
        'message': message,
        'period': period
    })


@login_required
def long_polling_view(request):
    # Logic to fetch the latest alerts for the user
    alerts = Alert.objects.filter(user=request.user)
    alerts_data = [{'title': alert.title, 'message': alert.message, 'period': alert.period} for alert in alerts]

    if alerts_data:
        return JsonResponse(alerts_data, safe=False)
    else:
        return JsonResponse({'message': 'No alerts available'}, status=204)  # No content


def send_push_notification(title, message, period):
    # Implement your push notification logic here
    url = "https://fcm.googleapis.com/v1/projects/YOUR_PROJECT_ID/messages:send"  # Use your project ID
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",  # Use the access token from your service account
        "Content-Type": "application/json"
    }

    payload = {
        "message": {
            "token": "DEVICE_REGISTRATION_TOKEN",  # Replace with the device token you want to send the notification to
            "notification": {
                "title": title,
                "body": message
            },
            "data": {
                "period": period
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Push notification sent successfully.")
    else:
        print("Failed to send push notification:", response.content)


@login_required
def delete_alert(request, alert_id):
    try:
        alert = Alert.objects.get(id=alert_id, user=request.user)
        alert.delete()
        return JsonResponse({'status': 'success'})
    except Alert.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Alert not found.'}, status=404)
