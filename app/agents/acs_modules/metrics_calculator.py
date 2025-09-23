"""
ACS Metrics Calculator Module

Calculates performance metrics, statistics, and KPIs for ACS analysis.
"""

import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta

class ACSMetricsCalculator:
    """Calculates comprehensive metrics for ACS performance analysis"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Metric categories
        self.performance_metrics = {}
        self.efficiency_metrics = {}
        self.reliability_metrics = {}
        self.temporal_metrics = {}
        
    def calculate_metrics(self, events: List[Dict[str, Any]], cycles: List[Dict[str, Any]], 
                         analysis_data: Dict[str, Any], failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive ACS metrics"""
        self.logger.info(f"Calculating metrics for {len(events)} events, {len(cycles)} cycles, {len(failures)} failures")
        
        # Calculate different metric categories
        self.performance_metrics = self._calculate_performance_metrics(events, cycles)
        self.efficiency_metrics = self._calculate_efficiency_metrics(cycles, analysis_data)
        self.reliability_metrics = self._calculate_reliability_metrics(cycles, failures)
        self.temporal_metrics = self._calculate_temporal_metrics(events, cycles)
        
        # Generate overall metrics summary
        return {
            'performance_metrics': self.performance_metrics,
            'efficiency_metrics': self.efficiency_metrics,
            'reliability_metrics': self.reliability_metrics,
            'temporal_metrics': self.temporal_metrics,
            'summary_scores': self._calculate_summary_scores(),
            'kpi_dashboard': self._generate_kpi_dashboard()
        }
    
    def _calculate_performance_metrics(self, events: List[Dict[str, Any]], 
                                     cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance-related metrics"""
        if not events and not cycles:
            return {'error': 'No data available for performance calculation'}
        
        # Cycle performance metrics
        completed_cycles = [c for c in cycles if c.get('status') == 'completed']
        failed_cycles = [c for c in cycles if c.get('status') == 'failed']
        incomplete_cycles = [c for c in cycles if c.get('status') == 'incomplete']
        
        total_cycles = len(cycles)
        success_rate = (len(completed_cycles) / max(1, total_cycles)) * 100
        
        # Duration metrics
        durations = [c.get('duration_seconds', 0) for c in completed_cycles if c.get('duration_seconds', 0) > 0]
        avg_duration = statistics.mean(durations) if durations else 0
        median_duration = statistics.median(durations) if durations else 0
        
        # Event processing metrics
        event_count = len(events)
        events_per_cycle = event_count / max(1, total_cycles)
        
        return {
            'cycle_success_rate': round(success_rate, 2),
            'total_cycles': total_cycles,
            'completed_cycles': len(completed_cycles),
            'failed_cycles': len(failed_cycles),
            'incomplete_cycles': len(incomplete_cycles),
            'average_cycle_duration': round(avg_duration, 2),
            'median_cycle_duration': round(median_duration, 2),
            'fastest_cycle': min(durations) if durations else 0,
            'slowest_cycle': max(durations) if durations else 0,
            'total_events': event_count,
            'events_per_cycle': round(events_per_cycle, 2),
            'duration_statistics': self._calculate_duration_statistics(durations)
        }
    
    def _calculate_efficiency_metrics(self, cycles: List[Dict[str, Any]], 
                                    analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate efficiency-related metrics"""
        if not cycles:
            return {'error': 'No cycles available for efficiency calculation'}
        
        # FSM efficiency
        fsm_data = analysis_data.get('fsm_analysis', {})
        state_transitions = fsm_data.get('total_state_changes', 0)
        completed_cycles = len([c for c in cycles if c.get('status') == 'completed'])
        
        fsm_efficiency = (completed_cycles / max(1, state_transitions)) * 100 if state_transitions > 0 else 0
        
        # Resource utilization
        radio_data = analysis_data.get('radio_analysis', {})
        total_radios = radio_data.get('total_radios', 1)
        active_radios = radio_data.get('active_radios', 0)
        radio_utilization = (active_radios / max(1, total_radios)) * 100
        
        # Optimization effectiveness
        channel_switches = self._count_channel_switches(cycles)
        optimization_ratio = channel_switches / max(1, len(cycles))
        
        # Time efficiency
        durations = [c.get('duration_seconds', 0) for c in cycles if c.get('duration_seconds', 0) > 0]
        time_efficiency = self._calculate_time_efficiency(durations)
        
        return {
            'fsm_efficiency': round(fsm_efficiency, 2),
            'radio_utilization': round(radio_utilization, 2),
            'optimization_ratio': round(optimization_ratio, 2),
            'time_efficiency': time_efficiency,
            'state_transition_efficiency': self._calculate_state_efficiency(fsm_data),
            'resource_efficiency': self._calculate_resource_efficiency(analysis_data)
        }
    
    def _calculate_reliability_metrics(self, cycles: List[Dict[str, Any]], 
                                     failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate reliability-related metrics"""
        total_cycles = len(cycles)
        total_failures = len(failures)
        
        if total_cycles == 0:
            return {'error': 'No cycles available for reliability calculation'}
        
        # Basic reliability metrics
        failure_rate = (total_failures / max(1, total_cycles)) * 100
        mtbf = self._calculate_mtbf(cycles, failures)
        
        # Availability metrics
        completed_cycles = len([c for c in cycles if c.get('status') == 'completed'])
        availability = (completed_cycles / total_cycles) * 100
        
        # Failure pattern analysis
        failure_severity = self._analyze_failure_severity(failures)
        
        # Recovery metrics
        recovery_time = self._calculate_recovery_time(cycles, failures)
        
        return {
            'failure_rate': round(failure_rate, 2),
            'availability': round(availability, 2),
            'mtbf_cycles': round(mtbf, 2),
            'total_failures': total_failures,
            'failure_severity_distribution': failure_severity,
            'recovery_metrics': recovery_time,
            'reliability_score': self._calculate_reliability_score(failure_rate, availability)
        }
    
    def _calculate_temporal_metrics(self, events: List[Dict[str, Any]], 
                                  cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate temporal pattern metrics"""
        if not events and not cycles:
            return {'error': 'No data available for temporal analysis'}
        
        # Extract timestamps
        event_timestamps = [e.get('timestamp', '') for e in events if e.get('timestamp')]
        cycle_timestamps = [c.get('start_time', '') for c in cycles if c.get('start_time')]
        
        all_timestamps = event_timestamps + cycle_timestamps
        if not all_timestamps:
            return {'error': 'No valid timestamps found'}
        
        # Convert to datetime objects
        dt_timestamps = []
        for ts in all_timestamps:
            try:
                dt = datetime.fromisoformat(ts.replace(' ', 'T'))
                dt_timestamps.append(dt)
            except:
                continue
        
        if not dt_timestamps:
            return {'error': 'No parseable timestamps found'}
        
        dt_timestamps.sort()
        
        # Calculate temporal metrics
        total_duration = (dt_timestamps[-1] - dt_timestamps[0]).total_seconds()
        hours = total_duration / 3600
        
        # Activity distribution
        activity_distribution = self._calculate_activity_distribution(dt_timestamps)
        
        # Peak activity periods
        peak_periods = self._identify_peak_periods(dt_timestamps)
        
        return {
            'analysis_timespan': {
                'start_time': dt_timestamps[0].isoformat(),
                'end_time': dt_timestamps[-1].isoformat(),
                'duration_hours': round(hours, 2),
                'duration_days': round(hours / 24, 2)
            },
            'activity_metrics': {
                'events_per_hour': round(len(event_timestamps) / max(hours, 1), 2),
                'cycles_per_hour': round(len(cycle_timestamps) / max(hours, 1), 2),
                'peak_activity_hour': peak_periods.get('peak_hour', 'Unknown'),
                'activity_distribution': activity_distribution
            },
            'temporal_patterns': {
                'busiest_period': peak_periods.get('busiest_period', 'Unknown'),
                'activity_variance': self._calculate_activity_variance(dt_timestamps),
                'temporal_clustering': self._analyze_temporal_clustering(dt_timestamps)
            }
        }
    
    def _calculate_duration_statistics(self, durations: List[float]) -> Dict[str, float]:
        """Calculate statistical metrics for durations"""
        if not durations:
            return {}
        
        return {
            'mean': round(statistics.mean(durations), 2),
            'median': round(statistics.median(durations), 2),
            'std_dev': round(statistics.stdev(durations), 2) if len(durations) > 1 else 0,
            'variance': round(statistics.variance(durations), 2) if len(durations) > 1 else 0,
            'min': round(min(durations), 2),
            'max': round(max(durations), 2),
            'q25': round(statistics.quantiles(durations, n=4)[0], 2) if len(durations) >= 4 else 0,
            'q75': round(statistics.quantiles(durations, n=4)[2], 2) if len(durations) >= 4 else 0
        }
    
    def _count_channel_switches(self, cycles: List[Dict[str, Any]]) -> int:
        """Count successful channel switches"""
        switches = 0
        for cycle in cycles:
            if cycle.get('status') == 'completed':
                # Look for channel changes in cycle events
                events = cycle.get('events', [])
                for event in events:
                    if 'channel' in event.get('event_type', '').lower():
                        switches += 1
                        break
        return switches
    
    def _calculate_time_efficiency(self, durations: List[float]) -> Dict[str, Any]:
        """Calculate time efficiency metrics"""
        if not durations:
            return {'score': 0, 'category': 'No data'}
        
        avg_duration = statistics.mean(durations)
        
        # Define efficiency categories based on average duration
        if avg_duration < 30:
            efficiency_score = 95
            category = 'Excellent'
        elif avg_duration < 60:
            efficiency_score = 85
            category = 'Good'
        elif avg_duration < 120:
            efficiency_score = 70
            category = 'Fair'
        elif avg_duration < 300:
            efficiency_score = 50
            category = 'Poor'
        else:
            efficiency_score = 25
            category = 'Very Poor'
        
        return {
            'score': efficiency_score,
            'category': category,
            'average_duration': round(avg_duration, 2),
            'efficiency_rating': f"{efficiency_score}/100"
        }
    
    def _calculate_state_efficiency(self, fsm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate FSM state transition efficiency"""
        total_transitions = fsm_data.get('total_state_changes', 0)
        unique_states = fsm_data.get('unique_states', 0)
        
        if total_transitions == 0:
            return {'score': 0, 'description': 'No state transitions'}
        
        # Efficiency based on state usage vs transitions
        efficiency = (unique_states / total_transitions) * 100 if total_transitions > 0 else 0
        
        return {
            'score': round(efficiency, 2),
            'total_transitions': total_transitions,
            'unique_states': unique_states,
            'transition_efficiency': round(efficiency, 2)
        }
    
    def _calculate_resource_efficiency(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate resource utilization efficiency"""
        radio_data = analysis_data.get('radio_analysis', {})
        event_data = analysis_data.get('event_distribution', {})
        
        # Radio efficiency
        total_radios = radio_data.get('total_radios', 1)
        active_radios = radio_data.get('active_radios', 0)
        radio_efficiency = (active_radios / total_radios) * 100 if total_radios > 0 else 0
        
        # Event processing efficiency
        total_events = sum(event_data.values()) if event_data else 0
        meaningful_events = event_data.get('state_transitions', 0) + event_data.get('selection_events', 0)
        event_efficiency = (meaningful_events / max(1, total_events)) * 100
        
        return {
            'radio_efficiency': round(radio_efficiency, 2),
            'event_efficiency': round(event_efficiency, 2),
            'overall_resource_efficiency': round((radio_efficiency + event_efficiency) / 2, 2)
        }
    
    def _calculate_mtbf(self, cycles: List[Dict[str, Any]], failures: List[Dict[str, Any]]) -> float:
        """Calculate Mean Time Between Failures in cycle units"""
        total_cycles = len(cycles)
        total_failures = len(failures)
        
        if total_failures == 0:
            return float('inf')  # No failures
        
        return total_cycles / total_failures
    
    def _analyze_failure_severity(self, failures: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze failure severity distribution"""
        severity_counts = defaultdict(int)
        for failure in failures:
            severity = failure.get('severity', 'unknown')
            severity_counts[severity] += 1
        
        return dict(severity_counts)
    
    def _calculate_recovery_time(self, cycles: List[Dict[str, Any]], 
                               failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate recovery time metrics"""
        # This is a simplified calculation - in practice would need more sophisticated failure tracking
        failed_cycles = [c for c in cycles if c.get('status') == 'failed']
        
        if not failed_cycles:
            return {'average_recovery_time': 0, 'recovery_success_rate': 100}
        
        recovery_times = []
        for failed_cycle in failed_cycles:
            duration = failed_cycle.get('duration_seconds', 0)
            if duration > 0:
                recovery_times.append(duration)
        
        avg_recovery = statistics.mean(recovery_times) if recovery_times else 0
        
        return {
            'average_recovery_time': round(avg_recovery, 2),
            'failed_cycle_count': len(failed_cycles),
            'recovery_attempts': len(recovery_times)
        }
    
    def _calculate_reliability_score(self, failure_rate: float, availability: float) -> Dict[str, Any]:
        """Calculate overall reliability score"""
        # Weighted score: 60% availability, 40% inverse failure rate
        failure_score = max(0, 100 - failure_rate)
        reliability_score = (availability * 0.6) + (failure_score * 0.4)
        
        if reliability_score >= 90:
            grade = 'A'
            description = 'Excellent'
        elif reliability_score >= 80:
            grade = 'B'
            description = 'Good'
        elif reliability_score >= 70:
            grade = 'C'
            description = 'Fair'
        elif reliability_score >= 60:
            grade = 'D'
            description = 'Poor'
        else:
            grade = 'F'
            description = 'Very Poor'
        
        return {
            'score': round(reliability_score, 2),
            'grade': grade,
            'description': description,
            'components': {
                'availability': round(availability, 2),
                'failure_resistance': round(failure_score, 2)
            }
        }
    
    def _calculate_activity_distribution(self, timestamps: List[datetime]) -> Dict[str, int]:
        """Calculate activity distribution by hour of day"""
        hourly_activity = defaultdict(int)
        
        for ts in timestamps:
            hour = ts.hour
            hourly_activity[hour] += 1
        
        return dict(hourly_activity)
    
    def _identify_peak_periods(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Identify peak activity periods"""
        hourly_activity = self._calculate_activity_distribution(timestamps)
        
        if not hourly_activity:
            return {}
        
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])
        
        # Identify busiest 4-hour period
        hour_counts = [(hour, count) for hour, count in hourly_activity.items()]
        hour_counts.sort()
        
        best_period_start = 0
        best_period_count = 0
        
        for start_hour in range(0, 24, 4):
            period_count = sum(count for hour, count in hour_counts if start_hour <= hour < start_hour + 4)
            if period_count > best_period_count:
                best_period_count = period_count
                best_period_start = start_hour
        
        return {
            'peak_hour': f"{peak_hour[0]:02d}:00 ({peak_hour[1]} events)",
            'busiest_period': f"{best_period_start:02d}:00-{(best_period_start + 4) % 24:02d}:00 ({best_period_count} events)"
        }
    
    def _calculate_activity_variance(self, timestamps: List[datetime]) -> float:
        """Calculate variance in activity levels"""
        hourly_activity = self._calculate_activity_distribution(timestamps)
        activity_counts = list(hourly_activity.values())
        
        if len(activity_counts) <= 1:
            return 0.0
        
        return round(statistics.variance(activity_counts), 2)
    
    def _analyze_temporal_clustering(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyze temporal clustering of events"""
        if len(timestamps) < 2:
            return {'clustering': 'Insufficient data'}
        
        # Calculate intervals between consecutive events
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return {'clustering': 'No intervals'}
        
        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        
        # Clustering indicator: low std relative to mean indicates regular spacing
        if avg_interval > 0:
            clustering_coefficient = std_interval / avg_interval
        else:
            clustering_coefficient = 0
        
        if clustering_coefficient < 0.5:
            clustering_type = 'Regular'
        elif clustering_coefficient < 1.0:
            clustering_type = 'Moderate'
        else:
            clustering_type = 'Random'
        
        return {
            'clustering_type': clustering_type,
            'clustering_coefficient': round(clustering_coefficient, 3),
            'average_interval': round(avg_interval, 2),
            'interval_std_dev': round(std_interval, 2)
        }
    
    def _calculate_summary_scores(self) -> Dict[str, Any]:
        """Calculate overall summary scores"""
        # Extract key metrics for scoring
        performance_score = self._score_performance()
        efficiency_score = self._score_efficiency()
        reliability_score = self._score_reliability()
        
        # Overall system score (weighted average)
        overall_score = (performance_score * 0.4 + efficiency_score * 0.3 + reliability_score * 0.3)
        
        return {
            'overall_score': round(overall_score, 1),
            'performance_score': round(performance_score, 1),
            'efficiency_score': round(efficiency_score, 1),
            'reliability_score': round(reliability_score, 1),
            'score_breakdown': {
                'performance_weight': '40%',
                'efficiency_weight': '30%',
                'reliability_weight': '30%'
            },
            'grade': self._get_score_grade(overall_score)
        }
    
    def _score_performance(self) -> float:
        """Score performance metrics (0-100)"""
        perf = self.performance_metrics
        
        if 'error' in perf:
            return 0
        
        success_rate = perf.get('cycle_success_rate', 0)
        avg_duration = perf.get('average_cycle_duration', 300)  # Default to 5 minutes
        
        # Score based on success rate (60%) and duration efficiency (40%)
        success_score = success_rate  # Already 0-100
        
        # Duration score: better for shorter durations
        if avg_duration <= 30:
            duration_score = 100
        elif avg_duration <= 60:
            duration_score = 80
        elif avg_duration <= 120:
            duration_score = 60
        elif avg_duration <= 300:
            duration_score = 40
        else:
            duration_score = 20
        
        return (success_score * 0.6) + (duration_score * 0.4)
    
    def _score_efficiency(self) -> float:
        """Score efficiency metrics (0-100)"""
        eff = self.efficiency_metrics
        
        if 'error' in eff:
            return 0
        
        fsm_efficiency = eff.get('fsm_efficiency', 0)
        radio_utilization = eff.get('radio_utilization', 0)
        time_efficiency = eff.get('time_efficiency', {}).get('score', 0)
        
        # Weighted average of efficiency components
        return (fsm_efficiency * 0.3) + (radio_utilization * 0.3) + (time_efficiency * 0.4)
    
    def _score_reliability(self) -> float:
        """Score reliability metrics (0-100)"""
        rel = self.reliability_metrics
        
        if 'error' in rel:
            return 0
        
        reliability_score = rel.get('reliability_score', {}).get('score', 0)
        return reliability_score
    
    def _get_score_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_kpi_dashboard(self) -> Dict[str, Any]:
        """Generate key performance indicators dashboard"""
        perf = self.performance_metrics
        eff = self.efficiency_metrics
        rel = self.reliability_metrics
        temp = self.temporal_metrics
        
        return {
            'key_indicators': {
                'success_rate': f"{perf.get('cycle_success_rate', 0):.1f}%",
                'average_duration': f"{perf.get('average_cycle_duration', 0):.1f}s",
                'failure_rate': f"{rel.get('failure_rate', 0):.1f}%",
                'availability': f"{rel.get('availability', 0):.1f}%",
                'efficiency_score': f"{eff.get('time_efficiency', {}).get('score', 0)}/100"
            },
            'operational_metrics': {
                'total_cycles': perf.get('total_cycles', 0),
                'completed_cycles': perf.get('completed_cycles', 0),
                'active_radios': eff.get('radio_utilization', 0),
                'analysis_duration': temp.get('analysis_timespan', {}).get('duration_hours', 0)
            },
            'health_indicators': {
                'system_health': self._assess_system_health(),
                'performance_trend': self._assess_performance_trend(),
                'attention_required': self._identify_attention_areas()
            }
        }
    
    def _assess_system_health(self) -> str:
        """Assess overall system health"""
        summary_scores = self._calculate_summary_scores()
        overall_score = summary_scores.get('overall_score', 0)
        
        if overall_score >= 85:
            return 'Excellent'
        elif overall_score >= 70:
            return 'Good'
        elif overall_score >= 55:
            return 'Fair'
        elif overall_score >= 40:
            return 'Poor'
        else:
            return 'Critical'
    
    def _assess_performance_trend(self) -> str:
        """Assess performance trend (simplified)"""
        success_rate = self.performance_metrics.get('cycle_success_rate', 0)
        
        if success_rate >= 90:
            return 'Stable High'
        elif success_rate >= 70:
            return 'Stable Medium'
        else:
            return 'Needs Attention'
    
    def _identify_attention_areas(self) -> List[str]:
        """Identify areas requiring attention"""
        attention_areas = []
        
        # Check performance
        success_rate = self.performance_metrics.get('cycle_success_rate', 0)
        if success_rate < 70:
            attention_areas.append('Low Success Rate')
        
        # Check efficiency
        time_efficiency = self.efficiency_metrics.get('time_efficiency', {}).get('score', 0)
        if time_efficiency < 60:
            attention_areas.append('Slow Performance')
        
        # Check reliability
        failure_rate = self.reliability_metrics.get('failure_rate', 0)
        if failure_rate > 20:
            attention_areas.append('High Failure Rate')
        
        return attention_areas if attention_areas else ['System Operating Normally']
