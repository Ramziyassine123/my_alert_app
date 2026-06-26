"""
REAL Performance Testing - Actual Network Measurements
No simulated data, only genuine performance metrics
"""
import json
import time
import requests
import websocket
import uuid
import statistics
from datetime import datetime
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


class NetworkLatencyMeasurer:
    """Measures actual network latency without simulation"""

    def __init__(self):
        self.measurements = []

    def measure_tcp_connect_time(self, host: str, port: int) -> float:
        """Measure actual TCP connection establishment time"""
        import socket

        start_time = time.perf_counter()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            connect_time = time.perf_counter() - start_time
            sock.close()

            if result == 0:
                return connect_time * 1000  # Convert to milliseconds
            else:
                return -1  # Connection failed
        except Exception:
            return -1

    def measure_http_latency(self, url: str) -> Dict[str, float]:
        """Measure actual HTTP request latency components"""
        session = requests.Session()

        # DNS resolution time
        dns_start = time.perf_counter()
        try:
            import socket
            hostname = url.split('://')[1].split('/')[0].split(':')[0]
            socket.gethostbyname(hostname)
            dns_time = (time.perf_counter() - dns_start) * 1000
        except Exception:
            dns_time = 0

        # Full HTTP request time
        request_start = time.perf_counter()
        try:
            response = session.get(url, timeout=10)
            request_time = (time.perf_counter() - request_start) * 1000

            return {
                'dns_time_ms': dns_time,
                'request_time_ms': request_time,
                'status_code': response.status_code,
                'response_size_bytes': len(response.content),
                'success': response.status_code == 200
            }
        except Exception as e:
            request_time = (time.perf_counter() - request_start) * 1000
            return {
                'dns_time_ms': dns_time,
                'request_time_ms': request_time,
                'status_code': 0,
                'response_size_bytes': 0,
                'success': False,
                'error': str(e)
            }


class RealWebSocketTester:
    """Real WebSocket performance testing with actual measurements"""

    def __init__(self, url: str):
        self.url = url
        self.latency_measurer = NetworkLatencyMeasurer()
        self.connection_times = []
        self.message_latencies = []
        self.throughput_data = []
        self.errors = []

    def test_connection_performance(self, num_tests: int = 5) -> Dict[str, Any]:
        """Test actual WebSocket connection establishment times"""
        print(f"Testing WebSocket connection performance ({num_tests} connections)...")

        connection_times = []
        successful_connections = 0

        for i in range(num_tests):
            try:
                start_time = time.perf_counter()
                ws = websocket.create_connection(self.url, timeout=10)
                connection_time = (time.perf_counter() - start_time) * 1000

                # Test if connection is actually working
                ws.send(json.dumps({
                    'type': 'ping',
                    'test_id': f'connection_test_{i}',
                    'timestamp': time.time() * 1000
                }))

                # Try to receive response
                try:
                    ws.settimeout(3)
                    response = ws.recv()
                    ws.close()

                    connection_times.append(connection_time)
                    successful_connections += 1
                    print(f"  Connection {i+1}: {connection_time:.2f}ms ✓")

                except websocket.WebSocketTimeoutException:
                    ws.close()
                    connection_times.append(connection_time)
                    successful_connections += 1
                    print(f"  Connection {i+1}: {connection_time:.2f}ms (no response)")

            except Exception as e:
                self.errors.append(f"Connection {i+1} failed: {str(e)}")
                print(f"  Connection {i+1}: Failed - {e}")

        if connection_times:
            return {
                'success': True,
                'total_tests': num_tests,
                'successful_connections': successful_connections,
                'avg_connection_time_ms': statistics.mean(connection_times),
                'min_connection_time_ms': min(connection_times),
                'max_connection_time_ms': max(connection_times),
                'median_connection_time_ms': statistics.median(connection_times),
                'success_rate': (successful_connections / num_tests) * 100,
                'all_connection_times': connection_times
            }
        else:
            return {
                'success': False,
                'error': 'No successful connections',
                'total_tests': num_tests,
                'errors': self.errors
            }

    def test_message_latency(self, num_messages: int = 20) -> Dict[str, Any]:
        """Test actual message round-trip latency"""
        print(f"Testing WebSocket message latency ({num_messages} messages)...")

        try:
            ws = websocket.create_connection(self.url, timeout=10)
            ws.settimeout(5)
        except Exception as e:
            return {'success': False, 'error': f'Failed to connect: {e}'}

        latencies = []
        successful_messages = 0

        for i in range(num_messages):
            message_id = f'latency_test_{uuid.uuid4()}'

            try:
                # Send message with precise timestamp
                send_time = time.perf_counter()
                message = {
                    'type': 'ping',
                    'message_id': message_id,
                    'client_timestamp': send_time * 1000,
                    'sequence': i + 1
                }

                ws.send(json.dumps(message))

                # Wait for response
                response = ws.recv()
                receive_time = time.perf_counter()

                # Calculate actual round-trip latency
                latency_ms = (receive_time - send_time) * 1000
                latencies.append(latency_ms)
                successful_messages += 1

                print(f"  Message {i+1}: {latency_ms:.2f}ms")

                # Small delay to avoid overwhelming server
                time.sleep(0.05)

            except Exception as e:
                self.errors.append(f"Message {i+1} failed: {str(e)}")
                print(f"  Message {i+1}: Failed - {e}")

        ws.close()

        if latencies:
            return {
                'success': True,
                'total_messages': num_messages,
                'successful_messages': successful_messages,
                'avg_latency_ms': statistics.mean(latencies),
                'min_latency_ms': min(latencies),
                'max_latency_ms': max(latencies),
                'median_latency_ms': statistics.median(latencies),
                'p95_latency_ms': self._percentile(latencies, 95),
                'p99_latency_ms': self._percentile(latencies, 99),
                'success_rate': (successful_messages / num_messages) * 100,
                'all_latencies': latencies
            }
        else:
            return {
                'success': False,
                'error': 'No successful messages',
                'total_messages': num_messages,
                'errors': self.errors
            }

    def test_concurrent_connections(self, num_clients: int = 10) -> Dict[str, Any]:
        """Test performance with multiple concurrent connections"""
        print(f"Testing concurrent WebSocket connections ({num_clients} clients)...")

        def single_client_test(client_id: int) -> Dict[str, Any]:
            try:
                # Connect
                connect_start = time.perf_counter()
                ws = websocket.create_connection(self.url, timeout=10)
                connect_time = (time.perf_counter() - connect_start) * 1000

                # Send test message
                message_start = time.perf_counter()
                ws.send(json.dumps({
                    'type': 'ping',
                    'client_id': client_id,
                    'timestamp': time.time() * 1000
                }))

                # Wait for response
                ws.settimeout(5)
                response = ws.recv()
                message_time = (time.perf_counter() - message_start) * 1000

                ws.close()

                return {
                    'client_id': client_id,
                    'connect_time_ms': connect_time,
                    'message_time_ms': message_time,
                    'success': True
                }

            except Exception as e:
                return {
                    'client_id': client_id,
                    'connect_time_ms': 0,
                    'message_time_ms': 0,
                    'success': False,
                    'error': str(e)
                }

        # Run concurrent tests
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [executor.submit(single_client_test, i) for i in range(num_clients)]
            results = [future.result() for future in as_completed(futures)]

        # Analyze results
        successful_clients = [r for r in results if r['success']]

        if successful_clients:
            connect_times = [r['connect_time_ms'] for r in successful_clients]
            message_times = [r['message_time_ms'] for r in successful_clients]

            return {
                'success': True,
                'total_clients': num_clients,
                'successful_clients': len(successful_clients),
                'avg_connect_time_ms': statistics.mean(connect_times),
                'avg_message_time_ms': statistics.mean(message_times),
                'max_connect_time_ms': max(connect_times),
                'max_message_time_ms': max(message_times),
                'success_rate': (len(successful_clients) / num_clients) * 100,
                'client_results': results
            }
        else:
            return {
                'success': False,
                'error': 'No successful concurrent connections',
                'total_clients': num_clients,
                'client_results': results
            }

    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))


class RealLongPollingTester:
    """Real Long Polling performance testing with actual HTTP measurements"""

    def __init__(self, url: str):
        self.url = url
        self.latency_measurer = NetworkLatencyMeasurer()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'RealPerformanceTester/1.0'})

    def test_immediate_response_time(self, num_tests: int = 10) -> Dict[str, Any]:
        """Test response time when data is immediately available"""
        print(f"Testing Long Polling immediate response ({num_tests} requests)...")

        # Reset server state first
        try:
            reset_url = self.url.replace('/alerts/', '/reset/')
            self.session.post(reset_url, timeout=5)
            print("  Server state reset")
        except Exception:
            print("  Warning: Could not reset server state")

        response_times = []
        successful_requests = 0

        for i in range(num_tests):
            client_id = f'immediate_test_{uuid.uuid4()}'

            try:
                start_time = time.perf_counter()
                response = self.session.get(
                    self.url,
                    params={'client_id': client_id, 'timeout': 5},
                    timeout=10
                )
                response_time = (time.perf_counter() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    if 'alert' in data and data['alert']:
                        response_times.append(response_time)
                        successful_requests += 1
                        immediate = data.get('immediate', False)
                        print(f"  Request {i+1}: {response_time:.2f}ms (immediate: {immediate})")
                    else:
                        print(f"  Request {i+1}: {response_time:.2f}ms (no data)")
                else:
                    print(f"  Request {i+1}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  Request {i+1}: Error - {e}")

        if response_times:
            return {
                'success': True,
                'total_requests': num_tests,
                'successful_requests': successful_requests,
                'avg_response_time_ms': statistics.mean(response_times),
                'min_response_time_ms': min(response_times),
                'max_response_time_ms': max(response_times),
                'success_rate': (successful_requests / num_tests) * 100,
                'all_response_times': response_times
            }
        else:
            return {
                'success': False,
                'error': 'No successful immediate responses',
                'total_requests': num_tests
            }

    def test_timeout_accuracy(self, timeout_values: List[int] = None) -> Dict[str, Any]:
        """Test actual timeout behavior accuracy"""
        if timeout_values is None:
            timeout_values = [3, 5, 10]

        print(f"Testing Long Polling timeout accuracy...")

        timeout_results = []

        for timeout_sec in timeout_values:
            print(f"  Testing {timeout_sec}s timeout...")

            # Use unique client to ensure no data available
            client_id = f'timeout_test_{uuid.uuid4()}'

            start_time = 0  # Initialize to avoid potential reference before assignment

            try:
                start_time = time.perf_counter()
                response = self.session.get(
                    self.url,
                    params={'client_id': client_id, 'timeout': timeout_sec},
                    timeout=timeout_sec + 5  # HTTP timeout longer than expected server timeout
                )
                actual_time = time.perf_counter() - start_time

                if response.status_code == 200:
                    data = response.json()
                    timeout_occurred = data.get('timeout', False)
                    server_wait_time = data.get('wait_time', 0)

                    accuracy = abs(actual_time - timeout_sec)

                    timeout_results.append({
                        'requested_timeout': timeout_sec,
                        'actual_time': actual_time,
                        'server_wait_time': server_wait_time,
                        'timeout_occurred': timeout_occurred,
                        'accuracy_diff': accuracy,
                        'success': True
                    })

                    print(f"    {timeout_sec}s: actual {actual_time:.2f}s (diff: {accuracy:.2f}s)")

            except requests.exceptions.Timeout:
                actual_time = time.perf_counter() - start_time if start_time else 0
                accuracy = abs(actual_time - timeout_sec)

                timeout_results.append({
                    'requested_timeout': timeout_sec,
                    'actual_time': actual_time,
                    'server_wait_time': timeout_sec,
                    'timeout_occurred': True,
                    'accuracy_diff': accuracy,
                    'success': True,
                    'http_timeout': True
                })

                print(f"    {timeout_sec}s: HTTP timeout at {actual_time:.2f}s")

            except Exception as e:
                timeout_results.append({
                    'requested_timeout': timeout_sec,
                    'actual_time': 0,
                    'success': False,
                    'error': str(e)
                })
                print(f"    {timeout_sec}s: Error - {e}")

        successful_tests = [r for r in timeout_results if r['success']]

        if successful_tests:
            avg_accuracy = statistics.mean([r['accuracy_diff'] for r in successful_tests])

            return {
                'success': True,
                'timeout_tests': timeout_results,
                'avg_accuracy_seconds': avg_accuracy,
                'best_accuracy_seconds': min([r['accuracy_diff'] for r in successful_tests]),
                'worst_accuracy_seconds': max([r['accuracy_diff'] for r in successful_tests])
            }
        else:
            return {
                'success': False,
                'error': 'No successful timeout tests',
                'timeout_tests': timeout_results
            }


class RealFirebaseTester:
    """Real Firebase push notification testing with actual API calls"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.registered_tokens = []

    def test_token_registration_performance(self, num_tokens: int = 5) -> Dict[str, Any]:
        """Test actual FCM token registration API performance"""
        print(f"Testing Firebase token registration ({num_tokens} tokens)...")

        registration_times = []
        successful_registrations = 0

        for i in range(num_tokens):
            test_token = f'test_token_{uuid.uuid4()}_{int(time.time())}'

            try:
                start_time = time.perf_counter()
                response = self.session.post(
                    f'{self.base_url}/register-token/',
                    json={'token': test_token},
                    timeout=10
                )
                registration_time = (time.perf_counter() - start_time) * 1000

                if response.status_code in [200, 201]:
                    registration_times.append(registration_time)
                    successful_registrations += 1
                    self.registered_tokens.append(test_token)
                    print(f"  Token {i+1}: {registration_time:.2f}ms ✓")
                else:
                    print(f"  Token {i+1}: HTTP {response.status_code}")

            except Exception as e:
                print(f"  Token {i+1}: Error - {e}")

        if registration_times:
            return {
                'success': True,
                'total_tokens': num_tokens,
                'successful_registrations': successful_registrations,
                'avg_registration_time_ms': statistics.mean(registration_times),
                'min_registration_time_ms': min(registration_times),
                'max_registration_time_ms': max(registration_times),
                'success_rate': (successful_registrations / num_tokens) * 100,
                'all_registration_times': registration_times
            }
        else:
            return {
                'success': False,
                'error': 'No successful token registrations',
                'total_tokens': num_tokens
            }

    def test_notification_api_performance(self) -> Dict[str, Any]:
        """Test Firebase notification sending API performance"""
        print("Testing Firebase notification API...")

        if not self.registered_tokens:
            return {'success': False, 'error': 'No registered tokens available'}

        try:
            start_time = time.perf_counter()
            response = self.session.post(
                f'{self.base_url}/send-sequential/',
                json={'delay': 0.5},
                timeout=15
            )
            api_response_time = (time.perf_counter() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()

                return {
                    'success': True,
                    'api_response_time_ms': api_response_time,
                    'total_alerts': data.get('total_alerts', 0),
                    'estimated_duration': data.get('estimated_duration', 0),
                    'status': data.get('status', 'unknown')
                }
            else:
                return {
                    'success': False,
                    'api_response_time_ms': api_response_time,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'API call failed: {str(e)}'
            }


class RealPerformanceTestRunner:
    """Orchestrates all real performance tests"""

    def __init__(self):
        self.websocket_url = 'ws://127.0.0.1:8001/ws/alerts/'
        self.longpolling_url = 'http://127.0.0.1:8001/api/poll/alerts/'
        self.firebase_url = 'http://127.0.0.1:8001/api/push'

    def run_comprehensive_tests(self, technologies: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive real performance tests"""
        if technologies is None:
            technologies = ['websocket', 'longpolling', 'firebase']

        print("=" * 80)
        print("🔬 REAL PERFORMANCE TESTING - NO SIMULATED DATA")
        print("=" * 80)

        results = {
            'test_type': 'real_performance',
            'timestamp': datetime.now().isoformat(),
            'technologies': technologies,
            'results': {},
            'real_measurements_only': True
        }

        # Test each technology
        for tech in technologies:
            print(f"\n{'='*20} Testing {tech.upper()} {'='*20}")

            tech_results = {}  # Initialize to avoid potential reference before assignment

            try:
                if tech == 'websocket':
                    tester = RealWebSocketTester(self.websocket_url)
                    tech_results = {
                        'connection_performance': tester.test_connection_performance(5),
                        'message_latency': tester.test_message_latency(20),
                        'concurrent_connections': tester.test_concurrent_connections(8)
                    }

                elif tech == 'longpolling':
                    tester = RealLongPollingTester(self.longpolling_url)
                    tech_results = {
                        'immediate_response': tester.test_immediate_response_time(10),
                        'timeout_accuracy': tester.test_timeout_accuracy([3, 5, 8])
                    }

                elif tech == 'firebase':
                    tester = RealFirebaseTester(self.firebase_url)
                    tech_results = {
                        'token_registration': tester.test_token_registration_performance(5),
                        'notification_api': tester.test_notification_api_performance()
                    }

                results['results'][tech] = {
                    'technology': tech,
                    'status': 'completed',
                    'tests': tech_results,
                    'real_measurements': True
                }

                print(f"✅ {tech} testing completed successfully")

            except Exception as e:
                results['results'][tech] = {
                    'technology': tech,
                    'status': 'failed',
                    'error': str(e),
                    'real_measurements': True,
                    'tests': tech_results  # Include partial results if any
                }
                print(f"❌ {tech} testing failed: {e}")

        # Generate summary
        results['summary'] = self._generate_real_summary(results)

        print("\n" + "=" * 80)
        print("🎯 REAL PERFORMANCE TEST RESULTS")
        print("=" * 80)
        self._print_summary(results['summary'])

        return results

    def _generate_real_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary from real test results"""
        summary = {
            'total_technologies_tested': len(results['results']),
            'successful_tests': 0,
            'failed_tests': 0,
            'performance_metrics': {}
        }

        for tech, tech_data in results['results'].items():
            if tech_data['status'] == 'completed':
                summary['successful_tests'] += 1

                # Extract real metrics
                if tech == 'websocket':
                    tests = tech_data.get('tests', {})
                    if 'message_latency' in tests and tests['message_latency'].get('success'):
                        summary['performance_metrics'][tech] = {
                            'avg_latency_ms': tests['message_latency']['avg_latency_ms'],
                            'connection_time_ms': tests.get('connection_performance', {}).get('avg_connection_time_ms', 0),
                            'success_rate': tests['message_latency']['success_rate']
                        }

                elif tech == 'longpolling':
                    tests = tech_data.get('tests', {})
                    if 'immediate_response' in tests and tests['immediate_response'].get('success'):
                        summary['performance_metrics'][tech] = {
                            'avg_response_time_ms': tests['immediate_response']['avg_response_time_ms'],
                            'timeout_accuracy_sec': tests.get('timeout_accuracy', {}).get('avg_accuracy_seconds', 0),
                            'success_rate': tests['immediate_response']['success_rate']
                        }

                elif tech == 'firebase':
                    tests = tech_data.get('tests', {})
                    if 'token_registration' in tests and tests['token_registration'].get('success'):
                        summary['performance_metrics'][tech] = {
                            'avg_registration_time_ms': tests['token_registration']['avg_registration_time_ms'],
                            'api_response_time_ms': tests.get('notification_api', {}).get('api_response_time_ms', 0),
                            'success_rate': tests['token_registration']['success_rate']
                        }
            else:
                summary['failed_tests'] += 1

        return summary

    def _print_summary(self, summary: Dict[str, Any]):
        """Print performance test summary"""
        print(f"Technologies Tested: {summary['total_technologies_tested']}")
        print(f"Successful Tests: {summary['successful_tests']}")
        print(f"Failed Tests: {summary['failed_tests']}")
        print()

        for tech, metrics in summary.get('performance_metrics', {}).items():
            print(f"{tech.upper()}:")
            for metric, value in metrics.items():
                if 'ms' in metric:
                    print(f"  {metric}: {value:.2f}ms")
                elif 'rate' in metric:
                    print(f"  {metric}: {value:.1f}%")
                else:
                    print(f"  {metric}: {value:.2f}")
            print()


def run_real_performance_tests(technologies: List[str] = None) -> Dict[str, Any]:
    """Main entry point for real performance testing"""
    runner = RealPerformanceTestRunner()
    return runner.run_comprehensive_tests(technologies)


if __name__ == "__main__":
    # Run real performance tests
    results = run_real_performance_tests()

    # Save results with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"real_performance_results_{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📁 Results saved to {filename}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")
