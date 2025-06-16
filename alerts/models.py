# alerts/models.py

from django.db import models


class FCMToken(models.Model):
    """Store Firebase Cloud Messaging tokens - No user association required"""
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"FCM Token: {self.token[:20]}..."

    class Meta:
        ordering = ['-created_at']


class PerformanceTestResult(models.Model):
    """Store performance test results for analysis"""
    test_id = models.CharField(max_length=100, unique=True)
    technology = models.CharField(max_length=20, choices=[
        ('websocket', 'WebSocket'),
        ('longpolling', 'Long Polling'),
        ('push', 'Push Notifications'),
    ])
    test_config = models.JSONField()  # Store test configuration
    metrics = models.JSONField()      # Store performance metrics
    status = models.CharField(max_length=50)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.technology} - {self.test_id}"

    class Meta:
        ordering = ['-created_at']


class AlertDeliveryLog(models.Model):
    """Log alert deliveries for performance tracking"""
    technology = models.CharField(max_length=20, choices=[
        ('websocket', 'WebSocket'),
        ('longpolling', 'Long Polling'),
        ('push', 'Push Notifications'),
    ])
    alert_title = models.CharField(max_length=255)
    alert_message = models.TextField()
    delivery_status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
    ])
    latency_ms = models.FloatField(null=True, blank=True)  # Delivery latency in milliseconds
    client_count = models.IntegerField(default=1)         # Number of clients that received the alert
    sent_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)  # Additional metadata

    def __str__(self):
        return f"{self.technology} - {self.alert_title} - {self.delivery_status}"

    class Meta:
        ordering = ['-sent_at']


class TechnologyMetrics(models.Model):
    """Store aggregated metrics for each technology"""
    technology = models.CharField(max_length=20, choices=[
        ('websocket', 'WebSocket'),
        ('longpolling', 'Long Polling'),
        ('push', 'Push Notifications'),
    ], unique=True)

    # Performance metrics
    avg_latency_ms = models.FloatField(default=0)
    min_latency_ms = models.FloatField(default=0)
    max_latency_ms = models.FloatField(default=0)

    # Reliability metrics
    total_attempts = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)

    # Throughput metrics
    max_concurrent_clients = models.IntegerField(default=0)
    messages_per_second = models.FloatField(default=0)

    # Resource usage
    avg_connection_time_ms = models.FloatField(default=0)
    total_data_transferred_bytes = models.BigIntegerField(default=0)

    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.technology} Metrics"

    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_attempts == 0:
            return 0
        return (self.successful_deliveries / self.total_attempts) * 100

    def update_metrics(self, latency_ms=None, success=True, data_bytes=0):
        """Update metrics with new data point"""
        self.total_attempts += 1

        if success:
            self.successful_deliveries += 1
        else:
            self.failed_deliveries += 1

        if latency_ms is not None:
            # Update latency metrics
            if self.avg_latency_ms == 0:
                self.avg_latency_ms = latency_ms
                self.min_latency_ms = latency_ms
                self.max_latency_ms = latency_ms
            else:
                # Calculate running average
                total_latency = self.avg_latency_ms * (self.total_attempts - 1) + latency_ms
                self.avg_latency_ms = total_latency / self.total_attempts
                self.min_latency_ms = min(self.min_latency_ms, latency_ms)
                self.max_latency_ms = max(self.max_latency_ms, latency_ms)

        self.total_data_transferred_bytes += data_bytes
        self.save()

    class Meta:
        ordering = ['technology']
        verbose_name_plural = "Technology Metrics"
