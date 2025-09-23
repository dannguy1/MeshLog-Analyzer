"""
TPYOPT Analysis Engine Module

Core analysis logic for TPYOPT behavior including FSM state tracking,
device behavior analysis, and topology optimization patterns.
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import statistics


class TPYOPTAnalysisEngine:
    """Core TPYOPT analysis engine for FSM and device behavior analysis"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
        # Analysis data
        self.fsm_states = defaultdict(lambda: {
            'current_state': 'UNKNOWN',
            'state_history': [],
            'state_durations': {},
            'transition_count': 0
        })
        
        self.device_behaviors = defaultdict(lambda: {
            'optimization_attempts': 0,
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'roaming_events': 0,
            'packet_loss_incidents': 0,
            'topology_changes': 0,
            'activity_timeline': []
        })
        
        # Analysis configuration
        self.tpyopt_states = [
            'IDLE', 'SCANNING', 'ANALYZING', 'OPTIMIZING', 
            'COORDINATING', 'IMPLEMENTING', 'MONITORING', 'ERROR'
        ]
        
    def analyze_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive TPYOPT analysis"""
        self.logger.info(f"Analyzing {len(events)} TPYOPT events")
        
        # Reset analysis state
        self.fsm_states.clear()
        self.device_behaviors.clear()
        
        # Process events
        for event in events:
            self._process_event(event)
        
        # Generate analysis results
        fsm_analysis = self._analyze_fsm_behavior()
        device_analysis = self._analyze_device_behavior()
        topology_analysis = self._analyze_topology_patterns()
        timeline_analysis = self._analyze_timeline_patterns(events)
        
        return {
            'fsm_analysis': fsm_analysis,
            'device_analysis': device_analysis,
            'topology_analysis': topology_analysis,
            'timeline_analysis': timeline_analysis,
            'total_devices': len(self.device_behaviors),
            'active_devices': len([d for d in self.device_behaviors.values() 
                                 if d['optimization_attempts'] > 0])
        }
    
    def _process_event(self, event: Dict[str, Any]) -> None:
        """Process individual event for analysis"""
        event_type = event.get('event_type', '')
        device_mac = event.get('device_mac')
        timestamp = event.get('timestamp', '')
        
        if not device_mac:
            return
        
        # Update device behavior tracking
        behavior = self.device_behaviors[device_mac]
        behavior['activity_timeline'].append({
            'timestamp': timestamp,
            'event_type': event_type,
            'details': event.get('reason', '')
        })
        
        # Process FSM transitions
        if event_type == 'fsm_transition':
            self._process_fsm_transition(event, device_mac)
        
        # Process optimization events
        elif event_type == 'optimization':
            self._process_optimization_event(event, device_mac)
        
        # Process roaming events
        elif event_type == 'roaming_command':
            behavior['roaming_events'] += 1
        
        # Process packet loss events
        elif event_type == 'packet_loss':
            behavior['packet_loss_incidents'] += 1
        
        # Process topology changes
        elif event_type == 'topology_change':
            behavior['topology_changes'] += 1
    
    def _process_fsm_transition(self, event: Dict[str, Any], device_mac: str) -> None:
        """Process FSM state transition"""
        from_state = event.get('from_state', 'UNKNOWN')
        to_state = event.get('to_state', 'UNKNOWN')
        timestamp = event.get('timestamp', '')
        
        fsm_data = self.fsm_states[device_mac]
        
        # Update current state
        previous_state = fsm_data['current_state']
        fsm_data['current_state'] = to_state
        fsm_data['transition_count'] += 1
        
        # Record transition
        transition = {
            'timestamp': timestamp,
            'from_state': from_state,
            'to_state': to_state,
            'previous_state': previous_state
        }
        fsm_data['state_history'].append(transition)
        
        # Track state durations
        if previous_state != 'UNKNOWN' and timestamp:
            duration_key = f"{previous_state}->{to_state}"
            if duration_key not in fsm_data['state_durations']:
                fsm_data['state_durations'][duration_key] = []
    
    def _process_optimization_event(self, event: Dict[str, Any], device_mac: str) -> None:
        """Process optimization-related event"""
        behavior = self.device_behaviors[device_mac]
        behavior['optimization_attempts'] += 1
        
        # Determine if optimization was successful based on event details
        reason = event.get('reason', '').lower()
        pattern_name = event.get('pattern_name', '').lower()
        
        if any(success_indicator in reason for success_indicator in 
               ['success', 'completed', 'optimized', 'improved']):
            behavior['successful_optimizations'] += 1
        elif any(failure_indicator in reason for failure_indicator in 
                ['failed', 'error', 'timeout', 'abort']):
            behavior['failed_optimizations'] += 1
    
    def _analyze_fsm_behavior(self) -> Dict[str, Any]:
        """Analyze FSM state behavior patterns"""
        fsm_analysis = {
            'total_devices_with_fsm': len(self.fsm_states),
            'state_distribution': Counter(),
            'transition_patterns': Counter(),
            'problematic_devices': [],
            'state_statistics': {}
        }
        
        total_transitions = 0
        
        for device_mac, fsm_data in self.fsm_states.items():
            current_state = fsm_data['current_state']
            transitions = fsm_data['state_history']
            transition_count = fsm_data['transition_count']
            
            # Update state distribution
            fsm_analysis['state_distribution'][current_state] += 1
            total_transitions += transition_count
            
            # Analyze transition patterns
            for transition in transitions:
                pattern = f"{transition['from_state']}->{transition['to_state']}"
                fsm_analysis['transition_patterns'][pattern] += 1
            
            # Identify problematic devices
            if transition_count > 50:  # High transition count
                fsm_analysis['problematic_devices'].append({
                    'device_mac': device_mac,
                    'transition_count': transition_count,
                    'current_state': current_state,
                    'issue': 'excessive_transitions'
                })
            elif current_state == 'ERROR':
                fsm_analysis['problematic_devices'].append({
                    'device_mac': device_mac,
                    'transition_count': transition_count,
                    'current_state': current_state,
                    'issue': 'error_state'
                })
        
        # Calculate statistics
        if self.fsm_states:
            transition_counts = [data['transition_count'] for data in self.fsm_states.values()]
            fsm_analysis['state_statistics'] = {
                'average_transitions_per_device': statistics.mean(transition_counts),
                'max_transitions': max(transition_counts),
                'min_transitions': min(transition_counts),
                'total_transitions': total_transitions,
                'devices_in_error_state': fsm_analysis['state_distribution']['ERROR']
            }
        
        return fsm_analysis
    
    def _analyze_device_behavior(self) -> Dict[str, Any]:
        """Analyze device behavior patterns"""
        device_analysis = {
            'total_devices': len(self.device_behaviors),
            'behavior_summary': {
                'high_activity': [],
                'low_activity': [],
                'problematic': []
            },
            'optimization_statistics': {},
            'activity_patterns': {}
        }
        
        if not self.device_behaviors:
            return device_analysis
        
        # Calculate optimization statistics
        total_attempts = sum(d['optimization_attempts'] for d in self.device_behaviors.values())
        total_successful = sum(d['successful_optimizations'] for d in self.device_behaviors.values())
        total_failed = sum(d['failed_optimizations'] for d in self.device_behaviors.values())
        
        device_analysis['optimization_statistics'] = {
            'total_optimization_attempts': total_attempts,
            'total_successful_optimizations': total_successful,
            'total_failed_optimizations': total_failed,
            'success_rate': total_successful / max(1, total_attempts),
            'failure_rate': total_failed / max(1, total_attempts)
        }
        
        # Categorize devices by behavior
        for device_mac, behavior in self.device_behaviors.items():
            total_activity = (behavior['optimization_attempts'] + 
                            behavior['roaming_events'] + 
                            behavior['packet_loss_incidents'])
            
            device_summary = {
                'device_mac': device_mac,
                'total_activity': total_activity,
                'optimization_attempts': behavior['optimization_attempts'],
                'success_rate': behavior['successful_optimizations'] / max(1, behavior['optimization_attempts'])
            }
            
            if total_activity > 20:
                device_analysis['behavior_summary']['high_activity'].append(device_summary)
            elif total_activity < 5:
                device_analysis['behavior_summary']['low_activity'].append(device_summary)
            
            if behavior['packet_loss_incidents'] > 10 or behavior['failed_optimizations'] > 5:
                device_analysis['behavior_summary']['problematic'].append(device_summary)
        
        return device_analysis
    
    def _analyze_topology_patterns(self) -> Dict[str, Any]:
        """Analyze topology optimization patterns"""
        topology_analysis = {
            'total_topology_changes': 0,
            'devices_with_changes': 0,
            'change_frequency': {},
            'optimization_correlation': {}
        }
        
        devices_with_changes = 0
        total_changes = 0
        
        for device_mac, behavior in self.device_behaviors.items():
            topology_changes = behavior['topology_changes']
            total_changes += topology_changes
            
            if topology_changes > 0:
                devices_with_changes += 1
                
                # Analyze correlation with optimizations
                optimization_ratio = behavior['optimization_attempts'] / max(1, topology_changes)
                topology_analysis['optimization_correlation'][device_mac] = optimization_ratio
        
        topology_analysis['total_topology_changes'] = total_changes
        topology_analysis['devices_with_changes'] = devices_with_changes
        
        if devices_with_changes > 0:
            avg_changes = total_changes / devices_with_changes
            topology_analysis['change_frequency']['average_per_device'] = avg_changes
        
        return topology_analysis
    
    def _analyze_timeline_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in TPYOPT behavior"""
        timeline_analysis = {
            'time_range': 'Unknown',
            'event_distribution': Counter(),
            'peak_activity_periods': [],
            'quiet_periods': []
        }
        
        if not events:
            return timeline_analysis
        
        # Sort events by timestamp
        sorted_events = sorted([e for e in events if e.get('timestamp')], 
                             key=lambda x: x['timestamp'])
        
        if sorted_events:
            first_event = sorted_events[0]['timestamp']
            last_event = sorted_events[-1]['timestamp']
            timeline_analysis['time_range'] = f"{first_event} to {last_event}"
        
        # Analyze event type distribution
        for event in events:
            event_type = event.get('event_type', 'unknown')
            timeline_analysis['event_distribution'][event_type] += 1
        
        return timeline_analysis
    
    def get_fsm_states(self) -> Dict[str, Any]:
        """Get FSM state data"""
        return dict(self.fsm_states)
    
    def get_device_behaviors(self) -> Dict[str, Any]:
        """Get device behavior data"""
        return dict(self.device_behaviors)
