# alerts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main entry point - connection type selection (redirect root to this)
    path('', views.connection_type_view, name='connection_type'),
    path('connection-type/', views.connection_type_view, name='connection_type'),

    # Technology-specific alert pages
    path('alerts/poll/', views.alerts_longpolling_view, name='alerts_longpolling'),
    path('alerts/websocket/', views.alerts_websocket_view, name='alerts_websocket'),
    path('alerts/push/', views.alerts_push_view, name='alerts_push'),

    # Performance testing endpoints
    path('test/', views.performance_test_dashboard, name='performance_test_dashboard'),
    path('test/run/', views.run_performance_test, name='run_performance_test'),
    path('test/results/', views.get_test_results, name='get_test_results'),
]
