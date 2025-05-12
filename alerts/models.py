from django.db import models
from django.contrib.auth.models import User


class Alert(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    period = models.IntegerField()
    notification_type = models.CharField(max_length=20)  # Store the technology used for this alert
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    connection_type = models.CharField(max_length=20, choices=[
        ('long_polling', 'HTTP Long Polling'),
        ('websocket', 'WebSockets'),
        ('push', 'Firebase Push Notifications'),
    ], default='long_polling')

    def __str__(self):
        return self.user.username
