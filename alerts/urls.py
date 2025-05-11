from django.urls import path
from alerts import views

urlpatterns = [
    path('', views.index, name='index'),  # homepage
    path('register/', views.register, name='register'),  #
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('alerts/delete/<int:alert_id>/', views.delete_alert, name='delete_alert'),
    path('user/preferences/', views.update_user_preference, name='update_user_preferences'),
]
