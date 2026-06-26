"""
Models for Firebase push notifications
"""
import logging
from django.db import models

logger = logging.getLogger(__name__)


class FCMToken(models.Model):
    """Store Firebase Cloud Messaging tokens"""
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"FCM Token: {self.token[:20]}..."

    @classmethod
    def cleanup_old_tokens(cls):
        """Keep only the 10 most recent active tokens"""
        if cls.objects.count() > 10:
            keep_ids = list(cls.objects.order_by('-created_at')[:10].values_list('id', flat=True))
            cls.objects.exclude(id__in=keep_ids).delete()


class AlertLog(models.Model):
    """Log sent alerts for tracking"""
    alert_title = models.CharField(max_length=255)
    alert_message = models.TextField()
    alert_type = models.CharField(max_length=20, default='push')
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.alert_title} - {self.sent_at}"
