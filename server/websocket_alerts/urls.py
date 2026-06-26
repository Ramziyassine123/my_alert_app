# ServerSide/websocket_alerts/urls.py

from django.urls import path
from . import views

# API endpoints only - frontend templates handled by my_alert_app (port 8000)
urlpatterns = [
    # Core WebSocket API endpoints
    path('api/health/', views.health_check, name='api_health_check'),
    path('api/stats/', views.server_stats, name='server_stats'),
    path('api/metrics/', views.performance_metrics, name='performance_metrics'),
    path('api/connection-info/', views.connection_info, name='connection_info'),
    path('api/reset-metrics/', views.reset_metrics, name='reset_metrics'),

    # Alternative URL patterns for compatibility
    path('health/', views.health_check, name='health_check_alt'),
    path('stats/', views.server_stats, name='server_stats_alt'),
    path('metrics/', views.performance_metrics, name='performance_metrics_alt'),
]
