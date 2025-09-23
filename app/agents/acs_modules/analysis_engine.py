"""
ACS Analysis Engine Module

Core analysis logic for ACS behavior including FSM state tracking,
radio management, and event categorization.
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime

class ACSAnalysisEngine:
    """Core analysis engine for ACS events"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Radio state tracking
        self.radio_states = defaultdict(lambda: {
            'current_state': None,
            'previous_state': None,
            'state_history': [],
            'current_channel': None,
            'channel_history': [],
            'last_update': None,
            'transitions': 0,
            'errors': []
        })
        
        # FSM state definitions
        self.fsm_states = {
            'idle', 'scanning', 'analyzing', 'selecting', 'switching',
            'verifying', 'completed', 'failed', 'aborted', 'pending'
        }
        
        # Event categorization
        self.event_categories = {
            'state_transitions': [],
            'channel_changes': [],
            'scan_events': [],
            'selection_events': [],
            'error_events': [],
            'completion_events': []
        }
    
    def analyze_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze ACS events and extract insights"""
        self.logger.info(f"Analyzing {len(events)} ACS events")
        
        # Reset state
        self._reset_analysis_state()
        
        # Process events chronologically
        sorted_events = sorted(events, key=lambda x: x.get('timestamp', ''))
        
        for event in sorted_events:
            self._process_event(event)
        
        # Generate analysis results
        return self._generate_analysis_results()
    
    def _reset_analysis_state(self):
        """Reset analysis state for new analysis"""
        self.radio_states.clear()
        for category in self.event_categories:
            self.event_categories[category].clear()
    
    def _process_event(self, event: Dict[str, Any]) -> None:
        """Process a single ACS event"""
        event_type = event.get('event_type', '')
        radio = event.get('radio', 'unknown')
        timestamp = event.get('timestamp', '')
        
        # Update radio state tracking
        self._update_radio_state(radio, event)
        
        # Categorize event
        self._categorize_event(event)
        
        # Handle specific event types
        if 'state' in event_type or 'fsm' in event_type:
            self._handle_state_transition(event)
        elif 'channel' in event_type:
            self._handle_channel_event(event)
        elif 'scan' in event_type:
            self._handle_scan_event(event)
        elif 'error' in event_type or 'fail' in event_type:
            self._handle_error_event(event)
    
    def _update_radio_state(self, radio: str, event: Dict[str, Any]) -> None:
        """Update radio state tracking"""
        radio_state = self.radio_states[radio]
        
        # Update FSM state if present
        if 'fsm_state' in event:
            new_state = event['fsm_state']
            if new_state != radio_state['current_state']:
                radio_state['previous_state'] = radio_state['current_state']
                radio_state['current_state'] = new_state
                radio_state['state_history'].append({
                    'state': new_state,
                    'timestamp': event.get('timestamp', ''),
                    'event_type': event.get('event_type', '')
                })
                radio_state['transitions'] += 1
        
        # Update channel if present
        if 'channel' in event:
            new_channel = event['channel']
            if new_channel != radio_state['current_channel']:
                radio_state['current_channel'] = new_channel
                radio_state['channel_history'].append({
                    'channel': new_channel,
                    'timestamp': event.get('timestamp', ''),
                    'event_type': event.get('event_type', '')
                })
        
        # Update last seen timestamp
        radio_state['last_update'] = event.get('timestamp', '')
    
    def _categorize_event(self, event: Dict[str, Any]) -> None:
        """Categorize event by type"""
        event_type = event.get('event_type', '').lower()
        
        if any(keyword in event_type for keyword in ['state', 'transition', 'fsm']):
            self.event_categories['state_transitions'].append(event)
        elif any(keyword in event_type for keyword in ['channel', 'freq', 'switch']):
            self.event_categories['channel_changes'].append(event)
        elif 'scan' in event_type:
            self.event_categories['scan_events'].append(event)
        elif any(keyword in event_type for keyword in ['select', 'choose', 'decision']):
            self.event_categories['selection_events'].append(event)
        elif any(keyword in event_type for keyword in ['error', 'fail', 'abort']):
            self.event_categories['error_events'].append(event)
        elif any(keyword in event_type for keyword in ['complete', 'finish', 'done']):
            self.event_categories['completion_events'].append(event)
    
    def _handle_state_transition(self, event: Dict[str, Any]) -> None:
        """Handle FSM state transition events"""
        # Additional state transition logic can be added here
        pass
    
    def _handle_channel_event(self, event: Dict[str, Any]) -> None:
        """Handle channel-related events"""
        # Additional channel event logic can be added here
        pass
    
    def _handle_scan_event(self, event: Dict[str, Any]) -> None:
        """Handle scanning events"""
        # Additional scan event logic can be added here
        pass
    
    def _handle_error_event(self, event: Dict[str, Any]) -> None:
        """Handle error events"""
        radio = event.get('radio', 'unknown')
        self.radio_states[radio]['errors'].append(event)
    
    def _generate_analysis_results(self) -> Dict[str, Any]:
        """Generate comprehensive analysis results"""
        return {
            'radio_analysis': self._analyze_radios(),
            'fsm_analysis': self._analyze_fsm_behavior(),
            'event_distribution': self._analyze_event_distribution(),
            'timeline_analysis': self._analyze_timeline(),
            'error_analysis': self._analyze_errors()
        }
    
    def _analyze_radios(self) -> Dict[str, Any]:
        """Analyze per-radio behavior"""
        radio_analysis = {}
        
        for radio, state in self.radio_states.items():
            radio_analysis[radio] = {
                'current_state': state['current_state'],
                'current_channel': state['current_channel'],
                'total_transitions': state['transitions'],
                'state_count': len(state['state_history']),
                'channel_count': len(state['channel_history']),
                'error_count': len(state['errors']),
                'last_update': state['last_update'],
                'state_distribution': self._get_state_distribution(state['state_history']),
                'channel_distribution': self._get_channel_distribution(state['channel_history'])
            }
        
        return {
            'total_radios': len(self.radio_states),
            'radio_details': radio_analysis,
            'active_radios': len([r for r in radio_analysis.values() if r['total_transitions'] > 0])
        }
    
    def _analyze_fsm_behavior(self) -> Dict[str, Any]:
        """Analyze FSM state behavior across all radios"""
        all_states = []
        state_transitions = defaultdict(int)
        
        for radio_state in self.radio_states.values():
            all_states.extend(state_history['state'] for state_history in radio_state['state_history'])
            
            # Count state transitions
            history = radio_state['state_history']
            for i in range(1, len(history)):
                prev_state = history[i-1]['state']
                curr_state = history[i]['state']
                transition = f"{prev_state} -> {curr_state}"
                state_transitions[transition] += 1
        
        return {
            'total_state_changes': len(all_states),
            'unique_states': len(set(all_states)),
            'state_distribution': dict(self._count_occurrences(all_states)),
            'common_transitions': dict(sorted(state_transitions.items(), key=lambda x: x[1], reverse=True)[:10]),
            'fsm_efficiency': self._calculate_fsm_efficiency()
        }
    
    def _analyze_event_distribution(self) -> Dict[str, Any]:
        """Analyze distribution of event types"""
        return {
            'state_transitions': len(self.event_categories['state_transitions']),
            'channel_changes': len(self.event_categories['channel_changes']),
            'scan_events': len(self.event_categories['scan_events']),
            'selection_events': len(self.event_categories['selection_events']),
            'error_events': len(self.event_categories['error_events']),
            'completion_events': len(self.event_categories['completion_events'])
        }
    
    def _analyze_timeline(self) -> Dict[str, Any]:
        """Analyze temporal patterns"""
        all_events = []
        for category_events in self.event_categories.values():
            all_events.extend(category_events)
        
        if not all_events:
            return {'time_range': 'No events', 'duration': '0 seconds'}
        
        timestamps = [event['timestamp'] for event in all_events if event.get('timestamp')]
        if not timestamps:
            return {'time_range': 'Unknown', 'duration': 'Unknown'}
        
        timestamps.sort()
        return {
            'time_range': f"{timestamps[0]} to {timestamps[-1]}",
            'first_event': timestamps[0],
            'last_event': timestamps[-1],
            'total_events': len(all_events),
            'events_with_timestamps': len(timestamps)
        }
    
    def _analyze_errors(self) -> Dict[str, Any]:
        """Analyze error patterns"""
        all_errors = []
        for radio_state in self.radio_states.values():
            all_errors.extend(radio_state['errors'])
        
        error_types = [error.get('event_type', 'unknown') for error in all_errors]
        error_radios = [error.get('radio', 'unknown') for error in all_errors]
        
        return {
            'total_errors': len(all_errors),
            'error_types': dict(self._count_occurrences(error_types)),
            'errors_by_radio': dict(self._count_occurrences(error_radios)),
            'error_rate': len(all_errors) / max(1, sum(len(cat) for cat in self.event_categories.values())) * 100
        }
    
    def _get_state_distribution(self, state_history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get state distribution for a radio"""
        states = [entry['state'] for entry in state_history]
        return dict(self._count_occurrences(states))
    
    def _get_channel_distribution(self, channel_history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get channel distribution for a radio"""
        channels = [entry['channel'] for entry in channel_history]
        return dict(self._count_occurrences(channels))
    
    def _count_occurrences(self, items: List[str]) -> defaultdict:
        """Count occurrences of items"""
        counts = defaultdict(int)
        for item in items:
            counts[item] += 1
        return counts
    
    def _calculate_fsm_efficiency(self) -> float:
        """Calculate FSM efficiency based on state transitions"""
        total_transitions = sum(radio['transitions'] for radio in self.radio_states.values())
        total_completions = len(self.event_categories['completion_events'])
        
        if total_transitions == 0:
            return 0.0
        
        # Efficiency = completions / transitions (higher is better)
        return (total_completions / total_transitions) * 100
    
    def get_radio_state(self, radio: str) -> Optional[Dict[str, Any]]:
        """Get current state for a specific radio"""
        return self.radio_states.get(radio)
    
    def get_all_radio_states(self) -> Dict[str, Dict[str, Any]]:
        """Get all radio states"""
        return dict(self.radio_states)
