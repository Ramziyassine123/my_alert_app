# ServerSide/websocket_alerts/views.py

import time
import psutil
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import logging

logger = logging.getLogger(__name__)

# Import websocket_metrics at module level to avoid import errors
try:
    from .consumers import websocket_metrics
except ImportError:
    # Create a dummy metrics object if import fails
    class DummyMetrics:
        def __init__(self):
            self.connections_count = 0
            self.messages_sent = 0
            self.messages_received = 0

        def get_real_metrics(self):
            return {
                'connection_time_ms': 0,
                'message_latency_ms': 0,
                'ping_latency_ms': 0,
                'latency_min_ms': 0,
                'latency_max_ms': 0,
                'latency_p95_ms': 0,
                'throughput_msg_per_sec': 0,
                'success_rate_percent': 100,
                'memory_usage_mb': 0,
                'cpu_usage_percent': 0,
                'network_bytes_sent': 0,
                'network_bytes_received': 0,
                'error_rate_percent': 0,
                'reconnection_count': 0,
                'active_connections': self.connections_count,
                'total_messages_sent': self.messages_sent,
                'total_messages_received': self.messages_received
            }

    websocket_metrics = DummyMetrics()
    logger.warning("Using dummy WebSocket metrics - consumers module not available")


@require_http_methods(["GET"])
def health_check(request):
    """Health check for WebSocket service"""
    try:
        health_status = {
            'status': 'healthy',
            'service': 'websocket_alerts',
            'timestamp': time.time() * 1000,
            'websocket_url': 'ws://127.0.0.1:8001/ws/alerts/',
            'role': 'SERVER',
            'port': 8001,
            'active_connections': websocket_metrics.connections_count,
            'messages_sent': websocket_metrics.messages_sent,
            'messages_received': websocket_metrics.messages_received,
        }

        # Check system resources
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)

            health_status['system'] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024 ** 3)
            }

            if memory.percent > 90 or cpu_percent > 95:
                health_status['status'] = 'degraded'

        except Exception as e:
            health_status['system_check_error'] = str(e)

        status_code = 200 if health_status['status'] == 'healthy' else 503
        return JsonResponse(health_status, status=status_code)

    except Exception as e:
        logger.error(f"WebSocket health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'service': 'websocket_alerts',
            'error': str(e),
            'timestamp': time.time() * 1000,
            'role': 'SERVER'
        }, status=500)


@require_http_methods(["GET"])
def server_stats(request):
    """Get WebSocket server statistics"""
    try:
        metrics = websocket_metrics.get_real_metrics()

        stats = {
            'service': 'websocket_alerts',
            'timestamp': time.time() * 1000,
            'metrics': metrics,
            'websocket_url': 'ws://127.0.0.1:8001/ws/alerts/',
            'server_info': {
                'name': 'ServerSide Alert Server',
                'port': 8001,
                'role': 'SERVER',
                'technology': 'WebSocket'
            }
        }

        return JsonResponse(stats)

    except Exception as e:
        logger.error(f"Failed to get WebSocket stats: {e}")
        return JsonResponse({
            'error': 'Failed to get WebSocket statistics',
            'details': str(e),
            'service': 'websocket_alerts',
            'role': 'SERVER'
        }, status=500)


@require_http_methods(["GET"])
def performance_metrics(request):
    """Get detailed WebSocket performance metrics"""
    try:
        metrics = websocket_metrics.get_real_metrics()

        performance_data = {
            'service': 'websocket_alerts',
            'technology': 'websocket',
            'timestamp': time.time() * 1000,
            'performance_metrics': metrics,
            'server_capabilities': {
                'max_connections': 1000,
                'protocols_supported': ['ws', 'wss'],
                'features': [
                    'real_time_messaging',
                    'delivery_confirmation',
                    'performance_tracking',
                    'connection_monitoring'
                ]
            },
            'server_info': {
                'name': 'ServerSide Alert Server',
                'port': 8001,
                'role': 'SERVER',
                'websocket_url': 'ws://127.0.0.1:8001/ws/alerts/'
            }
        }

        return JsonResponse(performance_data)

    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return JsonResponse({
            'error': 'Failed to get performance metrics',
            'details': str(e),
            'service': 'websocket_alerts',
            'role': 'SERVER'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reset_metrics(request):
    """Reset WebSocket performance metrics"""
    try:
        # Reset global metrics
        global websocket_metrics
        try:
            from .consumers import RealTimeWebSocketMetrics
            websocket_metrics = RealTimeWebSocketMetrics()
        except ImportError:
            # If import fails, create dummy metrics
            class DummyMetrics:
                def __init__(self):
                    self.connections_count = 0
                    self.messages_sent = 0
                    self.messages_received = 0

                def get_real_metrics(self):
                    return {
                        'connection_time_ms': 0, 'message_latency_ms': 0, 'ping_latency_ms': 0,
                        'latency_min_ms': 0, 'latency_max_ms': 0, 'latency_p95_ms': 0,
                        'throughput_msg_per_sec': 0, 'success_rate_percent': 100,
                        'memory_usage_mb': 0, 'cpu_usage_percent': 0,
                        'network_bytes_sent': 0, 'network_bytes_received': 0,
                        'error_rate_percent': 0, 'reconnection_count': 0,
                        'active_connections': self.connections_count,
                        'total_messages_sent': self.messages_sent,
                        'total_messages_received': self.messages_received
                    }

            websocket_metrics = DummyMetrics()

        return JsonResponse({
            'status': 'success',
            'message': 'WebSocket metrics reset successfully',
            'timestamp': time.time() * 1000,
            'service': 'websocket_alerts',
            'role': 'SERVER'
        })

    except Exception as e:
        logger.error(f"Failed to reset metrics: {e}")
        return JsonResponse({
            'error': 'Failed to reset metrics',
            'details': str(e),
            'service': 'websocket_alerts',
            'role': 'SERVER'
        }, status=500)


@require_http_methods(["GET"])
def connection_info(request):
    """Get WebSocket connection information"""
    try:
        connection_info = {
            'websocket_url': 'ws://127.0.0.1:8001/ws/alerts/',
            'protocol': 'WebSocket',
            'server_name': 'ServerSide Alert Server',
            'server_port': 8001,
            'role': 'SERVER',
            'connection_guide': {
                'javascript': 'new WebSocket("ws://127.0.0.1:8001/ws/alerts/")',
                'python': 'websocket.create_connection("ws://127.0.0.1:8001/ws/alerts/")',
                'supported_messages': [
                    'start_alerts',
                    'stop_alerts',
                    'ping',
                    'delivery_confirmation',
                    'performance_request'
                ]
            },
            'features': [
                'Real-time bidirectional communication',
                'Low latency message delivery',
                'Connection state monitoring',
                'Performance metrics collection',
                'Delivery confirmation support'
            ],
            'timestamp': time.time() * 1000
        }

        return JsonResponse(connection_info)

    except Exception as e:
        logger.error(f"Failed to get connection info: {e}")
        return JsonResponse({
            'error': 'Failed to get connection information',
            'details': str(e),
            'service': 'websocket_alerts',
            'role': 'SERVER'
        }, status=500)
