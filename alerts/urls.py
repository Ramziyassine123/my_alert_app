#urls.py

from django.urls import path
from .views import connection_type_view, login_view, logout_view, delete_alert, register, index,\
    long_polling_view, alerts_websocket_view


urlpatterns = [
    path('', index, name='index'),  # homepage
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),  # URL for the login view
    path('logout/', logout_view, name='logout'),
    path('connection-type/', connection_type_view, name='connection_type'),
    path('alerts/delete/<int:alert_id>/', delete_alert, name='delete_alert'),
    path('alerts/poll/', long_polling_view, name='long_polling'),  # New URL for long polling
    path('alerts/websocket/', alerts_websocket_view, name='alerts_websocket'),  # New URL for WebSocket alerts
]
