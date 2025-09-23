"""
ACS Cycle Detector Module

Detects and analyzes ACS optimization cycles, including cycle duration,
frequency, and success patterns.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import statistics

class ACSCycleDetector:
    """Detects and analyzes ACS optimization cycles"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Cycle detection parameters
        self.cycle_timeout = 300  # 5 minutes
        self.min_cycle_duration = 5  # 5 seconds
        
        # Detected cycles
        self.cycles = []
        self.incomplete_cycles = []
        
        # Cycle patterns
        self.cycle_triggers = {
            'interference_detected', 'channel_busy', 'poor_performance',
            'neighbor_change', 'manual_trigger', 'periodic_scan'
        }
        
        self.cycle_states = {
            'initiated', 'scanning', 'analyzing', 'selecting', 
            'switching', 'verifying', 'completed', 'failed'
        }
    
    def detect_cycles(self, events: List[Dict[str, Any]], radio_states: Dict[str, Any]) -> Dict[str, Any]:
        """Detect ACS cycles from events and radio states"""
        self.logger.info(f"Detecting ACS cycles from {len(events)} events")
        
        # Reset detection state
        self.cycles.clear()
        self.incomplete_cycles.clear()
        
        # Group events by radio
        radio_events = defaultdict(list)
        for event in events:
            radio = event.get('radio', 'unknown')
            radio_events[radio].append(event)
        
        # Detect cycles for each radio
        for radio, events_list in radio_events.items():
            self._detect_radio_cycles(radio, events_list)
        
        # Analyze cycle patterns
        return self._analyze_cycles()
    
    def _detect_radio_cycles(self, radio: str, events: List[Dict[str, Any]]) -> None:
        """Detect cycles for a specific radio"""
        if not events:
            return
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x.get('timestamp', ''))
        
        current_cycle = None
        
        for event in sorted_events:
            event_type = event.get('event_type', '').lower()
            timestamp = event.get('timestamp', '')
            
            # Check for cycle initiation
            if self._is_cycle_start_event(event):
                # Complete previous cycle if exists
                if current_cycle:
                    self._finalize_cycle(current_cycle, 'incomplete')
                
                # Start new cycle
                current_cycle = {
                    'radio': radio,
                    'start_time': timestamp,
                    'start_event': event,
                    'events': [event],
                    'states': [],
                    'trigger': self._extract_trigger(event),
                    'status': 'active'
                }
            
            # Add event to current cycle
            elif current_cycle:
                current_cycle['events'].append(event)
                
                # Track FSM states
                if 'fsm_state' in event:
                    current_cycle['states'].append(event['fsm_state'])
                
                # Check for cycle completion
                if self._is_cycle_end_event(event):
                    current_cycle['end_time'] = timestamp
                    current_cycle['end_event'] = event
                    current_cycle['status'] = 'completed' if 'complete' in event_type else 'failed'
                    self._finalize_cycle(current_cycle, current_cycle['status'])
                    current_cycle = None
        
        # Handle incomplete cycle
        if current_cycle:
            self._finalize_cycle(current_cycle, 'incomplete')
    
    def _is_cycle_start_event(self, event: Dict[str, Any]) -> bool:
        """Check if event indicates cycle start"""
        event_type = event.get('event_type', '').lower()
        return any(keyword in event_type for keyword in [
            'acs_start', 'acs_init', 'acs_trigger', 'scan_start',
            'channel_selection_start', 'optimization_start'
        ])
    
    def _is_cycle_end_event(self, event: Dict[str, Any]) -> bool:
        """Check if event indicates cycle end"""
        event_type = event.get('event_type', '').lower()
        return any(keyword in event_type for keyword in [
            'acs_complete', 'acs_finish', 'acs_done', 'acs_failed',
            'channel_selected', 'optimization_complete', 'acs_abort'
        ])
    
    def _extract_trigger(self, event: Dict[str, Any]) -> str:
        """Extract cycle trigger from start event"""
        event_type = event.get('event_type', '').lower()
        reason = event.get('reason', '').lower()
        raw_line = event.get('raw_line', '').lower()
        
        # Check for specific triggers
        if any(keyword in f"{event_type} {reason} {raw_line}" for keyword in ['interference', 'interfere']):
            return 'interference_detected'
        elif any(keyword in f"{event_type} {reason} {raw_line}" for keyword in ['busy', 'congestion']):
            return 'channel_busy'
        elif any(keyword in f"{event_type} {reason} {raw_line}" for keyword in ['performance', 'poor']):
            return 'poor_performance'
        elif any(keyword in f"{event_type} {reason} {raw_line}" for keyword in ['neighbor', 'peer']):
            return 'neighbor_change'
        elif any(keyword in f"{event_type} {reason} {raw_line}" for keyword in ['manual', 'user']):
            return 'manual_trigger'
        elif any(keyword in f"{event_type} {reason} {raw_line}" for keyword in ['periodic', 'timer']):
            return 'periodic_scan'
        else:
            return 'unknown'
    
    def _finalize_cycle(self, cycle: Dict[str, Any], status: str) -> None:
        """Finalize and analyze a cycle"""
        cycle['status'] = status
        
        # Calculate duration
        start_time = cycle.get('start_time', '')
        end_time = cycle.get('end_time', cycle.get('start_time', ''))
        
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace(' ', 'T'))
                end_dt = datetime.fromisoformat(end_time.replace(' ', 'T'))
                duration = (end_dt - start_dt).total_seconds()
                cycle['duration_seconds'] = duration
            except:
                cycle['duration_seconds'] = 0
        else:
            cycle['duration_seconds'] = 0
        
        # Analyze cycle events
        cycle['event_count'] = len(cycle['events'])
        cycle['unique_states'] = list(set(cycle['states']))
        cycle['state_transitions'] = len(cycle['states'])
        
        # Determine cycle quality
        cycle['quality'] = self._assess_cycle_quality(cycle)
        
        # Store cycle
        if status == 'incomplete':
            self.incomplete_cycles.append(cycle)
        else:
            self.cycles.append(cycle)
    
    def _assess_cycle_quality(self, cycle: Dict[str, Any]) -> str:
        """Assess the quality of a cycle"""
        status = cycle['status']
        duration = cycle.get('duration_seconds', 0)
        event_count = cycle.get('event_count', 0)
        state_transitions = cycle.get('state_transitions', 0)
        
        if status == 'completed':
            if duration < 30 and state_transitions >= 3:
                return 'excellent'  # Fast and complete
            elif duration < 60:
                return 'good'  # Reasonable duration
            elif duration < 300:
                return 'acceptable'  # Longer but completed
            else:
                return 'slow'  # Very long duration
        elif status == 'failed':
            if duration < 60:
                return 'quick_failure'  # Fast failure
            else:
                return 'slow_failure'  # Long failure
        else:
            return 'incomplete'  # Incomplete cycle
    
    def _analyze_cycles(self) -> Dict[str, Any]:
        """Analyze detected cycles and generate insights"""
        total_cycles = len(self.cycles) + len(self.incomplete_cycles)
        
        if total_cycles == 0:
            return {
                'cycle_summary': {
                    'total_cycles': 0,
                    'completed_cycles': 0,
                    'failed_cycles': 0,
                    'incomplete_cycles': 0,
                    'success_rate': 0.0
                },
                'cycle_details': [],
                'cycle_patterns': {},
                'recommendations': ['No ACS cycles detected in log data']
            }
        
        completed_cycles = [c for c in self.cycles if c['status'] == 'completed']
        failed_cycles = [c for c in self.cycles if c['status'] == 'failed']
        
        return {
            'cycle_summary': self._generate_cycle_summary(completed_cycles, failed_cycles),
            'cycle_details': self._format_cycle_details(),
            'cycle_patterns': self._analyze_cycle_patterns(),
            'performance_analysis': self._analyze_cycle_performance(),
            'recommendations': self._generate_cycle_recommendations()
        }
    
    def _generate_cycle_summary(self, completed: List[Dict], failed: List[Dict]) -> Dict[str, Any]:
        """Generate cycle summary statistics"""
        total_cycles = len(self.cycles) + len(self.incomplete_cycles)
        completed_count = len(completed)
        failed_count = len(failed)
        incomplete_count = len(self.incomplete_cycles)
        
        success_rate = (completed_count / max(1, total_cycles)) * 100
        
        # Duration statistics for completed cycles
        durations = [c['duration_seconds'] for c in completed if c.get('duration_seconds', 0) > 0]
        avg_duration = statistics.mean(durations) if durations else 0
        
        return {
            'total_cycles': total_cycles,
            'completed_cycles': completed_count,
            'failed_cycles': failed_count,
            'incomplete_cycles': incomplete_count,
            'success_rate': round(success_rate, 1),
            'average_duration_seconds': round(avg_duration, 1),
            'fastest_cycle': min(durations) if durations else 0,
            'slowest_cycle': max(durations) if durations else 0
        }
    
    def _format_cycle_details(self) -> List[Dict[str, Any]]:
        """Format cycle details for reporting"""
        details = []
        
        for cycle in (self.cycles + self.incomplete_cycles):
            detail = {
                'radio': cycle['radio'],
                'start_time': cycle['start_time'],
                'end_time': cycle.get('end_time', 'N/A'),
                'duration_seconds': cycle.get('duration_seconds', 0),
                'status': cycle['status'],
                'trigger': cycle['trigger'],
                'event_count': cycle['event_count'],
                'state_transitions': cycle['state_transitions'],
                'quality': cycle['quality'],
                'unique_states': cycle['unique_states']
            }
            details.append(detail)
        
        # Sort by start time
        details.sort(key=lambda x: x['start_time'])
        return details
    
    def _analyze_cycle_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in cycles"""
        all_cycles = self.cycles + self.incomplete_cycles
        
        # Trigger analysis
        triggers = [cycle['trigger'] for cycle in all_cycles]
        trigger_counts = defaultdict(int)
        for trigger in triggers:
            trigger_counts[trigger] += 1
        
        # Radio analysis
        radios = [cycle['radio'] for cycle in all_cycles]
        radio_counts = defaultdict(int)
        for radio in radios:
            radio_counts[radio] += 1
        
        # Quality analysis
        qualities = [cycle['quality'] for cycle in all_cycles]
        quality_counts = defaultdict(int)
        for quality in qualities:
            quality_counts[quality] += 1
        
        # Temporal patterns
        temporal_analysis = self._analyze_temporal_patterns(all_cycles)
        
        return {
            'trigger_distribution': dict(trigger_counts),
            'radio_distribution': dict(radio_counts),
            'quality_distribution': dict(quality_counts),
            'temporal_patterns': temporal_analysis,
            'most_common_trigger': max(trigger_counts.items(), key=lambda x: x[1])[0] if trigger_counts else 'unknown',
            'most_active_radio': max(radio_counts.items(), key=lambda x: x[1])[0] if radio_counts else 'unknown'
        }
    
    def _analyze_temporal_patterns(self, cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in cycles"""
        if not cycles:
            return {}
        
        # Extract start times
        start_times = []
        for cycle in cycles:
            start_time = cycle.get('start_time', '')
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace(' ', 'T'))
                    start_times.append(dt)
                except:
                    continue
        
        if not start_times:
            return {}
        
        start_times.sort()
        
        # Calculate intervals between cycles
        intervals = []
        for i in range(1, len(start_times)):
            interval = (start_times[i] - start_times[i-1]).total_seconds()
            intervals.append(interval)
        
        return {
            'first_cycle': start_times[0].isoformat() if start_times else None,
            'last_cycle': start_times[-1].isoformat() if start_times else None,
            'average_interval_seconds': round(statistics.mean(intervals), 1) if intervals else 0,
            'min_interval_seconds': min(intervals) if intervals else 0,
            'max_interval_seconds': max(intervals) if intervals else 0,
            'cycles_per_hour': self._calculate_cycles_per_hour(start_times)
        }
    
    def _calculate_cycles_per_hour(self, start_times: List[datetime]) -> float:
        """Calculate average cycles per hour"""
        if len(start_times) < 2:
            return 0.0
        
        total_duration = (start_times[-1] - start_times[0]).total_seconds()
        hours = total_duration / 3600
        
        if hours == 0:
            return 0.0
        
        return round(len(start_times) / hours, 2)
    
    def _analyze_cycle_performance(self) -> Dict[str, Any]:
        """Analyze cycle performance metrics"""
        completed_cycles = [c for c in self.cycles if c['status'] == 'completed']
        failed_cycles = [c for c in self.cycles if c['status'] == 'failed']
        
        if not (completed_cycles or failed_cycles):
            return {}
        
        # Performance by trigger
        trigger_performance = defaultdict(lambda: {'completed': 0, 'failed': 0, 'total': 0})
        
        for cycle in completed_cycles:
            trigger = cycle['trigger']
            trigger_performance[trigger]['completed'] += 1
            trigger_performance[trigger]['total'] += 1
        
        for cycle in failed_cycles:
            trigger = cycle['trigger']
            trigger_performance[trigger]['failed'] += 1
            trigger_performance[trigger]['total'] += 1
        
        # Calculate success rates
        for trigger_data in trigger_performance.values():
            total = trigger_data['total']
            completed = trigger_data['completed']
            trigger_data['success_rate'] = (completed / total * 100) if total > 0 else 0
        
        return {
            'performance_by_trigger': dict(trigger_performance),
            'best_performing_trigger': self._find_best_trigger(trigger_performance),
            'worst_performing_trigger': self._find_worst_trigger(trigger_performance)
        }
    
    def _find_best_trigger(self, trigger_performance: Dict) -> str:
        """Find trigger with best success rate"""
        best_trigger = None
        best_rate = -1
        
        for trigger, data in trigger_performance.items():
            if data['total'] >= 2 and data['success_rate'] > best_rate:
                best_rate = data['success_rate']
                best_trigger = trigger
        
        return best_trigger or 'unknown'
    
    def _find_worst_trigger(self, trigger_performance: Dict) -> str:
        """Find trigger with worst success rate"""
        worst_trigger = None
        worst_rate = 101
        
        for trigger, data in trigger_performance.items():
            if data['total'] >= 2 and data['success_rate'] < worst_rate:
                worst_rate = data['success_rate']
                worst_trigger = trigger
        
        return worst_trigger or 'unknown'
    
    def _generate_cycle_recommendations(self) -> List[str]:
        """Generate recommendations based on cycle analysis"""
        recommendations = []
        
        total_cycles = len(self.cycles) + len(self.incomplete_cycles)
        if total_cycles == 0:
            recommendations.append("No ACS cycles detected - verify ACS is enabled and properly configured")
            return recommendations
        
        completed_cycles = [c for c in self.cycles if c['status'] == 'completed']
        failed_cycles = [c for c in self.cycles if c['status'] == 'failed']
        incomplete_cycles = self.incomplete_cycles
        
        success_rate = (len(completed_cycles) / total_cycles) * 100
        
        # Success rate recommendations
        if success_rate < 50:
            recommendations.append(f"Low ACS success rate ({success_rate:.1f}%) - investigate failure causes")
        elif success_rate < 80:
            recommendations.append(f"Moderate ACS success rate ({success_rate:.1f}%) - optimization opportunities exist")
        else:
            recommendations.append(f"Good ACS success rate ({success_rate:.1f}%) - system performing well")
        
        # Duration recommendations
        durations = [c['duration_seconds'] for c in completed_cycles if c.get('duration_seconds', 0) > 0]
        if durations:
            avg_duration = statistics.mean(durations)
            if avg_duration > 120:
                recommendations.append(f"Average cycle duration is long ({avg_duration:.1f}s) - consider tuning scan parameters")
            elif avg_duration < 10:
                recommendations.append(f"Very fast cycles ({avg_duration:.1f}s) - may indicate insufficient analysis")
        
        # Incomplete cycle recommendations
        if len(incomplete_cycles) > len(completed_cycles):
            recommendations.append("Many incomplete cycles detected - check for premature termination")
        
        # Trigger-specific recommendations
        triggers = [cycle['trigger'] for cycle in self.cycles + self.incomplete_cycles]
        trigger_counts = defaultdict(int)
        for trigger in triggers:
            trigger_counts[trigger] += 1
        
        if trigger_counts.get('interference_detected', 0) > total_cycles * 0.5:
            recommendations.append("Frequent interference-triggered cycles - investigate RF environment")
        
        if trigger_counts.get('manual_trigger', 0) > total_cycles * 0.3:
            recommendations.append("Many manual triggers - consider automatic optimization settings")
        
        return recommendations
    
    def get_cycles(self) -> List[Dict[str, Any]]:
        """Get all detected cycles"""
        return self.cycles + self.incomplete_cycles
    
    def get_cycle_count(self) -> int:
        """Get total cycle count"""
        return len(self.cycles) + len(self.incomplete_cycles)
