# alerts/serializers.py

from rest_framework import serializers
from .models import FCMToken, PerformanceTestResult, TechnologyMetrics, AlertDeliveryLog, TestSession


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


class PerformanceTestConfigSerializer(serializers.Serializer):
    """Serializer for performance test configuration"""
    duration = serializers.IntegerField(min_value=10, max_value=600, default=60)
    e2e_clients = serializers.IntegerField(min_value=1, max_value=20, default=5)
    scalability_clients = serializers.IntegerField(min_value=1, max_value=1000, default=100)
    max_concurrent_clients = serializers.IntegerField(min_value=1, max_value=50, required=False)
    token_scale_test = serializers.IntegerField(min_value=1, max_value=1000, default=100)
    technologies = serializers.ListField(
        child=serializers.ChoiceField(choices=['websocket', 'longpolling', 'firebase']),
        min_length=1
    )
    network_profile = serializers.ChoiceField(
        choices=['perfect', 'local_wifi', 'good_mobile', 'poor_mobile', 'international', 'satellite'],
        default='good_mobile'
    )
    enable_resource_monitoring = serializers.BooleanField(default=True)
    test_description = serializers.CharField(max_length=500, required=False)


class PerformanceTestResponseSerializer(serializers.Serializer):
    """Serializer for performance test response"""
    status = serializers.CharField()
    message = serializers.CharField()
    test_id = serializers.CharField()
    config = serializers.DictField()
    enhancements = serializers.ListField(child=serializers.CharField(), required=False)
    testing_approach = serializers.CharField(required=False)
    architecture = serializers.DictField(required=False)


class PerformanceTestResultSerializer(serializers.ModelSerializer):
    """Serializer for performance test results"""
    duration_seconds = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()

    class Meta:
        model = PerformanceTestResult
        fields = '__all__'

    def validate_test_config(self, value):
        """Validate test configuration"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Test config must be a dictionary")

        required_fields = ['technologies']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Test config must include '{field}'")

        return value


class TechnologyMetricsSerializer(serializers.ModelSerializer):
    """Serializer for technology metrics"""
    success_rate = serializers.ReadOnlyField()
    error_rate = serializers.ReadOnlyField()
    avg_throughput = serializers.ReadOnlyField()
    performance_grade = serializers.ReadOnlyField(source='get_performance_grade')

    class Meta:
        model = TechnologyMetrics
        fields = '__all__'


class AlertDeliveryLogSerializer(serializers.ModelSerializer):
    """Serializer for alert delivery logs"""
    success_rate = serializers.ReadOnlyField()

    class Meta:
        model = AlertDeliveryLog
        fields = '__all__'


class TestSessionSerializer(serializers.ModelSerializer):
    """Serializer for test sessions"""
    success_rate = serializers.ReadOnlyField()
    duration_minutes = serializers.ReadOnlyField()

    class Meta:
        model = TestSession
        fields = '__all__'

    def validate_technologies_tested(self, value):
        """Validate technologies list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Technologies tested must be a list")

        valid_technologies = ['websocket', 'longpolling', 'firebase', 'push']
        for tech in value:
            if tech not in valid_technologies:
                raise serializers.ValidationError(f"Invalid technology: {tech}")

        return value


class SystemResourcesSerializer(serializers.Serializer):
    """Serializer for system resources"""
    monitoring_active = serializers.BooleanField()
    current_stats = serializers.DictField(required=False)
    historical_data = serializers.ListField(required=False)
    snapshot = serializers.DictField(required=False)
    timestamp = serializers.FloatField()
    enhancement_features = serializers.DictField(required=False)
    client_role = serializers.CharField(required=False)


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response"""
    status = serializers.CharField()
    timestamp = serializers.FloatField()
    services = serializers.DictField()
    system = serializers.DictField()
    version = serializers.CharField()
    uptime_seconds = serializers.FloatField()
    role = serializers.CharField()
    architecture = serializers.DictField(required=False)
    server_info = serializers.DictField(required=False)


class ConnectivityCheckSerializer(serializers.Serializer):
    """Serializer for connectivity check response"""
    overall_status = serializers.CharField()
    server_endpoints = serializers.DictField()
    timestamp = serializers.FloatField()
    client_perspective = serializers.BooleanField()
    architecture = serializers.DictField(required=False)


class LoadSimulationRequestSerializer(serializers.Serializer):
    """Serializer for load simulation request"""
    clients = serializers.IntegerField(min_value=1, max_value=20, default=5)
    duration = serializers.IntegerField(min_value=10, max_value=120, default=30)
    technology = serializers.ChoiceField(
        choices=['websocket', 'longpolling', 'firebase'],
        default='websocket'
    )


class LoadSimulationResponseSerializer(serializers.Serializer):
    """Serializer for load simulation response"""
    status = serializers.CharField()
    message = serializers.CharField()
    clients = serializers.IntegerField()
    duration = serializers.IntegerField()
    technology = serializers.CharField()
    architecture = serializers.CharField(required=False)


class MetricsComparisonSerializer(serializers.Serializer):
    """Serializer for metrics comparison"""
    timestamp = serializers.FloatField()
    technologies = serializers.DictField()
    client_perspective = serializers.BooleanField(required=False)
    role = serializers.CharField(required=False)
    architecture = serializers.CharField(required=False)


class LiveMetricsSerializer(serializers.Serializer):
    """Serializer for live metrics"""
    live_metrics = serializers.DictField()
    system_metrics = serializers.DictField(required=False)
    timestamp = serializers.FloatField()
    monitoring = serializers.BooleanField()
    client_measurements_only = serializers.BooleanField(required=False)
    role = serializers.CharField(required=False)
    architecture = serializers.CharField(required=False)


class EnhancedTestResultsSerializer(serializers.Serializer):
    """Serializer for enhanced test results"""
    test_id = serializers.CharField()
    test_type = serializers.CharField()
    timestamp = serializers.CharField()
    config = serializers.DictField()
    results = serializers.DictField()
    status = serializers.CharField()
    completed_at = serializers.CharField(required=False)
    summary = serializers.DictField(required=False)
    resource_monitoring = serializers.ListField(required=False)
    current_resources = serializers.DictField(required=False)
    enhancement_status = serializers.DictField(required=False)
    architecture_info = serializers.DictField(required=False)
    real_testing = serializers.BooleanField(required=False)
    client_server_testing = serializers.BooleanField(required=False)
    client_role = serializers.CharField(required=False)
    server_role = serializers.CharField(required=False)


class TechnologyTestResultSerializer(serializers.Serializer):
    """Serializer for individual technology test results"""
    technology = serializers.CharField()
    status = serializers.CharField()
    results = serializers.ListField()
    statistics = serializers.DictField(required=False)
    real_testing = serializers.BooleanField(required=False)
    client_server_testing = serializers.BooleanField(required=False)
    error = serializers.CharField(required=False)


class TestSummarySerializer(serializers.Serializer):
    """Serializer for test summary"""
    total_technologies_tested = serializers.IntegerField()
    successful_technologies = serializers.IntegerField()
    failed_technologies = serializers.IntegerField()
    overall_success_rate = serializers.FloatField()
    technology_performance = serializers.DictField()
    client_server_testing = serializers.BooleanField(required=False)
    testing_architecture = serializers.CharField(required=False)


class TechnologyPerformanceSerializer(serializers.Serializer):
    """Serializer for individual technology performance"""
    success_rate = serializers.FloatField()
    avg_latency_ms = serializers.FloatField()
    total_tests = serializers.IntegerField()
    status = serializers.CharField()
    client_server_measurement = serializers.BooleanField(required=False)
    error = serializers.CharField(required=False)
    