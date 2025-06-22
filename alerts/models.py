# alerts/models.py

from django.db import models
from django.utils import timezone


class FCMToken(models.Model):
    """Store Firebase Cloud Messaging tokens - No user association required"""
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"FCM Token: {self.token[:20]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name = "FCM Token"
        verbose_name_plural = "FCM Tokens"


class PerformanceTestResult(models.Model):
    """Store performance test results for analysis"""
    test_id = models.CharField(max_length=100, unique=True)
    technology = models.CharField(max_length=20, choices=[
        ('websocket', 'WebSocket'),
        ('longpolling', 'Long Polling'),
        ('push', 'Push Notifications'),
        ('firebase', 'Firebase Push'),
    ])
    test_config = models.JSONField()  # Store test configuration
    metrics = models.JSONField()      # Store performance metrics
    status = models.CharField(max_length=50, default='pending')
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Additional fields for enhanced testing
    client_server_testing = models.BooleanField(default=False)
    real_measurements = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.technology} - {self.test_id}"

    @property
    def duration_seconds(self):
        """Calculate test duration in seconds"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_completed(self):
        """Check if test is completed"""
        return self.status in ['completed', 'failed', 'error']

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Performance Test Result"
        verbose_name_plural = "Performance Test Results"


class AlertDeliveryLog(models.Model):
    """Log alert deliveries for performance tracking"""
    technology = models.CharField(max_length=20, choices=[
        ('websocket', 'WebSocket'),
        ('longpolling', 'Long Polling'),
        ('push', 'Push Notifications'),
        ('firebase', 'Firebase Push'),
    ])
    alert_title = models.CharField(max_length=255)
    alert_message = models.TextField()
    delivery_status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('confirmed', 'Confirmed'),
    ])
    latency_ms = models.FloatField(null=True, blank=True)  # Delivery latency in milliseconds
    client_count = models.IntegerField(default=1)         # Number of clients that received the alert
    sent_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)  # Additional metadata

    # Enhanced fields
    client_server_test = models.BooleanField(default=False)
    test_id = models.CharField(max_length=100, blank=True, null=True)
    source_app = models.CharField(max_length=50, blank=True, null=True)  # 'CLIENT' or 'SERVER'

    def __str__(self):
        return f"{self.technology} - {self.alert_title} - {self.delivery_status}"

    @property
    def success_rate(self):
        """Calculate success rate for this delivery"""
        if self.delivery_status in ['delivered', 'confirmed']:
            return 100.0
        elif self.delivery_status == 'sent':
            return 50.0
        else:
            return 0.0

    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Alert Delivery Log"
        verbose_name_plural = "Alert Delivery Logs"


class TechnologyMetrics(models.Model):
    """Store aggregated metrics for each technology"""
    technology = models.CharField(max_length=20, choices=[
        ('websocket', 'WebSocket'),
        ('longpolling', 'Long Polling'),
        ('push', 'Push Notifications'),
        ('firebase', 'Firebase Push'),
    ], unique=True)

    # Performance metrics
    avg_latency_ms = models.FloatField(default=0)
    min_latency_ms = models.FloatField(default=0)
    max_latency_ms = models.FloatField(default=0)
    median_latency_ms = models.FloatField(default=0)

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

    # Enhanced metrics
    client_server_measurements = models.IntegerField(default=0)
    last_test_id = models.CharField(max_length=100, blank=True, null=True)
    source_app = models.CharField(max_length=50, default='CLIENT')  # 'CLIENT' or 'SERVER'

    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.technology} Metrics ({self.source_app})"

    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_attempts == 0:
            return 0
        return (self.successful_deliveries / self.total_attempts) * 100

    @property
    def error_rate(self):
        """Calculate error rate percentage"""
        if self.total_attempts == 0:
            return 0
        return (self.failed_deliveries / self.total_attempts) * 100

    @property
    def avg_throughput(self):
        """Calculate average throughput"""
        return self.messages_per_second

    def update_metrics(self, latency_ms=None, success=True, data_bytes=0, connection_time_ms=None, test_id=None):
        """Update metrics with new data point"""
        self.total_attempts += 1

        if success:
            self.successful_deliveries += 1
        else:
            self.failed_deliveries += 1

        if latency_ms is not None and latency_ms > 0:
            # Update latency metrics
            if self.avg_latency_ms == 0:
                self.avg_latency_ms = latency_ms
                self.min_latency_ms = latency_ms
                self.max_latency_ms = latency_ms
                self.median_latency_ms = latency_ms
            else:
                # Calculate running average
                total_latency = self.avg_latency_ms * (self.total_attempts - 1) + latency_ms
                self.avg_latency_ms = total_latency / self.total_attempts
                self.min_latency_ms = min(self.min_latency_ms, latency_ms)
                self.max_latency_ms = max(self.max_latency_ms, latency_ms)

                # Simple median approximation (for performance)
                self.median_latency_ms = (self.min_latency_ms + self.max_latency_ms) / 2

        if connection_time_ms is not None and connection_time_ms > 0:
            # Update connection time
            if self.avg_connection_time_ms == 0:
                self.avg_connection_time_ms = connection_time_ms
            else:
                total_connection_time = self.avg_connection_time_ms * (self.total_attempts - 1) + connection_time_ms
                self.avg_connection_time_ms = total_connection_time / self.total_attempts

        self.total_data_transferred_bytes += data_bytes

        if test_id:
            self.last_test_id = test_id
            self.client_server_measurements += 1

        self.save()

    def reset_metrics(self):
        """Reset all metrics to zero"""
        self.avg_latency_ms = 0
        self.min_latency_ms = 0
        self.max_latency_ms = 0
        self.median_latency_ms = 0
        self.total_attempts = 0
        self.successful_deliveries = 0
        self.failed_deliveries = 0
        self.max_concurrent_clients = 0
        self.messages_per_second = 0
        self.avg_connection_time_ms = 0
        self.total_data_transferred_bytes = 0
        self.client_server_measurements = 0
        self.last_test_id = None
        self.save()

    def get_performance_grade(self):
        """Get a performance grade based on metrics"""
        if self.total_attempts == 0:
            return 'N/A'

        success_rate = self.success_rate
        avg_latency = self.avg_latency_ms

        # Grade based on success rate and latency
        if success_rate >= 95 and avg_latency <= 100:
            return 'A+'
        elif success_rate >= 90 and avg_latency <= 200:
            return 'A'
        elif success_rate >= 85 and avg_latency <= 500:
            return 'B+'
        elif success_rate >= 80 and avg_latency <= 1000:
            return 'B'
        elif success_rate >= 70 and avg_latency <= 2000:
            return 'C+'
        elif success_rate >= 60:
            return 'C'
        else:
            return 'D'

    class Meta:
        ordering = ['technology']
        verbose_name = "Technology Metrics"
        verbose_name_plural = "Technology Metrics"


class TestSession(models.Model):
    """Track performance test sessions"""
    session_id = models.CharField(max_length=100, unique=True)
    session_name = models.CharField(max_length=200, blank=True)
    technologies_tested = models.JSONField(default=list)
    configuration = models.JSONField(default=dict)

    # Session metadata
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='running')

    # Results summary
    total_tests = models.IntegerField(default=0)
    successful_tests = models.IntegerField(default=0)
    failed_tests = models.IntegerField(default=0)

    # Enhanced session tracking
    client_server_testing = models.BooleanField(default=True)
    resource_monitoring_enabled = models.BooleanField(default=False)
    real_measurements = models.BooleanField(default=True)

    def __str__(self):
        return f"Test Session {self.session_id} - {self.status}"

    @property
    def success_rate(self):
        """Calculate session success rate"""
        if self.total_tests == 0:
            return 0
        return (self.successful_tests / self.total_tests) * 100

    @property
    def duration_minutes(self):
        """Calculate session duration in minutes"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds() / 60
        return None

    def mark_completed(self):
        """Mark session as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, error_message=None):
        """Mark session as failed"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        if error_message:
            # Store error in configuration for reference
            self.configuration['error_message'] = error_message
        self.save()

    class Meta:
        ordering = ['-started_at']
        verbose_name = "Test Session"
        verbose_name_plural = "Test Sessions"
