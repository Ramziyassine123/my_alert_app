# ServerSide/websocket_alerts/routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from websocket_alerts.consumers import AlertConsumer

# WebSocket URL patterns - No auth required for performance testing
websocket_urlpatterns = [
    path('ws/alerts/', AlertConsumer.as_asgi()),  # This MUST be exactly 'ws/alerts/'
]

# Application routing configuration - Simplified for API-only server
application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns),  # Removed AuthMiddlewareStack
})
