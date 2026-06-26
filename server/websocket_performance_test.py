# ServerSide/websocket_performance_test.py

import json
import time
import websocket
import uuid
from typing import Dict, Any
from network_condition_simulator import NetworkConditionSimulator, EnhancedPerformanceMetrics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealWebSocketTester:
    """Enhanced WebSocket tester with network simulation and comprehensive metrics"""

    def __init__(self, url: str, test_config: Dict[str, Any]):
        self.url = url
        self.test_config = test_config
        self.ws = None
        self.running = False
        self.ping_responses = {}
        self.network_simulator = NetworkConditionSimulator()

    def run_test(self) -> Dict[str, Any]:
        """Run comprehensive WebSocket performance test"""
        logger.info(f"Starting enhanced WebSocket test: {self.test_config}")

        # Test all network conditions
        all_results = {}
        network_profiles = ['perfect', 'local_wifi', 'good_mobile', 'poor_mobile', 'satellite']

        for profile in network_profiles:
            logger.info(f"Testing WebSocket under {profile} network conditions...")

            def test_under_conditions():
                return self._run_single_test(profile)

            profile_results = self.network_simulator.apply_network_conditions(profile, test_under_conditions)
            all_results[profile] = profile_results

            # Wait between network condition tests
            time.sleep(2)

        return {
            'technology': 'WebSocket',
            'test_type': 'enhanced_performance',
            'network_condition_results': all_results,
            'summary': self._generate_summary(all_results)
        }

    def _run_single_test(self, network_profile: str) -> Dict[str, Any]:
        """Run single test under specific network conditions"""
        metrics = EnhancedPerformanceMetrics('websocket')
        metrics.start_test(network_profile)

        self.running = True

        try:
            # Test 1: Connection performance (multiple connections)
            connection_success = self._test_connection_performance(metrics)
            if not connection_success:
                return self._get_results(metrics, "Connection failed")

            # Test 2: Message latency with statistical analysis
            self._test_message_latency(metrics)

            # Test 3: Throughput measurement
            self._test_throughput(metrics)

            # Test 4: Scalability test with many clients
            self._test_scalability(metrics)

            # Test 5: Reliability under stress
            self._test_reliability(metrics)

        except Exception as e:
            logger.error(f"WebSocket test error under {network_profile}: {e}")
            metrics.record_failure()
        finally:
            self.running = False
            if self.ws:
                try:
                    self.ws.close()
                except:
                    pass
            metrics.end_test()

        return self._get_results(metrics, "Completed")

    def _test_connection_performance(self, metrics: EnhancedPerformanceMetrics) -> bool:
        """Test connection establishment performance with multiple attempts"""
        logger.info("Testing WebSocket connection performance...")

        successful_connections = 0

        # Test multiple connections to get statistical data
        for attempt in range(10):
            try:
                start_time = time.time()
                test_ws = websocket.create_connection(self.url, timeout=15)
                connection_time = (time.time() - start_time) * 1000

                metrics.record_connection_time(connection_time)
                metrics.record_success()
                successful_connections += 1

                logger.info(f"Connection {attempt + 1}: {connection_time:.2f}ms")

                if attempt == 9:  # Keep last connection for further tests
                    self.ws = test_ws
                else:
                    test_ws.close()

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                metrics.record_failure()

        return successful_connections > 0

    def _test_message_latency(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test message latency with comprehensive statistical collection"""
        logger.info("Testing WebSocket message latency...")

        if not self.ws:
            return

        self.ws.settimeout(10.0)

        # Send more messages for better statistical analysis
        message_count = self.test_config.get('message_count', 50)

        for i in range(message_count):
            ping_id = str(uuid.uuid4())
            send_time = time.time() * 1000

            ping_message = {
                'type': 'ping',
                'ping_id': ping_id,
                'timestamp': send_time,
                'sequence': i
            }

            try:
                message_json = json.dumps(ping_message)
                self.ws.send(message_json)
                metrics.record_data_transfer(bytes_sent=len(message_json.encode()))

                response = self.ws.recv()
                receive_time = time.time() * 1000

                metrics.record_data_transfer(bytes_received=len(response.encode()))

                data = json.loads(response)
                if data.get('type') == 'pong' and data.get('ping_id') == ping_id:
                    real_latency = receive_time - send_time
                    metrics.record_message_latency(real_latency)
                    metrics.record_success()

                    if i % 10 == 0:
                        logger.info(f"Message {i + 1}: {real_latency:.2f}ms")
                else:
                    metrics.record_failure()

                time.sleep(0.1)  # Small delay between messages

            except Exception as e:
                logger.error(f"Message {i + 1} failed: {e}")
                metrics.record_failure()

    def _test_throughput(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test message throughput with detailed measurement"""
        logger.info("Testing WebSocket throughput...")

        if not self.ws:
            return

        duration = self.test_config.get('duration', 30)
        start_time = time.time()
        messages_sent = 0

        # Sample throughput every 5 seconds
        last_sample_time = start_time
        last_sample_count = 0

        while (time.time() - start_time) < duration:
            try:
                message = {
                    'type': 'throughput_test',
                    'timestamp': time.time() * 1000,
                    'sequence': messages_sent
                }

                message_json = json.dumps(message)
                self.ws.send(message_json)

                metrics.record_data_transfer(bytes_sent=len(message_json.encode()))
                metrics.record_success()
                messages_sent += 1

                # Try to receive response (non-blocking)
                try:
                    self.ws.settimeout(0.1)
                    response = self.ws.recv()
                    metrics.record_data_transfer(bytes_received=len(response.encode()))
                except websocket.WebSocketTimeoutException:
                    pass

                # Sample throughput
                current_time = time.time()
                if current_time - last_sample_time >= 5:
                    sample_duration = current_time - last_sample_time
                    sample_messages = messages_sent - last_sample_count
                    metrics.record_throughput_sample(sample_messages, sample_duration)

                    last_sample_time = current_time
                    last_sample_count = messages_sent

                time.sleep(0.01)  # Small delay

            except Exception as e:
                logger.error(f"Throughput test error: {e}")
                metrics.record_failure()
                break

        # Final throughput sample
        total_duration = time.time() - start_time
        if total_duration > 0:
            metrics.record_throughput_sample(messages_sent, total_duration)
            throughput = messages_sent / total_duration
            logger.info(f"Overall throughput: {throughput:.2f} msg/s over {total_duration:.1f}s")

    def _test_scalability(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test scalability with simulated concurrent connections"""
        logger.info("Testing WebSocket scalability...")

        max_connections = self.test_config.get('max_connections', 100)
        concurrent_connections = []
        successful_connections = 0

        # Create multiple connections to test scalability
        for i in range(min(max_connections, 50)):  # Limit for local testing
            try:
                start_time = time.time()
                ws_conn = websocket.create_connection(self.url, timeout=10)
                connection_time = (time.time() - start_time) * 1000

                concurrent_connections.append(ws_conn)
                metrics.record_connection_time(connection_time)
                metrics.record_success()
                successful_connections += 1

                if i % 10 == 0:
                    logger.info(f"Established {successful_connections} concurrent connections")

            except Exception as e:
                logger.error(f"Failed to establish connection {i + 1}: {e}")
                metrics.record_failure()

        logger.info(f"Successfully established {successful_connections} concurrent connections")

        # Test message sending across all connections
        for i, ws_conn in enumerate(concurrent_connections):
            try:
                test_message = {
                    'type': 'scalability_test',
                    'connection_id': i,
                    'timestamp': time.time() * 1000
                }

                ws_conn.send(json.dumps(test_message))
                metrics.record_success()

            except Exception as e:
                logger.error(f"Failed to send on connection {i}: {e}")
                metrics.record_failure()

        # Clean up connections
        for ws_conn in concurrent_connections:
            try:
                ws_conn.close()
            except:
                pass

    def _test_reliability(self, metrics: EnhancedPerformanceMetrics) -> None:
        """Test reliability under stress conditions"""
        logger.info("Testing WebSocket reliability...")

        if not self.ws:
            return

        # Send burst of messages to test reliability
        burst_count = 100
        successful_messages = 0

        for i in range(burst_count):
            try:
                message = {
                    'type': 'reliability_test',
                    'burst_sequence': i,
                    'timestamp': time.time() * 1000
                }

                self.ws.send(json.dumps(message))
                metrics.record_success()
                successful_messages += 1

            except Exception as e:
                logger.error(f"Reliability test message {i} failed: {e}")
                metrics.record_failure()

                # Attempt reconnection
                try:
                    self.ws.close()
                    self.ws = websocket.create_connection(self.url, timeout=10)
                    metrics.record_reconnection()
                    logger.info(f"Reconnected after failure at message {i}")
                except:
                    logger.error(f"Failed to reconnect at message {i}")
                    break

        logger.info(f"Reliability test: {successful_messages}/{burst_count} messages successful")

    def _get_results(self, metrics: EnhancedPerformanceMetrics, status: str) -> Dict[str, Any]:
        """Get comprehensive test results"""
        return {
            'technology': 'WebSocket',
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


def test_websocket_performance() -> Dict[str, Any]:
    """Run enhanced WebSocket performance test and return results"""
    # Enhanced test configuration
    test_config = {
        'duration': 60,
        'message_count': 50,
        'max_connections': 100,
        'test_description': 'Enhanced WebSocket performance test with network simulation'
    }

    tester = RealWebSocketTester('ws://localhost:8001/ws/alerts/', test_config)
    return tester.run_test()


if __name__ == "__main__":
    results = test_websocket_performance()

    print(f"\n=== Enhanced WebSocket Performance Test Results ===")

    # Print results for each network profile
    for profile, result in results.get('network_condition_results', {}).items():
        if result['status'] == 'Completed':
            metrics = result['metrics']
            print(f"\n{profile.upper()} Network Conditions:")
            print(f"  Average Latency: {metrics.get('message_latency_ms', 0):.1f}ms ±{metrics.get('latency_std_dev', 0):.1f}ms")
            print(f"  Connection Time: {metrics.get('connection_time_ms', 0):.1f}ms")
            print(f"  Success Rate: {metrics.get('success_rate_percent', 0):.1f}%")
            print(f"  Throughput: {metrics.get('throughput_msg_per_sec', 0):.1f} msg/s")
            print(f"  95th Percentile: {metrics.get('latency_p95', 0):.1f}ms")
            print(f"  CPU Usage: {metrics.get('cpu_usage_percent', 0):.1f}%")
            print(f"  Memory Usage: {metrics.get('memory_usage_mb', 0):.1f}MB")

    # Print summary
    summary = results.get('summary', {})
    if summary:
        print(f"\nSummary:")
        print(f"  Best Performance: {summary.get('best_performance_profile', 'N/A')}")
        print(f"  Worst Performance: {summary.get('worst_performance_profile', 'N/A')}")
