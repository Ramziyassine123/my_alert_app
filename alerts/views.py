# alerts/views.py

from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import threading
import time
from .models import PerformanceTestResult, TechnologyMetrics
from .serializers import (
    PerformanceTestConfigSerializer,
    PerformanceTestResponseSerializer,
    PerformanceTestResultSerializer,
    TechnologyMetricsSerializer
)
from .performance_tests import RealPerformanceTestRunner
import logging

logger = logging.getLogger(__name__)


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
    """ViewSet for REAL performance test management"""
    queryset = PerformanceTestResult.objects.all()
    serializer_class = PerformanceTestResultSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def run_test(self, request):
        """Run REAL performance tests for selected technologies"""
        serializer = PerformanceTestConfigSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        config = serializer.validated_data
        logger.info(f"Starting REAL performance test with config: {config}")

        try:
            # Create test runner with REAL performance measurement
            test_runner = RealPerformanceTestRunner(config)

            # Run tests in background thread
            def run_real_tests():
                """Background function to run real tests"""
                try:
                    results = test_runner.run_tests()
                    RealPerformanceTestRunner.store_results(test_runner.test_id, results)
                    logger.info(f"REAL test completed: {test_runner.test_id}")
                except Exception as e:
                    logger.error(f"REAL test failed: {e}")
                    error_results = {
                        'test_id': test_runner.test_id,
                        'error': str(e),
                        'status': 'failed',
                        'config': config
                    }
                    RealPerformanceTestRunner.store_results(test_runner.test_id, error_results)

            thread = threading.Thread(target=run_real_tests)
            thread.daemon = True
            thread.start()

            response_data = {
                'status': 'started',
                'message': 'REAL performance tests started',
                'test_id': test_runner.test_id,
                'config': config,
                'test_type': 'real_performance'
            }

            response_serializer = PerformanceTestResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to start REAL performance test: {e}")
            return Response({
                'error': 'Failed to start REAL performance test',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def results(self, request):
        """Get REAL performance test results"""
        test_id = request.query_params.get('test_id')

        try:
            if test_id:
                results = RealPerformanceTestRunner.get_test_results(test_id)
            else:
                results = RealPerformanceTestRunner.get_latest_results()

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to get REAL test results: {e}")
            return Response({
                'error': 'Failed to get REAL test results',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def test_websocket(self, request):
        """Run isolated WebSocket performance test"""
        serializer = PerformanceTestConfigSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        config = serializer.validated_data
        logger.info(f"Running isolated WebSocket test: {config}")

        try:
            from .performance_tests import RealWebSocketTester

            def run_websocket_test():
                tester = RealWebSocketTester('ws://localhost:8001/ws/alerts/', config)
                results = tester.run_test()

                test_id = f"ws_test_{int(time.time())}"
                RealPerformanceTestRunner.store_results(test_id, {
                    'test_id': test_id,
                    'results': {'websocket': results},
                    'test_type': 'isolated_websocket'
                })

            thread = threading.Thread(target=run_websocket_test)
            thread.daemon = True
            thread.start()

            return Response({
                'status': 'started',
                'message': 'Isolated WebSocket test started',
                'technology': 'websocket'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to start WebSocket test: {e}")
            return Response({
                'error': 'Failed to start WebSocket test',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def test_longpolling(self, request):
        """Run isolated Long Polling performance test"""
        serializer = PerformanceTestConfigSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        config = serializer.validated_data
        logger.info(f"Running isolated Long Polling test: {config}")

        try:
            from .performance_tests import RealLongPollingTester

            def run_longpolling_test():
                tester = RealLongPollingTester('http://localhost:8001/api/poll/alerts/', config)
                results = tester.run_test()

                test_id = f"lp_test_{int(time.time())}"
                RealPerformanceTestRunner.store_results(test_id, {
                    'test_id': test_id,
                    'results': {'longpolling': results},
                    'test_type': 'isolated_longpolling'
                })

            thread = threading.Thread(target=run_longpolling_test)
            thread.daemon = True
            thread.start()

            return Response({
                'status': 'started',
                'message': 'Isolated Long Polling test started',
                'technology': 'longpolling'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to start Long Polling test: {e}")
            return Response({
                'error': 'Failed to start Long Polling test',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def test_firebase(self, request):
        """Run isolated Firebase performance test"""
        serializer = PerformanceTestConfigSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        config = serializer.validated_data
        logger.info(f"Running isolated Firebase test: {config}")

        try:
            from .performance_tests import RealFirebaseTester

            def run_firebase_test():
                tester = RealFirebaseTester('http://localhost:8001/api/push', config)
                results = tester.run_test()

                test_id = f"fb_test_{int(time.time())}"
                RealPerformanceTestRunner.store_results(test_id, {
                    'test_id': test_id,
                    'results': {'firebase': results},
                    'test_type': 'isolated_firebase'
                })

            thread = threading.Thread(target=run_firebase_test)
            thread.daemon = True
            thread.start()

            return Response({
                'status': 'started',
                'message': 'Isolated Firebase test started',
                'technology': 'firebase'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to start Firebase test: {e}")
            return Response({
                'error': 'Failed to start Firebase test',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def get_metrics_comparison(self, request):
        """Get real-time metrics comparison from live servers"""
        try:
            import requests
            import time

            comparison_data = {
                'timestamp': time.time() * 1000,
                'technologies': {}
            }

            # Get WebSocket metrics from server
            try:
                ws_response = requests.get('http://localhost:8001/api/ws/metrics/', timeout=5)
                if ws_response.status_code == 200:
                    comparison_data['technologies']['websocket'] = ws_response.json()
            except:
                comparison_data['technologies']['websocket'] = {'error': 'Unable to connect'}

            # Get Long Polling metrics from server
            try:
                lp_response = requests.get('http://localhost:8001/api/poll/metrics/', timeout=5)
                if lp_response.status_code == 200:
                    comparison_data['technologies']['longpolling'] = lp_response.json()
            except:
                comparison_data['technologies']['longpolling'] = {'error': 'Unable to connect'}

            # Get Firebase metrics from server
            try:
                fb_response = requests.get('http://localhost:8001/api/push/stats/', timeout=5)
                if fb_response.status_code == 200:
                    comparison_data['technologies']['firebase'] = fb_response.json()
            except:
                comparison_data['technologies']['firebase'] = {'error': 'Unable to connect'}

            return Response(comparison_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to get metrics comparison: {e}")
            return Response({
                'error': 'Failed to get metrics comparison',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TechnologyMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for technology metrics (read-only)"""
    queryset = TechnologyMetrics.objects.all()
    serializer_class = TechnologyMetricsSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def live_comparison(self, request):
        """Get live performance comparison"""
        try:
            metrics = {}

            # Get metrics for each technology
            for tech_obj in TechnologyMetrics.objects.all():
                metrics[tech_obj.technology] = {
                    'avg_latency_ms': tech_obj.avg_latency_ms,
                    'success_rate': tech_obj.success_rate,
                    'messages_per_second': tech_obj.messages_per_second,
                    'total_attempts': tech_obj.total_attempts,
                    'last_updated': tech_obj.last_updated.isoformat()
                }

            return Response({
                'live_metrics': metrics,
                'timestamp': time.time() * 1000
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to get live comparison: {e}")
            return Response({
                'error': 'Failed to get live comparison',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
