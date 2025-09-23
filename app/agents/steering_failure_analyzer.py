"""
WNC Steering Failure Analysis Module

This module provides detailed failure analysis capabilities for the WNC Steering Agent.
It tracks, categorizes, and analyzes steering failures to provide actionable insights.
"""

import re
from typing import Dict, List, Any, Optional
from collections import defaultdict

class SteeringFailureAnalyzer:
    """Handles detailed failure analysis for steering events"""
    
    def __init__(self):
        # Initialize enhanced failure detection patterns
        self._enhanced_patterns = {
            'btm_request_failed': re.compile(r'btm.*request.*failed.*([a-fA-F0-9:]{17})', re.IGNORECASE),
            'steering_timeout': re.compile(r'steering.*timeout.*([a-fA-F0-9:]{17})', re.IGNORECASE),
            'client_rejected_steering': re.compile(r'client\s+([a-fA-F0-9:]{17}).*reject.*steering', re.IGNORECASE),
            'no_suitable_target': re.compile(r'no.*suitable.*target.*([a-fA-F0-9:]{17})', re.IGNORECASE),
            'insufficient_rssi': re.compile(r'insufficient.*rssi.*([a-fA-F0-9:]{17})', re.IGNORECASE),
            'client_disconnected': re.compile(r'client\s+([a-fA-F0-9:]{17}).*disconnect.*steering', re.IGNORECASE),
            'ap_overloaded': re.compile(r'ap.*overload.*steering.*([a-fA-F0-9:]{17})', re.IGNORECASE),
            'radio_interference': re.compile(r'radio.*interference.*steering.*([a-fA-F0-9:]{17})', re.IGNORECASE),
            'bss_load_high': re.compile(r'bss.*load.*high.*steering.*([a-fA-F0-9:]{17})', re.IGNORECASE),
            'steering_blacklisted': re.compile(r'steering.*blacklist.*([a-fA-F0-9:]{17})', re.IGNORECASE),
            'client_roaming_disabled': re.compile(r'roaming.*disabled.*([a-fA-F0-9:]{17})', re.IGNORECASE),
            'target_ap_unavailable': re.compile(r'target.*ap.*unavailable.*([a-fA-F0-9:]{17})', re.IGNORECASE)
        }
        
        self.failure_incidents = []
        self.performance_metrics = {
            'total_steering_attempts': 0,
            'successful_steers': 0,
            'failed_steers': 0,
            'btm_failures': 0,
            'timeout_failures': 0,
            'rejection_failures': 0,
            'target_selection_failures': 0,
            'rssi_failures': 0
        }
    
    def record_failure_incident(self, client_mac: str, timestamp: str, 
                               failure_type: str, raw_line: str, event_data: dict) -> None:
        """Record a detailed failure incident for analysis"""
        incident = {
            'timestamp': timestamp,
            'client_mac': client_mac,
            'failure_type': failure_type,
            'failure_reason': event_data.get('failure_reason', ''),
            'rssi': event_data.get('rssi'),
            'raw_line': raw_line,
            'incident_id': f"{client_mac}_{timestamp}_{len(self.failure_incidents)}"
        }
        
        self.failure_incidents.append(incident)
        
        # Update performance metrics
        self.performance_metrics['failed_steers'] += 1
        
        # Update specific failure type counters
        if 'btm' in failure_type.lower():
            self.performance_metrics['btm_failures'] += 1
        elif 'timeout' in failure_type.lower():
            self.performance_metrics['timeout_failures'] += 1
        elif 'reject' in failure_type.lower():
            self.performance_metrics['rejection_failures'] += 1
        elif 'target' in failure_type.lower():
            self.performance_metrics['target_selection_failures'] += 1
        elif 'rssi' in failure_type.lower():
            self.performance_metrics['rssi_failures'] += 1
    
    def record_success(self):
        """Record a successful steering event"""
        self.performance_metrics['successful_steers'] += 1
    
    def record_attempt(self):
        """Record a steering attempt"""
        self.performance_metrics['total_steering_attempts'] += 1
    
    def analyze_failure_patterns(self) -> dict:
        """Analyze failure patterns and provide detailed breakdown"""
        if not self.failure_incidents:
            return {
                'total_failures': 0,
                'failure_types': {},
                'top_failing_clients': [],
                'common_reasons': [],
                'performance_metrics': self.performance_metrics
            }
        
        failure_types = defaultdict(int)
        failure_reasons = defaultdict(int)
        client_failures = defaultdict(int)
        
        for incident in self.failure_incidents:
            failure_types[incident['failure_type']] += 1
            if incident['failure_reason']:
                failure_reasons[incident['failure_reason']] += 1
            client_failures[incident['client_mac']] += 1
        
        # Get top failing clients (top 5)
        top_failing_clients = sorted(client_failures.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get common failure reasons (top 5)
        common_reasons = sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_failures': len(self.failure_incidents),
            'failure_types': dict(failure_types),
            'top_failing_clients': top_failing_clients,
            'common_reasons': common_reasons,
            'performance_metrics': self.performance_metrics
        }
    
    def get_recent_failures(self, count: int = 10) -> List[dict]:
        """Get the most recent failure incidents"""
        return self.failure_incidents[-count:] if len(self.failure_incidents) > count else self.failure_incidents
    
    def get_failure_summary(self) -> dict:
        """Get a summary of failure metrics"""
        total_attempts = self.performance_metrics['total_steering_attempts']
        total_failures = self.performance_metrics['failed_steers']
        
        return {
            'total_attempts': total_attempts,
            'total_failures': total_failures,
            'total_successes': self.performance_metrics['successful_steers'],
            'success_rate': round((self.performance_metrics['successful_steers'] / total_attempts * 100) if total_attempts > 0 else 0, 1),
            'failure_rate': round((total_failures / total_attempts * 100) if total_attempts > 0 else 0, 1),
            'btm_failure_rate': round((self.performance_metrics['btm_failures'] / total_failures * 100) if total_failures > 0 else 0, 1),
            'timeout_failure_rate': round((self.performance_metrics['timeout_failures'] / total_failures * 100) if total_failures > 0 else 0, 1),
            'rejection_rate': round((self.performance_metrics['rejection_failures'] / total_failures * 100) if total_failures > 0 else 0, 1)
        }
    
    def clear(self):
        """Clear all failure data for a new analysis"""
        self.failure_incidents.clear()
        self.performance_metrics = {
            'total_steering_attempts': 0,
            'successful_steers': 0,
            'failed_steers': 0,
            'btm_failures': 0,
            'timeout_failures': 0,
            'rejection_failures': 0,
            'target_selection_failures': 0,
            'rssi_failures': 0
        }
    
    def get_patterns(self) -> Dict[str, re.Pattern]:
        """Return the enhanced failure detection patterns"""
        return self._enhanced_patterns.copy()
