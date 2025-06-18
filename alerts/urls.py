# alerts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API endpoints
router = DefaultRouter()
router.register(r'performance-tests', views.PerformanceTestViewSet, basename='performance-test')
router.register(r'metrics', views.TechnologyMetricsViewSet, basename='metrics')

urlpatterns = [
    # Template views (UI)
    path('', views.connection_type_view, name='connection_type'),
    path('connection-type/', views.connection_type_view, name='connection_type'),
    path('alerts/poll/', views.alerts_longpolling_view, name='alerts_longpolling'),
    path('alerts/websocket/', views.alerts_websocket_view, name='alerts_websocket'),
    path('alerts/push/', views.alerts_push_view, name='alerts_push'),
    path('test/', views.performance_test_dashboard, name='performance_test_dashboard'),

    # DRF API endpoints
    path('api/', include(router.urls)),

    # Legacy API endpoints for backwards compatibility
    path('test/run/', views.PerformanceTestViewSet.as_view({'post': 'run_test'}), name='run_performance_test'),
    path('test/results/', views.PerformanceTestViewSet.as_view({'get': 'results'}), name='get_test_results'),
]
