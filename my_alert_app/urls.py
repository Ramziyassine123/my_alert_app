# my_alert_app/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse, Http404
import os


def serve_service_worker(request):
    """Serve the Firebase service worker from project root"""
    service_worker_path = os.path.join(settings.BASE_DIR, 'firebase-messaging-sw.js')

    if os.path.exists(service_worker_path):
        with open(service_worker_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/javascript')
    else:
        raise Http404("Service worker not found")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('alerts.urls')),  # Include alerts URLs
    path('firebase-messaging-sw.js', serve_service_worker, name='service_worker'),  # Serve service worker
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[
        0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
