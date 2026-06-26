from rest_framework import serializers
from .models import FCMToken


class FCMTokenSerializer(serializers.ModelSerializer):
    """Serializer for FCM token registration"""

    class Meta:
        model = FCMToken
        fields = ['id', 'token', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at']

    def validate_token(self, value):
        """Validate FCM token format"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Token cannot be empty")

        if len(value) < 10:
            raise serializers.ValidationError("Token is too short")

        if len(value) > 500:
            raise serializers.ValidationError("Token is too long")

        return value.strip()


class SequentialAlertRequestSerializer(serializers.Serializer):
    """Serializer for sequential alert request"""
    delay = serializers.FloatField(min_value=0.1, max_value=10.0, default=1.0)

    def validate_delay(self, value):
        """Validate delay parameter"""
        if value <= 0:
            raise serializers.ValidationError("Delay must be positive")
        return value


class SequentialAlertResponseSerializer(serializers.Serializer):
    """Serializer for sequential alert response"""
    status = serializers.CharField()
    message = serializers.CharField()
    total_alerts = serializers.IntegerField()
    delay_seconds = serializers.FloatField()
    estimated_duration = serializers.FloatField()


class PushStatsSerializer(serializers.Serializer):
    """Serializer for push notification statistics"""
    total_tokens = serializers.IntegerField()
    active_tokens = serializers.IntegerField()
    inactive_tokens = serializers.IntegerField()
    total_notifications_sent = serializers.IntegerField()
    last_notification_sent = serializers.DateTimeField(allow_null=True)
    server_status = serializers.CharField()
