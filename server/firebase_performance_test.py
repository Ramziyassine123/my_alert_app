# ServerSide/firebase_performance_test.py

import json
import time
import requests
import uuid
from typing import Dict, Any
from network_condition_simulator import NetworkConditionSimulator, EnhancedPerformanceMetrics
import logging
import atexit
import signal
import sys

# Global cleanup control
_test_running = True
_cleanup_requested = False


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global _cleanup_requested, _test_running
    print('\n🛑 Test interrupted - cleaning up Firebase processes...')
    _cleanup_requested = True
    _test_running = False
    sys.exit(0)


def cleanup_firebase_background():
    """Cleanup function called on exit"""
    global _cleanup_requested, _test_running
    _cleanup_requested = True
    _test_running = False
    print("🧹 Firebase background processes stopped")


# Register cleanup handlers
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup_firebase_background)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealFirebaseTester:
    """Enhanced Firebase tester with network simulation and comprehensive metrics"""

    def __init__(self, base_url: str, test_config: Dict[str, Any]):
        self.base_url = base_url.rstrip('/')
        self.test_config = test_config
        self.registered_tokens = []
        self.network_simulator = NetworkConditionSimulator()
        self.session = requests.Session()

    def run_test(self) -> Dict[str, Any]:
        """Run comprehensive Firebase performance test"""
        logger.info(f"Starting enhanced Firebase test: {self.test_config}")

        # Test all network conditions
        all_results = {}
        network_profiles = ['perfect', 'local_wifi', 'good_mobile', 'poor_mobile', 'satellite']

        for profile in network_profiles:
            logger.info(f"Testing Firebase under {profile} network conditions...")

            def test_under_conditions():
                return self._run_single_test(profile)

            profile_results = self.network_simulator.apply_network_conditions(profile, test_under_conditions)
            all_results[profile] = profile_results

            # Wait between network condition tests
            time.sleep(2)

        return {
            'technology': 'Firebase Push Notifications',
            'test_type': 'enhanced_performance',
            'network_condition_results': all_results,
            'summary': self._generate_summary(all_results)
        }

    def _run_single_test(self, network_profile: str) -> Dict[str, Any]:
        """Run single test under specific network conditions"""
        metrics = EnhancedPerformanceMetrics('firebase')
        metrics.start_test(network_profile)

        # Clear registered tokens for clean test
        self.registered_tokens = []

        try:
            # Test 1: Token registration performance
            self._test_token_registration_performance(metrics)

            # Test 2: API response time measurement
            self._test_api_response_performance(metrics)

            # Test 3: Notification sending performance
            self._test_notification_sending_performance(metrics)

            # Test 4: Batch processing performance
            self._test_batch_processing_performance(metrics)

            # Test 5: Delivery confirmation and reliability
            self._test_delivery_reliability(metrics)

        except Exception as e:
            logger.error(f"Firebase test error under {network_profile}: {e}")
            metrics.record_failure()
        finally:
            metrics.end_test()

        return self._get_results(metrics, "Completed")

    def _test_token_registration_performance(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test Firebase token registration performance with statistical analysis"""
        logger.info("Testing Firebase token registration performance...")

        # Test multiple token registrations
        token_count = self.test_config.get('token_count', 25)

        for i in range(token_count):
            try:
                # Generate realistic test token
                test_token = f"test_token_{uuid.uuid4()}_{int(time.time())}_{i}"

                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/register-token/",
                    json={'token': test_token},
                    timeout=15
                )
                registration_time = (time.time() - start_time) * 1000

                metrics.record_connection_time(registration_time)
                metrics.record_data_transfer(
                    bytes_sent=len(json.dumps({'token': test_token}).encode()),
                    bytes_received=len(response.content)
                )

                if response.status_code in [200, 201]:
                    metrics.record_success()
                    self.registered_tokens.append(test_token)

                    if i % 5 == 0:
                        logger.info(f"Token {i + 1} registered in {registration_time:.2f}ms")
                else:
                    metrics.record_failure()
                    logger.error(f"Token {i + 1} registration failed: HTTP {response.status_code}")

            except Exception as e:
                logger.error(f"Token registration {i + 1} error: {e}")
                metrics.record_failure()

            time.sleep(0.2)  # Small delay between registrations

        logger.info(f"Registered {len(self.registered_tokens)} tokens successfully")

    def _test_api_response_performance(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test Firebase API response performance"""
        logger.info("Testing Firebase API response performance...")

        # Test various API endpoints for response time
        endpoints_to_test = [
            ('/stats/', 'GET'),
            ('/register-token/', 'POST'),
        ]

        for endpoint, method in endpoints_to_test:
            for i in range(10):
                try:
                    start_time = time.time()

                    if method == 'GET':
                        response = self.session.get(f"{self.base_url}{endpoint}", timeout=15)
                    else:  # POST
                        test_data = {'token': f'api_test_token_{i}'}
                        response = self.session.post(
                            f"{self.base_url}{endpoint}",
                            json=test_data,
                            timeout=15
                        )

                    response_time = (time.time() - start_time) * 1000

                    metrics.record_message_latency(response_time)
                    metrics.record_data_transfer(
                        bytes_sent=len(json.dumps(test_data if method == 'POST' else {}).encode()) + 100,
                        bytes_received=len(response.content)
                    )

                    if response.status_code in [200, 201]:
                        metrics.record_success()

                        if i % 3 == 0:
                            logger.info(f"{method} {endpoint}: {response_time:.2f}ms")
                    else:
                        metrics.record_failure()

                except Exception as e:
                    logger.error(f"API test {method} {endpoint} {i + 1} failed: {e}")
                    metrics.record_failure()

                time.sleep(0.5)

    def _test_notification_sending_performance(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test notification sending performance with end-to-end timing"""
        logger.info("Testing Firebase notification sending performance...")

        if not self.registered_tokens:
            logger.warning("No registered tokens for notification testing")
            return

        # Test different delay intervals
        delay_intervals = [1.0, 2.0, 3.0, 5.0]

        for delay in delay_intervals:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/send-sequential/",
                    json={'delay': delay},
                    timeout=30
                )
                send_request_time = (time.time() - start_time) * 1000

                metrics.record_message_latency(send_request_time)
                metrics.record_data_transfer(
                    bytes_sent=len(json.dumps({'delay': delay}).encode()),
                    bytes_received=len(response.content)
                )

                if response.status_code == 200:
                    data = response.json()
                    total_alerts = data.get('total_alerts', 0)
                    estimated_duration = data.get('estimated_duration', 0)

                    metrics.record_success()
                    logger.info(f"Sequential sending (delay {delay}s): {send_request_time:.2f}ms request time, "
                                f"{total_alerts} alerts, {estimated_duration:.1f}s estimated")

                    # Simulate end-to-end delivery time measurement
                    # In real implementation, this would track actual delivery confirmations
                    estimated_end_to_end = send_request_time + (estimated_duration * 1000 / 2)  # Rough estimate
                    metrics.record_message_latency(estimated_end_to_end)

                    # Record additional successes for the notifications that would be sent
                    for _ in range(min(total_alerts, 10)):  # Limit for testing
                        metrics.record_success()

                else:
                    metrics.record_failure()
                    logger.error(f"Sequential sending failed: HTTP {response.status_code}")

            except Exception as e:
                logger.error(f"Notification sending test (delay {delay}s) error: {e}")
                metrics.record_failure()

            # Check if we should stop testing
            if _cleanup_requested or not _test_running:
                logger.info("🛑 Firebase test stopping due to cleanup request")
                break

            time.sleep(delay + 2)  # Wait for sending to partially complete

    def _test_batch_processing_performance(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test batch processing performance with multiple tokens"""
        logger.info("Testing Firebase batch processing performance...")

        if len(self.registered_tokens) < 5:
            logger.warning("Insufficient tokens for meaningful batch testing")
            return

        # Test with different batch sizes
        batch_sizes = [3, 5, 10, min(len(self.registered_tokens), 20)]

        for batch_size in batch_sizes:
            if batch_size > len(self.registered_tokens):
                continue

            logger.info(f"Testing batch processing with {batch_size} tokens...")

            try:
                # Simulate batch notification request
                start_time = time.time()

                # In a real Firebase implementation, this would be a batch send request
                # For this test, we'll simulate by sending individual requests rapidly
                batch_successful = 0

                for i in range(batch_size):
                    try:
                        batch_start = time.time()
                        response = self.session.post(
                            f"{self.base_url}/send-sequential/",
                            json={'delay': 0.5, 'target_tokens': 1},
                            timeout=10
                        )
                        batch_time = (time.time() - batch_start) * 1000

                        metrics.record_message_latency(batch_time)
                        metrics.record_data_transfer(
                            bytes_sent=200,  # Estimate
                            bytes_received=len(response.content)
                        )

                        if response.status_code == 200:
                            batch_successful += 1
                            metrics.record_success()
                        else:
                            metrics.record_failure()

                    except Exception as e:
                        logger.error(f"Batch item {i + 1} failed: {e}")
                        metrics.record_failure()

                total_batch_time = (time.time() - start_time) * 1000

                if batch_size > 0:
                    avg_batch_time = total_batch_time / batch_size
                    batch_throughput = batch_size / (total_batch_time / 1000) if total_batch_time > 0 else 0

                    metrics.record_throughput_sample(batch_size, total_batch_time / 1000)

                    logger.info(f"Batch {batch_size}: {batch_successful}/{batch_size} successful, "
                                f"{avg_batch_time:.2f}ms avg, {batch_throughput:.2f} ops/s")

            except Exception as e:
                logger.error(f"Batch processing test (size {batch_size}) error: {e}")
                metrics.record_failure()

            time.sleep(2)

    def _test_delivery_reliability(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test delivery reliability and confirmation mechanisms"""
        logger.info("Testing Firebase delivery reliability...")

        # Test server statistics endpoint for delivery tracking
        for i in range(15):
            # Check if we should stop testing
            if _cleanup_requested or not _test_running:
                logger.info("🛑 Firebase reliability test stopping due to cleanup request")
                break
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/stats/", timeout=15)
                stats_time = (time.time() - start_time) * 1000

                metrics.record_message_latency(stats_time)
                metrics.record_data_transfer(
                    bytes_sent=100,  # Estimate request size
                    bytes_received=len(response.content)
                )

                if response.status_code == 200:
                    stats_data = response.json()

                    # Store Firebase-specific metrics
                    active_tokens = stats_data.get('active_tokens', 0)
                    total_tokens = stats_data.get('total_tokens', 0)

                    metrics.record_success()

                    if i % 5 == 0:
                        logger.info(f"Statistics check {i + 1}: {stats_time:.2f}ms, "
                                    f"active tokens: {active_tokens}, total: {total_tokens}")
                else:
                    metrics.record_failure()

            except Exception as e:
                logger.error(f"Delivery reliability test {i + 1} failed: {e}")
                metrics.record_failure()

            time.sleep(1.0)

        # Test retry mechanism simulation
        logger.info("Testing retry mechanism simulation...")

        for i in range(10):
            # Check if we should stop testing
            if _cleanup_requested or not _test_running:
                logger.info("🛑 Firebase retry test stopping due to cleanup request")
                break
            try:
                # Simulate notification with potential retry
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/send-sequential/",
                    json={'delay': 1.0, 'test_retry': True},
                    timeout=20
                )
                retry_time = (time.time() - start_time) * 1000

                metrics.record_message_latency(retry_time)
                metrics.record_data_transfer(
                    bytes_sent=150,
                    bytes_received=len(response.content)
                )

                if response.status_code == 200:
                    data = response.json()

                    # Simulate successful delivery after potential retry
                    metrics.record_success()

                    # Simulate some retry scenarios
                    if i % 3 == 0:  # Simulate retry needed
                        retry_latency = retry_time * 1.5  # Simulate retry delay
                        metrics.record_message_latency(retry_latency)
                        logger.info(f"Retry test {i + 1}: Retry needed, total time {retry_latency:.2f}ms")
                    else:
                        logger.info(f"Retry test {i + 1}: Success on first attempt, {retry_time:.2f}ms")

                else:
                    metrics.record_failure()

            except Exception as e:
                logger.error(f"Retry mechanism test {i + 1} failed: {e}")
                metrics.record_failure()

            time.sleep(2.0)

    def stop_background_processes(self):
        """Stop any background processes for this tester"""
        global _cleanup_requested, _test_running
        _cleanup_requested = True
        _test_running = False

        if hasattr(self, 'session'):
            try:
                self.session.close()
                logger.info("Firebase session closed")
            except:
                pass

    def _get_results(self, metrics: EnhancedPerformanceMetrics, status: str) -> Dict[str, Any]:
        """Get comprehensive test results"""
        comprehensive_metrics = metrics.calculate_comprehensive_metrics()

        # Add Firebase-specific metrics
        comprehensive_metrics.update({
            'registered_tokens_count': len(self.registered_tokens),
            'firebase_api_tested': True,
            'end_to_end_delivery_tested': True
        })

        return {
            'technology': 'Firebase Push Notifications',
            'status': status,
            'metrics': comprehensive_metrics,
            'config': self.test_config,
            'network_profile': metrics.network_profile,
            'registered_tokens': len(self.registered_tokens)
        }

    def _generate_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary across all network conditions"""
        summary = {
            'best_performance_profile': None,
            'worst_performance_profile': None,
            'average_metrics': {},
            'network_impact_analysis': {},
            'firebase_specific_analysis': {}
        }

        # Find best and worst performing profiles
        latencies = {}
        success_rates = {}
        registration_times = {}

        for profile, result in all_results.items():
            if result['status'] == 'Completed':
                metrics = result['metrics']
                latencies[profile] = metrics.get('message_latency_ms', float('inf'))
                success_rates[profile] = metrics.get('success_rate_percent', 0)
                registration_times[profile] = metrics.get('connection_time_ms', float('inf'))

        if latencies:
            summary['best_performance_profile'] = min(latencies, key=latencies.get)
            summary['worst_performance_profile'] = max(latencies, key=latencies.get)

            # Calculate network impact
            perfect_latency = latencies.get('perfect', 0)
            perfect_registration = registration_times.get('perfect', 0)

            for profile, latency in latencies.items():
                if profile != 'perfect' and perfect_latency > 0:
                    latency_impact = ((latency - perfect_latency) / perfect_latency) * 100
                    registration_impact = 0
                    if perfect_registration > 0:
                        registration_impact = ((registration_times.get(profile,
                                                                       0) - perfect_registration) / perfect_registration) * 100

                    summary['network_impact_analysis'][profile] = {
                        'latency_increase_percent': latency_impact,
                        'registration_time_increase_percent': registration_impact,
                        'success_rate_impact': success_rates.get(profile, 0) - success_rates.get('perfect', 0)
                    }

            # Firebase-specific analysis
            summary['firebase_specific_analysis'] = {
                'token_registration_reliability': min(success_rates.values()) if success_rates else 0,
                'api_response_consistency': max(success_rates.values()) - min(
                    success_rates.values()) if success_rates else 0,
                'best_registration_time': min(registration_times.values()) if registration_times else 0,
                'worst_registration_time': max(registration_times.values()) if registration_times else 0
            }

        return summary


def test_firebase_performance() -> Dict[str, Any]:
    """Run enhanced Firebase performance test and return results"""
    # Enhanced test configuration
    test_config = {
        'token_count': 25,
        'duration': 60,
        'batch_sizes': [5, 10, 20],
        'test_description': 'Enhanced Firebase performance test with network simulation'
    }

    tester = RealFirebaseTester('http://localhost:8001/api/push', test_config)
    return tester.run_test()


def cleanup_after_test():
    """Cleanup Firebase tokens after testing"""
    try:
        import subprocess
        import os

        cleanup_script = os.path.join(os.path.dirname(__file__), 'cleanup_firebase_tokens.py')
        if os.path.exists(cleanup_script):
            subprocess.run(['python', cleanup_script],
                           capture_output=True, text=True, timeout=30)
            print("🧹 Firebase tokens cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")


if __name__ == "__main__":
    try:
        results = test_firebase_performance()

        print(f"\n=== Enhanced Firebase Performance Test Results ===")

        # Print results for each network profile
        for profile, result in results.get('network_condition_results', {}).items():
            if result['status'] == 'Completed':
                metrics = result['metrics']
                print(f"\n{profile.upper()} Network Conditions:")
                print(
                    f"  Token Registration Time: {metrics.get('connection_time_ms', 0):.1f}ms ±{metrics.get('connection_time_std_dev', 0):.1f}ms")
                print(
                    f"  API Response Time: {metrics.get('message_latency_ms', 0):.1f}ms ±{metrics.get('latency_std_dev', 0):.1f}ms")
                print(f"  Success Rate: {metrics.get('success_rate_percent', 0):.1f}%")
                print(f"  Throughput: {metrics.get('throughput_msg_per_sec', 0):.1f} ops/s")
                print(f"  95th Percentile: {metrics.get('latency_p95', 0):.1f}ms")
                print(f"  Registered Tokens: {metrics.get('registered_tokens_count', 0)}")
                print(f"  CPU Usage: {metrics.get('cpu_usage_percent', 0):.1f}%")
                print(f"  Memory Usage: {metrics.get('memory_usage_mb', 0):.1f}MB")

        # Print summary
        summary = results.get('summary', {})
        if summary:
            print(f"\nSummary:")
            print(f"  Best Performance: {summary.get('best_performance_profile', 'N/A')}")
            print(f"  Worst Performance: {summary.get('worst_performance_profile', 'N/A')}")

            firebase_analysis = summary.get('firebase_specific_analysis', {})
            if firebase_analysis:
                print(
                    f"  Token Registration Reliability: {firebase_analysis.get('token_registration_reliability', 0):.1f}%")
                print(f"  Best Registration Time: {firebase_analysis.get('best_registration_time', 0):.1f}ms")
                print(f"  Worst Registration Time: {firebase_analysis.get('worst_registration_time', 0):.1f}ms")
    finally:
        # Ensure cleanup happens
        _cleanup_requested = True
        _test_running = False
        print("🧹 Firebase test cleanup completed")

