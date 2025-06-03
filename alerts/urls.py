# alerts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('connection-type/', views.connection_type_view, name='connection_type'),
    path('alerts/poll/', views.alerts_longpolling_view, name='alerts_longpolling'),
    path('alerts/websocket/', views.alerts_websocket_view, name='alerts_websocket'),
    path('alerts/push/', views.alerts_push_view, name='alerts_push'),  # This should work now
]

