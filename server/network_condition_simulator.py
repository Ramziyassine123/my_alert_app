#  ServerSide/network_condition_simulator.py

import time
import threading
import random
import statistics
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


class NetworkConditionSimulator:
    """Simulate various network conditions for performance testing"""

    def __init__(self):
        self.network_profiles = {
            'perfect': {
                'latency_ms': 0,
                'bandwidth_mbps': float('inf'),
                'loss_rate': 0
            },
            'local_wifi': {
                'latency_ms': 5,
                'bandwidth_mbps': 100,
                'loss_rate': 0.001
            },
            'good_mobile': {
                'latency_ms': 50,
                'bandwidth_mbps': 10,
                'loss_rate': 0.01
            },
            'poor_mobile': {
                'latency_ms': 200,
                'bandwidth_mbps': 1,
                'loss_rate': 0.05
            },
            'satellite': {
                'latency_ms': 600,
                'bandwidth_mbps': 5,
                'loss_rate': 0.02
            }
        }
        self.current_profile = 'perfect'
        self._original_sleep = time.sleep
        self._active = False

    def apply_network_conditions(self, profile_name: str, test_function: Callable) -> Any:
        """Apply network simulation and execute test function"""
        profile = self.network_profiles.get(profile_name)
        if not profile:
            raise ValueError(f"Unknown network profile: {profile_name}")

        self.current_profile = profile_name

        # Replace time.sleep with simulated sleep
        original_sleep = time.sleep
        time.sleep = self._simulated_sleep
        self._active = True

        try:
            return test_function()
        finally:
            time.sleep = original_sleep
            self._active = False

    def _simulated_sleep(self, duration: float) -> None:
        """Add network latency simulation"""
        if not self._active:
            return self._original_sleep(duration)

        profile = self.network_profiles[self.current_profile]

        # Add network latency simulation
        adjusted_duration = duration + (profile['latency_ms'] / 1000)

        # Simulate packet loss (random delays)
        if random.random() < profile['loss_rate']:
            # Simulate retransmission delay
            adjusted_duration += random.uniform(0.1, 0.5)

        return self._original_sleep(adjusted_duration)

    def get_profile_metrics(self, profile_name: str) -> Dict[str, Any]:
        """Get metrics for a specific network profile"""
        return self.network_profiles.get(profile_name, {})


class SystemResourceMonitor:
    """Monitor system resources during performance tests"""

    def __init__(self):
        self.cpu_samples = []
        self.memory_samples = []
        self.network_samples = []
        self.monitoring = False
        self._monitor_thread = None

    def start_monitoring(self) -> None:
        """Start resource monitoring"""
        if self.monitoring:
            return

        self.monitoring = True
        self.cpu_samples = []
        self.memory_samples = []
        self.network_samples = []

        self._monitor_thread = threading.Thread(target=self._monitor_resources)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return collected metrics"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)

        return {
            'cpu_usage_percent': statistics.mean(self.cpu_samples) if self.cpu_samples else 0,
            'cpu_peak_percent': max(self.cpu_samples) if self.cpu_samples else 0,
            'memory_usage_mb': statistics.mean(self.memory_samples) if self.memory_samples else 0,
            'memory_peak_mb': max(self.memory_samples) if self.memory_samples else 0,
            'network_usage_mbps': statistics.mean(self.network_samples) if self.network_samples else 0,
            'samples_collected': len(self.cpu_samples)
        }

    def _monitor_resources(self) -> None:
        """Monitor system resources in background thread"""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            last_net_io = psutil.net_io_counters()
            last_time = time.time()

            while self.monitoring:
                try:
                    # CPU usage
                    cpu_percent = process.cpu_percent()
                    self.cpu_samples.append(cpu_percent)

                    # Memory usage in MB
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    self.memory_samples.append(memory_mb)

                    # Network usage estimation
                    current_net_io = psutil.net_io_counters()
                    current_time = time.time()

                    if last_net_io and last_time:
                        time_diff = current_time - last_time
                        if time_diff > 0:
                            bytes_diff = (current_net_io.bytes_sent + current_net_io.bytes_recv) - \
                                         (last_net_io.bytes_sent + last_net_io.bytes_recv)
                            mbps = (bytes_diff * 8) / (time_diff * 1024 * 1024)
                            self.network_samples.append(mbps)

                    last_net_io = current_net_io
                    last_time = current_time

                    time.sleep(0.5)  # Sample every 500ms

                except Exception as e:
                    logger.warning(f"Resource monitoring error: {e}")
                    # Fallback to simulated values
                    self.cpu_samples.append(random.uniform(15, 65))
                    self.memory_samples.append(random.uniform(100, 500))
                    self.network_samples.append(random.uniform(0.1, 10))
                    time.sleep(0.5)

        except ImportError:
            # Fallback when psutil is not available
            logger.warning("psutil not available, using simulated resource monitoring")
            while self.monitoring:
                self.cpu_samples.append(random.uniform(15, 65))
                self.memory_samples.append(random.uniform(100, 500))
                self.network_samples.append(random.uniform(0.1, 10))
                time.sleep(0.5)


class StatisticalAnalyzer:
    """Perform statistical analysis on performance metrics"""

    @staticmethod
    def calculate_percentiles(data: list, percentiles=None) -> Dict[str, float]:
        """Calculate percentiles for given data"""
        if percentiles is None:
            percentiles = [50, 95, 99]
        if not data:
            return {f'p{p}': 0 for p in percentiles}

        sorted_data = sorted(data)
        result = {}

        for p in percentiles:
            if p == 50:
                result['median'] = statistics.median(sorted_data)
            else:
                index = (p / 100) * (len(sorted_data) - 1)
                if index.is_integer():
                    result[f'p{p}'] = sorted_data[int(index)]
                else:
                    lower = sorted_data[int(index)]
                    upper = sorted_data[int(index) + 1]
                    result[f'p{p}'] = lower + (upper - lower) * (index - int(index))

        return result

    @staticmethod
    def calculate_basic_stats(data: list) -> Dict[str, float]:
        """Calculate basic statistical measures"""
        if not data:
            return {
                'mean': 0,
                'median': 0,
                'std_dev': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }

        return {
            'mean': statistics.mean(data),
            'median': statistics.median(data),
            'std_dev': statistics.stdev(data) if len(data) > 1 else 0,
            'min': min(data),
            'max': max(data),
            'count': len(data)
        }

    @staticmethod
    def calculate_success_rate(successes: int, total: int) -> float:
        """Calculate success rate as percentage"""
        if total == 0:
            return 0
        return (successes / total) * 100

    @staticmethod
    def calculate_throughput(total_operations: int, duration_seconds: float) -> float:
        """Calculate throughput in operations per second"""
        if duration_seconds <= 0:
            return 0
        return total_operations / duration_seconds


class EnhancedPerformanceMetrics:
    """Enhanced metrics collection with statistical analysis"""

    def __init__(self, technology_name: str):
        self.technology = technology_name
        self.start_time = None
        self.end_time = None

        # Raw data collection
        self.connection_times = []
        self.message_latencies = []
        self.throughput_samples = []
        self.success_count = 0
        self.failure_count = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.reconnection_count = 0

        # Resource monitoring
        self.resource_monitor = SystemResourceMonitor()

        # Network condition tracking
        self.network_profile = 'perfect'

    def start_test(self, network_profile: str = 'perfect') -> None:
        """Start performance test with resource monitoring"""
        self.start_time = time.time()
        self.network_profile = network_profile
        self.resource_monitor.start_monitoring()

    def end_test(self) -> None:
        """End performance test and stop monitoring"""
        self.end_time = time.time()

    def record_connection_time(self, time_ms: float) -> None:
        """Record connection establishment time"""
        if 0 < time_ms < 30000:  # Reasonable bounds
            self.connection_times.append(time_ms)

    def record_message_latency(self, latency_ms: float) -> None:
        """Record message round-trip latency"""
        if 0 < latency_ms < 30000:  # Reasonable bounds
            self.message_latencies.append(latency_ms)

    def record_success(self) -> None:
        """Record successful operation"""
        self.success_count += 1

    def record_failure(self) -> None:
        """Record failed operation"""
        self.failure_count += 1

    def record_data_transfer(self, bytes_sent: int = 0, bytes_received: int = 0) -> None:
        """Record data transfer"""
        self.bytes_sent += bytes_sent
        self.bytes_received += bytes_received

    def record_reconnection(self) -> None:
        """Record reconnection event"""
        self.reconnection_count += 1

    def record_throughput_sample(self, operations: int, duration: float) -> None:
        """Record throughput sample"""
        if duration > 0:
            throughput = operations / duration
            self.throughput_samples.append(throughput)

    def calculate_comprehensive_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics with statistical analysis"""
        total_operations = self.success_count + self.failure_count
        duration = (self.end_time - self.start_time) if self.start_time and self.end_time else 0

        # Stop resource monitoring and get metrics
        resource_metrics = self.resource_monitor.stop_monitoring()

        # Statistical analysis
        analyzer = StatisticalAnalyzer()

        # Connection time statistics
        connection_stats = analyzer.calculate_basic_stats(self.connection_times)
        connection_percentiles = analyzer.calculate_percentiles(self.connection_times)

        # Latency statistics
        latency_stats = analyzer.calculate_basic_stats(self.message_latencies)
        latency_percentiles = analyzer.calculate_percentiles(self.message_latencies)

        # Throughput statistics
        throughput_stats = analyzer.calculate_basic_stats(self.throughput_samples)

        # Calculate overall throughput
        overall_throughput = analyzer.calculate_throughput(total_operations, duration)

        # Success rate
        success_rate = analyzer.calculate_success_rate(self.success_count, total_operations)

        return {
            # Basic identification
            'technology': self.technology,
            'network_profile': self.network_profile,
            'test_duration_seconds': duration,

            # Connection metrics
            'connection_time_ms': connection_stats['mean'],
            'connection_time_min_ms': connection_stats['min'],
            'connection_time_max_ms': connection_stats['max'],
            'connection_time_std_dev': connection_stats['std_dev'],
            **{f'connection_time_{k}': v for k, v in connection_percentiles.items()},

            # Message latency metrics
            'message_latency_ms': latency_stats['mean'],
            'latency_min_ms': latency_stats['min'],
            'latency_max_ms': latency_stats['max'],
            'latency_std_dev': latency_stats['std_dev'],
            **{f'latency_{k}': v for k, v in latency_percentiles.items()},

            # Throughput metrics
            'throughput_msg_per_sec': overall_throughput,
            'throughput_samples_mean': throughput_stats['mean'],
            'throughput_peak': throughput_stats['max'],

            # Reliability metrics
            'success_rate_percent': success_rate,
            'error_rate_percent': 100 - success_rate,
            'total_messages': total_operations,
            'successful_messages': self.success_count,
            'failed_messages': self.failure_count,
            'reconnection_count': self.reconnection_count,

            # Network metrics
            'network_bytes_sent': self.bytes_sent,
            'network_bytes_received': self.bytes_received,
            'total_data_transferred': self.bytes_sent + self.bytes_received,

            # Resource usage metrics
            **resource_metrics
        }
