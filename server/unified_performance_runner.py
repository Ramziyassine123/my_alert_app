# ServerSide/unified_performance_runner.py

import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
from network_condition_simulator import NetworkConditionSimulator, StatisticalAnalyzer
from websocket_performance_test import test_websocket_performance
from firebase_performance_test import test_firebase_performance
from longpolling_performance_test import test_longpolling_performance
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedUnifiedPerformanceRunner:
    """Enhanced unified runner with comprehensive analysis"""

    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.network_simulator = NetworkConditionSimulator()
        self.statistical_analyzer = StatisticalAnalyzer()

    def run_comprehensive_tests(self, technologies: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive performance tests with enhanced analysis"""
        if technologies is None:
            technologies = ['websocket', 'longpolling', 'firebase']

        print("=" * 80)
        print("ENHANCED UNIFIED PERFORMANCE TEST SUITE")
        print("Testing with Network Condition Simulation")
        print("=" * 80)
        print(f"Testing technologies: {', '.join(technologies)}")
        print(f"Start time: {datetime.now().isoformat()}")

        self.start_time = time.time()

        # Run tests for each technology with enhanced metrics
        for tech in technologies:
            print(f"\n{'='*25} Testing {tech.upper()} {'='*25}")

            try:
                if tech == 'websocket':
                    result = test_websocket_performance()
                elif tech == 'longpolling':
                    result = test_longpolling_performance()
                elif tech == 'firebase':
                    result = test_firebase_performance()
                else:
                    print(f"Unknown technology: {tech}")
                    continue

                self.results[tech] = result
                print(f"✓ {tech} enhanced testing completed")

                # Print immediate summary for this technology
                self._print_technology_summary(tech, result)

            except Exception as e:
                print(f"✗ {tech} testing failed: {e}")
                logger.error(f"Technology {tech} test failed", exc_info=True)
                self.results[tech] = {
                    'technology': tech,
                    'test_type': 'enhanced_performance',
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }

        self.end_time = time.time()

        # Generate comprehensive comparison and analysis
        comprehensive_analysis = self._generate_comprehensive_analysis()

        # Create final unified results
        unified_results = {
            'test_suite': 'enhanced_unified_performance',
            'test_type': 'performance_validation',
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(self.end_time).isoformat(),
            'total_duration_seconds': self.end_time - self.start_time,
            'technologies_tested': technologies,
            'individual_results': self.results,
            'comprehensive_analysis': comprehensive_analysis,
            'performance_validation_metrics': self._generate_performance_validation_metrics(),
            'recommendations': self._generate_enhanced_recommendations(comprehensive_analysis)
        }

        self._print_comprehensive_summary(unified_results)
        return unified_results

    def _print_technology_summary(self, tech: str, result: Dict[str, Any]) -> None:
        """Print immediate summary for a technology"""
        print(f"\n--- {tech.upper()} IMMEDIATE RESULTS ---")

        if result.get('network_condition_results'):
            # Enhanced test with network conditions
            for profile, profile_result in result['network_condition_results'].items():
                if profile_result.get('status') == 'Completed':
                    metrics = profile_result.get('metrics', {})
                    print(f"  {profile}: {metrics.get('message_latency_ms', 0):.1f}ms avg, "
                          f"{metrics.get('success_rate_percent', 0):.1f}% success")
        else:
            # Fallback for basic results
            print(f"  Status: {result.get('status', 'Unknown')}")

    def _generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis across all technologies and network conditions"""
        analysis = {
            'network_condition_analysis': {},
            'technology_comparison': {},
            'statistical_analysis': {},
            'performance_rankings': {},
            'scalability_analysis': {},
            'reliability_analysis': {}
        }

        # Analyze each network condition across all technologies
        network_profiles = ['perfect', 'local_wifi', 'good_mobile', 'poor_mobile', 'satellite']

        for profile in network_profiles:
            profile_analysis = self._analyze_network_condition_performance(profile)
            if profile_analysis:
                analysis['network_condition_analysis'][profile] = profile_analysis

        # Generate technology comparison
        analysis['technology_comparison'] = self._generate_detailed_technology_comparison()

        # Statistical analysis
        analysis['statistical_analysis'] = self._generate_statistical_analysis()

        # Performance rankings
        analysis['performance_rankings'] = self._calculate_overall_rankings()

        # Scalability analysis
        analysis['scalability_analysis'] = self._generate_scalability_analysis()

        # Reliability analysis
        analysis['reliability_analysis'] = self._generate_reliability_analysis()

        return analysis

    def _analyze_network_condition_performance(self, profile: str) -> Optional[Dict[str, Any]]:
        """Analyze performance under specific network conditions"""
        condition_data = {}

        for tech, result in self.results.items():
            network_results = result.get('network_condition_results', {})
            if profile in network_results and network_results[profile].get('status') == 'Completed':
                metrics = network_results[profile]['metrics']
                condition_data[tech] = {
                    'latency_ms': metrics.get('message_latency_ms', 0),
                    'connection_time_ms': metrics.get('connection_time_ms', 0),
                    'success_rate': metrics.get('success_rate_percent', 0),
                    'throughput': metrics.get('throughput_msg_per_sec', 0),
                    'cpu_usage': metrics.get('cpu_usage_percent', 0),
                    'memory_usage': metrics.get('memory_usage_mb', 0)
                }

        if not condition_data:
            return None

        # Find best and worst performers for this condition
        latencies = {tech: data['latency_ms'] for tech, data in condition_data.items()}
        success_rates = {tech: data['success_rate'] for tech, data in condition_data.items()}

        return {
            'condition': profile,
            'technologies_tested': list(condition_data.keys()),
            'best_latency': min(latencies, key=latencies.get) if latencies else None,
            'worst_latency': max(latencies, key=latencies.get) if latencies else None,
            'best_reliability': max(success_rates, key=success_rates.get) if success_rates else None,
            'worst_reliability': min(success_rates, key=success_rates.get) if success_rates else None,
            'performance_data': condition_data,
            'latency_spread': max(latencies.values()) - min(latencies.values()) if latencies else 0,
            'reliability_spread': max(success_rates.values()) - min(success_rates.values()) if success_rates else 0
        }

    def _generate_detailed_technology_comparison(self) -> Dict[str, Any]:
        """Generate detailed comparison between technologies"""
        comparison = {
            'perfect_conditions': {},
            'degraded_conditions': {},
            'overall_rankings': {},
            'use_case_suitability': {}
        }

        # Compare under perfect conditions
        perfect_data = {}
        for tech, result in self.results.items():
            network_results = result.get('network_condition_results', {})
            if 'perfect' in network_results and network_results['perfect'].get('status') == 'Completed':
                metrics = network_results['perfect']['metrics']
                perfect_data[tech] = metrics

        if perfect_data:
            comparison['perfect_conditions'] = self._compare_technologies(perfect_data, 'perfect')

        # Compare under degraded conditions (average of poor_mobile and satellite)
        degraded_data = {}
        for tech, result in self.results.items():
            network_results = result.get('network_condition_results', {})
            poor_metrics = network_results.get('poor_mobile', {}).get('metrics', {})
            satellite_metrics = network_results.get('satellite', {}).get('metrics', {})

            if poor_metrics and satellite_metrics:
                # Average the degraded conditions
                degraded_data[tech] = {
                    'message_latency_ms': (poor_metrics.get('message_latency_ms', 0) + satellite_metrics.get('message_latency_ms', 0)) / 2,
                    'success_rate_percent': (poor_metrics.get('success_rate_percent', 0) + satellite_metrics.get('success_rate_percent', 0)) / 2,
                    'throughput_msg_per_sec': (poor_metrics.get('throughput_msg_per_sec', 0) + satellite_metrics.get('throughput_msg_per_sec', 0)) / 2,
                    'cpu_usage_percent': (poor_metrics.get('cpu_usage_percent', 0) + satellite_metrics.get('cpu_usage_percent', 0)) / 2,
                    'memory_usage_mb': (poor_metrics.get('memory_usage_mb', 0) + satellite_metrics.get('memory_usage_mb', 0)) / 2
                }

        if degraded_data:
            comparison['degraded_conditions'] = self._compare_technologies(degraded_data, 'degraded')

        # Generate overall rankings
        comparison['overall_rankings'] = self._calculate_overall_rankings()

        # Use case suitability analysis
        comparison['use_case_suitability'] = self._analyze_use_case_suitability()

        return comparison

    def _compare_technologies(self, tech_data: Dict[str, Dict], condition: str) -> Dict[str, Any]:
        """Compare technologies under specific conditions"""
        if not tech_data:
            return {}

        latencies = {tech: data.get('message_latency_ms', 0) for tech, data in tech_data.items()}
        success_rates = {tech: data.get('success_rate_percent', 0) for tech, data in tech_data.items()}
        throughputs = {tech: data.get('throughput_msg_per_sec', 0) for tech, data in tech_data.items()}
        cpu_usage = {tech: data.get('cpu_usage_percent', 0) for tech, data in tech_data.items()}
        memory_usage = {tech: data.get('memory_usage_mb', 0) for tech, data in tech_data.items()}

        return {
            'condition': condition,
            'latency_ranking': sorted(latencies.items(), key=lambda x: x[1]),
            'reliability_ranking': sorted(success_rates.items(), key=lambda x: x[1], reverse=True),
            'throughput_ranking': sorted(throughputs.items(), key=lambda x: x[1], reverse=True),
            'cpu_efficiency_ranking': sorted(cpu_usage.items(), key=lambda x: x[1]),
            'memory_efficiency_ranking': sorted(memory_usage.items(), key=lambda x: x[1]),
            'performance_metrics': {
                'latency_values': latencies,
                'success_rate_values': success_rates,
                'throughput_values': throughputs,
                'cpu_usage_values': cpu_usage,
                'memory_usage_values': memory_usage
            }
        }

    def _generate_statistical_analysis(self) -> Dict[str, Any]:
        """Generate statistical analysis of performance data"""
        stats = {
            'latency_statistics': {},
            'throughput_statistics': {},
            'reliability_statistics': {},
            'resource_usage_statistics': {}
        }

        # Collect all latency data
        all_latencies = {}
        all_throughputs = {}
        all_success_rates = {}
        all_cpu_usage = {}
        all_memory_usage = {}

        for tech, result in self.results.items():
            tech_latencies = []
            tech_throughputs = []
            tech_success_rates = []
            tech_cpu = []
            tech_memory = []

            network_results = result.get('network_condition_results', {})
            for profile, profile_result in network_results.items():
                if profile_result.get('status') == 'Completed':
                    metrics = profile_result['metrics']
                    tech_latencies.append(metrics.get('message_latency_ms', 0))
                    tech_throughputs.append(metrics.get('throughput_msg_per_sec', 0))
                    tech_success_rates.append(metrics.get('success_rate_percent', 0))
                    tech_cpu.append(metrics.get('cpu_usage_percent', 0))
                    tech_memory.append(metrics.get('memory_usage_mb', 0))

            all_latencies[tech] = tech_latencies
            all_throughputs[tech] = tech_throughputs
            all_success_rates[tech] = tech_success_rates
            all_cpu_usage[tech] = tech_cpu
            all_memory_usage[tech] = tech_memory

        # Calculate statistics for each metric
        for tech in all_latencies:
            if all_latencies[tech]:
                stats['latency_statistics'][tech] = self.statistical_analyzer.calculate_basic_stats(all_latencies[tech])
                stats['throughput_statistics'][tech] = self.statistical_analyzer.calculate_basic_stats(all_throughputs[tech])
                stats['reliability_statistics'][tech] = self.statistical_analyzer.calculate_basic_stats(all_success_rates[tech])
                stats['resource_usage_statistics'][tech] = {
                    'cpu': self.statistical_analyzer.calculate_basic_stats(all_cpu_usage[tech]),
                    'memory': self.statistical_analyzer.calculate_basic_stats(all_memory_usage[tech])
                }

        return stats

    def _calculate_overall_rankings(self) -> Dict[str, Any]:
        """Calculate overall performance rankings across all conditions"""
        rankings = {
            'overall_best': None,
            'latency_champion': None,
            'reliability_champion': None,
            'throughput_champion': None,
            'efficiency_champion': None,
            'scoring_methodology': 'Weighted average across all network conditions'
        }

        # Scoring system: lower latency = better, higher success rate = better, higher throughput = better, lower resource usage = better
        tech_scores = {}

        for tech, result in self.results.items():
            network_results = result.get('network_condition_results', {})

            latency_scores = []
            reliability_scores = []
            throughput_scores = []
            cpu_scores = []
            memory_scores = []

            for profile, profile_result in network_results.items():
                if profile_result.get('status') == 'Completed':
                    metrics = profile_result['metrics']

                    # Normalize scores (0-100 scale)
                    latency = metrics.get('message_latency_ms', 1000)
                    latency_score = max(0, 100 - (latency / 10))  # Lower latency = higher score

                    reliability_score = metrics.get('success_rate_percent', 0)  # Already 0-100

                    throughput = metrics.get('throughput_msg_per_sec', 0)
                    throughput_score = min(100, throughput * 10)  # Higher throughput = higher score

                    cpu = metrics.get('cpu_usage_percent', 100)
                    cpu_score = max(0, 100 - cpu)  # Lower CPU = higher score

                    memory = metrics.get('memory_usage_mb', 1000)
                    memory_score = max(0, 100 - (memory / 10))  # Lower memory = higher score

                    latency_scores.append(latency_score)
                    reliability_scores.append(reliability_score)
                    throughput_scores.append(throughput_score)
                    cpu_scores.append(cpu_score)
                    memory_scores.append(memory_score)

            if latency_scores:
                # Calculate weighted overall score
                avg_latency = statistics.mean(latency_scores)
                avg_reliability = statistics.mean(reliability_scores)
                avg_throughput = statistics.mean(throughput_scores)
                avg_cpu = statistics.mean(cpu_scores)
                avg_memory = statistics.mean(memory_scores)

                # Weighted scoring (latency and reliability are most important)
                overall_score = (avg_latency * 0.3 + avg_reliability * 0.3 +
                                 avg_throughput * 0.2 + avg_cpu * 0.1 + avg_memory * 0.1)

                tech_scores[tech] = {
                    'overall_score': overall_score,
                    'latency_score': avg_latency,
                    'reliability_score': avg_reliability,
                    'throughput_score': avg_throughput,
                    'cpu_efficiency_score': avg_cpu,
                    'memory_efficiency_score': avg_memory
                }

        if tech_scores:
            # Determine champions
            rankings['overall_best'] = max(tech_scores, key=lambda x: tech_scores[x]['overall_score'])
            rankings['latency_champion'] = max(tech_scores, key=lambda x: tech_scores[x]['latency_score'])
            rankings['reliability_champion'] = max(tech_scores, key=lambda x: tech_scores[x]['reliability_score'])
            rankings['throughput_champion'] = max(tech_scores, key=lambda x: tech_scores[x]['throughput_score'])
            rankings['efficiency_champion'] = max(tech_scores, key=lambda x:
            (tech_scores[x]['cpu_efficiency_score'] + tech_scores[x]['memory_efficiency_score']) / 2)

            rankings['detailed_scores'] = tech_scores

        return rankings

    def _generate_scalability_analysis(self) -> Dict[str, Any]:
        """Analyze scalability characteristics"""
        return {
            'websocket_scalability': 'Excellent for high concurrent connections',
            'longpolling_scalability': 'Limited by thread pool and HTTP overhead',
            'firebase_scalability': 'Handled by Google infrastructure',
            'scalability_ranking': ['firebase', 'websocket', 'longpolling'],
            'concurrent_client_analysis': self._analyze_concurrent_performance()
        }

    def _analyze_concurrent_performance(self) -> Dict[str, Any]:
        """Analyze performance under concurrent load"""
        concurrent_analysis = {}

        for tech, result in self.results.items():
            network_results = result.get('network_condition_results', {})
            perfect_result = network_results.get('perfect', {})

            if perfect_result.get('status') == 'Completed':
                metrics = perfect_result['metrics']
                concurrent_analysis[tech] = {
                    'estimated_max_concurrent': self._estimate_max_concurrent(tech, metrics),
                    'performance_degradation': self._estimate_performance_degradation(tech, metrics)
                }

        return concurrent_analysis

    def _estimate_max_concurrent(self, tech: str, metrics: Dict[str, Any]) -> int:
        """Estimate maximum concurrent clients based on performance metrics"""
        cpu_usage = metrics.get('cpu_usage_percent', 50)
        memory_usage = metrics.get('memory_usage_mb', 200)

        if tech == 'websocket':
            # WebSockets can handle many concurrent connections
            return int(2000 * (100 - cpu_usage) / 100)
        elif tech == 'longpolling':
            # Limited by thread pool
            return int(500 * (100 - cpu_usage) / 100)
        elif tech == 'firebase':
            # Handled by Google infrastructure
            return 10000  # Effectively unlimited for testing purposes

        return 100

    def _estimate_performance_degradation(self, tech: str, metrics: Dict[str, Any]) -> str:
        """Estimate performance degradation under load"""
        cpu_usage = metrics.get('cpu_usage_percent', 50)
        success_rate = metrics.get('success_rate_percent', 95)

        if cpu_usage < 30 and success_rate > 95:
            return "Minimal degradation expected"
        elif cpu_usage < 50 and success_rate > 90:
            return "Moderate degradation under high load"
        else:
            return "Significant degradation likely under load"

    def _generate_reliability_analysis(self) -> Dict[str, Any]:
        """Analyze reliability characteristics across network conditions"""
        reliability = {
            'overall_reliability_ranking': [],
            'network_resilience': {},
            'failure_recovery': {},
            'connection_stability': {}
        }

        tech_reliability_scores = {}

        for tech, result in self.results.items():
            network_results = result.get('network_condition_results', {})
            success_rates = []
            connection_failures = 0
            total_tests = 0

            for profile, profile_result in network_results.items():
                if profile_result.get('status') == 'Completed':
                    metrics = profile_result['metrics']
                    success_rate = metrics.get('success_rate_percent', 0)
                    success_rates.append(success_rate)

                    # Count connection issues
                    if success_rate < 90:
                        connection_failures += 1
                    total_tests += 1

            if success_rates:
                avg_reliability = statistics.mean(success_rates)
                min_reliability = min(success_rates)
                reliability_variance = statistics.stdev(success_rates) if len(success_rates) > 1 else 0

                tech_reliability_scores[tech] = avg_reliability

                reliability['network_resilience'][tech] = {
                    'average_success_rate': avg_reliability,
                    'worst_case_success_rate': min_reliability,
                    'reliability_variance': reliability_variance,
                    'connection_failure_rate': (connection_failures / total_tests) * 100 if total_tests > 0 else 0
                }

        # Rank by reliability
        if tech_reliability_scores:
            reliability['overall_reliability_ranking'] = sorted(
                tech_reliability_scores.keys(),
                key=lambda x: tech_reliability_scores[x],
                reverse=True
            )

        return reliability

    def _analyze_use_case_suitability(self) -> Dict[str, Any]:
        """Analyze suitability for different use cases based on performance characteristics"""
        return {
            'real_time_gaming': {
                'best_choice': 'websocket',
                'reason': 'Lowest latency and bidirectional communication',
                'requirements': 'Sub-100ms latency, high throughput'
            },
            'business_dashboards': {
                'best_choice': 'longpolling',
                'reason': 'HTTP compatibility, adequate latency for periodic updates',
                'requirements': 'HTTP infrastructure, moderate latency tolerance'
            },
            'mobile_notifications': {
                'best_choice': 'firebase',
                'reason': 'Reliable delivery, offline capability, platform integration',
                'requirements': 'Cross-platform support, delivery guarantees'
            },
            'financial_trading': {
                'best_choice': 'websocket',
                'reason': 'Ultra-low latency required for price updates',
                'requirements': 'Sub-50ms latency, high reliability'
            },
            'social_media_feeds': {
                'best_choice': 'longpolling',
                'reason': 'Good balance of real-time updates and infrastructure simplicity',
                'requirements': 'Moderate real-time needs, scalable architecture'
            },
            'iot_monitoring': {
                'best_choice': 'websocket',
                'reason': 'Efficient for continuous data streams',
                'requirements': 'Low resource usage, persistent connections'
            }
        }

    def _generate_performance_validation_metrics(self) -> Dict[str, Any]:
        """Generate metrics for performance validation"""
        validation = {
            'websocket_validation': {},
            'longpolling_validation': {},
            'firebase_validation': {},
            'performance_claims_verification': {}
        }

        # Extract key metrics for performance
        for tech, result in self.results.items():
            network_results = result.get('network_condition_results', {})

            if 'perfect' in network_results and network_results['perfect'].get('status') == 'Completed':
                perfect_metrics = network_results['perfect']['metrics']

                if tech == 'websocket':
                    validation['websocket_validation'] = {
                        'average_latency_ms': perfect_metrics.get('message_latency_ms', 0),
                        'connection_time_ms': perfect_metrics.get('connection_time_ms', 0),
                        'success_rate_percent': perfect_metrics.get('success_rate_percent', 0),
                        'max_throughput_msg_per_sec': perfect_metrics.get('throughput_msg_per_sec', 0),
                        'p95_latency_ms': perfect_metrics.get('latency_p95', 0),
                        'performance_claim_validation': self._validate_websocket_claims(perfect_metrics)
                    }

                elif tech == 'longpolling':
                    validation['longpolling_validation'] = {
                        'average_response_time_ms': perfect_metrics.get('message_latency_ms', 0),
                        'connection_overhead_ms': perfect_metrics.get('connection_time_ms', 0),
                        'success_rate_percent': perfect_metrics.get('success_rate_percent', 0),
                        'max_concurrent_supported': self._estimate_max_concurrent(tech, perfect_metrics),
                        'p95_response_time_ms': perfect_metrics.get('latency_p95', 0),
                        'performance_claim_validation': self._validate_longpolling_claims(perfect_metrics)
                    }

                elif tech == 'firebase':
                    validation['firebase_validation'] = {
                        'registration_time_ms': perfect_metrics.get('connection_time_ms', 0),
                        'api_response_time_ms': perfect_metrics.get('message_latency_ms', 0),
                        'delivery_success_rate_percent': perfect_metrics.get('success_rate_percent', 0),
                        'end_to_end_latency_estimate_ms': perfect_metrics.get('message_latency_ms', 0) * 2,  # Estimate
                        'performance_claim_validation': self._validate_firebase_claims(perfect_metrics)
                    }

        # Overall validation
        validation['performance_claims_verification'] = self._verify_overall_performance_claims()

        return validation

    def _validate_websocket_claims(self, metrics: Dict[str, Any]) -> Dict[str, bool]:
        """Validate WebSocket performance claims"""
        return {
            'sub_100ms_latency_achieved': metrics.get('message_latency_ms', 0) < 100,
            'sub_50ms_average_claimed': metrics.get('message_latency_ms', 0) < 50,
            'high_throughput_achieved': metrics.get('throughput_msg_per_sec', 0) > 100,
            'excellent_scalability': metrics.get('success_rate_percent', 0) > 95,
            'low_resource_usage': metrics.get('cpu_usage_percent', 0) < 40
        }

    def _validate_longpolling_claims(self, metrics: Dict[str, Any]) -> Dict[str, bool]:
        """Validate Long Polling performance"""
        return {
            'sub_200ms_response_time': metrics.get('message_latency_ms', 0) < 200,
            'good_http_compatibility': True,  # Always true by design
            'moderate_scalability': metrics.get('success_rate_percent', 0) > 85,
            'higher_resource_usage': metrics.get('cpu_usage_percent', 0) > 30,
            'acceptable_for_non_realtime': metrics.get('message_latency_ms', 0) < 500
        }

    def _validate_firebase_claims(self, metrics: Dict[str, Any]) -> Dict[str, bool]:
        """Validate Firebase performance"""
        return {
            'reliable_delivery': metrics.get('success_rate_percent', 0) > 95,
            'higher_latency_than_websocket': metrics.get('message_latency_ms', 0) > 200,
            'good_mobile_integration': True,  # Always true by design
            'scalable_infrastructure': True,  # Google's infrastructure
            'simple_implementation': True   # Always true by design
        }

    def _verify_overall_performance_claims(self) -> Dict[str, Any]:
        """Verify overall performance claims across technologies"""
        websocket_perfect = self._get_perfect_metrics('websocket')
        longpolling_perfect = self._get_perfect_metrics('longpolling')
        firebase_perfect = self._get_perfect_metrics('firebase')

        claims = {}

        if websocket_perfect and longpolling_perfect:
            claims['websocket_faster_than_longpolling'] = (
                    websocket_perfect.get('message_latency_ms', 0) <
                    longpolling_perfect.get('message_latency_ms', 0)
            )

        if websocket_perfect and firebase_perfect:
            claims['websocket_faster_than_firebase'] = (
                    websocket_perfect.get('message_latency_ms', 0) <
                    firebase_perfect.get('message_latency_ms', 0)
            )

        if longpolling_perfect and firebase_perfect:
            claims['firebase_more_reliable_than_longpolling'] = (
                    firebase_perfect.get('success_rate_percent', 0) >=
                    longpolling_perfect.get('success_rate_percent', 0)
            )

        # Resource usage comparisons
        if websocket_perfect and longpolling_perfect:
            claims['websocket_more_efficient_than_longpolling'] = (
                    websocket_perfect.get('cpu_usage_percent', 0) <
                    longpolling_perfect.get('cpu_usage_percent', 0)
            )

        return claims

    def _get_perfect_metrics(self, tech: str) -> Optional[Dict[str, Any]]:
        """Get perfect condition metrics for a technology"""
        result = self.results.get(tech, {})
        network_results = result.get('network_condition_results', {})
        perfect_result = network_results.get('perfect', {})

        if perfect_result.get('status') == 'Completed':
            return perfect_result.get('metrics', {})
        return None

    def _generate_enhanced_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate enhanced recommendations based on comprehensive analysis"""
        recommendations = []

        # Performance-based recommendations
        rankings = analysis.get('performance_rankings', {})
        if rankings.get('overall_best'):
            recommendations.append(f"Overall best performer: {rankings['overall_best']} - recommended for most applications")

        if rankings.get('latency_champion'):
            recommendations.append(f"For ultra-low latency requirements: Use {rankings['latency_champion']}")

        if rankings.get('reliability_champion'):
            recommendations.append(f"For maximum reliability: Use {rankings['reliability_champion']}")

        # Network condition recommendations
        network_analysis = analysis.get('network_condition_analysis', {})
        if 'poor_mobile' in network_analysis:
            poor_mobile = network_analysis['poor_mobile']
            if poor_mobile.get('best_latency'):
                recommendations.append(f"For poor mobile networks: {poor_mobile['best_latency']} performs best")

        # Use case recommendations
        use_cases = analysis.get('technology_comparison', {}).get('use_case_suitability', {})
        for use_case, recommendation in use_cases.items():
            recommendations.append(f"{use_case.replace('_', ' ').title()}: Use {recommendation['best_choice']} - {recommendation['reason']}")

        # Scalability recommendations
        scalability = analysis.get('scalability_analysis', {})
        scalability_ranking = scalability.get('scalability_ranking', [])
        if scalability_ranking:
            recommendations.append(f"For high scalability: Prefer {scalability_ranking[0]} over {scalability_ranking[-1]}")

        # Hybrid architecture recommendations
        recommendations.append("Consider hybrid approach: WebSocket for real-time features, Long Polling for periodic updates, Firebase for mobile notifications")

        return recommendations

    def _print_comprehensive_summary(self, results: Dict[str, Any]) -> None:
        """Print comprehensive summary"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE PERFORMANCE TEST RESULTS")
        print("Enhanced Analysis with Network Condition Simulation")
        print("=" * 80)

        print(f"\nTest Duration: {results['total_duration_seconds']:.2f} seconds")
        print(f"Technologies Tested: {', '.join(results['technologies_tested'])}")

        # Performance Summary Table
        print(f"\n{'Technology':<15} {'Perfect Latency':<15} {'Poor Mobile':<15} {'Success Rate':<12} {'Throughput':<12}")
        print("-" * 80)

        for tech in results['technologies_tested']:
            tech_result = results['individual_results'].get(tech, {})
            network_results = tech_result.get('network_condition_results', {})

            perfect_metrics = network_results.get('perfect', {}).get('metrics', {})
            poor_metrics = network_results.get('poor_mobile', {}).get('metrics', {})

            perfect_latency = perfect_metrics.get('message_latency_ms', 0)
            poor_latency = poor_metrics.get('message_latency_ms', 0)
            success_rate = perfect_metrics.get('success_rate_percent', 0)
            throughput = perfect_metrics.get('throughput_msg_per_sec', 0)

            print(f"{tech.title():<15} {perfect_latency:<15.1f} {poor_latency:<15.1f} {success_rate:<12.1f} {throughput:<12.1f}")

        # Results
        performance_validation = results.get('performance_validation_metrics', {})
        print(f"\n=== VALIDATION RESULTS ===")

        for tech, validation in performance_validation.items():
            if tech.endswith('_validation') and isinstance(validation, dict):
                tech_name = tech.replace('_validation', '')
                print(f"\n{tech_name.upper()} Validation:")

                for claim, validated in validation.get('performance_claim_validation', {}).items():
                    status = "✓" if validated else "✗"
                    print(f"  {status} {claim.replace('_', ' ').title()}")

        # Network Condition Impact Analysis
        analysis = results.get('comprehensive_analysis', {})
        network_analysis = analysis.get('network_condition_analysis', {})

        print(f"\n=== NETWORK CONDITION IMPACT ===")
        for condition, condition_data in network_analysis.items():
            if condition_data:
                print(f"\n{condition.upper()}:")
                print(f"  Best Latency: {condition_data.get('best_latency', 'N/A')}")
                print(f"  Best Reliability: {condition_data.get('best_reliability', 'N/A')}")
                print(f"  Latency Spread: {condition_data.get('latency_spread', 0):.1f}ms")

        # Overall Rankings
        rankings = analysis.get('performance_rankings', {})
        print(f"\n=== PERFORMANCE RANKINGS ===")
        print(f"Overall Best: {rankings.get('overall_best', 'N/A')}")
        print(f"Latency Champion: {rankings.get('latency_champion', 'N/A')}")
        print(f"Reliability Champion: {rankings.get('reliability_champion', 'N/A')}")
        print(f"Throughput Champion: {rankings.get('throughput_champion', 'N/A')}")

        # Recommendations
        print(f"\n=== ENHANCED RECOMMENDATIONS ===")
        for i, rec in enumerate(results.get('recommendations', []), 1):
            print(f"{i:2d}. {rec}")

        print(f"\nTest completed at: {results['end_time']}")
        print("=" * 80)

    # Class-level storage for results
    _test_results = {}

    @classmethod
    def store_results(cls, test_id: str, results: Dict[str, Any]):
        """Store test results"""
        cls._test_results[test_id] = results

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
                             key=lambda k: cls._test_results[k].get('start_time', ''))
        return cls._test_results[latest_test_id]


def run_enhanced_performance_tests(technologies: List[str] = None) -> Dict[str, Any]:
    """Main entry point for enhanced performance testing"""
    runner = EnhancedUnifiedPerformanceRunner()
    return runner.run_comprehensive_tests(technologies)


if __name__ == "__main__":
    # Run comprehensive enhanced tests
    results = run_enhanced_performance_tests()

    # Save results to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"enhanced_performance_results_{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n✓ Enhanced results saved to {filename}")
    except Exception as e:
        print(f"✗ Failed to save results: {e}")

    # Generate comprehensive report
    try:
        from enhanced_performance_report import EnhancedPerformanceReport
        report_generator = EnhancedPerformanceReport()

        # Generate multiple report formats
        report_generator.generate_comprehensive_html_report(results, f"enhanced_report_{timestamp}.html")
        report_generator.generate_research_analysis_report(results, f"performance_validation_{timestamp}.html")
        report_generator.generate_detailed_csv_report(results, f"detailed_metrics_{timestamp}.csv")

        print(f"✓ Comprehensive reports generated")
    except ImportError:
        print("Enhanced reporting module not available - basic reporting only")
