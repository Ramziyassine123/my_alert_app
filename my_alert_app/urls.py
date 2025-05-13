#myalertapp urls 

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('alerts.urls')),  # Include alerts app URLs
]
