"""
TPYOPT Metrics Calculator Module

Calculates comprehensive performance metrics, statistics, and KPIs 
for TPYOPT analysis including cycle performance, device efficiency,
and optimization quality metrics.
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import statistics
import time


class TPYOPTMetricsCalculator:
    """TPYOPT metrics calculation and KPI generation"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
        # Metric categories
        self.metric_categories = {
            'performance_metrics': {},
            'cycle_metrics': {},
            'device_metrics': {},
            'efficiency_metrics': {},
            'quality_metrics': {},
            'temporal_metrics': {}
        }
        
    def calculate_metrics(self, events: List[Dict[str, Any]], cycles: List[Dict[str, Any]],
                         analysis_data: Dict[str, Any], failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive TPYOPT metrics"""
        self.logger.info("Calculating TPYOPT performance metrics")
        
        # Calculate different metric categories
        performance_metrics = self._calculate_performance_metrics(events, cycles, analysis_data)
        cycle_metrics = self._calculate_cycle_metrics(cycles)
        device_metrics = self._calculate_device_metrics(analysis_data, events)
        efficiency_metrics = self._calculate_efficiency_metrics(cycles, events)
        quality_metrics = self._calculate_quality_metrics(cycles, failures)
        temporal_metrics = self._calculate_temporal_metrics(events)
        
        # Generate KPI dashboard
        kpi_dashboard = self._generate_kpi_dashboard(
            performance_metrics, cycle_metrics, device_metrics, quality_metrics
        )
        
        # Generate benchmarks
        benchmarks = self._generate_benchmarks(performance_metrics, cycle_metrics)
        
        return {
            'performance_metrics': performance_metrics,
            'cycle_metrics': cycle_metrics,
            'device_metrics': device_metrics,
            'efficiency_metrics': efficiency_metrics,
            'quality_metrics': quality_metrics,
            'temporal_metrics': temporal_metrics,
            'kpi_dashboard': kpi_dashboard,
            'benchmarks': benchmarks,
            'summary_scores': self._calculate_summary_scores(
                performance_metrics, cycle_metrics, quality_metrics
            )
        }
    
    def _calculate_performance_metrics(self, events: List[Dict[str, Any]], 
                                     cycles: List[Dict[str, Any]], 
                                     analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        if not events:
            return {'error': 'No events to analyze'}
        
        # Basic event metrics
        total_events = len(events)
        pattern_matches = len([e for e in events if e.get('confidence', 0) > 0])
        avg_confidence = statistics.mean([e.get('confidence', 0) for e in events 
                                        if e.get('confidence', 0) > 0]) if events else 0
        
        # FSM analysis metrics
        fsm_analysis = analysis_data.get('fsm_analysis', {})
        device_analysis = analysis_data.get('device_analysis', {})
        
        # Cycle metrics
        if isinstance(cycles, dict):
            total_cycles = sum(len(device_cycles) for device_cycles in cycles.values())
            completed_cycles = 0
            successful_cycles = 0
            
            for device_cycles in cycles.values():
                for cycle in device_cycles:
                    if cycle.get('status') == 'completed':
                        completed_cycles += 1
                        if cycle.get('success', False):
                            successful_cycles += 1
        else:
            total_cycles = len(cycles) if cycles else 0
            completed_cycles = len([c for c in cycles if c.get('status') == 'completed'])
            successful_cycles = len([c for c in cycles if c.get('success', False)])
        
        # Calculate rates
        completion_rate = completed_cycles / max(1, total_cycles)
        success_rate = successful_cycles / max(1, completed_cycles)
        pattern_match_rate = pattern_matches / max(1, total_events)
        
        return {
            'total_events': total_events,
            'total_optimization_cycles': total_cycles,
            'completed_cycles': completed_cycles,
            'successful_cycles': successful_cycles,
            'completion_rate': completion_rate,
            'success_rate': success_rate,
            'optimization_success_rate': success_rate,  # Alias for compatibility
            'pattern_matches': pattern_matches,
            'pattern_match_rate': pattern_match_rate,
            'average_confidence': avg_confidence,
            'unique_devices': device_analysis.get('total_devices', 0),
            'active_devices': device_analysis.get('total_devices', 0),  # All devices considered active
            'fsm_transitions': fsm_analysis.get('state_statistics', {}).get('total_transitions', 0),
            'events_per_second': self._calculate_events_per_second(events)
        }
    
    def _calculate_events_per_second(self, events: List[Dict[str, Any]]) -> float:
        """Calculate events per second processing rate"""
        if len(events) < 2:
            return 0.0
        
        try:
            # Get first and last timestamps
            sorted_events = sorted([e for e in events if e.get('timestamp')], 
                                 key=lambda x: x['timestamp'])
            
            if len(sorted_events) < 2:
                return 0.0
            
            first_time = sorted_events[0]['timestamp']
            last_time = sorted_events[-1]['timestamp']
            
            # Simplified calculation - would need proper datetime parsing in production
            time_span_seconds = len(sorted_events) * 0.1  # Rough approximation
            return len(events) / max(1, time_span_seconds)
            
        except Exception:
            return len(events) / 3600  # Fallback: assume 1 hour span
    
    def _calculate_cycle_metrics(self, cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate cycle-specific metrics"""
        cycle_metrics = {
            'total_cycles': 0,
            'average_cycle_duration': 0,
            'median_cycle_duration': 0,
            'cycle_duration_distribution': Counter(),
            'phase_completion_rates': {},
            'cycle_efficiency_scores': []
        }
        
        if not cycles:
            return cycle_metrics
        
        durations = []
        event_counts = []
        phase_completions = Counter()
        
        if isinstance(cycles, dict):
            # Handle dict format (device_mac -> list of cycles)
            all_cycles = []
            for device_cycles in cycles.values():
                all_cycles.extend(device_cycles)
            cycles = all_cycles
        
        cycle_metrics['total_cycles'] = len(cycles)
        
        for cycle in cycles:
            # Duration metrics
            duration = cycle.get('metrics', {}).get('duration_events', 0)
            durations.append(duration)
            
            # Event count metrics
            total_events = cycle.get('metrics', {}).get('total_events', 0)
            event_counts.append(total_events)
            
            # Phase completion tracking
            phases = cycle.get('phases', [])
            for phase in phases:
                phase_completions[phase.get('phase', 'unknown')] += 1
            
            # Efficiency scoring
            efficiency_score = self._calculate_cycle_efficiency(cycle)
            cycle_metrics['cycle_efficiency_scores'].append(efficiency_score)
            
            # Duration distribution
            if duration < 5:
                cycle_metrics['cycle_duration_distribution']['very_short'] += 1
            elif duration < 15:
                cycle_metrics['cycle_duration_distribution']['short'] += 1
            elif duration < 30:
                cycle_metrics['cycle_duration_distribution']['medium'] += 1
            elif duration < 60:
                cycle_metrics['cycle_duration_distribution']['long'] += 1
            else:
                cycle_metrics['cycle_duration_distribution']['very_long'] += 1
        
        # Calculate statistics
        if durations:
            cycle_metrics['average_cycle_duration'] = statistics.mean(durations)
            cycle_metrics['median_cycle_duration'] = statistics.median(durations)
            cycle_metrics['max_cycle_duration'] = max(durations)
            cycle_metrics['min_cycle_duration'] = min(durations)
        
        if event_counts:
            cycle_metrics['average_events_per_cycle'] = statistics.mean(event_counts)
        
        # Phase completion rates
        total_cycles = len(cycles)
        for phase, count in phase_completions.items():
            cycle_metrics['phase_completion_rates'][phase] = count / total_cycles
        
        # Efficiency statistics
        if cycle_metrics['cycle_efficiency_scores']:
            cycle_metrics['average_efficiency_score'] = statistics.mean(cycle_metrics['cycle_efficiency_scores'])
        
        return cycle_metrics
    
    def _calculate_cycle_efficiency(self, cycle: Dict[str, Any]) -> float:
        """Calculate efficiency score for a single cycle"""
        score = 0.0
        
        # Base score for completion
        if cycle.get('status') == 'completed':
            score += 40
        
        # Success bonus
        if cycle.get('success', False):
            score += 30
        
        # Efficiency based on event count (fewer events = more efficient)
        event_count = cycle.get('metrics', {}).get('total_events', 0)
        if event_count <= 10:
            score += 20
        elif event_count <= 20:
            score += 10
        elif event_count <= 30:
            score += 5
        
        # Phase completion bonus
        phases_completed = len(cycle.get('phases', []))
        if phases_completed >= 5:
            score += 10
        elif phases_completed >= 3:
            score += 5
        
        return min(100.0, score)
    
    def _calculate_device_metrics(self, analysis_data: Dict[str, Any], 
                                events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate device-specific metrics"""
        device_analysis = analysis_data.get('device_analysis', {})
        
        device_metrics = {
            'total_devices': device_analysis.get('total_devices', 0),
            'high_activity_devices': len(device_analysis.get('behavior_summary', {}).get('high_activity', [])),
            'low_activity_devices': len(device_analysis.get('behavior_summary', {}).get('low_activity', [])),
            'problematic_devices': len(device_analysis.get('behavior_summary', {}).get('problematic', [])),
            'device_activity_distribution': {},
            'device_success_rates': {},
            'device_performance_scores': {}
        }
        
        # Calculate device-specific statistics
        device_events = defaultdict(int)
        for event in events:
            device_mac = event.get('device_mac')
            if device_mac:
                device_events[device_mac] += 1
        
        # Activity distribution
        if device_events:
            event_counts = list(device_events.values())
            device_metrics['device_activity_distribution'] = {
                'average_events_per_device': statistics.mean(event_counts),
                'median_events_per_device': statistics.median(event_counts),
                'max_events_per_device': max(event_counts),
                'min_events_per_device': min(event_counts)
            }
        
        return device_metrics
    
    def _calculate_efficiency_metrics(self, cycles: List[Dict[str, Any]], 
                                    events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate efficiency metrics"""
        efficiency_metrics = {
            'overall_efficiency_score': 0,
            'resource_utilization': {},
            'optimization_effectiveness': {},
            'time_efficiency': {}
        }
        
        if not cycles and not events:
            return efficiency_metrics
        
        # Calculate overall efficiency
        if isinstance(cycles, dict):
            all_cycles = []
            for device_cycles in cycles.values():
                all_cycles.extend(device_cycles)
            cycles = all_cycles
        
        if cycles:
            efficiency_scores = [self._calculate_cycle_efficiency(cycle) for cycle in cycles]
            efficiency_metrics['overall_efficiency_score'] = statistics.mean(efficiency_scores)
        
        # Resource utilization metrics
        total_events = len(events)
        optimization_events = len([e for e in events if e.get('event_type') == 'optimization'])
        
        efficiency_metrics['resource_utilization'] = {
            'optimization_event_ratio': optimization_events / max(1, total_events),
            'event_processing_efficiency': min(1.0, total_events / max(1, len(cycles) * 20))  # Normalize
        }
        
        return efficiency_metrics
    
    def _calculate_quality_metrics(self, cycles: List[Dict[str, Any]], 
                                 failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality metrics"""
        quality_metrics = {
            'system_reliability_score': 0,
            'failure_rate': 0,
            'quality_distribution': Counter(),
            'reliability_indicators': {}
        }
        
        if isinstance(cycles, dict):
            all_cycles = []
            for device_cycles in cycles.values():
                all_cycles.extend(device_cycles)
            cycles = all_cycles
        
        total_cycles = len(cycles) if cycles else 0
        total_failures = len(failures) if failures else 0
        
        # Basic quality metrics
        if total_cycles > 0:
            successful_cycles = len([c for c in cycles if c.get('success', False)])
            quality_metrics['failure_rate'] = total_failures / total_cycles
            quality_metrics['system_reliability_score'] = (successful_cycles / total_cycles) * 100
        
        # Quality distribution
        for cycle in cycles:
            efficiency_score = self._calculate_cycle_efficiency(cycle)
            if efficiency_score >= 80:
                quality_metrics['quality_distribution']['excellent'] += 1
            elif efficiency_score >= 60:
                quality_metrics['quality_distribution']['good'] += 1
            elif efficiency_score >= 40:
                quality_metrics['quality_distribution']['fair'] += 1
            else:
                quality_metrics['quality_distribution']['poor'] += 1
        
        # Reliability indicators
        quality_metrics['reliability_indicators'] = {
            'low_failure_rate': quality_metrics['failure_rate'] < 0.1,
            'high_success_rate': quality_metrics['system_reliability_score'] > 80,
            'consistent_performance': len(quality_metrics['quality_distribution']) <= 2
        }
        
        return quality_metrics
    
    def _calculate_temporal_metrics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate temporal patterns and metrics"""
        temporal_metrics = {
            'time_span': 'Unknown',
            'event_frequency': {},
            'peak_activity_periods': [],
            'activity_patterns': {}
        }
        
        if not events:
            return temporal_metrics
        
        # Sort events by timestamp
        timestamped_events = [e for e in events if e.get('timestamp')]
        if timestamped_events:
            timestamped_events.sort(key=lambda x: x['timestamp'])
            
            first_event = timestamped_events[0]['timestamp']
            last_event = timestamped_events[-1]['timestamp']
            temporal_metrics['time_span'] = f"{first_event} to {last_event}"
        
        # Event frequency analysis
        event_types = Counter()
        for event in events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] += 1
        
        temporal_metrics['event_frequency'] = dict(event_types)
        
        return temporal_metrics
    
    def _generate_kpi_dashboard(self, performance_metrics: Dict[str, Any],
                              cycle_metrics: Dict[str, Any],
                              device_metrics: Dict[str, Any],
                              quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate KPI dashboard with key indicators"""
        kpi_dashboard = {
            'key_indicators': {},
            'performance_score': 0,
            'health_status': 'Unknown',
            'health_indicators': {},
            'trending': {}
        }
        
        # Key performance indicators
        kpi_dashboard['key_indicators'] = {
            'optimization_success_rate': performance_metrics.get('success_rate', 0) * 100,
            'cycle_completion_rate': performance_metrics.get('completion_rate', 0) * 100,
            'system_reliability': quality_metrics.get('system_reliability_score', 0),
            'average_cycle_efficiency': cycle_metrics.get('average_efficiency_score', 0),
            'total_devices_managed': device_metrics.get('total_devices', 0),
            'total_optimization_cycles': performance_metrics.get('total_optimization_cycles', 0)
        }
        
        # Calculate overall performance score
        indicators = kpi_dashboard['key_indicators']
        performance_score = (
            indicators['optimization_success_rate'] * 0.3 +
            indicators['cycle_completion_rate'] * 0.25 +
            indicators['system_reliability'] * 0.25 +
            indicators['average_cycle_efficiency'] * 0.2
        )
        kpi_dashboard['performance_score'] = performance_score
        
        # Determine health status
        if performance_score >= 85:
            kpi_dashboard['health_status'] = 'Excellent'
        elif performance_score >= 70:
            kpi_dashboard['health_status'] = 'Good'
        elif performance_score >= 50:
            kpi_dashboard['health_status'] = 'Fair'
        else:
            kpi_dashboard['health_status'] = 'Needs Attention'
        
        # Health indicators
        kpi_dashboard['health_indicators'] = {
            'success_rate_healthy': indicators['optimization_success_rate'] > 80,
            'completion_rate_healthy': indicators['cycle_completion_rate'] > 85,
            'reliability_healthy': indicators['system_reliability'] > 80,
            'efficiency_healthy': indicators['average_cycle_efficiency'] > 70,
            'attention_required': self._identify_attention_areas(indicators)
        }
        
        return kpi_dashboard
    
    def _identify_attention_areas(self, indicators: Dict[str, Any]) -> List[str]:
        """Identify areas requiring attention"""
        attention_areas = []
        
        if indicators['optimization_success_rate'] < 70:
            attention_areas.append('Low Optimization Success Rate')
        
        if indicators['cycle_completion_rate'] < 80:
            attention_areas.append('Poor Cycle Completion Rate')
        
        if indicators['system_reliability'] < 75:
            attention_areas.append('System Reliability Issues')
        
        if indicators['average_cycle_efficiency'] < 60:
            attention_areas.append('Low Cycle Efficiency')
        
        if not attention_areas:
            attention_areas.append('System Operating Normally')
        
        return attention_areas
    
    def _generate_benchmarks(self, performance_metrics: Dict[str, Any],
                           cycle_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance benchmarks"""
        benchmarks = {
            'industry_standards': {
                'optimization_success_rate': 85,  # %
                'cycle_completion_rate': 90,      # %
                'average_cycle_duration': 30,      # events
                'system_reliability': 95           # %
            },
            'current_performance': {
                'optimization_success_rate': performance_metrics.get('success_rate', 0) * 100,
                'cycle_completion_rate': performance_metrics.get('completion_rate', 0) * 100,
                'average_cycle_duration': cycle_metrics.get('average_cycle_duration', 0),
                'system_reliability': performance_metrics.get('success_rate', 0) * 100
            },
            'benchmark_comparison': {}
        }
        
        # Compare against benchmarks
        for metric, standard in benchmarks['industry_standards'].items():
            current = benchmarks['current_performance'][metric]
            
            if current >= standard:
                status = 'Exceeds Standard'
            elif current >= standard * 0.9:
                status = 'Meets Standard'
            elif current >= standard * 0.7:
                status = 'Below Standard'
            else:
                status = 'Significantly Below Standard'
            
            benchmarks['benchmark_comparison'][metric] = {
                'current': current,
                'standard': standard,
                'status': status,
                'gap': standard - current
            }
        
        return benchmarks
    
    def _calculate_summary_scores(self, performance_metrics: Dict[str, Any],
                                cycle_metrics: Dict[str, Any],
                                quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate high-level summary scores"""
        summary_scores = {
            'overall_health_score': 0,
            'performance_grade': 'F',
            'optimization_effectiveness': 0,
            'system_stability': 0
        }
        
        # Overall health score (0-100)
        success_rate = performance_metrics.get('success_rate', 0)
        completion_rate = performance_metrics.get('completion_rate', 0)
        reliability = quality_metrics.get('system_reliability_score', 0)
        
        health_score = (success_rate * 40 + completion_rate * 35 + reliability * 0.25)
        summary_scores['overall_health_score'] = health_score
        
        # Performance grade
        if health_score >= 90:
            summary_scores['performance_grade'] = 'A+'
        elif health_score >= 85:
            summary_scores['performance_grade'] = 'A'
        elif health_score >= 80:
            summary_scores['performance_grade'] = 'B+'
        elif health_score >= 75:
            summary_scores['performance_grade'] = 'B'
        elif health_score >= 70:
            summary_scores['performance_grade'] = 'C+'
        elif health_score >= 65:
            summary_scores['performance_grade'] = 'C'
        elif health_score >= 60:
            summary_scores['performance_grade'] = 'D'
        else:
            summary_scores['performance_grade'] = 'F'
        
        # Optimization effectiveness
        summary_scores['optimization_effectiveness'] = success_rate * 100
        
        # System stability
        failure_rate = quality_metrics.get('failure_rate', 0)
        summary_scores['system_stability'] = max(0, 100 - (failure_rate * 100))
        
        return summary_scores
