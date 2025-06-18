from rest_framework import serializers
from .models import PerformanceTestResult, TechnologyMetrics


class PerformanceTestConfigSerializer(serializers.Serializer):
    """Serializer for performance test configuration"""
    duration = serializers.IntegerField(min_value=10, max_value=300, default=60)
    message_count = serializers.IntegerField(min_value=1, max_value=100, default=10)
    concurrent_clients = serializers.IntegerField(min_value=1, max_value=20, default=5)
    message_interval = serializers.IntegerField(min_value=1, max_value=10, default=2)
    technologies = serializers.ListField(
        child=serializers.ChoiceField(choices=['websocket', 'longpolling', 'push']),
        min_length=1
    )


class PerformanceTestResponseSerializer(serializers.Serializer):
    """Serializer for performance test response"""
    status = serializers.CharField()
    message = serializers.CharField()
    test_id = serializers.CharField()
    config = serializers.DictField()


class PerformanceTestResultSerializer(serializers.ModelSerializer):
    """Serializer for performance test results"""

    class Meta:
        model = PerformanceTestResult
        fields = '__all__'


class TechnologyMetricsSerializer(serializers.ModelSerializer):
    """Serializer for technology metrics"""
    success_rate = serializers.ReadOnlyField()

    class Meta:
        model = TechnologyMetrics
        fields = '__all__'
