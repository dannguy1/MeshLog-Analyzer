"""
ACS Failure Analyzer Module

Detects and analyzes ACS failure patterns, error conditions,
and performance issues.
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics

class ACSFailureAnalyzer:
    """Analyzes ACS failure patterns and performance issues"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Failure tracking
        self.failure_incidents = []
        self.error_patterns = defaultdict(int)
        self.radio_failures = defaultdict(list)
        
        # Failure categories
        self.failure_types = {
            'scan_failures': [],
            'selection_failures': [],
            'switching_failures': [],
            'timeout_failures': [],
            'resource_failures': [],
            'interference_failures': [],
            'configuration_failures': []
        }
        
        # Error patterns to detect
        self.error_keywords = {
            'timeout': ['timeout', 'timed out', 'expired'],
            'resource': ['resource', 'memory', 'busy', 'unavailable'],
            'interference': ['interference', 'interfere', 'collision'],
            'configuration': ['config', 'invalid', 'unsupported'],
            'hardware': ['hardware', 'hw', 'radio', 'antenna'],
            'network': ['network', 'connection', 'unreachable']
        }
    
    def analyze_failures(self, events: List[Dict[str, Any]], cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze failures from events and cycles"""
        self.logger.info(f"Analyzing failures from {len(events)} events and {len(cycles)} cycles")
        
        # Reset analysis state
        self._reset_failure_state()
        
        # Analyze event-based failures
        self._analyze_event_failures(events)
        
        # Analyze cycle-based failures
        self._analyze_cycle_failures(cycles)
        
        # Generate failure analysis
        return self._generate_failure_analysis()
    
    def _reset_failure_state(self):
        """Reset failure analysis state"""
        self.failure_incidents.clear()
        self.error_patterns.clear()
        self.radio_failures.clear()
        for failure_type in self.failure_types:
            self.failure_types[failure_type].clear()
    
    def _analyze_event_failures(self, events: List[Dict[str, Any]]) -> None:
        """Analyze failure events"""
        for event in events:
            event_type = event.get('event_type', '').lower()
            raw_line = event.get('raw_line', '').lower()
            
            # Check for failure indicators
            if self._is_failure_event(event):
                self._process_failure_event(event)
    
    def _analyze_cycle_failures(self, cycles: List[Dict[str, Any]]) -> None:
        """Analyze failed cycles"""
        for cycle in cycles:
            if cycle.get('status') in ['failed', 'incomplete']:
                self._process_failed_cycle(cycle)
    
    def _is_failure_event(self, event: Dict[str, Any]) -> bool:
        """Check if event indicates a failure"""
        event_type = event.get('event_type', '').lower()
        raw_line = event.get('raw_line', '').lower()
        reason = event.get('reason', '').lower()
        
        failure_indicators = [
            'error', 'fail', 'abort', 'timeout', 'invalid', 
            'unable', 'cannot', 'denied', 'refused', 'rejected'
        ]
        
        text_to_check = f"{event_type} {raw_line} {reason}"
        return any(indicator in text_to_check for indicator in failure_indicators)
    
    def _process_failure_event(self, event: Dict[str, Any]) -> None:
        """Process a failure event"""
        radio = event.get('radio', 'unknown')
        timestamp = event.get('timestamp', '')
        event_type = event.get('event_type', '')
        raw_line = event.get('raw_line', '')
        reason = event.get('reason', '')
        
        # Create failure incident
        incident = {
            'timestamp': timestamp,
            'radio': radio,
            'event_type': event_type,
            'reason': reason,
            'raw_line': raw_line,
            'failure_category': self._categorize_failure(event),
            'severity': self._assess_failure_severity(event),
            'source': 'event'
        }
        
        self.failure_incidents.append(incident)
        self.radio_failures[radio].append(incident)
        
        # Update error patterns
        self._update_error_patterns(event)
        
        # Categorize failure
        self._categorize_failure_type(incident)
    
    def _process_failed_cycle(self, cycle: Dict[str, Any]) -> None:
        """Process a failed cycle"""
        radio = cycle.get('radio', 'unknown')
        start_time = cycle.get('start_time', '')
        status = cycle.get('status', 'failed')
        
        # Create failure incident from cycle
        incident = {
            'timestamp': start_time,
            'radio': radio,
            'event_type': f'cycle_{status}',
            'reason': f'Cycle {status} after {cycle.get("duration_seconds", 0)}s',
            'raw_line': f'Cycle with {cycle.get("event_count", 0)} events',
            'failure_category': 'cycle_failure',
            'severity': 'high' if status == 'failed' else 'medium',
            'source': 'cycle',
            'cycle_data': cycle
        }
        
        self.failure_incidents.append(incident)
        self.radio_failures[radio].append(incident)
        
        # Categorize cycle failure
        self._categorize_failure_type(incident)
    
    def _categorize_failure(self, event: Dict[str, Any]) -> str:
        """Categorize the type of failure"""
        event_type = event.get('event_type', '').lower()
        raw_line = event.get('raw_line', '').lower()
        reason = event.get('reason', '').lower()
        
        text_to_check = f"{event_type} {raw_line} {reason}"
        
        # Check against error keyword categories
        for category, keywords in self.error_keywords.items():
            if any(keyword in text_to_check for keyword in keywords):
                return category
        
        # Default categorization based on event type
        if 'scan' in event_type:
            return 'scan_failure'
        elif 'select' in event_type or 'choice' in event_type:
            return 'selection_failure'
        elif 'switch' in event_type or 'change' in event_type:
            return 'switching_failure'
        else:
            return 'general_failure'
    
    def _assess_failure_severity(self, event: Dict[str, Any]) -> str:
        """Assess the severity of a failure"""
        event_type = event.get('event_type', '').lower()
        raw_line = event.get('raw_line', '').lower()
        
        # High severity indicators
        high_severity = ['critical', 'fatal', 'emergency', 'panic', 'abort']
        if any(indicator in f"{event_type} {raw_line}" for indicator in high_severity):
            return 'critical'
        
        # Medium severity indicators
        medium_severity = ['error', 'fail', 'timeout', 'unable']
        if any(indicator in f"{event_type} {raw_line}" for indicator in medium_severity):
            return 'high'
        
        # Low severity indicators
        low_severity = ['warning', 'retry', 'fallback']
        if any(indicator in f"{event_type} {raw_line}" for indicator in low_severity):
            return 'medium'
        
        return 'low'
    
    def _update_error_patterns(self, event: Dict[str, Any]) -> None:
        """Update error pattern tracking"""
        event_type = event.get('event_type', '')
        reason = event.get('reason', '')
        
        # Track by event type
        self.error_patterns[event_type] += 1
        
        # Track by reason if available
        if reason:
            self.error_patterns[f"reason:{reason}"] += 1
    
    def _categorize_failure_type(self, incident: Dict[str, Any]) -> None:
        """Categorize failure into specific type buckets"""
        category = incident['failure_category']
        
        if category == 'timeout' or 'timeout' in incident['event_type']:
            self.failure_types['timeout_failures'].append(incident)
        elif category in ['resource', 'hardware']:
            self.failure_types['resource_failures'].append(incident)
        elif category == 'interference':
            self.failure_types['interference_failures'].append(incident)
        elif category == 'configuration':
            self.failure_types['configuration_failures'].append(incident)
        elif 'scan' in incident['event_type']:
            self.failure_types['scan_failures'].append(incident)
        elif any(keyword in incident['event_type'] for keyword in ['select', 'choice']):
            self.failure_types['selection_failures'].append(incident)
        elif any(keyword in incident['event_type'] for keyword in ['switch', 'change']):
            self.failure_types['switching_failures'].append(incident)
    
    def _generate_failure_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive failure analysis"""
        total_failures = len(self.failure_incidents)
        
        if total_failures == 0:
            return {
                'failure_summary': {
                    'total_failures': 0,
                    'failure_rate': 0.0,
                    'most_common_failure': 'None',
                    'most_affected_radio': 'None'
                },
                'failure_breakdown': {},
                'failure_patterns': {},
                'radio_analysis': {},
                'recommendations': ['No failures detected - ACS system operating normally']
            }
        
        return {
            'failure_summary': self._generate_failure_summary(),
            'failure_breakdown': self._generate_failure_breakdown(),
            'failure_patterns': self._analyze_failure_patterns(),
            'radio_analysis': self._analyze_radio_failures(),
            'temporal_analysis': self._analyze_temporal_failures(),
            'severity_analysis': self._analyze_failure_severity(),
            'recommendations': self._generate_failure_recommendations()
        }
    
    def _generate_failure_summary(self) -> Dict[str, Any]:
        """Generate failure summary statistics"""
        total_failures = len(self.failure_incidents)
        
        # Most common failure type
        failure_categories = [incident['failure_category'] for incident in self.failure_incidents]
        category_counts = defaultdict(int)
        for category in failure_categories:
            category_counts[category] += 1
        
        most_common = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else 'None'
        
        # Most affected radio
        radio_counts = defaultdict(int)
        for radio, failures in self.radio_failures.items():
            radio_counts[radio] = len(failures)
        
        most_affected = max(radio_counts.items(), key=lambda x: x[1])[0] if radio_counts else 'None'
        
        return {
            'total_failures': total_failures,
            'unique_radios_affected': len(self.radio_failures),
            'most_common_failure': most_common,
            'most_affected_radio': most_affected,
            'average_failures_per_radio': round(total_failures / max(1, len(self.radio_failures)), 1)
        }
    
    def _generate_failure_breakdown(self) -> Dict[str, Any]:
        """Generate breakdown of failure types"""
        breakdown = {}
        
        for failure_type, incidents in self.failure_types.items():
            if incidents:
                breakdown[failure_type] = {
                    'count': len(incidents),
                    'percentage': round((len(incidents) / len(self.failure_incidents)) * 100, 1),
                    'example_incidents': [
                        {
                            'timestamp': incident['timestamp'],
                            'radio': incident['radio'],
                            'reason': incident['reason']
                        }
                        for incident in incidents[:3]  # First 3 examples
                    ]
                }
        
        return breakdown
    
    def _analyze_failure_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in failures"""
        # Error pattern analysis
        top_patterns = sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Timing patterns
        timestamps = [incident['timestamp'] for incident in self.failure_incidents if incident['timestamp']]
        
        # Severity patterns
        severity_counts = defaultdict(int)
        for incident in self.failure_incidents:
            severity_counts[incident['severity']] += 1
        
        return {
            'top_error_patterns': dict(top_patterns),
            'severity_distribution': dict(severity_counts),
            'failure_frequency': self._calculate_failure_frequency(timestamps),
            'common_failure_sequences': self._find_failure_sequences()
        }
    
    def _analyze_radio_failures(self) -> Dict[str, Any]:
        """Analyze failures by radio"""
        radio_analysis = {}
        
        for radio, failures in self.radio_failures.items():
            if failures:
                # Failure types for this radio
                categories = [f['failure_category'] for f in failures]
                category_counts = defaultdict(int)
                for category in categories:
                    category_counts[category] += 1
                
                # Severity distribution
                severities = [f['severity'] for f in failures]
                severity_counts = defaultdict(int)
                for severity in severities:
                    severity_counts[severity] += 1
                
                radio_analysis[radio] = {
                    'total_failures': len(failures),
                    'failure_categories': dict(category_counts),
                    'severity_distribution': dict(severity_counts),
                    'most_common_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else 'None',
                    'first_failure': failures[0]['timestamp'] if failures else None,
                    'last_failure': failures[-1]['timestamp'] if failures else None
                }
        
        return radio_analysis
    
    def _analyze_temporal_failures(self) -> Dict[str, Any]:
        """Analyze temporal patterns in failures"""
        timestamps = [incident['timestamp'] for incident in self.failure_incidents if incident['timestamp']]
        
        if not timestamps:
            return {}
        
        timestamps.sort()
        
        return {
            'first_failure': timestamps[0],
            'last_failure': timestamps[-1],
            'failure_timespan': f"{timestamps[0]} to {timestamps[-1]}",
            'failures_per_hour': self._calculate_failures_per_hour(timestamps)
        }
    
    def _analyze_failure_severity(self) -> Dict[str, Any]:
        """Analyze failure severity distribution"""
        severity_counts = defaultdict(int)
        severity_by_radio = defaultdict(lambda: defaultdict(int))
        
        for incident in self.failure_incidents:
            severity = incident['severity']
            radio = incident['radio']
            
            severity_counts[severity] += 1
            severity_by_radio[radio][severity] += 1
        
        return {
            'overall_severity': dict(severity_counts),
            'severity_by_radio': {radio: dict(severities) for radio, severities in severity_by_radio.items()},
            'critical_failure_count': severity_counts.get('critical', 0),
            'high_failure_count': severity_counts.get('high', 0)
        }
    
    def _calculate_failure_frequency(self, timestamps: List[str]) -> Dict[str, Any]:
        """Calculate failure frequency metrics"""
        if len(timestamps) < 2:
            return {'frequency': 'Insufficient data'}
        
        try:
            from datetime import datetime
            dt_timestamps = []
            for ts in timestamps:
                try:
                    dt = datetime.fromisoformat(ts.replace(' ', 'T'))
                    dt_timestamps.append(dt)
                except:
                    continue
            
            if len(dt_timestamps) < 2:
                return {'frequency': 'Invalid timestamps'}
            
            dt_timestamps.sort()
            total_duration = (dt_timestamps[-1] - dt_timestamps[0]).total_seconds()
            hours = total_duration / 3600
            
            return {
                'failures_per_hour': round(len(dt_timestamps) / max(hours, 1), 2),
                'average_interval_seconds': round(total_duration / max(len(dt_timestamps) - 1, 1), 1),
                'total_duration_hours': round(hours, 2)
            }
        except Exception as e:
            return {'frequency': f'Calculation error: {str(e)}'}
    
    def _calculate_failures_per_hour(self, timestamps: List[str]) -> float:
        """Calculate failures per hour"""
        freq_data = self._calculate_failure_frequency(timestamps)
        return freq_data.get('failures_per_hour', 0.0)
    
    def _find_failure_sequences(self) -> List[Dict[str, Any]]:
        """Find common sequences of failures"""
        # Group failures by radio and look for sequences
        sequences = []
        
        for radio, failures in self.radio_failures.items():
            if len(failures) >= 2:
                # Sort by timestamp
                sorted_failures = sorted(failures, key=lambda x: x['timestamp'])
                
                # Look for consecutive failure patterns
                for i in range(len(sorted_failures) - 1):
                    current = sorted_failures[i]
                    next_failure = sorted_failures[i + 1]
                    
                    sequence = {
                        'radio': radio,
                        'first_failure': current['failure_category'],
                        'second_failure': next_failure['failure_category'],
                        'time_between': self._calculate_time_between(current['timestamp'], next_failure['timestamp'])
                    }
                    sequences.append(sequence)
        
        return sequences[:5]  # Return top 5 sequences
    
    def _calculate_time_between(self, timestamp1: str, timestamp2: str) -> str:
        """Calculate time between two timestamps"""
        try:
            from datetime import datetime
            dt1 = datetime.fromisoformat(timestamp1.replace(' ', 'T'))
            dt2 = datetime.fromisoformat(timestamp2.replace(' ', 'T'))
            delta = dt2 - dt1
            return f"{delta.total_seconds():.0f} seconds"
        except:
            return "Unknown"
    
    def _generate_failure_recommendations(self) -> List[str]:
        """Generate recommendations based on failure analysis"""
        recommendations = []
        total_failures = len(self.failure_incidents)
        
        if total_failures == 0:
            recommendations.append("No failures detected - system operating normally")
            return recommendations
        
        # General failure rate recommendations
        if total_failures > 10:
            recommendations.append(f"High failure count ({total_failures}) detected - investigate root causes")
        
        # Failure type specific recommendations
        for failure_type, incidents in self.failure_types.items():
            if len(incidents) > total_failures * 0.3:  # More than 30% of failures
                if failure_type == 'timeout_failures':
                    recommendations.append("Frequent timeout failures - consider increasing scan timeouts")
                elif failure_type == 'resource_failures':
                    recommendations.append("Resource failures detected - check system load and memory")
                elif failure_type == 'interference_failures':
                    recommendations.append("Interference failures - analyze RF environment")
                elif failure_type == 'configuration_failures':
                    recommendations.append("Configuration failures - review ACS settings")
        
        # Radio-specific recommendations
        for radio, failures in self.radio_failures.items():
            if len(failures) > total_failures * 0.5:  # One radio has >50% of failures
                recommendations.append(f"Radio {radio} has excessive failures - check hardware and configuration")
        
        # Severity-based recommendations
        critical_failures = sum(1 for incident in self.failure_incidents if incident['severity'] == 'critical')
        if critical_failures > 0:
            recommendations.append(f"{critical_failures} critical failures detected - immediate attention required")
        
        return recommendations
    
    def get_failure_incidents(self) -> List[Dict[str, Any]]:
        """Get all failure incidents"""
        return self.failure_incidents
    
    def get_radio_failures(self, radio: str) -> List[Dict[str, Any]]:
        """Get failures for a specific radio"""
        return self.radio_failures.get(radio, [])
    
    def get_failure_count(self) -> int:
        """Get total failure count"""
        return len(self.failure_incidents)
