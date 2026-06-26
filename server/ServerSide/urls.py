"""
URL configuration for ServerSide project
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def api_status(request):
    """Simple API status endpoint"""
    return JsonResponse({
        'status': 'online',
        'server': 'Unified Alert Server',
        'port': 8001,
        'services': {
            'websocket': 'ws://localhost:8001/ws/alerts/',
            'longpolling': 'http://localhost:8001/api/poll/alerts/',
            'push': 'http://localhost:8001/api/push/',
        },
        'message': 'All alert services are running'
    })


urlpatterns = [

    # API status endpoint
    path('api/status/', api_status, name='api_status'),

    # Include app URLs with API prefix
    path('api/poll/', include('longpolling.urls')),  # Long polling endpoints
    path('api/push/', include('push.urls')),  # Push notification endpoints
    path('api/ws/', include('websocket_alerts.urls')),  # WebSocket info endpoints

    # WebSocket routing is handled by ASGI in routing.py
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
