"""
TPYOPT Failure Analyzer Module

Analyzes TPYOPT failures including optimization failures, topology build issues,
roaming command failures, and performance degradation patterns.
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import statistics


class TPYOPTFailureAnalyzer:
    """TPYOPT failure detection and analysis"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
        # Failure classification thresholds
        self.packet_loss_threshold = 20  # % packet loss
        self.high_packet_loss_threshold = 30
        self.cycle_failure_timeout = 300  # seconds
        self.max_retries_threshold = 3
        
        # Failure categories
        self.failure_categories = {
            'optimization_failures': [],
            'topology_failures': [],
            'roaming_failures': [],
            'algorithm_failures': [],
            'timeout_failures': [],
            'coordination_failures': []
        }
    
    def analyze_failures(self, events: List[Dict[str, Any]], cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive TPYOPT failure analysis"""
        self.logger.info("Analyzing TPYOPT failures and performance issues")
        
        # Reset failure data
        for category in self.failure_categories:
            self.failure_categories[category].clear()
        
        # Analyze different types of failures
        optimization_failures = self._analyze_optimization_failures(cycles)
        topology_failures = self._analyze_topology_failures(events)
        roaming_failures = self._analyze_roaming_failures(events)
        algorithm_failures = self._analyze_algorithm_failures(events, cycles)
        timeout_failures = self._analyze_timeout_failures(cycles)
        coordination_failures = self._analyze_coordination_failures(events)
        
        # Generate failure summary
        failure_summary = self._generate_failure_summary()
        failure_patterns = self._analyze_failure_patterns()
        severity_assessment = self._assess_failure_severity()
        
        return {
            'failure_summary': failure_summary,
            'failure_categories': {
                'optimization_failures': optimization_failures,
                'topology_failures': topology_failures,
                'roaming_failures': roaming_failures,
                'algorithm_failures': algorithm_failures,
                'timeout_failures': timeout_failures,
                'coordination_failures': coordination_failures
            },
            'failure_patterns': failure_patterns,
            'severity_assessment': severity_assessment,
            'failure_incidents': self._generate_failure_incidents(),
            'recommendations': self._generate_failure_recommendations()
        }
    
    def _analyze_optimization_failures(self, cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze optimization cycle failures"""
        optimization_failures = {
            'total_failed_cycles': 0,
            'failure_reasons': Counter(),
            'failed_devices': set(),
            'failure_details': []
        }
        
        for device_mac, device_cycles in cycles.items() if isinstance(cycles, dict) else []:
            for cycle in device_cycles:
                if not cycle.get('success', False) and cycle.get('status') != 'active':
                    optimization_failures['total_failed_cycles'] += 1
                    optimization_failures['failed_devices'].add(device_mac)
                    
                    # Determine failure reason
                    failure_reason = self._determine_cycle_failure_reason(cycle)
                    optimization_failures['failure_reasons'][failure_reason] += 1
                    
                    failure_detail = {
                        'device_mac': device_mac,
                        'cycle_id': cycle.get('cycle_id'),
                        'start_time': cycle.get('start_time'),
                        'failure_reason': failure_reason,
                        'duration': cycle.get('metrics', {}).get('duration_events', 0),
                        'events_in_cycle': cycle.get('metrics', {}).get('total_events', 0),
                        'failure_events': cycle.get('metrics', {}).get('failure_events', 0)
                    }
                    optimization_failures['failure_details'].append(failure_detail)
                    
                    # Store in category
                    self.failure_categories['optimization_failures'].append(failure_detail)
        
        optimization_failures['failed_devices'] = list(optimization_failures['failed_devices'])
        
        return optimization_failures
    
    def _determine_cycle_failure_reason(self, cycle: Dict[str, Any]) -> str:
        """Determine the reason for cycle failure"""
        status = cycle.get('status', '')
        events = cycle.get('events', [])
        phases = cycle.get('phases', [])
        
        if status == 'timeout':
            return 'timeout'
        
        # Check for specific failure events
        failure_events = [e for e in events if e.get('event_type') == 'failure']
        if failure_events:
            # Analyze failure event patterns
            for event in failure_events:
                reason = event.get('reason', '').lower()
                if 'topology' in reason:
                    return 'topology_build_failure'
                elif 'algorithm' in reason:
                    return 'algorithm_failure'
                elif 'coordination' in reason:
                    return 'coordination_failure'
                elif 'resource' in reason:
                    return 'resource_constraint'
        
        # Check phases completed
        if not phases:
            return 'no_phases_completed'
        elif len(phases) == 1:
            return 'scanning_failure'
        elif len(phases) == 2:
            return 'analysis_failure'
        elif len(phases) >= 3:
            return 'optimization_implementation_failure'
        
        return 'unknown_failure'
    
    def _analyze_topology_failures(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze topology build failures"""
        topology_failures = {
            'total_failures': 0,
            'failure_types': Counter(),
            'affected_devices': set(),
            'failure_details': []
        }
        
        for event in events:
            if (event.get('event_type') == 'failure' and 
                'topology' in event.get('pattern_name', '').lower()):
                
                topology_failures['total_failures'] += 1
                
                device_mac = event.get('device_mac')
                if device_mac:
                    topology_failures['affected_devices'].add(device_mac)
                
                # Classify topology failure type
                reason = event.get('reason', '').lower()
                if 'build' in reason:
                    failure_type = 'topology_build_failure'
                elif 'constraint' in reason:
                    failure_type = 'topology_constraint_violation'
                elif 'invalid' in reason:
                    failure_type = 'invalid_topology'
                else:
                    failure_type = 'general_topology_failure'
                
                topology_failures['failure_types'][failure_type] += 1
                
                failure_detail = {
                    'device_mac': device_mac,
                    'timestamp': event.get('timestamp'),
                    'failure_type': failure_type,
                    'context': event.get('raw_line', ''),
                    'reason': event.get('reason', '')
                }
                topology_failures['failure_details'].append(failure_detail)
                self.failure_categories['topology_failures'].append(failure_detail)
        
        topology_failures['affected_devices'] = list(topology_failures['affected_devices'])
        
        return topology_failures
    
    def _analyze_roaming_failures(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze roaming command failures and packet loss issues"""
        roaming_failures = {
            'high_packet_loss_events': 0,
            'critical_packet_loss_events': 0,
            'affected_devices': set(),
            'packet_loss_distribution': Counter(),
            'failure_details': []
        }
        
        for event in events:
            if event.get('event_type') == 'packet_loss':
                packet_loss = event.get('packet_loss', 0)
                
                try:
                    packet_loss_percent = float(packet_loss)
                except (ValueError, TypeError):
                    continue
                
                device_mac = event.get('device_mac')
                
                if packet_loss_percent > self.packet_loss_threshold:
                    roaming_failures['high_packet_loss_events'] += 1
                    
                    if device_mac:
                        roaming_failures['affected_devices'].add(device_mac)
                    
                    severity = 'critical' if packet_loss_percent > self.high_packet_loss_threshold else 'high'
                    
                    if severity == 'critical':
                        roaming_failures['critical_packet_loss_events'] += 1
                    
                    # Categorize packet loss level
                    if packet_loss_percent < 25:
                        loss_category = 'moderate'
                    elif packet_loss_percent < 40:
                        loss_category = 'high'
                    else:
                        loss_category = 'critical'
                    
                    roaming_failures['packet_loss_distribution'][loss_category] += 1
                    
                    failure_detail = {
                        'device_mac': device_mac,
                        'timestamp': event.get('timestamp'),
                        'packet_loss_percent': packet_loss_percent,
                        'severity': severity,
                        'rssi': event.get('rssi'),
                        'channel': event.get('channel')
                    }
                    roaming_failures['failure_details'].append(failure_detail)
                    self.failure_categories['roaming_failures'].append(failure_detail)
        
        roaming_failures['affected_devices'] = list(roaming_failures['affected_devices'])
        
        return roaming_failures
    
    def _analyze_algorithm_failures(self, events: List[Dict[str, Any]], cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze algorithm decision failures"""
        algorithm_failures = {
            'poor_decisions': 0,
            'algorithm_errors': 0,
            'decision_patterns': Counter(),
            'failure_details': []
        }
        
        # Analyze events for algorithm-related failures
        for event in events:
            if (event.get('event_type') == 'failure' and 
                'algorithm' in event.get('pattern_name', '').lower()):
                
                algorithm_failures['algorithm_errors'] += 1
                
                failure_detail = {
                    'device_mac': event.get('device_mac'),
                    'timestamp': event.get('timestamp'),
                    'failure_type': 'algorithm_error',
                    'context': event.get('reason', ''),
                    'raw_line': event.get('raw_line', '')
                }
                algorithm_failures['failure_details'].append(failure_detail)
                self.failure_categories['algorithm_failures'].append(failure_detail)
        
        # Analyze cycles for poor algorithmic decisions
        if isinstance(cycles, dict):
            for device_mac, device_cycles in cycles.items():
                for cycle in device_cycles:
                    if self._is_poor_algorithm_decision(cycle):
                        algorithm_failures['poor_decisions'] += 1
                        
                        decision_pattern = self._classify_poor_decision(cycle)
                        algorithm_failures['decision_patterns'][decision_pattern] += 1
                        
                        failure_detail = {
                            'device_mac': device_mac,
                            'cycle_id': cycle.get('cycle_id'),
                            'decision_type': decision_pattern,
                            'start_time': cycle.get('start_time'),
                            'duration': cycle.get('metrics', {}).get('duration_events', 0)
                        }
                        algorithm_failures['failure_details'].append(failure_detail)
                        self.failure_categories['algorithm_failures'].append(failure_detail)
        
        return algorithm_failures
    
    def _is_poor_algorithm_decision(self, cycle: Dict[str, Any]) -> bool:
        """Determine if cycle represents a poor algorithmic decision"""
        # Very short cycles might indicate poor decision making
        duration = cycle.get('metrics', {}).get('duration_events', 0)
        if duration < 3:
            return True
        
        # Cycles with many failures
        failure_events = cycle.get('metrics', {}).get('failure_events', 0)
        total_events = cycle.get('metrics', {}).get('total_events', 1)
        if failure_events / total_events > 0.5:
            return True
        
        # Incomplete cycles with many events (hung cycles)
        if cycle.get('status') != 'completed' and total_events > 50:
            return True
        
        return False
    
    def _classify_poor_decision(self, cycle: Dict[str, Any]) -> str:
        """Classify the type of poor algorithmic decision"""
        duration = cycle.get('metrics', {}).get('duration_events', 0)
        failure_events = cycle.get('metrics', {}).get('failure_events', 0)
        total_events = cycle.get('metrics', {}).get('total_events', 1)
        
        if duration < 3:
            return 'premature_termination'
        elif failure_events / total_events > 0.5:
            return 'high_failure_rate'
        elif cycle.get('status') != 'completed' and total_events > 50:
            return 'infinite_loop'
        else:
            return 'suboptimal_decision'
    
    def _analyze_timeout_failures(self, cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timeout-related failures"""
        timeout_failures = {
            'total_timeouts': 0,
            'timeout_phases': Counter(),
            'affected_devices': set(),
            'failure_details': []
        }
        
        if isinstance(cycles, dict):
            for device_mac, device_cycles in cycles.items():
                for cycle in device_cycles:
                    if cycle.get('status') == 'timeout':
                        timeout_failures['total_timeouts'] += 1
                        timeout_failures['affected_devices'].add(device_mac)
                        
                        # Determine timeout phase
                        phases = cycle.get('phases', [])
                        timeout_phase = phases[-1]['phase'] if phases else 'unknown'
                        timeout_failures['timeout_phases'][timeout_phase] += 1
                        
                        failure_detail = {
                            'device_mac': device_mac,
                            'cycle_id': cycle.get('cycle_id'),
                            'timeout_phase': timeout_phase,
                            'start_time': cycle.get('start_time'),
                            'events_before_timeout': cycle.get('metrics', {}).get('total_events', 0)
                        }
                        timeout_failures['failure_details'].append(failure_detail)
                        self.failure_categories['timeout_failures'].append(failure_detail)
        
        timeout_failures['affected_devices'] = list(timeout_failures['affected_devices'])
        
        return timeout_failures
    
    def _analyze_coordination_failures(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze device coordination failures"""
        coordination_failures = {
            'coordination_errors': 0,
            'affected_device_pairs': set(),
            'failure_details': []
        }
        
        for event in events:
            if (event.get('event_type') == 'failure' and 
                'coordination' in event.get('pattern_name', '').lower()):
                
                coordination_failures['coordination_errors'] += 1
                
                # Track device pairs if available
                from_mac = event.get('from_mac')
                to_mac = event.get('to_mac')
                if from_mac and to_mac:
                    device_pair = tuple(sorted([from_mac, to_mac]))
                    coordination_failures['affected_device_pairs'].add(device_pair)
                
                failure_detail = {
                    'device_mac': event.get('device_mac'),
                    'from_mac': from_mac,
                    'to_mac': to_mac,
                    'timestamp': event.get('timestamp'),
                    'reason': event.get('reason', ''),
                    'context': event.get('raw_line', '')
                }
                coordination_failures['failure_details'].append(failure_detail)
                self.failure_categories['coordination_failures'].append(failure_detail)
        
        coordination_failures['affected_device_pairs'] = list(coordination_failures['affected_device_pairs'])
        
        return coordination_failures
    
    def _generate_failure_summary(self) -> Dict[str, Any]:
        """Generate overall failure summary"""
        total_failures = sum(len(failures) for failures in self.failure_categories.values())
        
        summary = {
            'total_failures': total_failures,
            'failure_breakdown': {
                category: len(failures) 
                for category, failures in self.failure_categories.items()
            },
            'critical_issues': 0,
            'high_priority_issues': 0,
            'status': 'healthy' if total_failures == 0 else 'needs_attention'
        }
        
        # Count critical and high priority issues
        for failures in self.failure_categories.values():
            for failure in failures:
                severity = failure.get('severity', 'medium')
                if severity == 'critical':
                    summary['critical_issues'] += 1
                elif severity == 'high':
                    summary['high_priority_issues'] += 1
        
        # Update status based on severity
        if summary['critical_issues'] > 0:
            summary['status'] = 'critical'
        elif summary['high_priority_issues'] > 3:
            summary['status'] = 'degraded'
        elif total_failures > 10:
            summary['status'] = 'needs_attention'
        
        return summary
    
    def _analyze_failure_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in failures"""
        patterns = {
            'most_common_failures': Counter(),
            'device_failure_correlation': {},
            'temporal_clustering': {},
            'root_cause_analysis': []
        }
        
        # Count all failure types
        for category, failures in self.failure_categories.items():
            for failure in failures:
                failure_type = failure.get('failure_type', category)
                patterns['most_common_failures'][failure_type] += 1
        
        return patterns
    
    def _assess_failure_severity(self) -> Dict[str, Any]:
        """Assess overall failure severity"""
        severity_counts = Counter()
        
        for failures in self.failure_categories.values():
            for failure in failures:
                severity = failure.get('severity', 'medium')
                severity_counts[severity] += 1
        
        total_failures = sum(severity_counts.values())
        
        assessment = {
            'severity_distribution': dict(severity_counts),
            'overall_severity': 'low',
            'action_required': False
        }
        
        if total_failures == 0:
            assessment['overall_severity'] = 'none'
        elif severity_counts['critical'] > 0:
            assessment['overall_severity'] = 'critical'
            assessment['action_required'] = True
        elif severity_counts['high'] > 5:
            assessment['overall_severity'] = 'high'
            assessment['action_required'] = True
        elif total_failures > 20:
            assessment['overall_severity'] = 'medium'
        
        return assessment
    
    def _generate_failure_incidents(self) -> List[Dict[str, Any]]:
        """Generate list of all failure incidents"""
        incidents = []
        
        for category, failures in self.failure_categories.items():
            for failure in failures:
                incident = {
                    'category': category,
                    'timestamp': failure.get('timestamp', ''),
                    'device_mac': failure.get('device_mac', ''),
                    'description': self._generate_incident_description(category, failure),
                    'severity': failure.get('severity', 'medium'),
                    'details': failure
                }
                incidents.append(incident)
        
        # Sort by timestamp (most recent first)
        incidents.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return incidents
    
    def _generate_incident_description(self, category: str, failure: Dict[str, Any]) -> str:
        """Generate human-readable incident description"""
        if category == 'optimization_failures':
            reason = failure.get('failure_reason', 'unknown')
            return f"Optimization cycle failed: {reason}"
        elif category == 'topology_failures':
            failure_type = failure.get('failure_type', 'general')
            return f"Topology failure: {failure_type}"
        elif category == 'roaming_failures':
            packet_loss = failure.get('packet_loss_percent', 0)
            return f"High packet loss detected: {packet_loss}%"
        elif category == 'algorithm_failures':
            decision_type = failure.get('decision_type', 'error')
            return f"Algorithm issue: {decision_type}"
        elif category == 'timeout_failures':
            phase = failure.get('timeout_phase', 'unknown')
            return f"Cycle timeout in {phase} phase"
        elif category == 'coordination_failures':
            return "Device coordination failure"
        else:
            return f"Failure in {category}"
    
    def _generate_failure_recommendations(self) -> List[str]:
        """Generate recommendations based on failure analysis"""
        recommendations = []
        
        total_failures = sum(len(failures) for failures in self.failure_categories.values())
        
        if total_failures == 0:
            recommendations.append("No significant failures detected - TPYOPT system operating normally")
            return recommendations
        
        # Optimization failure recommendations
        opt_failures = len(self.failure_categories['optimization_failures'])
        if opt_failures > 0:
            recommendations.append(f"Address {opt_failures} optimization failures - review TPYOPT configuration")
        
        # Topology failure recommendations
        topo_failures = len(self.failure_categories['topology_failures'])
        if topo_failures > 0:
            recommendations.append(f"Investigate {topo_failures} topology build failures - check network constraints")
        
        # Roaming failure recommendations
        roaming_failures = len(self.failure_categories['roaming_failures'])
        if roaming_failures > 0:
            recommendations.append(f"High packet loss detected in {roaming_failures} events - review RF environment")
        
        # Timeout recommendations
        timeout_failures = len(self.failure_categories['timeout_failures'])
        if timeout_failures > 0:
            recommendations.append(f"Address {timeout_failures} timeout failures - consider increasing timeout thresholds")
        
        return recommendations
