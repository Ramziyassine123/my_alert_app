from django.db import models
from django.contrib.auth.models import User


class Alert(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    period = models.PositiveIntegerField()  # Store period in seconds
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notification_method = models.CharField(max_length=10, choices=[('LP', 'Long Polling'), ('WS', 'WebSocket'),
                                                                   ('FPN', 'Firebase Push Notification')])
    polling_period = models.PositiveIntegerField(default=5)  # Default polling period
