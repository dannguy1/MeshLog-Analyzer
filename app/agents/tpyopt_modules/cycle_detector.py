"""
TPYOPT Cycle Detector Module

Detects and analyzes TPYOPT optimization cycles including duration,
frequency, success patterns, and cycle quality assessment.
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import statistics


class TPYOPTCycleDetector:
    """TPYOPT optimization cycle detection and analysis"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
        # Cycle detection configuration
        self.cycle_timeout_minutes = 5
        self.cycle_triggers = [
            ('WaitTrigger', 'SendScan'),
            ('IDLE', 'SCANNING'),
            ('ANALYZING', 'OPTIMIZING')
        ]
        self.cycle_completion_states = ['WaitTrigger', 'IDLE', 'MONITORING']
        
    def detect_cycles(self, events: List[Dict[str, Any]], device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect and analyze optimization cycles"""
        self.logger.info("Detecting TPYOPT optimization cycles")
        
        # Group events by device
        device_events = defaultdict(list)
        for event in events:
            device_mac = event.get('device_mac')
            if device_mac:
                device_events[device_mac].append(event)
        
        # Sort events by timestamp for each device
        for device_mac in device_events:
            device_events[device_mac].sort(key=lambda x: x.get('timestamp', ''))
        
        # Detect cycles for each device
        all_cycles = {}
        cycle_statistics = {}
        
        for device_mac, device_event_list in device_events.items():
            device_cycles = self._detect_device_cycles(device_mac, device_event_list)
            all_cycles[device_mac] = device_cycles
            
        # Calculate overall cycle statistics
        cycle_summary = self._calculate_cycle_summary(all_cycles)
        cycle_quality = self._assess_cycle_quality(all_cycles)
        cycle_patterns = self._analyze_cycle_patterns(all_cycles)
        
        return {
            'cycle_details': all_cycles,
            'cycle_summary': cycle_summary,
            'cycle_quality': cycle_quality,
            'cycle_patterns': cycle_patterns,
            'recommendations': self._generate_cycle_recommendations(cycle_summary, cycle_quality)
        }
    
    def _detect_device_cycles(self, device_mac: str, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect optimization cycles for a specific device"""
        cycles = []
        
        i = 0
        while i < len(events):
            event = events[i]
            
            # Check if this event starts a new cycle
            if self._is_cycle_trigger(event):
                cycle = self._build_cycle(device_mac, events, i)
                if cycle:
                    cycles.append(cycle)
                    # Skip to end of this cycle
                    i = cycle.get('end_index', i) + 1
                else:
                    i += 1
            else:
                i += 1
        
        return cycles
    
    def _is_cycle_trigger(self, event: Dict[str, Any]) -> bool:
        """Check if event triggers a new optimization cycle"""
        event_type = event.get('event_type', '')
        from_state = event.get('from_state', '')
        to_state = event.get('to_state', '')
        
        # FSM transition triggers
        if event_type == 'fsm_transition':
            for trigger_from, trigger_to in self.cycle_triggers:
                if from_state == trigger_from and to_state == trigger_to:
                    return True
        
        # Optimization event triggers
        if event_type == 'optimization':
            pattern_name = event.get('pattern_name', '').lower()
            if 'start' in pattern_name or 'begin' in pattern_name:
                return True
        
        return False
    
    def _build_cycle(self, device_mac: str, events: List[Dict[str, Any]], start_index: int) -> Optional[Dict[str, Any]]:
        """Build a complete optimization cycle starting from trigger event"""
        start_event = events[start_index]
        
        cycle = {
            'cycle_id': f"{device_mac}_cycle_{start_index}",
            'device_mac': device_mac,
            'start_time': start_event.get('timestamp', ''),
            'start_event': start_event,
            'events': [start_event],
            'status': 'active',
            'start_index': start_index,
            'phases': []
        }
        
        # Look for cycle completion
        for i in range(start_index + 1, len(events)):
            event = events[i]
            cycle['events'].append(event)
            
            # Track cycle phases
            self._track_cycle_phase(cycle, event)
            
            # Check for cycle completion
            if self._is_cycle_completion(event):
                cycle['status'] = 'completed'
                cycle['end_time'] = event.get('timestamp', '')
                cycle['end_event'] = event
                cycle['end_index'] = i
                break
            
            # Check for cycle timeout
            if self._is_cycle_timeout(cycle, event):
                cycle['status'] = 'timeout'
                cycle['end_time'] = event.get('timestamp', '')
                cycle['end_index'] = i
                break
        
        # Calculate cycle metrics
        self._calculate_cycle_metrics(cycle)
        
        return cycle
    
    def _is_cycle_completion(self, event: Dict[str, Any]) -> bool:
        """Check if event completes an optimization cycle"""
        event_type = event.get('event_type', '')
        to_state = event.get('to_state', '')
        
        # FSM transition completion
        if event_type == 'fsm_transition':
            return to_state in self.cycle_completion_states
        
        # Optimization completion events
        if event_type == 'optimization':
            pattern_name = event.get('pattern_name', '').lower()
            reason = event.get('reason', '').lower()
            return any(completion in pattern_name or completion in reason 
                      for completion in ['complete', 'finish', 'success', 'done'])
        
        return False
    
    def _is_cycle_timeout(self, cycle: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """Check if cycle has exceeded timeout threshold"""
        start_time = cycle.get('start_time', '')
        current_time = event.get('timestamp', '')
        
        if not start_time or not current_time:
            return False
        
        try:
            # Simple timeout check (would need proper datetime parsing in production)
            return len(cycle['events']) > 100  # Simplified timeout check
        except:
            return False
    
    def _track_cycle_phase(self, cycle: Dict[str, Any], event: Dict[str, Any]) -> None:
        """Track phases within an optimization cycle"""
        event_type = event.get('event_type', '')
        to_state = event.get('to_state', '')
        
        # Define cycle phases based on FSM states
        phase_mapping = {
            'SendScan': 'scanning',
            'SCANNING': 'scanning',
            'ReceiveScan': 'analyzing',
            'ANALYZING': 'analyzing',
            'SendOptimize': 'optimizing',
            'OPTIMIZING': 'optimizing',
            'ReceiveOptimize': 'implementing',
            'IMPLEMENTING': 'implementing',
            'MONITORING': 'monitoring'
        }
        
        if event_type == 'fsm_transition' and to_state in phase_mapping:
            phase = phase_mapping[to_state]
            
            # Add phase if not already present
            if not cycle['phases'] or cycle['phases'][-1]['phase'] != phase:
                cycle['phases'].append({
                    'phase': phase,
                    'start_time': event.get('timestamp', ''),
                    'start_event': event
                })
    
    def _calculate_cycle_metrics(self, cycle: Dict[str, Any]) -> None:
        """Calculate metrics for a single cycle"""
        cycle['metrics'] = {
            'total_events': len(cycle['events']),
            'phases_completed': len(cycle['phases']),
            'duration_events': len(cycle['events']),  # Simplified duration
            'fsm_transitions': len([e for e in cycle['events'] if e.get('event_type') == 'fsm_transition']),
            'optimization_events': len([e for e in cycle['events'] if e.get('event_type') == 'optimization']),
            'failure_events': len([e for e in cycle['events'] if e.get('event_type') == 'failure'])
        }
        
        # Determine cycle success
        if cycle['status'] == 'completed':
            failure_count = cycle['metrics']['failure_events']
            cycle['success'] = failure_count == 0
        else:
            cycle['success'] = False
    
    def _calculate_cycle_summary(self, all_cycles: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate overall cycle statistics"""
        total_cycles = 0
        completed_cycles = 0
        successful_cycles = 0
        timeout_cycles = 0
        
        durations = []
        event_counts = []
        
        for device_mac, cycles in all_cycles.items():
            total_cycles += len(cycles)
            
            for cycle in cycles:
                if cycle['status'] == 'completed':
                    completed_cycles += 1
                    if cycle.get('success', False):
                        successful_cycles += 1
                elif cycle['status'] == 'timeout':
                    timeout_cycles += 1
                
                # Collect metrics
                duration = cycle['metrics']['duration_events']
                durations.append(duration)
                event_counts.append(cycle['metrics']['total_events'])
        
        summary = {
            'total_cycles': total_cycles,
            'completed_cycles': completed_cycles,
            'successful_cycles': successful_cycles,
            'timeout_cycles': timeout_cycles,
            'active_cycles': total_cycles - completed_cycles - timeout_cycles,
            'success_rate': successful_cycles / max(1, completed_cycles),
            'completion_rate': completed_cycles / max(1, total_cycles),
            'timeout_rate': timeout_cycles / max(1, total_cycles)
        }
        
        if durations:
            summary['duration_statistics'] = {
                'average_duration': statistics.mean(durations),
                'median_duration': statistics.median(durations),
                'max_duration': max(durations),
                'min_duration': min(durations)
            }
        
        if event_counts:
            summary['event_statistics'] = {
                'average_events_per_cycle': statistics.mean(event_counts),
                'max_events': max(event_counts),
                'min_events': min(event_counts)
            }
        
        return summary
    
    def _assess_cycle_quality(self, all_cycles: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Assess quality of optimization cycles"""
        quality_scores = []
        quality_factors = {
            'completion_bonus': 0,
            'success_bonus': 0,
            'efficiency_bonus': 0,
            'stability_bonus': 0
        }
        
        for device_mac, cycles in all_cycles.items():
            for cycle in cycles:
                score = 0
                
                # Completion bonus
                if cycle['status'] == 'completed':
                    score += 40
                    quality_factors['completion_bonus'] += 1
                
                # Success bonus
                if cycle.get('success', False):
                    score += 30
                    quality_factors['success_bonus'] += 1
                
                # Efficiency bonus (fewer events = more efficient)
                event_count = cycle['metrics']['total_events']
                if event_count < 10:
                    score += 20
                    quality_factors['efficiency_bonus'] += 1
                elif event_count < 20:
                    score += 10
                
                # Stability bonus (no failures)
                if cycle['metrics']['failure_events'] == 0:
                    score += 10
                    quality_factors['stability_bonus'] += 1
                
                quality_scores.append(score)
        
        quality_assessment = {
            'average_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
            'quality_distribution': Counter(),
            'quality_factors': quality_factors,
            'recommendations': []
        }
        
        # Categorize quality scores
        for score in quality_scores:
            if score >= 80:
                quality_assessment['quality_distribution']['excellent'] += 1
            elif score >= 60:
                quality_assessment['quality_distribution']['good'] += 1
            elif score >= 40:
                quality_assessment['quality_distribution']['fair'] += 1
            else:
                quality_assessment['quality_distribution']['poor'] += 1
        
        return quality_assessment
    
    def _analyze_cycle_patterns(self, all_cycles: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze patterns in optimization cycles"""
        patterns = {
            'common_failure_points': Counter(),
            'phase_analysis': Counter(),
            'device_performance': {},
            'temporal_patterns': []
        }
        
        for device_mac, cycles in all_cycles.items():
            device_stats = {
                'total_cycles': len(cycles),
                'success_rate': 0,
                'average_duration': 0,
                'common_issues': []
            }
            
            successful_cycles = 0
            durations = []
            
            for cycle in cycles:
                if cycle.get('success', False):
                    successful_cycles += 1
                
                durations.append(cycle['metrics']['duration_events'])
                
                # Track failure points
                if not cycle.get('success', False):
                    last_phase = cycle['phases'][-1]['phase'] if cycle['phases'] else 'unknown'
                    patterns['common_failure_points'][last_phase] += 1
                
                # Track phase completion
                for phase in cycle['phases']:
                    patterns['phase_analysis'][phase['phase']] += 1
            
            device_stats['success_rate'] = successful_cycles / max(1, len(cycles))
            device_stats['average_duration'] = statistics.mean(durations) if durations else 0
            
            patterns['device_performance'][device_mac] = device_stats
        
        return patterns
    
    def _generate_cycle_recommendations(self, cycle_summary: Dict[str, Any], 
                                      cycle_quality: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on cycle analysis"""
        recommendations = []
        
        success_rate = cycle_summary.get('success_rate', 0)
        completion_rate = cycle_summary.get('completion_rate', 0)
        timeout_rate = cycle_summary.get('timeout_rate', 0)
        
        if success_rate < 0.7:
            recommendations.append("Low optimization success rate - review TPYOPT configuration and network conditions")
        
        if completion_rate < 0.8:
            recommendations.append("High incomplete cycle rate - investigate timeout settings and network stability")
        
        if timeout_rate > 0.2:
            recommendations.append("Frequent cycle timeouts - consider increasing timeout thresholds or optimizing scan parameters")
        
        avg_quality = cycle_quality.get('average_quality_score', 0)
        if avg_quality < 50:
            recommendations.append("Poor overall cycle quality - focus on improving completion rates and reducing failures")
        
        if not recommendations:
            recommendations.append("TPYOPT optimization cycles performing well - maintain current configuration")
        
        return recommendations
