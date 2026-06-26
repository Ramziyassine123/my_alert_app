"""
URL patterns for push notifications
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register view sets
router = DefaultRouter()
router.register(r'tokens', views.FCMTokenViewSet, basename='fcmtoken')

urlpatterns = [
    # DRF router URLs
    path('', include(router.urls)),

    # Legacy endpoints for backwards compatibility
    path('register-token/', views.FCMTokenViewSet.as_view({'post': 'create'}), name='register_token'),
    path('send-sequential/', views.FCMTokenViewSet.as_view({'post': 'send_sequential'}), name='send_sequential'),
    path('stats/', views.FCMTokenViewSet.as_view({'get': 'stats'}), name='push_stats'),
    path('send-sequential/', views.FCMTokenViewSet.as_view({'post': 'send_sequential_with_tracking'}), name='\
    send_sequential_tracked'),
    path('delivery-stats/', views.FCMTokenViewSet.as_view({'get': 'delivery_stats'}), name='delivery_stats'),
    path('confirm-delivery/', views.FCMTokenViewSet.as_view({'post': 'confirm_delivery'}), name='confirm_delivery'),
]

