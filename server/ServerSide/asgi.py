"""
ASGI config for ServerSide project with WebSocket support for performance testing
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ServerSide.settings')

# Import Django ASGI application early to ensure Django is set up
django_asgi_app = get_asgi_application()

# Import WebSocket consumer after Django setup
from websocket_alerts.consumers import AlertConsumer

# WebSocket URL patterns
websocket_urlpatterns = [
    path('ws/alerts/', AlertConsumer.as_asgi()),  # CRITICAL: Exact path for performance tests
]

# ASGI application configuration - REMOVED AuthMiddlewareStack for API-only server
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': URLRouter(websocket_urlpatterns),  # No auth needed for performance testing
})
