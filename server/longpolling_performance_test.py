# ServerSide/longpolling_performance_test.py


import time
import requests
import uuid
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from network_condition_simulator import NetworkConditionSimulator, EnhancedPerformanceMetrics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealLongPollingTester:
    """Enhanced Long Polling tester with network simulation and comprehensive metrics"""

    def __init__(self, url: str, test_config: Dict[str, Any]):
        self.url = url
        self.alerts_url = f"{url.rstrip('/')}/alerts/" if not url.endswith('/alerts/') else url
        self.reset_url = f"{url.rstrip('/')}/reset/"
        self.status_url = f"{url.rstrip('/')}/status/"
        self.test_config = test_config
        self.network_simulator = NetworkConditionSimulator()
        self.session = requests.Session()

    def run_test(self) -> Dict[str, Any]:
        """Run comprehensive Long Polling performance test"""
        logger.info(f"Starting enhanced Long Polling test: {self.test_config}")

        # Test all network conditions
        all_results = {}
        network_profiles = ['perfect', 'local_wifi', 'good_mobile', 'poor_mobile', 'satellite']

        for profile in network_profiles:
            logger.info(f"Testing Long Polling under {profile} network conditions...")

            def test_under_conditions():
                return self._run_single_test(profile)

            profile_results = self.network_simulator.apply_network_conditions(profile, test_under_conditions)
            all_results[profile] = profile_results

            # Wait between network condition tests
            time.sleep(2)

        return {
            'technology': 'Long Polling',
            'test_type': 'enhanced_performance',
            'network_condition_results': all_results,
            'summary': self._generate_summary(all_results)
        }

    def _run_single_test(self, network_profile: str) -> Dict[str, Any]:
        """Run single test under specific network conditions"""
        metrics = EnhancedPerformanceMetrics('longpolling')
        metrics.start_test(network_profile)

        try:
            # Test 1: Connection overhead measurement
            self._test_connection_overhead(metrics)

            # Test 2: Immediate response performance
            self._test_immediate_response_performance(metrics)

            # Test 3: Long poll timeout behavior
            self._test_timeout_behavior(metrics)

            # Test 4: Concurrent polling performance
            self._test_concurrent_polling_performance(metrics)

            # Test 5: Scalability under load
            self._test_scalability_performance(metrics)

        except Exception as e:
            logger.error(f"Long Polling test error under {network_profile}: {e}")
            metrics.record_failure()
        finally:
            metrics.end_test()

        return self._get_results(metrics, "Completed")

    def _test_connection_overhead(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test HTTP connection establishment overhead"""
        logger.info("Testing HTTP connection overhead...")

        # Test multiple HTTP requests to measure connection overhead
        for i in range(20):
            try:
                start_time = time.time()
                response = self.session.get(self.status_url, timeout=15)
                connection_time = (time.time() - start_time) * 1000

                metrics.record_connection_time(connection_time)
                metrics.record_data_transfer(
                    bytes_sent=len(str(response.request.body or "").encode()) + 200,  # Estimate headers
                    bytes_received=len(response.content)
                )

                if response.status_code == 200:
                    metrics.record_success()
                else:
                    metrics.record_failure()

                if i % 5 == 0:
                    logger.info(f"HTTP request {i + 1}: {connection_time:.2f}ms, status: {response.status_code}")

            except Exception as e:
                logger.error(f"Connection test {i + 1} failed: {e}")
                metrics.record_failure()

            time.sleep(0.2)

    def _test_immediate_response_performance(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test performance when data is immediately available"""
        logger.info("Testing immediate response performance...")

        # Reset to ensure data is available
        try:
            self.session.post(self.reset_url, timeout=10)
            logger.info("Alert sequence reset for immediate response test")
        except Exception as e:
            logger.warning(f"Could not reset alert sequence: {e}")

        client_id = f"immediate_test_{uuid.uuid4()}"

        # Test immediate responses
        for i in range(30):
            try:
                start_time = time.time()
                response = self.session.get(
                    self.alerts_url,
                    params={'client_id': client_id, 'timeout': 5},
                    timeout=15
                )
                response_time = (time.time() - start_time) * 1000

                metrics.record_message_latency(response_time)
                metrics.record_data_transfer(
                    bytes_sent=150,  # Estimate request size
                    bytes_received=len(response.content)
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get('alert') and data['alert'] is not None:
                        metrics.record_success()
                        immediate = data.get('immediate', False)
                        if i % 5 == 0:
                            logger.info(f"Request {i + 1}: {response_time:.2f}ms (immediate: {immediate})")
                    else:
                        # No data available - expected for later requests
                        metrics.record_failure()
                else:
                    metrics.record_failure()

            except Exception as e:
                logger.error(f"Immediate response test {i + 1} failed: {e}")
                metrics.record_failure()

            time.sleep(0.5)

    def _test_timeout_behavior(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test long poll timeout behavior accuracy"""
        logger.info("Testing timeout behavior...")

        client_id = f"timeout_test_{uuid.uuid4()}"
        timeout_values = [5, 10, 15, 20, 30]  # Different timeout values to test

        for timeout_val in timeout_values:
            try:
                start_time = time.time()
                response = self.session.get(
                    self.alerts_url,
                    params={'client_id': client_id, 'timeout': timeout_val},
                    timeout=timeout_val + 10
                )
                actual_time = (time.time() - start_time) * 1000

                metrics.record_message_latency(actual_time)
                metrics.record_data_transfer(
                    bytes_sent=150,
                    bytes_received=len(response.content)
                )

                if response.status_code == 200:
                    data = response.json()
                    server_wait_time = data.get('wait_time', 0) * 1000
                    timeout_occurred = data.get('timeout', False)

                    if timeout_occurred:
                        timeout_accuracy = abs(actual_time - (timeout_val * 1000))
                        logger.info(f"Timeout test {timeout_val}s: {actual_time:.0f}ms actual, accuracy: ±{timeout_accuracy:.0f}ms")
                        metrics.record_success()
                    else:
                        logger.info(f"Timeout test {timeout_val}s: Received data before timeout")
                        metrics.record_success()
                else:
                    metrics.record_failure()

            except requests.exceptions.Timeout:
                actual_time = (time.time() - start_time) * 1000
                logger.info(f"HTTP timeout occurred for {timeout_val}s test after {actual_time:.0f}ms")
                metrics.record_message_latency(actual_time)
                metrics.record_success()  # HTTP timeout is expected behavior

            except Exception as e:
                logger.error(f"Timeout test {timeout_val}s failed: {e}")
                metrics.record_failure()

    def _test_concurrent_polling_performance(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test concurrent polling performance with statistical analysis"""
        logger.info("Testing concurrent polling performance...")

        concurrent_clients = self.test_config.get('concurrent_clients', 20)
        duration = self.test_config.get('duration', 45)

        # Reset for fresh data
        try:
            self.session.post(self.reset_url, timeout=10)
        except Exception as e:
            logger.warning(f"Could not reset for concurrent test: {e}")

        def polling_worker(client_id: int) -> Dict[str, Any]:
            """Worker for concurrent polling with detailed metrics"""
            session = requests.Session()
            worker_requests = 0
            worker_successes = 0
            worker_latencies = []
            start_time = time.time()

            while (time.time() - start_time) < duration:
                try:
                    request_start = time.time()
                    response = session.get(
                        self.alerts_url,
                        params={'client_id': f'concurrent_{client_id}', 'timeout': 8},
                        timeout=15
                    )
                    response_time = (time.time() - request_start) * 1000

                    worker_requests += 1
                    worker_latencies.append(response_time)

                    if response.status_code == 200:
                        data = response.json()
                        if 'alert' in data:
                            worker_successes += 1

                            if data.get('alert'):
                                alert_title = data['alert'].get('title', 'Unknown')
                                if worker_requests % 10 == 0:
                                    logger.info(f"Client {client_id}: Got '{alert_title}' in {response_time:.2f}ms")

                    # Record metrics for this worker
                    metrics.record_message_latency(response_time)
                    metrics.record_data_transfer(
                        bytes_sent=150,
                        bytes_received=len(response.content)
                    )

                    if response.status_code == 200:
                        metrics.record_success()
                    else:
                        metrics.record_failure()

                    time.sleep(2.0)  # Wait between requests

                except Exception as e:
                    logger.error(f"Client {client_id} error: {e}")
                    metrics.record_failure()
                    worker_requests += 1
                    time.sleep(5.0)  # Longer wait on error

            return {
                'client_id': client_id,
                'requests_made': worker_requests,
                'successful_requests': worker_successes,
                'latencies': worker_latencies,
                'duration': time.time() - start_time
            }

        # Run concurrent clients
        logger.info(f"Starting {concurrent_clients} concurrent polling clients...")

        with ThreadPoolExecutor(max_workers=concurrent_clients) as executor:
            futures = [executor.submit(polling_worker, i) for i in range(concurrent_clients)]
            client_results = []

            for future in as_completed(futures):
                try:
                    result = future.result()
                    client_results.append(result)
                    logger.info(f"Client {result['client_id']} completed: "
                                f"{result['successful_requests']}/{result['requests_made']} successful")
                except Exception as e:
                    logger.error(f"Concurrent client failed: {e}")

        # Calculate concurrent performance metrics
        total_requests = sum(r['requests_made'] for r in client_results)
        total_successful = sum(r['successful_requests'] for r in client_results)

        if total_requests > 0:
            overall_duration = max((r['duration'] for r in client_results), default=duration)
            throughput = total_requests / overall_duration
            success_throughput = total_successful / overall_duration

            metrics.record_throughput_sample(total_requests, overall_duration)

            logger.info(f"Concurrent test results: {total_successful}/{total_requests} successful")
            logger.info(f"Overall throughput: {throughput:.2f} req/s, successful: {success_throughput:.2f} req/s")

    def _test_scalability_performance(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test scalability with increasing load"""
        logger.info("Testing scalability performance...")

        # Test with increasing numbers of concurrent clients
        client_counts = [10, 25, 50, 100, 200]

        for client_count in client_counts:
            # Limit based on test configuration
            actual_client_count = min(client_count, self.test_config.get('max_concurrent_clients', 50))

            logger.info(f"Testing with {actual_client_count} concurrent clients...")

            def scalability_worker(worker_id: int) -> int:
                """Simple worker for scalability testing"""
                session = requests.Session()
                successful_requests = 0

                for _ in range(5):  # Each worker makes 5 requests
                    try:
                        start_time = time.time()
                        response = session.get(
                            self.alerts_url,
                            params={'client_id': f'scale_{worker_id}', 'timeout': 5},
                            timeout=10
                        )
                        response_time = (time.time() - start_time) * 1000

                        metrics.record_message_latency(response_time)
                        metrics.record_data_transfer(
                            bytes_sent=150,
                            bytes_received=len(response.content)
                        )

                        if response.status_code == 200:
                            successful_requests += 1
                            metrics.record_success()
                        else:
                            metrics.record_failure()

                    except Exception as e:
                        logger.error(f"Scalability worker {worker_id} error: {e}")
                        metrics.record_failure()

                    time.sleep(1.0)

                return successful_requests

            # Run scalability test
            start_time = time.time()

            with ThreadPoolExecutor(max_workers=actual_client_count) as executor:
                futures = [executor.submit(scalability_worker, i) for i in range(actual_client_count)]
                results = [future.result() for future in as_completed(futures)]

            test_duration = time.time() - start_time
            total_successful = sum(results)
            total_requests = actual_client_count * 5

            throughput = total_requests / test_duration
            success_rate = (total_successful / total_requests) * 100

            metrics.record_throughput_sample(total_requests, test_duration)

            logger.info(f"Scalability test {actual_client_count} clients: "
                        f"{success_rate:.1f}% success rate, {throughput:.2f} req/s")

            # Wait between scalability tests
            time.sleep(3)

    def _get_results(self, metrics: EnhancedPerformanceMetrics, status: str) -> Dict[str, Any]:
        """Get comprehensive test results"""
        return {
            'technology': 'Long Polling',
            'status': status,
            'metrics': metrics.calculate_comprehensive_metrics(),
            'config': self.test_config,
            'network_profile': metrics.network_profile
        }

    def _generate_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary across all network conditions"""
        summary = {
            'best_performance_profile': None,
            'worst_performance_profile': None,
            'average_metrics': {},
            'network_impact_analysis': {}
        }

        # Find best and worst performing profiles
        latencies = {}
        success_rates = {}

        for profile, result in all_results.items():
            if result['status'] == 'Completed':
                metrics = result['metrics']
                latencies[profile] = metrics.get('message_latency_ms', float('inf'))
                success_rates[profile] = metrics.get('success_rate_percent', 0)

        if latencies:
            summary['best_performance_profile'] = min(latencies, key=latencies.get)
            summary['worst_performance_profile'] = max(latencies, key=latencies.get)

            # Calculate network impact
            perfect_latency = latencies.get('perfect', 0)
            for profile, latency in latencies.items():
                if profile != 'perfect' and perfect_latency > 0:
                    impact = ((latency - perfect_latency) / perfect_latency) * 100
                    summary['network_impact_analysis'][profile] = {
                        'latency_increase_percent': impact,
                        'success_rate_impact': success_rates.get(profile, 0) - success_rates.get('perfect', 0)
                    }

        return summary


def test_longpolling_performance() -> Dict[str, Any]:
    """Run enhanced Long Polling performance test and return results"""
    test_config = {
        'duration': 60,
        'concurrent_clients': 25,
        'max_concurrent_clients': 100,
        'test_description': 'Enhanced Long Polling performance test with network simulation'
    }

    tester = RealLongPollingTester('http://localhost:8001/api/poll/', test_config)
    return tester.run_test()


if __name__ == "__main__":
    results = test_longpolling_performance()

    print(f"\n=== Enhanced Long Polling Performance Test Results ===")

    # Print results for each network profile
    for profile, result in results.get('network_condition_results', {}).items():
        if result['status'] == 'Completed':
            metrics = result['metrics']
            print(f"\n{profile.upper()} Network Conditions:")
            print(f"  Average Response Time: {metrics.get('message_latency_ms', 0):.1f}ms ±{metrics.get('latency_std_dev', 0):.1f}ms")
            print(f"  Connection Time: {metrics.get('connection_time_ms', 0):.1f}ms")
            print(f"  Success Rate: {metrics.get('success_rate_percent', 0):.1f}%")
            print(f"  Throughput: {metrics.get('throughput_msg_per_sec', 0):.1f} req/s")
            print(f"  95th Percentile: {metrics.get('latency_p95', 0):.1f}ms")
            print(f"  CPU Usage: {metrics.get('cpu_usage_percent', 0):.1f}%")
            print(f"  Memory Usage: {metrics.get('memory_usage_mb', 0):.1f}MB")

    # Print summary
    summary = results.get('summary', {})
    if summary:
        print(f"\nSummary:")
        print(f"  Best Performance: {summary.get('best_performance_profile', 'N/A')}")
        print(f"  Worst Performance: {summary.get('worst_performance_profile', 'N/A')}")
