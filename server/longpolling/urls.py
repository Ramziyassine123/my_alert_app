"""
URL patterns for long polling alerts
"""
from django.urls import path
from . import views

urlpatterns = [
    path('alerts/', views.long_poll_alerts, name='long_poll_alerts'),  # Main endpoint
    path('all-alerts/', views.get_all_alerts, name='get_all_alerts'),
    path('reset/', views.reset_alert_index, name='reset_alert_index'),
    path('status/', views.poll_status, name='poll_status'),
    path('simulate/', views.simulate_new_alert, name='simulate_new_alert'),  # For testing

    # NEW: Add this line for dynamic alert addition
    path('add-alert/', views.add_new_alert, name='add_new_alert'),

    # Performance testing endpoints
    path('metrics/', views.get_performance_metrics, name='longpolling_metrics'),
    path('metrics/reset/', views.reset_performance_metrics, name='reset_longpolling_metrics'),
]
