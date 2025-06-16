# alerts/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import threading
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


@csrf_exempt
@require_http_methods(["POST"])
def run_performance_test(request):
    """Run performance tests for all three technologies"""
    try:
        data = json.loads(request.body)
        test_config = {
            'duration': data.get('duration', 60),  # Test duration in seconds
            'message_count': data.get('message_count', 10),  # Number of messages to send
            'concurrent_clients': data.get('concurrent_clients', 5),  # Number of concurrent clients
            'message_interval': data.get('message_interval', 2),  # Interval between messages
            'technologies': data.get('technologies', ['websocket', 'longpolling', 'push'])
        }

        # Run tests in background thread
        test_runner = PerformanceTestRunner(test_config)
        thread = threading.Thread(target=test_runner.run_tests)
        thread.daemon = True
        thread.start()

        return JsonResponse({
            'status': 'started',
            'message': 'Performance tests started',
            'test_id': test_runner.test_id,
            'config': test_config
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_test_results(request):
    """Get performance test results"""
    try:
        test_id = request.GET.get('test_id')
        if test_id:
            # Get specific test results
            results = PerformanceTestRunner.get_test_results(test_id)
        else:
            # Get latest test results
            results = PerformanceTestRunner.get_latest_results()

        return JsonResponse(results)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
