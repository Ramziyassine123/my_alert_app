# alerts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API endpoints
router = DefaultRouter()
router.register(r'performance-tests', views.PerformanceTestViewSet, basename='performance-test')
router.register(r'metrics', views.TechnologyMetricsViewSet, basename='metrics')

urlpatterns = [
    # Main pages
    path('', views.connection_type_view, name='connection_type'),
    path('connection-type/', views.connection_type_view, name='connection_type'),

    # Alert technology pages
    path('alerts/poll/', views.alerts_longpolling_view, name='alerts_longpolling'),
    path('alerts/websocket/', views.alerts_websocket_view, name='alerts_websocket'),
    path('alerts/push/', views.alerts_push_view, name='alerts_push'),

    # Performance Testing Dashboard
    path('test/', views.performance_test_dashboard, name='performance_test_dashboard'),

    # API endpoints
    path('api/', include(router.urls)),

    # Enhanced Performance Testing API endpoints
    path('api/start-enhanced-performance-test/',
         views.start_enhanced_performance_test,
         name='start_enhanced_performance_test'),
    path('api/get-enhanced-test-results/',
         views.get_enhanced_test_results,
         name='get_enhanced_test_results'),
    path('api/get-system-resources/',
         views.get_system_resources,
         name='get_system_resources'),

    # Additional CLIENT utility endpoints
    path('api/server-connectivity/', views.server_connectivity_check, name='server_connectivity_check'),
    path('api/simulate-load/', views.simulate_performance_load, name='simulate_performance_load'),

    # Health check endpoint
    path('api/health/', views.health_check, name='health_check'),

    # Legacy API endpoints for backwards compatibility
    path('test/performance/run/', views.start_enhanced_performance_test, name='start_performance_test'),
    path('test/performance/results/', views.get_enhanced_test_results, name='get_performance_results'),
    path('test/performance/resources/', views.get_system_resources, name='get_system_resources_legacy'),

    # Legacy endpoints
    path('test/run/', views.PerformanceTestViewSet.as_view({'post': 'run_test'}), name='run_performance_test'),
    path('test/results/', views.PerformanceTestViewSet.as_view({'get': 'results'}), name='get_test_results'),

    # Live metrics endpoints
    path('test/metrics/comparison/', views.PerformanceTestViewSet.as_view({'get': 'get_metrics_comparison'}), name='get_metrics_comparison'),
    path('test/metrics/live/', views.TechnologyMetricsViewSet.as_view({'get': 'live_comparison'}), name='live_metrics_comparison'),
]
