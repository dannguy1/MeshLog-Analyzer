"""
ACS Channel Analyzer Module

Analyzes channel selection patterns, preferences, and radio behavior.
"""

import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

class ACSChannelAnalyzer:
    """Analyzes channel selection patterns and radio behavior"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Channel tracking
        self.channel_usage = defaultdict(int)
        self.radio_channels = defaultdict(list)
        self.channel_transitions = []
        
        # Radio analysis
        self.radio_preferences = defaultdict(lambda: {
            'preferred_channels': defaultdict(int),
            'avoided_channels': defaultdict(int),
            'switch_frequency': 0,
            'stability_score': 0
        })
        
        # Channel quality metrics
        self.channel_metrics = defaultdict(lambda: {
            'selection_count': 0,
            'success_rate': 0,
            'avg_duration': 0,
            'interference_reports': 0,
            'performance_score': 0
        })
        
        # Band analysis (2.4GHz, 5GHz, 6GHz)
        self.band_analysis = {
            '2.4GHz': {'channels': set(), 'usage': 0, 'radios': set()},
            '5GHz': {'channels': set(), 'usage': 0, 'radios': set()},
            '6GHz': {'channels': set(), 'usage': 0, 'radios': set()},
            'unknown': {'channels': set(), 'usage': 0, 'radios': set()}
        }
    
    def analyze_channels(self, events: List[Dict[str, Any]], cycles: List[Dict[str, Any]], 
                        radio_states: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze channel selection patterns and behavior"""
        self.logger.info(f"Analyzing channel patterns from {len(events)} events and {len(cycles)} cycles")
        
        # Reset analysis state
        self._reset_channel_state()
        
        # Process events for channel information
        self._process_channel_events(events)
        
        # Analyze cycles for channel transitions
        self._analyze_cycle_channels(cycles)
        
        # Analyze radio channel behavior
        self._analyze_radio_channels(radio_states)
        
        # Generate comprehensive analysis
        return self._generate_channel_analysis()
    
    def _reset_channel_state(self):
        """Reset channel analysis state"""
        self.channel_usage.clear()
        self.radio_channels.clear()
        self.channel_transitions.clear()
        self.radio_preferences.clear()
        self.channel_metrics.clear()
        
        for band_data in self.band_analysis.values():
            band_data['channels'].clear()
            band_data['usage'] = 0
            band_data['radios'].clear()
    
    def _process_channel_events(self, events: List[Dict[str, Any]]) -> None:
        """Process events to extract channel information"""
        for event in events:
            channel = event.get('channel')
            radio = event.get('radio', 'unknown')
            event_type = event.get('event_type', '').lower()
            
            if channel:
                # Track channel usage
                self.channel_usage[channel] += 1
                self.radio_channels[radio].append({
                    'channel': channel,
                    'timestamp': event.get('timestamp', ''),
                    'event_type': event_type
                })
                
                # Update band analysis
                band = self._determine_channel_band(channel)
                self.band_analysis[band]['channels'].add(channel)
                self.band_analysis[band]['usage'] += 1
                self.band_analysis[band]['radios'].add(radio)
                
                # Track channel quality indicators
                self._update_channel_quality(channel, event)
    
    def _analyze_cycle_channels(self, cycles: List[Dict[str, Any]]) -> None:
        """Analyze channel changes within cycles"""
        for cycle in cycles:
            radio = cycle.get('radio', 'unknown')
            events = cycle.get('events', [])
            
            # Track channel transitions within cycle
            channels_in_cycle = []
            for event in events:
                if 'channel' in event:
                    channels_in_cycle.append(event['channel'])
            
            # Analyze channel transitions
            for i in range(1, len(channels_in_cycle)):
                from_channel = channels_in_cycle[i-1]
                to_channel = channels_in_cycle[i]
                
                if from_channel != to_channel:
                    transition = {
                        'radio': radio,
                        'from_channel': from_channel,
                        'to_channel': to_channel,
                        'cycle_status': cycle.get('status', 'unknown'),
                        'timestamp': cycle.get('start_time', '')
                    }
                    self.channel_transitions.append(transition)
                    
                    # Update radio preferences
                    self._update_radio_preferences(radio, from_channel, to_channel, cycle)
    
    def _analyze_radio_channels(self, radio_states: Dict[str, Any]) -> None:
        """Analyze per-radio channel behavior"""
        radio_details = radio_states.get('radio_details', {})
        
        for radio, state in radio_details.items():
            current_channel = state.get('current_channel')
            channel_history = state.get('channel_distribution', {})
            
            if channel_history:
                # Calculate radio preferences
                total_usage = sum(channel_history.values())
                preferences = self.radio_preferences[radio]
                
                for channel, count in channel_history.items():
                    usage_percentage = (count / total_usage) * 100
                    
                    if usage_percentage > 30:  # Preferred if >30% usage
                        preferences['preferred_channels'][channel] = usage_percentage
                    elif usage_percentage < 5:  # Avoided if <5% usage
                        preferences['avoided_channels'][channel] = usage_percentage
                
                # Calculate stability score
                preferences['stability_score'] = self._calculate_radio_stability(channel_history)
                preferences['switch_frequency'] = len(channel_history) - 1  # Number of switches
    
    def _determine_channel_band(self, channel: str) -> str:
        """Determine which band a channel belongs to"""
        try:
            if channel.isdigit():
                ch_num = int(channel)
                if 1 <= ch_num <= 14:
                    return '2.4GHz'
                elif 36 <= ch_num <= 177:
                    return '5GHz'
                elif ch_num >= 1:  # 6GHz channels start from various numbers
                    return '6GHz'
            elif 'MHz' in channel or 'GHz' in channel:
                # Frequency format
                if '2.4' in channel or '2400' in channel:
                    return '2.4GHz'
                elif '5.' in channel or '5000' in channel:
                    return '5GHz'
                elif '6.' in channel or '6000' in channel:
                    return '6GHz'
        except:
            pass
        
        return 'unknown'
    
    def _update_channel_quality(self, channel: str, event: Dict[str, Any]) -> None:
        """Update channel quality metrics"""
        metrics = self.channel_metrics[channel]
        event_type = event.get('event_type', '').lower()
        
        # Count selections
        if 'select' in event_type or 'chosen' in event_type:
            metrics['selection_count'] += 1
        
        # Track interference reports
        if 'interference' in event_type or 'interfere' in event_type:
            metrics['interference_reports'] += 1
        
        # Track performance indicators
        if 'success' in event_type or 'complete' in event_type:
            metrics['performance_score'] += 1
        elif 'fail' in event_type or 'error' in event_type:
            metrics['performance_score'] -= 1
    
    def _update_radio_preferences(self, radio: str, from_channel: str, 
                                 to_channel: str, cycle: Dict[str, Any]) -> None:
        """Update radio channel preferences based on transitions"""
        preferences = self.radio_preferences[radio]
        
        # Track successful transitions
        if cycle.get('status') == 'completed':
            preferences['preferred_channels'][to_channel] += 1
        elif cycle.get('status') == 'failed':
            preferences['avoided_channels'][from_channel] += 1
    
    def _calculate_radio_stability(self, channel_distribution: Dict[str, int]) -> float:
        """Calculate channel stability score for a radio"""
        if not channel_distribution:
            return 0.0
        
        total_usage = sum(channel_distribution.values())
        if total_usage == 0:
            return 0.0
        
        # Stability = how concentrated the usage is (entropy-based)
        entropy = 0
        for count in channel_distribution.values():
            if count > 0:
                p = count / total_usage
                entropy -= p * (p.bit_length() - 1) if p > 0 else 0
        
        # Convert to 0-100 scale (lower entropy = higher stability)
        max_entropy = (len(channel_distribution).bit_length() - 1) if len(channel_distribution) > 1 else 1
        stability = max(0, 100 - (entropy / max_entropy * 100)) if max_entropy > 0 else 100
        
        return round(stability, 2)
    
    def _generate_channel_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive channel analysis"""
        return {
            'channel_usage_summary': self._summarize_channel_usage(),
            'band_analysis': self._analyze_bands(),
            'radio_channel_behavior': self._analyze_radio_behavior(),
            'channel_quality_analysis': self._analyze_channel_quality(),
            'transition_patterns': self._analyze_transition_patterns(),
            'optimization_insights': self._generate_optimization_insights(),
            'recommendations': self._generate_channel_recommendations()
        }
    
    def _summarize_channel_usage(self) -> Dict[str, Any]:
        """Summarize overall channel usage patterns"""
        if not self.channel_usage:
            return {'total_channels': 0, 'message': 'No channel data found'}
        
        total_events = sum(self.channel_usage.values())
        most_used = max(self.channel_usage.items(), key=lambda x: x[1])
        least_used = min(self.channel_usage.items(), key=lambda x: x[1])
        
        # Channel distribution
        sorted_channels = sorted(self.channel_usage.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_channels': len(self.channel_usage),
            'total_channel_events': total_events,
            'most_used_channel': {'channel': most_used[0], 'usage': most_used[1]},
            'least_used_channel': {'channel': least_used[0], 'usage': least_used[1]},
            'channel_distribution': dict(sorted_channels[:10]),  # Top 10
            'usage_statistics': {
                'mean_usage': round(statistics.mean(self.channel_usage.values()), 2),
                'median_usage': round(statistics.median(self.channel_usage.values()), 2),
                'std_dev': round(statistics.stdev(self.channel_usage.values()), 2) if len(self.channel_usage) > 1 else 0
            }
        }
    
    def _analyze_bands(self) -> Dict[str, Any]:
        """Analyze usage by frequency band"""
        band_summary = {}
        
        for band, data in self.band_analysis.items():
            if data['usage'] > 0:
                band_summary[band] = {
                    'channel_count': len(data['channels']),
                    'total_usage': data['usage'],
                    'radio_count': len(data['radios']),
                    'channels': sorted(list(data['channels'])),
                    'usage_percentage': 0  # Will be calculated below
                }
        
        # Calculate usage percentages
        total_usage = sum(data['total_usage'] for data in band_summary.values())
        for band_data in band_summary.values():
            band_data['usage_percentage'] = round((band_data['total_usage'] / max(1, total_usage)) * 100, 1)
        
        # Identify preferred band
        preferred_band = max(band_summary.items(), key=lambda x: x[1]['usage_percentage'])[0] if band_summary else 'unknown'
        
        return {
            'band_distribution': band_summary,
            'preferred_band': preferred_band,
            'band_diversity': len(band_summary),
            'multi_band_operation': len(band_summary) > 1
        }
    
    def _analyze_radio_behavior(self) -> Dict[str, Any]:
        """Analyze per-radio channel behavior"""
        radio_analysis = {}
        
        for radio, preferences in self.radio_preferences.items():
            if preferences['preferred_channels'] or preferences['switch_frequency'] > 0:
                # Most and least preferred channels
                preferred = preferences['preferred_channels']
                avoided = preferences['avoided_channels']
                
                most_preferred = max(preferred.items(), key=lambda x: x[1])[0] if preferred else 'None'
                most_avoided = max(avoided.items(), key=lambda x: x[1])[0] if avoided else 'None'
                
                radio_analysis[radio] = {
                    'stability_score': preferences['stability_score'],
                    'switch_frequency': preferences['switch_frequency'],
                    'preferred_channel_count': len(preferred),
                    'avoided_channel_count': len(avoided),
                    'most_preferred_channel': most_preferred,
                    'most_avoided_channel': most_avoided,
                    'behavior_category': self._categorize_radio_behavior(preferences),
                    'channel_diversity': len(preferences['preferred_channels']) + len(preferences['avoided_channels'])
                }
        
        # Overall radio behavior summary
        if radio_analysis:
            avg_stability = statistics.mean([data['stability_score'] for data in radio_analysis.values()])
            avg_switches = statistics.mean([data['switch_frequency'] for data in radio_analysis.values()])
        else:
            avg_stability = 0
            avg_switches = 0
        
        return {
            'radio_details': radio_analysis,
            'summary': {
                'total_radios_analyzed': len(radio_analysis),
                'average_stability_score': round(avg_stability, 2),
                'average_switch_frequency': round(avg_switches, 2),
                'most_stable_radio': self._find_most_stable_radio(radio_analysis),
                'most_active_radio': self._find_most_active_radio(radio_analysis)
            }
        }
    
    def _analyze_channel_quality(self) -> Dict[str, Any]:
        """Analyze channel quality metrics"""
        if not self.channel_metrics:
            return {'message': 'No channel quality data available'}
        
        quality_analysis = {}
        
        for channel, metrics in self.channel_metrics.items():
            selection_count = metrics['selection_count']
            interference_count = metrics['interference_reports']
            performance_score = metrics['performance_score']
            
            # Calculate quality score
            quality_score = self._calculate_channel_quality_score(metrics)
            
            quality_analysis[channel] = {
                'selection_count': selection_count,
                'interference_reports': interference_count,
                'performance_score': performance_score,
                'quality_score': quality_score,
                'quality_category': self._categorize_channel_quality(quality_score)
            }
        
        # Find best and worst channels
        if quality_analysis:
            best_channel = max(quality_analysis.items(), key=lambda x: x[1]['quality_score'])
            worst_channel = min(quality_analysis.items(), key=lambda x: x[1]['quality_score'])
        else:
            best_channel = ('Unknown', {'quality_score': 0})
            worst_channel = ('Unknown', {'quality_score': 0})
        
        return {
            'channel_quality_details': quality_analysis,
            'quality_summary': {
                'channels_analyzed': len(quality_analysis),
                'best_channel': {'channel': best_channel[0], 'score': best_channel[1]['quality_score']},
                'worst_channel': {'channel': worst_channel[0], 'score': worst_channel[1]['quality_score']},
                'average_quality': round(statistics.mean([data['quality_score'] for data in quality_analysis.values()]), 2) if quality_analysis else 0
            }
        }
    
    def _analyze_transition_patterns(self) -> Dict[str, Any]:
        """Analyze channel transition patterns"""
        if not self.channel_transitions:
            return {'message': 'No channel transitions detected'}
        
        # Transition frequency analysis
        transition_counts = defaultdict(int)
        successful_transitions = 0
        failed_transitions = 0
        
        for transition in self.channel_transitions:
            from_ch = transition['from_channel']
            to_ch = transition['to_channel']
            transition_key = f"{from_ch} -> {to_ch}"
            transition_counts[transition_key] += 1
            
            if transition['cycle_status'] == 'completed':
                successful_transitions += 1
            else:
                failed_transitions += 1
        
        # Most common transitions
        common_transitions = sorted(transition_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Transition success rate
        total_transitions = len(self.channel_transitions)
        success_rate = (successful_transitions / total_transitions * 100) if total_transitions > 0 else 0
        
        return {
            'total_transitions': total_transitions,
            'successful_transitions': successful_transitions,
            'failed_transitions': failed_transitions,
            'transition_success_rate': round(success_rate, 1),
            'most_common_transitions': common_transitions,
            'transition_patterns': self._identify_transition_patterns()
        }
    
    def _categorize_radio_behavior(self, preferences: Dict[str, Any]) -> str:
        """Categorize radio behavior based on preferences"""
        stability = preferences['stability_score']
        switches = preferences['switch_frequency']
        
        if stability > 80 and switches < 3:
            return 'Stable'
        elif stability > 60:
            return 'Moderately Stable'
        elif switches > 10:
            return 'Highly Dynamic'
        elif switches > 5:
            return 'Dynamic'
        else:
            return 'Inactive'
    
    def _calculate_channel_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate quality score for a channel (0-100)"""
        selection_count = metrics['selection_count']
        interference_count = metrics['interference_reports']
        performance_score = metrics['performance_score']
        
        # Base score from selections (popularity)
        popularity_score = min(selection_count * 10, 50)  # Max 50 points
        
        # Performance score (can be negative)
        perf_score = max(-25, min(25, performance_score * 5))  # -25 to +25 points
        
        # Interference penalty
        interference_penalty = min(interference_count * 5, 25)  # Max 25 point penalty
        
        # Calculate final score
        quality_score = popularity_score + perf_score - interference_penalty
        return max(0, min(100, quality_score))
    
    def _categorize_channel_quality(self, quality_score: float) -> str:
        """Categorize channel quality"""
        if quality_score >= 80:
            return 'Excellent'
        elif quality_score >= 60:
            return 'Good'
        elif quality_score >= 40:
            return 'Fair'
        elif quality_score >= 20:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def _find_most_stable_radio(self, radio_analysis: Dict[str, Any]) -> str:
        """Find the most stable radio"""
        if not radio_analysis:
            return 'None'
        
        most_stable = max(radio_analysis.items(), key=lambda x: x[1]['stability_score'])
        return most_stable[0]
    
    def _find_most_active_radio(self, radio_analysis: Dict[str, Any]) -> str:
        """Find the most active radio (most switches)"""
        if not radio_analysis:
            return 'None'
        
        most_active = max(radio_analysis.items(), key=lambda x: x[1]['switch_frequency'])
        return most_active[0]
    
    def _identify_transition_patterns(self) -> Dict[str, Any]:
        """Identify common transition patterns"""
        # Group transitions by radio
        radio_transitions = defaultdict(list)
        for transition in self.channel_transitions:
            radio = transition['radio']
            radio_transitions[radio].append(transition)
        
        patterns = {}
        for radio, transitions in radio_transitions.items():
            if len(transitions) >= 2:
                # Look for patterns in this radio's transitions
                channels = [t['from_channel'] for t in transitions] + [transitions[-1]['to_channel']]
                
                # Identify if radio tends to return to certain channels
                channel_counts = defaultdict(int)
                for channel in channels:
                    channel_counts[channel] += 1
                
                # Find most visited channel
                if channel_counts:
                    favorite_channel = max(channel_counts.items(), key=lambda x: x[1])
                    patterns[radio] = {
                        'transition_count': len(transitions),
                        'favorite_channel': favorite_channel[0],
                        'favorite_channel_visits': favorite_channel[1],
                        'unique_channels': len(set(channels))
                    }
        
        return patterns
    
    def _generate_optimization_insights(self) -> List[str]:
        """Generate channel optimization insights"""
        insights = []
        
        # Band distribution insights
        band_analysis = self._analyze_bands()
        band_dist = band_analysis.get('band_distribution', {})
        
        if len(band_dist) == 1:
            band_name = list(band_dist.keys())[0]
            insights.append(f"Operating exclusively on {band_name} - consider multi-band optimization")
        elif '2.4GHz' in band_dist and band_dist['2.4GHz']['usage_percentage'] > 70:
            insights.append("Heavy reliance on 2.4GHz band - may benefit from 5GHz migration")
        
        # Channel quality insights
        quality_analysis = self._analyze_channel_quality()
        if 'quality_summary' in quality_analysis:
            avg_quality = quality_analysis['quality_summary'].get('average_quality', 0)
            if avg_quality < 50:
                insights.append("Low average channel quality detected - review RF environment")
            
            best_ch = quality_analysis['quality_summary'].get('best_channel', {})
            if best_ch.get('score', 0) > 80:
                insights.append(f"Channel {best_ch.get('channel', 'unknown')} shows excellent performance")
        
        # Transition insights
        transition_analysis = self._analyze_transition_patterns()
        if 'transition_success_rate' in transition_analysis:
            success_rate = transition_analysis['transition_success_rate']
            if success_rate < 70:
                insights.append(f"Low transition success rate ({success_rate:.1f}%) - investigate switching issues")
            elif success_rate > 90:
                insights.append(f"High transition success rate ({success_rate:.1f}%) - optimization working well")
        
        # Radio behavior insights
        radio_behavior = self._analyze_radio_behavior()
        summary = radio_behavior.get('summary', {})
        avg_stability = summary.get('average_stability_score', 0)
        
        if avg_stability > 80:
            insights.append("Radios showing stable channel behavior - good optimization")
        elif avg_stability < 50:
            insights.append("Unstable channel behavior detected - review optimization parameters")
        
        return insights if insights else ['Channel analysis complete - no specific insights identified']
    
    def _generate_channel_recommendations(self) -> List[str]:
        """Generate actionable channel recommendations"""
        recommendations = []
        
        # Usage recommendations
        if self.channel_usage:
            total_usage = sum(self.channel_usage.values())
            if len(self.channel_usage) < 5 and total_usage > 50:
                recommendations.append("Limited channel diversity - consider expanding channel range")
        
        # Band recommendations
        band_analysis = self._analyze_bands()
        if band_analysis.get('band_diversity', 0) == 1:
            recommendations.append("Single-band operation detected - enable multi-band ACS for better optimization")
        
        # Quality recommendations
        quality_analysis = self._analyze_channel_quality()
        if 'channel_quality_details' in quality_analysis:
            poor_channels = [
                ch for ch, data in quality_analysis['channel_quality_details'].items()
                if data['quality_score'] < 30
            ]
            if poor_channels:
                recommendations.append(f"Consider avoiding poor-performing channels: {', '.join(poor_channels[:3])}")
        
        # Transition recommendations
        transition_analysis = self._analyze_transition_patterns()
        if transition_analysis.get('transition_success_rate', 100) < 80:
            recommendations.append("Improve transition success rate by reviewing scan parameters and switching logic")
        
        # Radio-specific recommendations
        radio_behavior = self._analyze_radio_behavior()
        radio_details = radio_behavior.get('radio_details', {})
        
        unstable_radios = [
            radio for radio, data in radio_details.items()
            if data['stability_score'] < 60
        ]
        if unstable_radios:
            recommendations.append(f"Review configuration for unstable radios: {', '.join(unstable_radios[:3])}")
        
        return recommendations if recommendations else ['No specific recommendations - channel optimization appears effective']
    
    def get_channel_usage(self) -> Dict[str, int]:
        """Get channel usage statistics"""
        return dict(self.channel_usage)
    
    def get_radio_channels(self, radio: str) -> List[Dict[str, Any]]:
        """Get channel history for a specific radio"""
        return self.radio_channels.get(radio, [])
    
    def get_channel_transitions(self) -> List[Dict[str, Any]]:
        """Get all channel transitions"""
        return self.channel_transitions
