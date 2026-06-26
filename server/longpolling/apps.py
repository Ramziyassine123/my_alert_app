# ServerSide/longpolling/apps.py
from django.apps import AppConfig


class LongpollingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'longpolling'
