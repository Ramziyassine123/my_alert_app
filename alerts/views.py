# alerts/views.py

from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import threading
from .models import PerformanceTestResult, TechnologyMetrics
from .serializers import (
    PerformanceTestConfigSerializer,
    PerformanceTestResponseSerializer,
    PerformanceTestResultSerializer,
    TechnologyMetricsSerializer
)
from .performance_tests import PerformanceTestRunner


def connection_type_view(request):
    """Main entry point - choose alert technology (no authentication required)"""
    if request.method == 'POST':
        connection_type = request.POST.get('connection_type')

        if connection_type == "websocket":
            return redirect('alerts_websocket')
        elif connection_type == "long_polling":
            return redirect('alerts_longpolling')
        elif connection_type == "push":
            return redirect('alerts_push')
        else:
            # Invalid selection, redirect back
            return redirect('connection_type')

    return render(request, 'connection_type.html')


def alerts_websocket_view(request):
    """WebSocket alerts page"""
    context = {
        'websocket_url': 'ws://localhost:8001/ws/alerts/',
        'server_port': '8001',
        'server_name': 'Unified Alert Server'
    }
    return render(request, 'alerts/alerts_websocket.html', context)


def alerts_longpolling_view(request):
    """Long polling alerts page"""
    context = {
        'longpolling_url': 'http://localhost:8001/api/poll/alerts/',
        'server_port': '8001',
        'server_name': 'Unified Alert Server'
    }
    return render(request, 'alerts/alerts_longpolling.html', context)


def alerts_push_view(request):
    """Push notifications alerts page"""
    context = {
        'push_api_url': 'http://localhost:8001/api/push/',
        'server_port': '8001',
        'server_name': 'Unified Alert Server'
    }
    return render(request, 'alerts/alerts_push.html', context)


def performance_test_dashboard(request):
    """Performance testing dashboard"""
    return render(request, 'alerts/performance_test_dashboard.html')


class PerformanceTestViewSet(viewsets.ModelViewSet):
    """ViewSet for performance test management"""
    queryset = PerformanceTestResult.objects.all()
    serializer_class = PerformanceTestResultSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def run_test(self, request):
        """Run performance tests for selected technologies"""
        serializer = PerformanceTestConfigSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        config = serializer.validated_data

        try:
            # Start performance test
            test_runner = PerformanceTestRunner(config)
            thread = threading.Thread(target=test_runner.run_tests)
            thread.daemon = True
            thread.start()

            response_data = {
                'status': 'started',
                'message': 'Performance tests started',
                'test_id': test_runner.test_id,
                'config': config
            }

            response_serializer = PerformanceTestResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': 'Failed to start performance test',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def results(self, request):
        """Get performance test results"""
        test_id = request.query_params.get('test_id')

        try:
            if test_id:
                results = PerformanceTestRunner.get_test_results(test_id)
            else:
                results = PerformanceTestRunner.get_latest_results()

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': 'Failed to get test results',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TechnologyMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for technology metrics (read-only)"""
    queryset = TechnologyMetrics.objects.all()
    serializer_class = TechnologyMetricsSerializer
    permission_classes = [AllowAny]
