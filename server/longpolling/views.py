"""
Simple Long Polling Views - For simple alert generation testing
"""
import json
import time
import threading
import psutil
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# Performance Metrics Collection
class RealTimeMetrics:
    def __init__(self):
        self.request_times = []
        self.response_sizes = []
        self.memory_usage = []
        self.cpu_usage = []
        self.active_connections = 0
        self.total_requests = 0
        self.failed_requests = 0
        self.start_time = time.time()

    def record_request(self, response_time_ms, response_size_bytes, success=True):
        """Record real request metrics"""
        self.request_times.append(response_time_ms)
        self.response_sizes.append(response_size_bytes)
        self.total_requests += 1

        if not success:
            self.failed_requests += 1

        # Capture system metrics
        try:
            process = psutil.Process(os.getpid())
            self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
            self.cpu_usage.append(process.cpu_percent())
        except:
            pass  # Skip if psutil fails

    def get_real_metrics(self):
        """Get real-time performance metrics"""
        if not self.request_times:
            return self._empty_metrics()

        import statistics

        duration = time.time() - self.start_time

        return {
            'connection_time_ms': min(self.request_times) if self.request_times else 0,
            'message_latency_ms': statistics.mean(self.request_times),
            'latency_min_ms': min(self.request_times),
            'latency_max_ms': max(self.request_times),
            'latency_p95_ms': self._percentile(self.request_times, 95),
            'throughput_msg_per_sec': self.total_requests / duration if duration > 0 else 0,
            'success_rate_percent': (self.total_requests - self.failed_requests) / self.total_requests * 100 if self.total_requests > 0 else 0,
            'memory_usage_mb': statistics.mean(self.memory_usage) if self.memory_usage else 0,
            'cpu_usage_percent': statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
            'network_bytes_sent': sum(self.response_sizes),
            'network_bytes_received': self.total_requests * 100,
            'error_rate_percent': self.failed_requests / self.total_requests * 100 if self.total_requests > 0 else 0,
            'reconnection_count': 0,
            'total_requests': self.total_requests,
            'active_connections': self.active_connections
        }

    def _percentile(self, data, percentile):
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def _empty_metrics(self):
        """Return empty metrics structure"""
        return {
            'connection_time_ms': 0, 'message_latency_ms': 0, 'latency_min_ms': 0,
            'latency_max_ms': 0, 'latency_p95_ms': 0, 'throughput_msg_per_sec': 0,
            'success_rate_percent': 0, 'memory_usage_mb': 0, 'cpu_usage_percent': 0,
            'network_bytes_sent': 0, 'network_bytes_received': 0, 'error_rate_percent': 0,
            'reconnection_count': 0, 'total_requests': 0, 'active_connections': 0
        }


# Simple Alert Management System for testing
class AlertManager:
    def __init__(self):
        self.alerts = []
        self.client_positions = {}  # Track where each client is in the sequence
        self.last_update_time = time.time()
        self._lock = threading.Lock()
        self.alert_id_counter = 0  # For unique alert IDs

    def load_alerts(self):
        """Load alerts from JSON file"""
        try:
            with open(settings.ALERTS_JSON_FILE, 'r') as f:
                data = json.load(f)
                with self._lock:
                    file_alerts = data.get('alerts', [])
                    # Add alert IDs to file alerts if they don't have them
                    for i, alert in enumerate(file_alerts):
                        if 'alert_id' not in alert:
                            alert['alert_id'] = f"file_alert_{i}"
                            alert['source'] = 'file'
                    self.alerts = file_alerts
                    self.last_update_time = time.time()
                logger.info(f"Loaded {len(self.alerts)} alerts from JSON")
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
            self.alerts = []

    def add_alert(self, title, message):
        """Add a new alert dynamically - will be available to all clients"""
        with self._lock:
            self.alert_id_counter += 1
            new_alert = {
                'alert_id': f"generated_alert_{self.alert_id_counter}",
                'title': title,
                'message': message,
                'timestamp': time.time() * 1000,
                'source': 'dynamic',
                'created_at': time.time()
            }
            self.alerts.append(new_alert)
            self.last_update_time = time.time()

            logger.info(f"Added alert: {title} (Total alerts: {len(self.alerts)})")
            return new_alert

    def get_next_alert_for_client(self, client_id):
        """Get next alert for specific client"""
        with self._lock:
            if client_id not in self.client_positions:
                self.client_positions[client_id] = 0

            current_position = self.client_positions[client_id]

            if current_position < len(self.alerts):
                alert = self.alerts[current_position]
                logger.info(f"Serving alert {current_position + 1}/{len(self.alerts)} to client {client_id}: {alert.get('title', 'Untitled')}")
                return alert

        return None

    def mark_alert_delivered(self, client_id):
        """Mark alert as delivered and increment client position"""
        with self._lock:
            if client_id in self.client_positions:
                self.client_positions[client_id] += 1
                logger.info(f"Client {client_id} position incremented to {self.client_positions[client_id]}")

    def has_new_data_for_client(self, client_id):
        """Check if client has unseen alerts"""
        with self._lock:
            position = self.client_positions.get(client_id, 0)
            has_more = position < len(self.alerts)
            logger.debug(f"Client {client_id}: position {position}/{len(self.alerts)}, has_more: {has_more}")
            return has_more

    def reset_client_position(self, client_id=None):
        """Reset client position(s)"""
        with self._lock:
            if client_id:
                self.client_positions[client_id] = 0
                logger.info(f"Reset position for client {client_id}")
            else:
                self.client_positions.clear()
                logger.info("Reset positions for all clients")

    def get_client_status(self, client_id):
        """Get status for a specific client"""
        with self._lock:
            position = self.client_positions.get(client_id, 0)
            total = len(self.alerts)
            return {
                'current_position': position,
                'total_alerts': total,
                'has_more': position < total,
                'next_alert_title': self.alerts[position].get('title', 'N/A') if position < total else 'No more alerts'
            }


# Global instances
metrics_collector = RealTimeMetrics()
alert_manager = AlertManager()
alert_manager.load_alerts()


@csrf_exempt
@require_http_methods(["GET", "POST"])
def long_poll_alerts(request):
    """PROPER Long polling endpoint - waits for data or times out"""
    request_start_time = time.time()
    metrics_collector.active_connections += 1

    try:
        # Get parameters
        client_id = request.GET.get('client_id', f'client_{int(time.time() * 1000)}')
        timeout = min(int(request.GET.get('timeout', 20)), 60)

        logger.info(f"Long poll request from client {client_id}, timeout: {timeout}s")

        # Check for immediate data availability
        if alert_manager.has_new_data_for_client(client_id):
            alert = alert_manager.get_next_alert_for_client(client_id)

            if alert:
                alert_manager.mark_alert_delivered(client_id)

                response_data = {
                    'alert': {
                        'title': alert.get('title', 'Alert'),
                        'message': alert.get('message', 'Alert message'),
                        'sequence': alert_manager.client_positions.get(client_id, 1),
                        'total': len(alert_manager.alerts),
                        'timestamp': time.time() * 1000,
                        'alert_id': alert.get('alert_id', 'unknown'),
                        'source': alert.get('source', 'unknown'),
                        'server_process_time': (time.time() - request_start_time) * 1000
                    },
                    'has_more': alert_manager.has_new_data_for_client(client_id),
                    'client_id': client_id,
                    'wait_time': time.time() - request_start_time,
                    'immediate': True,
                    'server_timestamp': time.time() * 1000
                }

                response = JsonResponse(response_data)
                response_time = (time.time() - request_start_time) * 1000
                response_size = len(response.content)
                metrics_collector.record_request(response_time, response_size, True)

                logger.info(f"Immediate alert delivered to {client_id}: {alert.get('title', 'Unknown')} - {response_time:.2f}ms")
                return response

        # No immediate data - implement PROPER long polling
        poll_start_time = time.time()
        poll_interval = 0.1

        logger.info(f"Starting long poll for client {client_id}, checking every {poll_interval}s")

        while (time.time() - poll_start_time) < timeout:
            time.sleep(poll_interval)

            # Check for new data
            if alert_manager.has_new_data_for_client(client_id):
                alert = alert_manager.get_next_alert_for_client(client_id)

                if alert:
                    alert_manager.mark_alert_delivered(client_id)

                    poll_duration = time.time() - poll_start_time
                    total_duration = time.time() - request_start_time

                    response_data = {
                        'alert': {
                            'title': alert.get('title', 'Alert'),
                            'message': alert.get('message', 'Alert message'),
                            'sequence': alert_manager.client_positions.get(client_id, 1),
                            'total': len(alert_manager.alerts),
                            'timestamp': time.time() * 1000,
                            'alert_id': alert.get('alert_id', 'unknown'),
                            'source': alert.get('source', 'unknown'),
                            'server_process_time': total_duration * 1000
                        },
                        'has_more': alert_manager.has_new_data_for_client(client_id),
                        'client_id': client_id,
                        'wait_time': total_duration,
                        'poll_duration': poll_duration,
                        'immediate': False,
                        'server_timestamp': time.time() * 1000,
                        'poll_cycles': int(poll_duration / poll_interval)
                    }

                    response = JsonResponse(response_data)
                    response_time = total_duration * 1000
                    response_size = len(response.content)
                    metrics_collector.record_request(response_time, response_size, True)

                    logger.info(f"Long poll alert delivered to {client_id} after {poll_duration:.2f}s: {alert.get('title', 'Unknown')}")
                    return response

        # Timeout reached
        total_duration = time.time() - request_start_time
        timeout_response_data = {
            'alert': None,
            'timeout': True,
            'client_id': client_id,
            'wait_time': total_duration,
            'poll_duration': total_duration,
            'message': 'Long poll timeout - no new alerts available',
            'server_timestamp': time.time() * 1000,
            'poll_cycles': int(total_duration / poll_interval),
            'has_more': alert_manager.has_new_data_for_client(client_id)
        }

        response = JsonResponse(timeout_response_data)
        response_time = total_duration * 1000
        response_size = len(response.content)
        metrics_collector.record_request(response_time, response_size, True)

        logger.info(f"Long poll timeout for {client_id} after {total_duration:.2f}s")
        return response

    except Exception as e:
        logger.error(f"Error in long polling for {client_id}: {e}")
        error_response = JsonResponse({
            'error': str(e),
            'client_id': client_id,
            'server_timestamp': time.time() * 1000
        }, status=500)

        response_time = (time.time() - request_start_time) * 1000
        response_size = len(error_response.content)
        metrics_collector.record_request(response_time, response_size, False)
        return error_response
    finally:
        metrics_collector.active_connections -= 1


@csrf_exempt
@require_http_methods(["POST"])
def add_new_alert(request):
    """Add a new alert that will be immediately available to polling clients"""
    request_start_time = time.time()

    try:
        data = json.loads(request.body)
        title = data.get('title', f'Alert {int(time.time())}')
        message = data.get('message', 'New alert message')

        # Add the alert to the manager
        new_alert = alert_manager.add_alert(title, message)

        response_data = {
            'success': True,
            'message': 'Alert added successfully',
            'alert': new_alert,
            'total_alerts': len(alert_manager.alerts),
            'active_clients': len(alert_manager.client_positions),
            'server_timestamp': time.time() * 1000
        }

        response = JsonResponse(response_data)
        response_time = (time.time() - request_start_time) * 1000
        response_size = len(response.content)
        metrics_collector.record_request(response_time, response_size, True)

        logger.info(f"New alert added via API: {title}")
        return response
    except Exception as e:
        logger.error(f"Error adding new alert: {e}")
        error_response = JsonResponse({
            'success': False,
            'error': str(e),
            'server_timestamp': time.time() * 1000
        }, status=500)

        response_time = (time.time() - request_start_time) * 1000
        response_size = len(error_response.content)
        metrics_collector.record_request(response_time, response_size, False)
        return error_response


@require_http_methods(["GET"])
def get_all_alerts(request):
    """Get all available alerts"""
    request_start_time = time.time()

    try:
        response_data = {
            'alerts': alert_manager.alerts,
            'total_count': len(alert_manager.alerts),
            'file_alerts': len([a for a in alert_manager.alerts if a.get('source') == 'file']),
            'dynamic_alerts': len([a for a in alert_manager.alerts if a.get('source') == 'dynamic']),
            'server_timestamp': time.time() * 1000
        }

        response = JsonResponse(response_data)
        response_time = (time.time() - request_start_time) * 1000
        response_size = len(response.content)
        metrics_collector.record_request(response_time, response_size, True)

        return response
    except Exception as e:
        logger.error(f"Error getting all alerts: {e}")
        error_response = JsonResponse({'error': str(e)}, status=500)
        response_time = (time.time() - request_start_time) * 1000
        response_size = len(error_response.content)
        metrics_collector.record_request(response_time, response_size, False)
        return error_response


@csrf_exempt
@require_http_methods(["POST"])
def reset_alert_index(request):
    """Reset the alert index for a client or all clients"""
    request_start_time = time.time()

    try:
        client_id = request.POST.get('client_id')

        if client_id:
            alert_manager.reset_client_position(client_id)
            message = f'Alert position reset for client {client_id}'
        else:
            alert_manager.reset_client_position()
            message = 'Alert positions reset for all clients'

        response_data = {
            'success': True,
            'message': message,
            'timestamp': time.time() * 1000,
            'server_timestamp': time.time() * 1000,
            'client_id': client_id if client_id else 'all',
            'total_alerts': len(alert_manager.alerts)
        }

        response = JsonResponse(response_data)
        response_time = (time.time() - request_start_time) * 1000
        response_size = len(response.content)
        metrics_collector.record_request(response_time, response_size, True)

        logger.info(message)
        return response
    except Exception as e:
        logger.error(f"Error resetting alert index: {e}")
        error_response = JsonResponse({'error': str(e)}, status=500)
        response_time = (time.time() - request_start_time) * 1000
        response_size = len(error_response.content)
        metrics_collector.record_request(response_time, response_size, False)
        return error_response


@require_http_methods(["GET"])
def poll_status(request):
    """Get current polling status"""
    request_start_time = time.time()

    try:
        client_id = request.GET.get('client_id', 'unknown')
        status_info = alert_manager.get_client_status(client_id)

        response_data = {
            'client_id': client_id,
            **status_info,
            'server_timestamp': time.time() * 1000,
            'total_clients': len(alert_manager.client_positions),
            'active_connections': metrics_collector.active_connections
        }

        response = JsonResponse(response_data)
        response_time = (time.time() - request_start_time) * 1000
        response_size = len(response.content)
        metrics_collector.record_request(response_time, response_size, True)

        return response
    except Exception as e:
        logger.error(f"Error getting poll status: {e}")
        error_response = JsonResponse({'error': str(e)}, status=500)
        response_time = (time.time() - request_start_time) * 1000
        response_size = len(error_response.content)
        metrics_collector.record_request(response_time, response_size, False)
        return error_response


@csrf_exempt
@require_http_methods(["POST"])
def simulate_new_alert(request):
    """Legacy endpoint - redirects to add_new_alert for backwards compatibility"""
    return add_new_alert(request)


@require_http_methods(["GET"])
def get_performance_metrics(request):
    """Get real-time performance metrics for long polling"""
    request_start_time = time.time()

    try:
        real_metrics = metrics_collector.get_real_metrics()

        response_data = {
            'technology': 'longpolling',
            'metrics': real_metrics,
            'timestamp': time.time() * 1000,
            'uptime_seconds': time.time() - metrics_collector.start_time,
            'active_clients': len(alert_manager.client_positions),
            'total_alerts': len(alert_manager.alerts),
            'file_alerts': len([a for a in alert_manager.alerts if a.get('source') == 'file']),
            'dynamic_alerts': len([a for a in alert_manager.alerts if a.get('source') == 'dynamic'])
        }

        response = JsonResponse(response_data)
        response_time = (time.time() - request_start_time) * 1000
        response_size = len(response.content)
        metrics_collector.record_request(response_time, response_size, True)

        return response
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        error_response = JsonResponse({'error': str(e)}, status=500)
        response_time = (time.time() - request_start_time) * 1000
        response_size = len(error_response.content)
        metrics_collector.record_request(response_time, response_size, False)
        return error_response


@csrf_exempt
@require_http_methods(["POST"])
def reset_performance_metrics(request):
    """Reset performance metrics"""
    global metrics_collector
    metrics_collector = RealTimeMetrics()

    return JsonResponse({
        'message': 'Performance metrics reset',
        'timestamp': time.time() * 1000
    })
