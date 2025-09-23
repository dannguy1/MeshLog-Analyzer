"""
TPYOPT Roaming Analyzer Module

Analyzes roaming commands, device coordination patterns, and mesh topology
optimization behaviors for TPYOPT systems.
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import statistics


class TPYOPTRoamingAnalyzer:
    """TPYOPT roaming command and device coordination analyzer"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
        # Roaming analysis data structures
        self.roaming_commands = []
        self.device_pairs = defaultdict(list)
        self.topology_changes = []
        self.coordination_events = []
        
    def analyze_roaming(self, events: List[Dict[str, Any]], cycles: List[Dict[str, Any]],
                       device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive roaming and coordination analysis"""
        self.logger.info("Analyzing TPYOPT roaming commands and device coordination")
        
        # Reset analysis data
        self.roaming_commands.clear()
        self.device_pairs.clear()
        self.topology_changes.clear()
        self.coordination_events.clear()
        
        # Extract roaming-related events
        self._extract_roaming_events(events)
        
        # Analyze roaming patterns
        roaming_patterns = self._analyze_roaming_patterns()
        device_coordination = self._analyze_device_coordination()
        topology_optimization = self._analyze_topology_optimization(cycles)
        mesh_behavior = self._analyze_mesh_behavior()
        
        # Generate insights and recommendations
        insights = self._generate_roaming_insights(roaming_patterns, device_coordination)
        recommendations = self._generate_roaming_recommendations(roaming_patterns, mesh_behavior)
        
        return {
            'roaming_summary': self._generate_roaming_summary(),
            'roaming_patterns': roaming_patterns,
            'device_coordination': device_coordination,
            'topology_optimization': topology_optimization,
            'mesh_behavior': mesh_behavior,
            'roaming_insights': insights,
            'recommendations': recommendations,
            'device_pair_analysis': self._analyze_device_pairs()
        }
    
    def _extract_roaming_events(self, events: List[Dict[str, Any]]) -> None:
        """Extract and categorize roaming-related events"""
        for event in events:
            event_type = event.get('event_type', '')
            pattern_name = event.get('pattern_name', '').lower()
            
            # Roaming command events
            if event_type == 'roaming_command' or 'roaming' in pattern_name:
                self.roaming_commands.append(event)
                
                # Track device pairs
                from_mac = event.get('from_mac')
                to_mac = event.get('to_mac')
                if from_mac and to_mac:
                    pair_key = tuple(sorted([from_mac, to_mac]))
                    self.device_pairs[pair_key].append(event)
            
            # Topology change events
            elif event_type == 'topology_change' or 'topology' in pattern_name:
                self.topology_changes.append(event)
            
            # Coordination events
            elif 'coordination' in pattern_name or 'coordinate' in pattern_name:
                self.coordination_events.append(event)
    
    def _analyze_roaming_patterns(self) -> Dict[str, Any]:
        """Analyze roaming command patterns"""
        patterns = {
            'total_roaming_commands': len(self.roaming_commands),
            'roaming_frequency': {},
            'directional_patterns': Counter(),
            'roaming_triggers': Counter(),
            'success_patterns': {}
        }
        
        if not self.roaming_commands:
            return patterns
        
        # Analyze roaming frequency by device
        device_roaming_count = Counter()
        for command in self.roaming_commands:
            from_mac = command.get('from_mac')
            to_mac = command.get('to_mac')
            
            if from_mac:
                device_roaming_count[from_mac] += 1
            if to_mac:
                device_roaming_count[to_mac] += 1
        
        patterns['roaming_frequency'] = dict(device_roaming_count)
        
        # Analyze directional patterns
        for command in self.roaming_commands:
            from_mac = command.get('from_mac', '')
            to_mac = command.get('to_mac', '')
            
            if from_mac and to_mac:
                direction = f"{from_mac[:8]}...→{to_mac[:8]}..."
                patterns['directional_patterns'][direction] += 1
        
        # Analyze roaming triggers
        for command in self.roaming_commands:
            reason = command.get('reason', '').lower()
            if 'rssi' in reason or 'signal' in reason:
                patterns['roaming_triggers']['signal_strength'] += 1
            elif 'packet' in reason or 'loss' in reason:
                patterns['roaming_triggers']['packet_loss'] += 1
            elif 'optimization' in reason:
                patterns['roaming_triggers']['optimization'] += 1
            elif 'load' in reason or 'balance' in reason:
                patterns['roaming_triggers']['load_balancing'] += 1
            else:
                patterns['roaming_triggers']['other'] += 1
        
        return patterns
    
    def _analyze_device_coordination(self) -> Dict[str, Any]:
        """Analyze device coordination patterns"""
        coordination = {
            'total_coordination_events': len(self.coordination_events),
            'coordination_success_rate': 0,
            'coordination_patterns': Counter(),
            'device_coordination_matrix': {},
            'coordination_timing': {}
        }
        
        if not self.coordination_events:
            return coordination
        
        # Analyze coordination success
        successful_coordination = 0
        for event in self.coordination_events:
            reason = event.get('reason', '').lower()
            if any(success_word in reason for success_word in ['success', 'complete', 'done']):
                successful_coordination += 1
        
        coordination['coordination_success_rate'] = successful_coordination / len(self.coordination_events)
        
        # Analyze coordination patterns
        for event in self.coordination_events:
            pattern_name = event.get('pattern_name', '')
            coordination['coordination_patterns'][pattern_name] += 1
        
        # Build coordination matrix
        coordination_pairs = Counter()
        for event in self.coordination_events:
            from_mac = event.get('from_mac')
            to_mac = event.get('to_mac')
            device_mac = event.get('device_mac')
            
            if from_mac and to_mac:
                pair = tuple(sorted([from_mac, to_mac]))
                coordination_pairs[pair] += 1
            elif device_mac:
                # Single device coordination
                coordination_pairs[(device_mac, 'self')] += 1
        
        coordination['device_coordination_matrix'] = dict(coordination_pairs)
        
        return coordination
    
    def _analyze_topology_optimization(self, cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze topology optimization in relation to roaming"""
        topology_optimization = {
            'topology_changes': len(self.topology_changes),
            'optimization_triggered_roaming': 0,
            'roaming_triggered_optimization': 0,
            'topology_stability': {},
            'optimization_effectiveness': {}
        }
        
        if not cycles:
            return topology_optimization
        
        # Analyze relationship between roaming and optimization cycles
        if isinstance(cycles, dict):
            all_cycles = []
            for device_cycles in cycles.values():
                all_cycles.extend(device_cycles)
            cycles = all_cycles
        
        # Count optimization-triggered roaming
        optimization_timestamps = set()
        for cycle in cycles:
            start_time = cycle.get('start_time', '')
            if start_time:
                optimization_timestamps.add(start_time)
        
        for command in self.roaming_commands:
            command_time = command.get('timestamp', '')
            reason = command.get('reason', '').lower()
            
            # Check if roaming was triggered by optimization
            if 'optimization' in reason or 'optimize' in reason:
                topology_optimization['optimization_triggered_roaming'] += 1
        
        # Analyze topology stability
        if self.topology_changes:
            change_timestamps = [change.get('timestamp', '') for change in self.topology_changes]
            topology_optimization['topology_stability'] = {
                'total_changes': len(self.topology_changes),
                'change_frequency': len(self.topology_changes) / max(1, len(cycles)),
                'stability_score': max(0, 100 - (len(self.topology_changes) * 5))  # Arbitrary scoring
            }
        
        return topology_optimization
    
    def _analyze_mesh_behavior(self) -> Dict[str, Any]:
        """Analyze overall mesh behavior patterns"""
        mesh_behavior = {
            'mesh_adaptation_score': 0,
            'load_balancing_efficiency': 0,
            'network_responsiveness': {},
            'mesh_optimization_patterns': Counter()
        }
        
        # Calculate mesh adaptation score based on roaming activity
        total_roaming = len(self.roaming_commands)
        total_topology_changes = len(self.topology_changes)
        
        if total_roaming > 0:
            # High roaming with few topology changes = good adaptation
            if total_topology_changes < total_roaming * 0.3:
                mesh_behavior['mesh_adaptation_score'] = 85
            elif total_topology_changes < total_roaming * 0.5:
                mesh_behavior['mesh_adaptation_score'] = 70
            else:
                mesh_behavior['mesh_adaptation_score'] = 50
        
        # Analyze load balancing efficiency
        if self.device_pairs:
            balanced_pairs = 0
            for pair, events in self.device_pairs.items():
                # Consider pairs balanced if roaming is bidirectional
                from_to_count = len([e for e in events if e.get('from_mac') == pair[0]])
                to_from_count = len([e for e in events if e.get('from_mac') == pair[1]])
                
                if abs(from_to_count - to_from_count) <= 2:  # Roughly balanced
                    balanced_pairs += 1
            
            mesh_behavior['load_balancing_efficiency'] = balanced_pairs / len(self.device_pairs) * 100
        
        # Network responsiveness
        mesh_behavior['network_responsiveness'] = {
            'roaming_commands_per_topology_change': total_roaming / max(1, total_topology_changes),
            'coordination_success_rate': len([e for e in self.coordination_events 
                                            if 'success' in e.get('reason', '').lower()]) / max(1, len(self.coordination_events)) * 100
        }
        
        return mesh_behavior
    
    def _analyze_device_pairs(self) -> Dict[str, Any]:
        """Analyze device pair interactions"""
        pair_analysis = {
            'total_device_pairs': len(self.device_pairs),
            'most_active_pairs': [],
            'pair_stability': {},
            'bidirectional_pairs': 0
        }
        
        if not self.device_pairs:
            return pair_analysis
        
        # Sort pairs by activity level
        sorted_pairs = sorted(self.device_pairs.items(), 
                            key=lambda x: len(x[1]), reverse=True)
        
        # Get most active pairs
        pair_analysis['most_active_pairs'] = [
            {
                'devices': f"{pair[0]} ↔ {pair[1]}",
                'interaction_count': len(events),
                'roaming_events': len([e for e in events if e.get('event_type') == 'roaming_command'])
            }
            for pair, events in sorted_pairs[:5]
        ]
        
        # Analyze bidirectional communication
        for pair, events in self.device_pairs.items():
            device1_to_device2 = len([e for e in events if e.get('from_mac') == pair[0]])
            device2_to_device1 = len([e for e in events if e.get('from_mac') == pair[1]])
            
            if device1_to_device2 > 0 and device2_to_device1 > 0:
                pair_analysis['bidirectional_pairs'] += 1
                
                # Calculate stability score
                total_interactions = len(events)
                balance_score = 1 - abs(device1_to_device2 - device2_to_device1) / total_interactions
                pair_analysis['pair_stability'][f"{pair[0][:8]}...↔{pair[1][:8]}..."] = balance_score * 100
        
        return pair_analysis
    
    def _generate_roaming_summary(self) -> Dict[str, Any]:
        """Generate overall roaming summary"""
        return {
            'total_roaming_commands': len(self.roaming_commands),
            'total_topology_changes': len(self.topology_changes),
            'total_coordination_events': len(self.coordination_events),
            'unique_device_pairs': len(self.device_pairs),
            'roaming_activity_level': self._calculate_activity_level(),
            'status': 'analyzed' if self.roaming_commands else 'no_roaming_activity'
        }
    
    def _calculate_activity_level(self) -> str:
        """Calculate overall roaming activity level"""
        total_events = len(self.roaming_commands) + len(self.topology_changes) + len(self.coordination_events)
        
        if total_events == 0:
            return 'inactive'
        elif total_events < 10:
            return 'low'
        elif total_events < 50:
            return 'moderate'
        elif total_events < 100:
            return 'high'
        else:
            return 'very_high'
    
    def _generate_roaming_insights(self, roaming_patterns: Dict[str, Any],
                                 device_coordination: Dict[str, Any]) -> List[str]:
        """Generate insights about roaming behavior"""
        insights = []
        
        total_roaming = roaming_patterns.get('total_roaming_commands', 0)
        coordination_success = device_coordination.get('coordination_success_rate', 0)
        
        if total_roaming == 0:
            insights.append("No roaming commands detected - mesh topology appears stable")
        elif total_roaming < 10:
            insights.append("Low roaming activity - network topology is relatively stable")
        elif total_roaming > 50:
            insights.append("High roaming activity detected - active mesh optimization occurring")
        
        if coordination_success > 0.8:
            insights.append("Excellent device coordination - mesh devices communicating effectively")
        elif coordination_success > 0.6:
            insights.append("Good device coordination with some room for improvement")
        elif coordination_success < 0.5:
            insights.append("Poor device coordination detected - investigate communication issues")
        
        # Analyze roaming triggers
        triggers = roaming_patterns.get('roaming_triggers', {})
        if triggers:
            main_trigger = max(triggers.items(), key=lambda x: x[1])[0]
            insights.append(f"Primary roaming trigger: {main_trigger}")
        
        return insights
    
    def _generate_roaming_recommendations(self, roaming_patterns: Dict[str, Any],
                                        mesh_behavior: Dict[str, Any]) -> List[str]:
        """Generate recommendations for roaming optimization"""
        recommendations = []
        
        total_roaming = roaming_patterns.get('total_roaming_commands', 0)
        adaptation_score = mesh_behavior.get('mesh_adaptation_score', 0)
        load_balancing = mesh_behavior.get('load_balancing_efficiency', 0)
        
        if total_roaming == 0:
            recommendations.append("Consider enabling TPYOPT optimization to improve mesh performance")
        
        if adaptation_score < 60:
            recommendations.append("Mesh adaptation score is low - review TPYOPT configuration parameters")
        
        if load_balancing < 50:
            recommendations.append("Poor load balancing detected - optimize roaming thresholds and triggers")
        
        # Analyze roaming triggers for recommendations
        triggers = roaming_patterns.get('roaming_triggers', {})
        if triggers.get('packet_loss', 0) > triggers.get('signal_strength', 0):
            recommendations.append("Packet loss is primary roaming trigger - investigate RF interference")
        
        if not recommendations:
            recommendations.append("Roaming behavior appears optimal - maintain current configuration")
        
        return recommendations
