"""
Comprehensive Performance Testing Suite for Alert Technologies
Tests WebSocket, HTTP Long Polling, and Firebase Push Notifications
"""

import json
import time
import threading
import requests
import websocket
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import statistics
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Class to track and calculate performance metrics"""

    def __init__(self):
        self.latencies = []
        self.success_count = 0
        self.failure_count = 0
        self.start_time = None
        self.end_time = None
        self.connection_times = []
        self.reconnection_count = 0
        self.data_transferred = 0
        self.memory_usage = []
        self.cpu_usage = []

    def add_latency(self, latency_ms: float):
        """Add a latency measurement"""
        self.latencies.append(latency_ms)

    def record_success(self):
        """Record a successful operation"""
        self.success_count += 1

    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1

    def add_connection_time(self, time_ms: float):
        """Add connection establishment time"""
        self.connection_times.append(time_ms)

    def calculate_stats(self) -> Dict[str, Any]:
        """Calculate comprehensive statistics"""
        total_messages = self.success_count + self.failure_count
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0

        stats = {
            'total_messages': total_messages,
            'successful_messages': self.success_count,
            'failed_messages': self.failure_count,
            'success_rate': (self.success_count / total_messages * 100) if total_messages > 0 else 0,
            'duration_seconds': duration,
            'messages_per_second': total_messages / duration if duration > 0 else 0,
            'reconnections': self.reconnection_count,
            'data_transferred_bytes': self.data_transferred,
        }

        if self.latencies:
            stats.update({
                'latency_avg_ms': statistics.mean(self.latencies),
                'latency_min_ms': min(self.latencies),
                'latency_max_ms': max(self.latencies),
                'latency_median_ms': statistics.median(self.latencies),
                'latency_95th_percentile_ms': self._percentile(self.latencies, 95),
                'latency_99th_percentile_ms': self._percentile(self.latencies, 99),
                'latency_std_dev': statistics.stdev(self.latencies) if len(self.latencies) > 1 else 0,
            })

        if self.connection_times:
            stats.update({
                'connection_time_avg_ms': statistics.mean(self.connection_times),
                'connection_time_max_ms': max(self.connection_times),
                'connection_time_min_ms': min(self.connection_times),
            })

        return stats

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))


class WebSocketTester:
    """WebSocket performance tester"""

    def __init__(self, url: str, test_config: Dict[str, Any]):
        self.url = url
        self.test_config = test_config
        self.metrics = PerformanceMetrics()
        self.ws = None
        self.messages_received = 0
        self.message_times = {}

    def run_test(self) -> Dict[str, Any]:
        """Run WebSocket performance test"""
        logger.info(f"Starting WebSocket test with {self.test_config['concurrent_clients']} clients")
        self.metrics.start_time = datetime.now()

        # Test connection establishment
        connection_start = time.time()
        try:
            self.ws = websocket.create_connection(self.url)
            connection_time = (time.time() - connection_start) * 1000
            self.metrics.add_connection_time(connection_time)
            logger.info(f"WebSocket connected in {connection_time:.2f}ms")
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            self.metrics.record_failure()
            return self._get_results("Connection failed")

        # Set up message handling
        self.ws.settimeout(1.0)

        # Start receiving messages in a separate thread
        receive_thread = threading.Thread(target=self._receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Request alerts from server
        try:
            start_message = json.dumps({
                'type': 'start_alerts',
                'test_id': str(uuid.uuid4()),
                'timestamp': time.time()
            })
            self.ws.send(start_message)
            self.metrics.data_transferred += len(start_message.encode())
        except Exception as e:
            logger.error(f"Failed to send start message: {e}")
            self.metrics.record_failure()

        # Run test for specified duration
        test_duration = self.test_config.get('duration', 60)
        time.sleep(test_duration)

        # Stop alerts
        try:
            stop_message = json.dumps({
                'type': 'stop_alerts',
                'timestamp': time.time()
            })
            self.ws.send(stop_message)
            self.metrics.data_transferred += len(stop_message.encode())
        except Exception as e:
            logger.error(f"Failed to send stop message: {e}")

        self.metrics.end_time = datetime.now()

        # Close connection
        if self.ws:
            self.ws.close()

        return self._get_results("Completed")

    def _receive_messages(self):
        """Receive and process WebSocket messages"""
        while True:
            try:
                message = self.ws.recv()
                receive_time = time.time() * 1000
                self.metrics.data_transferred += len(message.encode())

                try:
                    data = json.loads(message)
                    if data.get('type') == 'alert':
                        self.messages_received += 1
                        self.metrics.record_success()

                        # Calculate latency if timestamp is available
                        latency = (receive_time - self.metrics.start_time.timestamp()) * 1000
                        if latency > 0:  # Only add positive latencies
                            self.metrics.add_latency(latency)

                except json.JSONDecodeError:
                    logger.warning("Received non-JSON message")

            except websocket.WebSocketTimeoutException:
                continue
            except Exception as e:
                logger.error(f"WebSocket receive error: {e}")
                self.metrics.record_failure()
                break

    def _get_results(self, status: str) -> Dict[str, Any]:
        """Get test results"""
        stats = self.metrics.calculate_stats()
        return {
            'technology': 'WebSocket',
            'status': status,
            'messages_received': self.messages_received,
            'metrics': stats,
            'config': self.test_config
        }


class LongPollingTester:
    """HTTP Long Polling performance tester"""

    def __init__(self, url: str, test_config: Dict[str, Any]):
        self.url = url
        self.test_config = test_config
        self.metrics = PerformanceMetrics()
        self.running = False

    def run_test(self) -> Dict[str, Any]:
        """Run Long Polling performance test"""
        logger.info(f"Starting Long Polling test with {self.test_config['concurrent_clients']} clients")
        self.metrics.start_time = datetime.now()
        self.running = True

        # Run concurrent polling clients
        with ThreadPoolExecutor(max_workers=self.test_config['concurrent_clients']) as executor:
            futures = []
            for i in range(self.test_config['concurrent_clients']):
                future = executor.submit(self._polling_client, i)
                futures.append(future)

            # Wait for specified duration
            time.sleep(self.test_config.get('duration', 60))
            self.running = False

            # Wait for all clients to finish
            for future in as_completed(futures, timeout=10):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Polling client error: {e}")
                    self.metrics.record_failure()

        self.metrics.end_time = datetime.now()
        return self._get_results("Completed")

    def _polling_client(self, client_id: int):
        """Individual polling client"""
        session = requests.Session()
        session.timeout = (5, 30)  # Connection timeout, read timeout

        while self.running:
            try:
                start_time = time.time()
                response = session.get(self.url)
                end_time = time.time()

                latency = (end_time - start_time) * 1000
                self.metrics.add_latency(latency)
                self.metrics.data_transferred += len(response.content)

                if response.status_code == 200:
                    self.metrics.record_success()
                    try:
                        data = response.json()
                        if 'alert' in data:
                            logger.debug(f"Client {client_id} received alert: {data['alert'].get('title', 'Unknown')}")
                    except json.JSONDecodeError:
                        logger.warning(f"Client {client_id} received non-JSON response")
                else:
                    self.metrics.record_failure()
                    logger.warning(f"Client {client_id} received status {response.status_code}")

            except requests.exceptions.Timeout:
                logger.warning(f"Client {client_id} request timeout")
                self.metrics.record_failure()
            except requests.exceptions.ConnectionError:
                logger.error(f"Client {client_id} connection error")
                self.metrics.record_failure()
                self.metrics.reconnection_count += 1
                time.sleep(1)  # Wait before retry
            except Exception as e:
                logger.error(f"Client {client_id} unexpected error: {e}")
                self.metrics.record_failure()
                break

    def _get_results(self, status: str) -> Dict[str, Any]:
        """Get test results"""
        stats = self.metrics.calculate_stats()
        return {
            'technology': 'Long Polling',
            'status': status,
            'metrics': stats,
            'config': self.test_config
        }


class PushNotificationTester:
    """Firebase Push Notification performance tester"""

    def __init__(self, base_url: str, test_config: Dict[str, Any]):
        self.base_url = base_url
        self.test_config = test_config
        self.metrics = PerformanceMetrics()

    def run_test(self) -> Dict[str, Any]:
        """Run Push Notification performance test"""
        logger.info("Starting Push Notification test")
        self.metrics.start_time = datetime.now()

        # Test token registration
        registration_success = self._test_token_registration()
        if not registration_success:
            return self._get_results("Token registration failed")

        # Test sequential alert sending
        send_success = self._test_sequential_alerts()
        if not send_success:
            return self._get_results("Alert sending failed")

        # Test statistics endpoint
        self._test_statistics_endpoint()

        self.metrics.end_time = datetime.now()
        return self._get_results("Completed")

    def _test_token_registration(self) -> bool:
        """Test FCM token registration"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/stats/", timeout=10)
            end_time = time.time()

            latency = (end_time - start_time) * 1000
            self.metrics.add_latency(latency)

            if response.status_code == 200:
                self.metrics.record_success()
                return True
            else:
                self.metrics.record_failure()
                return False

        except Exception as e:
            self.metrics.record_failure()
            return False

    def _test_sequential_alerts(self) -> bool:
        """Test sequential alert sending"""
        try:
            delay = self.test_config.get('message_interval', 3)

            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/send-sequential/",
                json={'delay': delay},
                timeout=10
            )
            end_time = time.time()

            latency = (end_time - start_time) * 1000
            self.metrics.add_latency(latency)
            self.metrics.data_transferred += len(response.content)

            if response.status_code == 200:
                self.metrics.record_success()
                data = response.json()
                total_alerts = data.get('total_alerts', 0)
                logger.info(f"Sequential alerts started: {total_alerts} alerts")

                # Wait for alerts to be sent
                estimated_time = total_alerts * delay
                time.sleep(min(estimated_time, self.test_config.get('duration', 60)))

                return True
            else:
                self.metrics.record_failure()
                logger.error(f"Sequential alerts failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Sequential alerts error: {e}")
            self.metrics.record_failure()
            return False

    def _test_statistics_endpoint(self):
        """Test statistics endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/stats/", timeout=10)
            end_time = time.time()

            latency = (end_time - start_time) * 1000
            self.metrics.add_latency(latency)
            self.metrics.data_transferred += len(response.content)

            if response.status_code == 200:
                self.metrics.record_success()
                stats = response.json()
                logger.info(f"Statistics retrieved: {stats}")
            else:
                self.metrics.record_failure()
                logger.error(f"Statistics retrieval failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Statistics endpoint error: {e}")
            self.metrics.record_failure()

    def _get_results(self, status: str) -> Dict[str, Any]:
        """Get test results"""
        stats = self.metrics.calculate_stats()
        return {
            'technology': 'Push Notifications',
            'status': status,
            'metrics': stats,
            'config': self.test_config
        }


class PerformanceTestRunner:
    """Main performance test runner"""

    # Class variable to store test results
    _test_results = {}

    def __init__(self, test_config: Dict[str, Any]):
        self.test_config = test_config
        self.test_id = str(uuid.uuid4())
        self.results = {}

        # Server URLs
        self.websocket_url = 'ws://localhost:8001/ws/alerts/'
        self.longpolling_url = 'http://localhost:8001/api/poll/alerts/'
        self.push_url = 'http://localhost:8001/api/push'

    def run_tests(self):
        """Run performance tests for all selected technologies"""
        logger.info(f"Starting performance test suite - ID: {self.test_id}")
        start_time = datetime.now()

        technologies = self.test_config.get('technologies', ['websocket', 'longpolling', 'push'])

        for tech in technologies:
            logger.info(f"Testing {tech}...")

            try:
                if tech == 'websocket':
                    tester = WebSocketTester(self.websocket_url, self.test_config)
                    result = tester.run_test()
                elif tech == 'longpolling':
                    tester = LongPollingTester(self.longpolling_url, self.test_config)
                    result = tester.run_test()
                elif tech == 'push':
                    tester = PushNotificationTester(self.push_url, self.test_config)
                    result = tester.run_test()
                else:
                    logger.warning(f"Unknown technology: {tech}")
                    continue

                self.results[tech] = result
                logger.info(f"{tech} test completed: {result['status']}")

            except Exception as e:
                logger.error(f"Error testing {tech}: {e}")
                self.results[tech] = {
                    'technology': tech,
                    'status': f'Error: {str(e)}',
                    'metrics': {},
                    'config': self.test_config
                }

        end_time = datetime.now()

        # Compile final results
        final_results = {
            'test_id': self.test_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': (end_time - start_time).total_seconds(),
            'config': self.test_config,
            'results': self.results,
            'summary': self._generate_summary()
        }

        # Store results
        self._test_results[self.test_id] = final_results
        logger.info(f"Performance test suite completed - ID: {self.test_id}")

        return final_results

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary and comparisons"""
        summary = {
            'total_technologies_tested': len(self.results),
            'successful_tests': len([r for r in self.results.values() if r['status'] == 'Completed']),
            'comparisons': {}
        }

        # Compare latencies
        latencies = {}
        success_rates = {}
        throughput = {}

        for tech, result in self.results.items():
            metrics = result.get('metrics', {})
            latencies[tech] = metrics.get('latency_avg_ms', 0)
            success_rates[tech] = metrics.get('success_rate', 0)
            throughput[tech] = metrics.get('messages_per_second', 0)

        if latencies:
            summary['comparisons']['latency'] = {
                'lowest': min(latencies, key=latencies.get),
                'highest': max(latencies, key=latencies.get),
                'values': latencies
            }

        if success_rates:
            summary['comparisons']['reliability'] = {
                'most_reliable': max(success_rates, key=success_rates.get),
                'least_reliable': min(success_rates, key=success_rates.get),
                'values': success_rates
            }

        if throughput:
            summary['comparisons']['throughput'] = {
                'highest': max(throughput, key=throughput.get),
                'lowest': min(throughput, key=throughput.get),
                'values': throughput
            }

        return summary

    @classmethod
    def get_test_results(cls, test_id: str) -> Dict[str, Any]:
        """Get results for a specific test"""
        return cls._test_results.get(test_id, {'error': 'Test not found'})

    @classmethod
    def get_latest_results(cls) -> Dict[str, Any]:
        """Get the latest test results"""
        if not cls._test_results:
            return {'error': 'No tests have been run'}

        latest_test_id = max(cls._test_results.keys(),
                             key=lambda k: cls._test_results[k]['start_time'])
        return cls._test_results[latest_test_id]

    @classmethod
    def get_all_test_ids(cls) -> List[str]:
        """Get all test IDs"""
        return list(cls._test_results.keys())
