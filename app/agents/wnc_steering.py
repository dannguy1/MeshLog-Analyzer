"""
Enhanced WNC Steering Agent for MeshLog Integrated Agent System

This agent provides comprehensive analysis of WiFi client steering behavior,
featuring advanced failure pattern detection, modular components, and
detailed reporting capabilities with actionable insights.
"""

import re
import json
import logging
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

from app.core.agent_interface import AgentInterface
from app.core.pattern_recognition import PatternRegistry, AgentPatternInterface
from .steering_failure_analyzer import SteeringFailureAnalyzer
from .steering_report_generator import SteeringReportGenerator

class WNCSteeringAgent(AgentInterface):
    """Enhanced WNC Steering Analysis Agent with comprehensive failure detection and modular architecture"""
    
    @property
    def agent_type(self) -> str:
        return "wnc-steering"
    
    @property
    def version(self) -> str:
        return "2.1.0-enhanced"
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize pattern recognition framework
        self.pattern_registry = PatternRegistry()
        self.pattern_interface = AgentPatternInterface("wnc-steering", self.pattern_registry)
        
        # Agent metadata
        self.capabilities = [
            "steering_analysis", 
            "client_transition_tracking", 
            "failure_pattern_detection",
            "bss_transition_analysis",
            "neighbor_report_analysis",
            "beacon_measurement_analysis",
            "enhanced_failure_patterns",
            "modular_components",
            "rssi_tracking",
            "client_capability_detection",
            "performance_metrics",
            "timeline_analysis",
            "html_report_generation",
            "csv_data_export",
            "actionable_insights"
        ]
        
        self.description = "Enhanced WNC WiFi Client Steering Agent with modular failure analysis and comprehensive pattern detection"
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "log_data": {
                    "type": "object",
                    "description": "Log data from MeshLog storage"
                },
                "analysis_config": {
                    "type": "object",
                    "properties": {
                        "time_range": {"type": "string"},
                        "client_filter": {"type": "string"},
                        "enable_enhanced_patterns": {"type": "boolean", "default": True},
                        "generate_html_report": {"type": "boolean", "default": True},
                        "include_raw_data": {"type": "boolean", "default": False}
                    }
                }
            }
        }
        
        self.output_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "analysis_data": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "object"},
                        "steering_events": {"type": "array"},
                        "failure_patterns": {"type": "object"},
                        "client_transitions": {"type": "array"},
                        "recommendations": {"type": "array"}
                    }
                },
                "metadata": {"type": "object"}
            }
        }
        
        # Initialize modular components with error handling
        try:
            self.failure_analyzer = SteeringFailureAnalyzer()
            self.report_generator = SteeringReportGenerator()
            self.logger.info("Modular components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize modular components: {e}")
            # Fallback to basic functionality
            self.failure_analyzer = None
            self.report_generator = None
        
        # Get enhanced patterns from failure analyzer for additional processing
        self.enhanced_patterns = {}
        if self.failure_analyzer:
            try:
                self.enhanced_patterns = self.failure_analyzer.get_patterns()
                self.logger.info(f"Loaded {len(self.enhanced_patterns)} enhanced failure patterns")
            except Exception as e:
                self.logger.warning(f"Failed to load enhanced patterns: {e}")
                self.enhanced_patterns = {}
        
        # Log pattern framework integration status
        try:
            steering_patterns = self.pattern_registry.get_patterns_for_agent("wnc-steering")
            self.logger.info(f"Pattern framework loaded {len(steering_patterns)} steering patterns")
        except Exception as e:
            self.logger.warning(f"Failed to load patterns from framework: {e}")
        
        # Initialize tracking data
        self.steering_events = []
        self.client_stats = defaultdict(lambda: {
            'weak_signals': 0,
            'steering_attempts': 0,
            'steering_successes': 0,
            'steering_failures': 0,
            'supports_11k': False,
            'supports_11v': False,
            'first_seen': None,
            'last_seen': None,
            'rssi_values': []
        })
    
    def analyze(self, log_paths: list, output_path: str, analysis_config: dict = None) -> dict:
        """Enhanced steering analysis with comprehensive failure detection and modular reporting"""
        start_time = time.time()
        config = analysis_config or {}
        
        try:
            self.logger.info(f"Starting enhanced steering analysis with {len(log_paths)} files")
            
            # Ensure output directory exists
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Reset analysis state
            self.steering_events.clear()
            self.client_stats.clear()
            if self.failure_analyzer:
                self.failure_analyzer.clear()  # Reset failure analysis data
            
            # Process log files
            total_lines = 0
            matched_lines = 0
            
            for log_file in log_paths:
                lines_processed, lines_matched = self._process_log_file(log_file)
                total_lines += lines_processed
                matched_lines += lines_matched
            
            # Generate analysis results
            analysis_data = self._generate_analysis_results()
            
            # Include 802.11k/v capability analysis in results
            capability_analysis = self._generate_capability_analysis()
            analysis_data["client_capabilities"] = capability_analysis
            
            # Create results structure
            results = {
                "status": "completed",
                "analysis_id": f"steering_enhanced_{int(time.time())}",
                "analysis_data": analysis_data,
                "metadata": {
                    "agent_type": self.agent_type,
                    "version": self.version,
                    "processing_time": time.time() - start_time,
                    "input_files": len(log_paths),
                    "total_lines_processed": total_lines,
                    "matched_lines": matched_lines,
                    "events_extracted": len(self.steering_events),
                    "unique_clients": len(self.client_stats)
                }
            }
            
            # Write results to standard files
            self._write_results_to_files(results, output_dir)
            
            self.logger.info(f"Steering analysis completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Steering analysis failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_log_file(self, log_file: str) -> tuple[int, int]:
        """Process a single log file and extract steering events using pattern framework"""
        lines_processed = 0
        lines_matched = 0
        
        try:
            self.logger.info(f"Processing log file: {log_file}")
            
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    lines_processed += 1
                    line = line.strip()
                    
                    if not line or 'wnc-steer' not in line.lower():
                        continue
                    
                    # Use pattern recognition framework - get all matches
                    matches = self.pattern_interface.engine.match_line(line, self.agent_type)
                    
                    if matches:
                        lines_matched += 1
                        # Process all matches, prioritizing steering-specific patterns
                        self._process_all_matches(matches, line, line_num)
                    else:
                        # Check enhanced patterns from failure analyzer as fallback
                        self._check_enhanced_patterns(line, line_num)
                            
        except Exception as e:
            self.logger.warning(f"Error processing file {log_file}: {e}")
        
        return lines_processed, lines_matched
    
    def _process_all_matches(self, matches: list, line: str, line_num: int) -> None:
        """Process all pattern matches, prioritizing steering-specific patterns over timestamp"""
        # Find the best steering-specific match (not just timestamp)
        steering_match = None
        timestamp_match = None
        
        for match in matches:
            if match.pattern_name.startswith('steering_') or match.pattern_name.startswith('wnc_component_steering'):
                steering_match = match
                break
            elif 'timestamp' in match.pattern_name:
                timestamp_match = match
        
        # Process the steering match if found, otherwise use timestamp match
        primary_match = steering_match or timestamp_match
        
        if primary_match:
            # Convert match object to result format
            result = {
                'status': 'matched',
                'pattern_name': primary_match.pattern_name,
                'match_data': primary_match.match_data
            }
            self._process_pattern_match(result, line, line_num)
        
        # If we only got a timestamp match, try to find steering patterns in the line
        # by testing individual steering patterns against the line
        if not steering_match and timestamp_match:
            self._try_steering_patterns_on_line(line, line_num)
    
    def _try_steering_patterns_on_line(self, line: str, line_num: int) -> None:
        """Try to find steering patterns in the line by testing individual patterns"""
        try:
            # Get all steering patterns from the registry
            steering_patterns = self.pattern_registry.get_patterns_for_agent("wnc-steering")
            
            # Sort patterns to prioritize specific steering patterns over component patterns
            specific_patterns = []
            component_patterns = []
            
            for pattern_def in steering_patterns:
                if 'timestamp' in pattern_def.name or pattern_def.name == 'mac_address_standard':
                    continue
                elif pattern_def.name.startswith('steering_'):
                    specific_patterns.append(pattern_def)
                elif pattern_def.name.startswith('wnc_component_steering'):
                    component_patterns.append(pattern_def)
            
            # Test specific patterns first, then component patterns
            patterns_to_test = specific_patterns + component_patterns
            
            for pattern_def in patterns_to_test:
                # Test the pattern against the line
                import re
                pattern = re.compile(pattern_def.pattern)
                match = pattern.search(line)
                
                if match:
                    # Found a steering pattern match
                    timestamp = self._extract_timestamp(line)
                    
                    # Create event
                    result = {
                        'status': 'matched',
                        'pattern_name': pattern_def.name,
                        'match_data': match.groupdict() if match.groupdict() else {'mac': match.group(1)} if match.groups() else {}
                    }
                    
                    # Add timestamp to match data if available
                    if timestamp:
                        result['match_data']['timestamp'] = timestamp
                    
                    self._process_pattern_match(result, line, line_num)
                    break  # Only process the first steering pattern match
                    
        except Exception as e:
            self.logger.warning(f"Error testing steering patterns on line: {e}")
    
    def _extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line using pattern framework"""
        # Use pattern recognition for timestamp extraction
        timestamp_result = self.pattern_interface.parse_log_line(line)
        
        if timestamp_result['status'] == 'matched' and 'timestamp' in timestamp_result['pattern_name']:
            match_data = timestamp_result.get('match_data', {})
            # Format timestamp from match data
            if all(key in match_data for key in ['year', 'month', 'day', 'hour', 'minute', 'second']):
                return f"{match_data['year']}-{match_data['month']}-{match_data['day']} {match_data['hour']}:{match_data['minute']}:{match_data['second']}"
        return ""
    
    def _process_pattern_match(self, result: dict, line: str, line_num: int) -> None:
        """Process a pattern match from the pattern framework and update tracking data"""
        pattern_name = result['pattern_name']
        match_data = result.get('match_data', {})
        timestamp = match_data.get('timestamp', '')
        
        # Extract client MAC from match data
        client_mac = None
        for key in ['mac', 'client_mac', 'client']:
            if key in match_data:
                client_mac = match_data[key].lower()
                break
        
        if not client_mac:
            return
        
        # Create event
        event = {
            'timestamp': timestamp,
            'event_type': pattern_name,
            'client_mac': client_mac,
            'raw_line': line,
            'line_number': line_num
        }
        
        # Extract additional data based on pattern
        if 'rssi' in match_data:
            try:
                rssi = int(match_data['rssi'])
                event['rssi'] = rssi
                self.client_stats[client_mac]['rssi_values'].append(rssi)
            except ValueError:
                pass
        
        # Update client statistics
        client_stat = self.client_stats[client_mac]
        
        # Update time range
        if not client_stat['first_seen'] or (timestamp and timestamp < client_stat['first_seen']):
            client_stat['first_seen'] = timestamp
        if not client_stat['last_seen'] or (timestamp and timestamp > client_stat['last_seen']):
            client_stat['last_seen'] = timestamp
        
        # Update event counters based on pattern name
        self._update_client_stats_for_pattern(pattern_name, client_stat, event, line)
        
        # Add event to list
        self.steering_events.append(event)
    
    def _update_client_stats_for_pattern(self, pattern_name: str, client_stat: dict, event: dict, line: str) -> None:
        """Update client statistics based on pattern name with enhanced 802.11k/v capability detection"""
        if pattern_name == 'steering_weak_signal':
            client_stat['weak_signals'] += 1
        elif pattern_name == 'steering_request':
            client_stat['steering_attempts'] += 1
            if self.failure_analyzer:
                self.failure_analyzer.record_attempt()
        elif pattern_name == 'steering_success':
            client_stat['steering_successes'] += 1
            if self.failure_analyzer:
                self.failure_analyzer.record_success()
        elif pattern_name == 'steering_failure':
            client_stat['steering_failures'] += 1
            if self.failure_analyzer:
                self.failure_analyzer.record_failure_incident(
                    client_mac=event['client_mac'],
                    timestamp=event['timestamp'],
                    failure_type='steering_failure',
                    raw_line=line,
                    event_data=event
                )
        
        # Enhanced 802.11k/v capability detection
        elif pattern_name == 'steering_capability_explicit':
            # Extract explicit capability information from parsed data
            self._process_explicit_capabilities(client_stat, event, line)
        elif pattern_name == 'steering_rrm_capability':
            client_stat['supports_11k'] = True
            client_stat.setdefault('capability_confidence', 0.95)
            self._add_capability_evidence(client_stat, '802.11k_direct', True, 0.95, event.get('timestamp'))
        elif pattern_name == 'steering_btm_capability':
            client_stat['supports_11v'] = True
            client_stat.setdefault('capability_confidence', 0.95)
            self._add_capability_evidence(client_stat, '802.11v_direct', True, 0.95, event.get('timestamp'))
        elif 'neighbor_report' in pattern_name:
            if 'failed' not in pattern_name:
                client_stat['supports_11k'] = True
                self._add_capability_evidence(client_stat, '802.11k_behavioral', True, 0.8, event.get('timestamp'))
            else:
                client_stat['supports_11k'] = False
                self._add_capability_evidence(client_stat, '802.11k_failure', False, 0.9, event.get('timestamp'))
        elif 'bss_transition' in pattern_name:
            if 'failed' not in pattern_name and 'rejected' not in pattern_name:
                client_stat['supports_11v'] = True
                self._add_capability_evidence(client_stat, '802.11v_behavioral', True, 0.8, event.get('timestamp'))
            else:
                client_stat['supports_11v'] = False
                self._add_capability_evidence(client_stat, '802.11v_failure', False, 0.9, event.get('timestamp'))
        elif pattern_name == 'steering_beacon_report':
            client_stat['supports_11k'] = True
            self._add_capability_evidence(client_stat, '802.11k_behavioral', True, 0.7, event.get('timestamp'))
        
        # Handle enhanced failure patterns
        elif pattern_name in ['btm_request_failed', 'steering_timeout', 'client_rejected_steering', 
                              'no_suitable_target', 'insufficient_rssi', 'client_disconnected', 
                              'ap_overloaded', 'radio_interference', 'bss_load_high', 
                              'steering_blacklisted', 'client_roaming_disabled', 'target_ap_unavailable']:
            client_stat['steering_failures'] += 1
            if self.failure_analyzer:
                self.failure_analyzer.record_failure_incident(
                    client_mac=event['client_mac'],
                    timestamp=event['timestamp'],
                    failure_type=pattern_name,
                    raw_line=line,
                    event_data=event
                )
    
    def _process_explicit_capabilities(self, client_stat: dict, event: dict, line: str) -> None:
        """Process explicit capability information from clientCapability events"""
        # Look for RRM/BTM flags in the line
        import re
        
        # Try to extract RRM capability
        rrm_match = re.search(r'rrm[_=](\w+)', line, re.IGNORECASE)
        if rrm_match:
            rrm_value = rrm_match.group(1).lower()
            supports_k = rrm_value in ['1', 'true', 'enabled', 'yes']
            client_stat['supports_11k'] = supports_k
            self._add_capability_evidence(client_stat, '802.11k_explicit', supports_k, 1.0, event.get('timestamp'))
        
        # Try to extract BTM capability
        btm_match = re.search(r'btm[_=](\w+)', line, re.IGNORECASE)
        if btm_match:
            btm_value = btm_match.group(1).lower()
            supports_v = btm_value in ['1', 'true', 'enabled', 'yes']
            client_stat['supports_11v'] = supports_v
            self._add_capability_evidence(client_stat, '802.11v_explicit', supports_v, 1.0, event.get('timestamp'))
    
    def _add_capability_evidence(self, client_stat: dict, evidence_type: str, value: bool, confidence: float, timestamp: str) -> None:
        """Add capability evidence and update confidence scoring"""
        if 'k_v_evidence' not in client_stat:
            client_stat['k_v_evidence'] = {
                'explicit_capabilities': [],
                'behavioral_indicators': [],
                'failure_indicators': []
            }
        
        evidence_entry = {
            'type': evidence_type,
            'value': value,
            'confidence': confidence,
            'timestamp': timestamp or ''
        }
        
        if 'explicit' in evidence_type:
            client_stat['k_v_evidence']['explicit_capabilities'].append(evidence_entry)
        elif 'failure' in evidence_type:
            client_stat['k_v_evidence']['failure_indicators'].append(evidence_entry)
        else:
            client_stat['k_v_evidence']['behavioral_indicators'].append(evidence_entry)
        
        # Update overall confidence
        self._update_capability_confidence(client_stat)
    
    def _update_capability_confidence(self, client_stat: dict) -> None:
        """Calculate confidence score for 802.11k/v capability determination"""
        if 'k_v_evidence' not in client_stat:
            client_stat['capability_confidence'] = 0.0
            return
        
        evidence = client_stat['k_v_evidence']
        total_confidence = 0.0
        evidence_count = 0
        
        # Weight explicit evidence highest
        for exp in evidence.get('explicit_capabilities', []):
            total_confidence += exp['confidence']
            evidence_count += 1
            
        # Weight behavioral evidence moderately
        for behav in evidence.get('behavioral_indicators', []):
            total_confidence += behav['confidence'] * 0.7
            evidence_count += 1
            
        # Weight failure evidence highly for negative indication
        for fail in evidence.get('failure_indicators', []):
            total_confidence += fail['confidence'] * 0.9
            evidence_count += 1
            
        if evidence_count > 0:
            client_stat['capability_confidence'] = min(total_confidence / evidence_count, 1.0)
        else:
            client_stat['capability_confidence'] = 0.0
    
    def _check_enhanced_patterns(self, line: str, line_num: int) -> None:
        """Check enhanced patterns from failure analyzer as fallback"""
        if not self.enhanced_patterns:
            return
            
        for pattern_name, pattern in self.enhanced_patterns.items():
            match = pattern.search(line)
            if match:
                # Extract timestamp
                timestamp = self._extract_timestamp(line)
                
                # Create event for enhanced pattern
                client_mac = match.group(1).lower() if match.groups() else 'unknown'
                event = {
                    'timestamp': timestamp,
                    'event_type': pattern_name,
                    'client_mac': client_mac,
                    'raw_line': line,
                    'line_number': line_num
                }
                
                # Update client statistics
                client_stat = self.client_stats[client_mac]
                client_stat['steering_failures'] += 1
                
                # Record failure incident
                if self.failure_analyzer:
                    self.failure_analyzer.record_failure_incident(
                        client_mac=client_mac,
                        timestamp=timestamp,
                        failure_type=pattern_name,
                        raw_line=line,
                        event_data=event
                    )
                
                # Add event to list
                self.steering_events.append(event)
                break
    
    def _generate_analysis_results(self) -> dict:
        """Generate comprehensive analysis results"""
        
        # Calculate summary statistics
        total_clients = len(self.client_stats)
        total_steering_attempts = sum(stats['steering_attempts'] for stats in self.client_stats.values())
        total_steering_successes = sum(stats['steering_successes'] for stats in self.client_stats.values())
        success_rate = (total_steering_successes / total_steering_attempts * 100) if total_steering_attempts > 0 else 0
        
        clients_with_11k = sum(1 for stats in self.client_stats.values() if stats['supports_11k'])
        clients_with_11v = sum(1 for stats in self.client_stats.values() if stats['supports_11v'])
        
        # Generate summary
        summary = {
            'total_events': len(self.steering_events),
            'total_clients': total_clients,
            'total_steering_attempts': total_steering_attempts,
            'total_steering_successes': total_steering_successes,
            'success_rate_percent': round(success_rate, 1),
            'clients_supporting_11k': clients_with_11k,
            'clients_supporting_11v': clients_with_11v,
            'time_range': self._get_time_range(),
            'status': 'completed'
        }
        
        # Generate timeline (last 50 events for performance)
        timeline = self.steering_events[-50:] if len(self.steering_events) > 50 else self.steering_events
        
        # Generate metrics with safe failure analysis
        metrics = {
            'events_by_type': self._count_events_by_type(),
            'client_capability_distribution': {
                '802.11k_support_percentage': round((clients_with_11k / total_clients * 100) if total_clients > 0 else 0, 1),
                '802.11v_support_percentage': round((clients_with_11v / total_clients * 100) if total_clients > 0 else 0, 1)
            },
            'steering_effectiveness': {
                'overall_success_rate': round(success_rate, 1),
                'avg_attempts_per_client': round(total_steering_attempts / total_clients, 1) if total_clients > 0 else 0
            }
        }
        
        # Add failure analysis if available
        if self.failure_analyzer:
            try:
                metrics['failure_analysis'] = self.failure_analyzer.get_failure_summary()
            except Exception as e:
                self.logger.warning(f"Failed to get failure summary: {e}")
                metrics['failure_analysis'] = {'error': 'Failure analysis unavailable'}
        
        # Generate insights (enhanced with failure insights if available)
        insights = self._generate_insights(summary, metrics)
        if self.failure_analyzer:
            try:
                failure_patterns = self.failure_analyzer.analyze_failure_patterns()
                if failure_patterns['total_failures'] > 0:
                    insights.append(f"Detected {failure_patterns['total_failures']} steering failures with detailed analysis available")
                    if failure_patterns['top_failing_clients']:
                        top_client, count = failure_patterns['top_failing_clients'][0]
                        insights.append(f"Top failing client: {top_client} with {count} failures")
            except Exception as e:
                self.logger.warning(f"Failed to analyze failure patterns: {e}")
        
        return {
            'summary': summary,
            'timeline': timeline,
            'metrics': metrics,
            'insights': insights,
            'capability_analysis': self._generate_capability_analysis()
        }
    
    def _get_time_range(self) -> str:
        """Get the time range of events"""
        if not self.steering_events:
            return "No events found"
        
        timestamps = [event['timestamp'] for event in self.steering_events if event['timestamp']]
        if not timestamps:
            return "Unknown time range"
        
        return f"{min(timestamps)} to {max(timestamps)}"
    
    def _count_events_by_type(self) -> dict:
        """Count events by type"""
        counts = defaultdict(int)
        for event in self.steering_events:
            counts[event['event_type']] += 1
        return dict(counts)
    
    def _analyze_client_capabilities(self) -> dict:
        """Analyze 802.11k/v capabilities for all clients with detailed breakdown"""
        total_clients = len(self.client_stats)
        if total_clients == 0:
            return {
                'total_clients_analyzed': 0,
                'capabilities': {
                    '802.11k_support_percentage': 0,
                    '802.11v_support_percentage': 0,
                    'both_supported_percentage': 0,
                    'neither_supported_percentage': 0
                },
                'client_details': {},
                'patterns_matched': []
            }
        
        k_support_count = 0
        v_support_count = 0
        both_support_count = 0
        neither_support_count = 0
        client_details = {}
        patterns_matched = []
        
        for mac, stats in self.client_stats.items():
            # Determine final capability status based on evidence
            supports_k = self._determine_capability_status(stats, '802.11k')
            supports_v = self._determine_capability_status(stats, '802.11v')
            
            # Update stats
            stats['supports_11k'] = supports_k
            stats['supports_11v'] = supports_v
            
            if supports_k:
                k_support_count += 1
            if supports_v:
                v_support_count += 1
            if supports_k and supports_v:
                both_support_count += 1
            elif not supports_k and not supports_v:
                neither_support_count += 1
            
            # Build detailed client information
            evidence = stats.get('k_v_evidence', {})
            client_details[mac] = {
                'mac_address': mac,
                'supports_802_11k': supports_k,
                'supports_802_11v': supports_v,
                'capability_confidence': stats.get('capability_confidence', 0.0),
                'steering_attempts': stats.get('steering_attempts', 0),
                'steering_successes': stats.get('steering_successes', 0),
                'steering_failures': stats.get('steering_failures', 0),
                'first_seen': stats.get('first_seen', 'Unknown'),
                'last_seen': stats.get('last_seen', 'Unknown'),
                'evidence_summary': self._summarize_evidence(evidence),
                'capability_determination': self._explain_capability_determination(supports_k, supports_v, evidence)
            }
            
            # Collect patterns that contributed to this determination
            for evidence_type in ['explicit_capabilities', 'behavioral_indicators', 'failure_indicators']:
                for ev in evidence.get(evidence_type, []):
                    pattern_info = {
                        'client_mac': mac,
                        'pattern_type': ev['type'],
                        'value': ev['value'],
                        'confidence': ev['confidence'],
                        'timestamp': ev['timestamp']
                    }
                    if pattern_info not in patterns_matched:
                        patterns_matched.append(pattern_info)
        
        return {
            'total_clients_analyzed': total_clients,
            'capabilities': {
                '802.11k_support_percentage': round((k_support_count / total_clients) * 100, 1),
                '802.11v_support_percentage': round((v_support_count / total_clients) * 100, 1),
                'both_supported_percentage': round((both_support_count / total_clients) * 100, 1),
                'neither_supported_percentage': round((neither_support_count / total_clients) * 100, 1)
            },
            'client_details': client_details,
            'patterns_matched': patterns_matched
        }
    
    def _determine_capability_status(self, stats: dict, capability: str) -> bool:
        """Determine if client supports given capability based on evidence"""
        evidence = stats.get('k_v_evidence', {})
        if not evidence:
            return stats.get('supports_11k' if '802.11k' in capability else 'supports_11v', False)
        
        # Check explicit evidence first (highest priority)
        for exp in evidence.get('explicit_capabilities', []):
            if capability in exp['type']:
                return exp['value']
        
        # Check for failure evidence (negative indication)
        for fail in evidence.get('failure_indicators', []):
            if capability in fail['type'] and fail['value'] is False:
                return False
        
        # Check behavioral evidence
        behavioral_support = False
        for behav in evidence.get('behavioral_indicators', []):
            if capability in behav['type'] and behav['value']:
                behavioral_support = True
                break
        
        return behavioral_support or stats.get('supports_11k' if '802.11k' in capability else 'supports_11v', False)
    
    def _summarize_evidence(self, evidence: dict) -> dict:
        """Summarize evidence for a client's capability determination"""
        return {
            'explicit_indicators': len(evidence.get('explicit_capabilities', [])),
            'behavioral_indicators': len(evidence.get('behavioral_indicators', [])),
            'failure_indicators': len(evidence.get('failure_indicators', [])),
            'total_evidence_points': (
                len(evidence.get('explicit_capabilities', [])) +
                len(evidence.get('behavioral_indicators', [])) +
                len(evidence.get('failure_indicators', []))
            )
        }
    
    def _explain_capability_determination(self, supports_k: bool, supports_v: bool, evidence: dict) -> str:
        """Generate human-readable explanation of capability determination"""
        explanations = []
        
        if evidence.get('explicit_capabilities'):
            explanations.append("Direct capability declaration detected")
        
        if evidence.get('behavioral_indicators'):
            explanations.append("Behavioral patterns indicating capability")
        
        if evidence.get('failure_indicators'):
            explanations.append("Failure patterns indicating lack of capability")
        
        if not explanations:
            explanations.append("No clear evidence - using default detection")
        
        k_status = "supports" if supports_k else "does not support"
        v_status = "supports" if supports_v else "does not support"
        
        return f"Client {k_status} 802.11k and {v_status} 802.11v. Evidence: {', '.join(explanations)}"
    
    def _generate_capability_analysis(self) -> dict:
        """Generate comprehensive 802.11k/v capability analysis with detailed client breakdown"""
        capability_summary = self._analyze_client_capabilities()
        
        # Extract capability metrics
        capabilities = capability_summary.get('capabilities', {})
        k_support = capabilities.get('802.11k_support_percentage', 0)
        v_support = capabilities.get('802.11v_support_percentage', 0)
        client_details = capability_summary.get('client_details', {})
        
        # Categorize clients for detailed reporting
        capable_clients = []
        k_only_clients = []
        v_only_clients = []
        legacy_clients = []
        
        for mac, details in client_details.items():
            if details['supports_802_11k'] and details['supports_802_11v']:
                capable_clients.append(details)
            elif details['supports_802_11k'] and not details['supports_802_11v']:
                k_only_clients.append(details)
            elif not details['supports_802_11k'] and details['supports_802_11v']:
                v_only_clients.append(details)
            else:
                legacy_clients.append(details)
        
        # Generate detailed analysis
        analysis = {
            'overview': {
                'total_clients_analyzed': capability_summary.get('total_clients_analyzed', 0),
                'k_support_percentage': k_support,
                'v_support_percentage': v_support,
                'fully_capable_percentage': capabilities.get('both_supported_percentage', 0),
                'legacy_only_percentage': capabilities.get('neither_supported_percentage', 0)
            },
            'client_breakdown': {
                'fully_capable_clients': {
                    'count': len(capable_clients),
                    'clients': capable_clients
                },
                'k_only_clients': {
                    'count': len(k_only_clients),
                    'clients': k_only_clients
                },
                'v_only_clients': {
                    'count': len(v_only_clients),
                    'clients': v_only_clients
                },
                'legacy_clients': {
                    'count': len(legacy_clients),
                    'clients': legacy_clients
                }
            },
            'patterns_detected': capability_summary.get('patterns_matched', []),
            'steering_strategy_recommendations': []
        }
        
        # Store for use in insights generation
        self._last_capability_analysis = analysis
        
        # Generate detailed strategy recommendations based on client breakdown
        total_clients = capability_summary.get('total_clients_analyzed', 0)
        if total_clients > 0:
            # Primary strategy based on overall capability distribution
            if k_support >= 80 and v_support >= 80:
                analysis['steering_strategy_recommendations'].append({
                    'strategy': 'Advanced Band Steering',
                    'description': f'High 802.11k/v support ({len(capable_clients)}/{total_clients} clients fully capable) enables sophisticated steering',
                    'confidence': 'High',
                    'applicable_clients': [client['mac_address'] for client in capable_clients]
                })
            elif k_support >= 50 or v_support >= 50:
                analysis['steering_strategy_recommendations'].append({
                    'strategy': 'Hybrid Steering Approach',
                    'description': f'Mixed environment: {len(capable_clients)} fully capable, {len(legacy_clients)} legacy clients require different approaches',
                    'confidence': 'Medium',
                    'capable_clients': [client['mac_address'] for client in capable_clients],
                    'legacy_clients': [client['mac_address'] for client in legacy_clients]
                })
            else:
                analysis['steering_strategy_recommendations'].append({
                    'strategy': 'Legacy RSSI-Based Steering',
                    'description': f'Limited 802.11k/v support ({len(legacy_clients)}/{total_clients} clients are legacy) requires traditional approaches',
                    'confidence': 'Medium',
                    'legacy_clients': [client['mac_address'] for client in legacy_clients]
                })
            
            # Specific recommendations for partial capability clients
            if len(k_only_clients) > 0:
                analysis['steering_strategy_recommendations'].append({
                    'strategy': 'Optimize 802.11k-Only Clients',
                    'description': f'{len(k_only_clients)} clients support 802.11k but not 802.11v - use neighbor reports for steering',
                    'confidence': 'High',
                    'applicable_clients': [client['mac_address'] for client in k_only_clients],
                    'specific_actions': [
                        'Enable neighbor report requests for these clients',
                        'Use signal strength thresholds for steering decisions',
                        'Avoid BSS transition management frames'
                    ]
                })
            
            if len(v_only_clients) > 0:
                analysis['steering_strategy_recommendations'].append({
                    'strategy': 'Optimize 802.11v-Only Clients', 
                    'description': f'{len(v_only_clients)} clients support 802.11v but not 802.11k - use BSS transition for steering',
                    'confidence': 'High',
                    'applicable_clients': [client['mac_address'] for client in v_only_clients],
                    'specific_actions': [
                        'Use BSS transition management for steering',
                        'Provide clear alternative AP recommendations',
                        'Monitor transition success rates'
                    ]
                })
            
            # Additional recommendations based on client performance
            failed_steering_clients = [
                client for client in client_details.values() 
                if client['steering_failures'] > client['steering_successes'] and client['steering_attempts'] > 2
            ]
            
            if failed_steering_clients:
                analysis['steering_strategy_recommendations'].append({
                    'strategy': 'Address Problematic Clients',
                    'description': f'{len(failed_steering_clients)} clients have poor steering success rates',
                    'confidence': 'High',
                    'problematic_clients': [
                        {
                            'mac': client['mac_address'],
                            'success_rate': round((client['steering_successes'] / max(client['steering_attempts'], 1)) * 100, 1),
                            'capabilities': f"802.11k: {'Yes' if client['supports_802_11k'] else 'No'}, 802.11v: {'Yes' if client['supports_802_11v'] else 'No'}"
                        } for client in failed_steering_clients
                    ],
                    'specific_actions': [
                        'Review client-specific steering policies',
                        'Consider alternative steering mechanisms for these clients',
                        'Investigate potential compatibility issues'
                    ]
                })
            
            # Capability-specific infrastructure recommendations
            if k_support < 30:
                analysis['steering_strategy_recommendations'].append({
                    'strategy': 'Enhanced AP Coordination',
                    'description': f'Limited 802.11k support ({k_support:.1f}%) requires infrastructure improvements',
                    'confidence': 'High',
                    'affected_clients': [client['mac_address'] for client in legacy_clients + v_only_clients],
                    'specific_actions': [
                        'Improve AP-to-AP communication for steering coordination',
                        'Implement centralized steering decisions',
                        'Consider radio environment optimization'
                    ]
                })
            
            if v_support < 30:
                analysis['steering_strategy_recommendations'].append({
                    'strategy': 'Alternative Steering Methods',
                    'description': f'Limited 802.11v support ({v_support:.1f}%) may require alternative approaches',
                    'confidence': 'Medium',
                    'affected_clients': [client['mac_address'] for client in legacy_clients + k_only_clients],
                    'specific_actions': [
                        'Consider controlled disconnection for legacy clients',
                        'Implement load balancing at connection time',
                        'Use beacon adjustments to influence client decisions'
                    ]
                })
        
        return analysis
    
    def _generate_insights(self, summary: dict, metrics: dict) -> list:
        """Generate actionable insights with specific client information"""
        insights = []
        
        # Success rate insights
        success_rate = summary.get('success_rate_percent', 0)
        if success_rate > 80:
            insights.append("Excellent steering success rate - client steering is working effectively")
        elif success_rate > 60:
            insights.append("Good steering success rate - some optimization opportunities exist")
        elif success_rate > 40:
            insights.append("Moderate steering success rate - consider reviewing steering policies")
        else:
            insights.append("Low steering success rate - steering configuration may need attention")
        
        # Get capability analysis for detailed insights
        capability_analysis = getattr(self, '_last_capability_analysis', None)
        if capability_analysis and 'client_breakdown' in capability_analysis:
            breakdown = capability_analysis['client_breakdown']
            overview = capability_analysis['overview']
            total_clients = overview.get('total_clients_analyzed', 0)
            
            if total_clients > 0:
                # Specific client capability insights
                fully_capable = breakdown['fully_capable_clients']['count']
                k_only = breakdown['k_only_clients']['count'] 
                v_only = breakdown['v_only_clients']['count']
                legacy = breakdown['legacy_clients']['count']
                
                if fully_capable > 0:
                    fully_capable_macs = [client['mac_address'] for client in breakdown['fully_capable_clients']['clients']]
                    insights.append(f"✅ {fully_capable} clients fully support 802.11k/v: {', '.join(fully_capable_macs[:3])}{'...' if len(fully_capable_macs) > 3 else ''}")
                
                if k_only > 0:
                    k_only_macs = [client['mac_address'] for client in breakdown['k_only_clients']['clients']]
                    insights.append(f"🔶 {k_only} clients support 802.11k only: {', '.join(k_only_macs[:3])}{'...' if len(k_only_macs) > 3 else ''} - optimize neighbor report usage")
                
                if v_only > 0:
                    v_only_macs = [client['mac_address'] for client in breakdown['v_only_clients']['clients']]
                    insights.append(f"🔷 {v_only} clients support 802.11v only: {', '.join(v_only_macs[:3])}{'...' if len(v_only_macs) > 3 else ''} - use BSS transition management")
                
                if legacy > 0:
                    legacy_macs = [client['mac_address'] for client in breakdown['legacy_clients']['clients']]
                    insights.append(f"⚠️  {legacy} legacy clients (no 802.11k/v): {', '.join(legacy_macs[:3])}{'...' if len(legacy_macs) > 3 else ''} - require RSSI-based steering")
                
                # Performance-based insights for specific clients
                problematic_clients = []
                for client_type in ['fully_capable_clients', 'k_only_clients', 'v_only_clients', 'legacy_clients']:
                    for client in breakdown[client_type]['clients']:
                        if client['steering_attempts'] > 2 and client['steering_failures'] > client['steering_successes']:
                            success_rate = (client['steering_successes'] / client['steering_attempts']) * 100
                            problematic_clients.append((client['mac_address'], success_rate))
                
                if problematic_clients:
                    problematic_clients.sort(key=lambda x: x[1])  # Sort by success rate
                    worst_clients = problematic_clients[:3]
                    client_list = [f"{mac} ({rate:.0f}%)" for mac, rate in worst_clients]
                    insights.append(f"🚨 Clients with poor steering performance: {', '.join(client_list)} - review steering policies")
                
                # Capability-specific recommendations
                k_support = overview.get('k_support_percentage', 0)
                v_support = overview.get('v_support_percentage', 0)
                
                if k_support < 50:
                    insights.append(f"📊 802.11k support at {k_support:.1f}% - neighbor reports limited for {k_only + legacy} clients")
                if v_support < 50:
                    insights.append(f"📊 802.11v support at {v_support:.1f}% - BSS transition limited for {v_only + legacy} clients")
                
        else:
            # Fallback to generic insights if capability analysis not available
            k_support = metrics.get('client_capability_distribution', {}).get('802.11k_support_percentage', 0)
            v_support = metrics.get('client_capability_distribution', {}).get('802.11v_support_percentage', 0)
            
            if k_support < 50:
                insights.append("Low 802.11k support detected - neighbor reports may be limited")
            if v_support < 50:
                insights.append("Low 802.11v support detected - BSS transition effectiveness may be limited")
        
        # Activity insights
        total_clients = summary.get('total_clients', 0)
        if total_clients == 0:
            insights.append("No steering activity detected in logs - verify steering is enabled")
        elif total_clients < 5:
            insights.append("Limited client activity detected - this may be normal for smaller networks")
        
        return insights
    
    def _write_results_to_files(self, results: dict, output_dir: Path) -> None:
        """Write analysis results to standard files"""
        
        # Write agent_data.json
        json_file = output_dir / "agent_data.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Write agent_data.csv
        csv_file = output_dir / "agent_data.csv"
        with open(csv_file, 'w', newline='') as f:
            import csv
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Timestamp', 'Event Type', 'Client MAC', 'Details'])
            
            # Write timeline data
            timeline = results['analysis_data']['timeline']
            for event in timeline:
                details = []
                if 'rssi' in event:
                    details.append(f"RSSI: {event['rssi']} dBm")
                
                writer.writerow([
                    event.get('timestamp', ''),
                    event.get('event_type', ''),
                    event.get('client_mac', ''),
                    ', '.join(details)
                ])
        
        # Write agent_report.html
        html_file = output_dir / "agent_report.html"
        html_content = self._generate_html_report(results)
        with open(html_file, 'w') as f:
            f.write(html_content)
    
    def _generate_html_report(self, results: dict) -> str:
        """Generate HTML report using the modular report generator"""
        analysis_data = results['analysis_data']
        summary = analysis_data['summary']
        metrics = analysis_data['metrics']
        insights = analysis_data['insights']
        
        # Use the modular report generator if available
        if self.report_generator:
            try:
                # Create results structure for the report generator
                report_results = {
                    'analysis_data': {
                        'summary': summary,
                        'metrics': metrics,
                        'insights': insights
                    },
                    'metadata': self.get_metadata()
                }
                return self.report_generator.generate_html_report(report_results)
            except Exception as e:
                self.logger.warning(f"Failed to generate modular HTML report: {e}")
        
        # Fallback to basic HTML report
        return self._generate_basic_html_report(summary, metrics, insights)
    
    def _generate_basic_html_report(self, summary: dict, metrics: dict, insights: list) -> str:
        """Generate basic HTML report as fallback"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>WNC Steering Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .summary {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .metrics {{ background: #f0f8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .insights {{ background: #fff8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .metric {{ margin: 5px 0; }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>WNC Steering Analysis Report</h1>
                <p><strong>Agent Version:</strong> {self.version}</p>
                <p><strong>Agent Type:</strong> {self.agent_type}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <div class="metric"><strong>Total Events:</strong> {summary.get('total_events', 0)}</div>
                <div class="metric"><strong>Unique Clients:</strong> {summary.get('total_clients', 0)}</div>
                <div class="metric"><strong>Steering Attempts:</strong> {summary.get('total_steering_attempts', 0)}</div>
                <div class="metric"><strong>Steering Successes:</strong> {summary.get('total_steering_successes', 0)}</div>
                <div class="metric"><strong>Success Rate:</strong> {summary.get('success_rate_percent', 0)}%</div>
                <div class="metric"><strong>Time Range:</strong> {summary.get('time_range', 'Unknown')}</div>
            </div>
            
            <div class="insights">
                <h2>Insights & Recommendations</h2>
        """
        
        for insight in insights:
            html += f'<div style="margin: 10px 0;">{insight}</div>'
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def get_metadata(self) -> dict:
        """Get metadata for the agent"""
        # Get pattern framework statistics
        framework_patterns = 0
        try:
            steering_patterns = self.pattern_registry.get_patterns_for_agent("wnc-steering")
            framework_patterns = len(steering_patterns)
        except Exception:
            pass
            
        return {
            'agent_type': self.agent_type,
            'name': self.agent_type,  # Frontend compatibility
            'version': self.version,
            'capabilities': getattr(self, 'capabilities', []),
            'supported_log_types': getattr(self, 'capabilities', []),  # Frontend compatibility
            'description': getattr(self, 'description', ''),
            'input_schema': getattr(self, 'input_schema', {}),
            'output_schema': getattr(self, 'output_schema', {}),
            'pattern_framework': {
                'integrated': True,
                'framework_patterns': framework_patterns,
                'enhanced_patterns': len(self.enhanced_patterns)
            },
            'modular_components': {
                'failure_analyzer': hasattr(self, 'failure_analyzer') and self.failure_analyzer is not None,
                'report_generator': hasattr(self, 'report_generator') and self.report_generator is not None
            }
        }
    
    def get_steering_strategy_recommendation(self, mac_address: str) -> Dict[str, Any]:
        """Get recommended steering strategy based on client 802.11k/v capabilities."""
        if mac_address not in self.client_stats:
            return {
                'strategy': 'unknown',
                'reason': 'Client not found in statistics',
                'confidence': 0.0,
                'methods': []
            }
            
        client_stat = self.client_stats[mac_address]
        supports_k = client_stat.get('supports_11k')
        supports_v = client_stat.get('supports_11v')
        confidence = client_stat.get('capability_confidence', 0.0)
        
        if supports_k and supports_v:
            return {
                'strategy': 'advanced_steering',
                'methods': ['neighbor_reports', 'bss_transition_management', 'beacon_requests'],
                'reason': 'Client supports both 802.11k and 802.11v',
                'confidence': confidence,
                'recommendation': 'Use BSS transition management for seamless handoffs'
            }
        elif supports_k:
            return {
                'strategy': 'k_based_steering',
                'methods': ['neighbor_reports', 'beacon_requests'],
                'reason': 'Client supports 802.11k only',
                'confidence': confidence,
                'recommendation': 'Use neighbor reports to help client discover better APs'
            }
        elif supports_v:
            return {
                'strategy': 'v_based_steering',
                'methods': ['bss_transition_management'],
                'reason': 'Client supports 802.11v only',
                'confidence': confidence,
                'recommendation': 'Use BSS transition requests for directed steering'
            }
        elif supports_k is False or supports_v is False:
            return {
                'strategy': 'legacy_steering',
                'methods': ['deauth_steering', 'power_management', 'band_steering'],
                'reason': 'Client does not support 802.11k/v features',
                'confidence': confidence,
                'recommendation': 'Use legacy steering methods - may cause brief disconnections'
            }
        else:
            return {
                'strategy': 'adaptive_discovery',
                'methods': ['capability_probing', 'behavioral_analysis'],
                'reason': 'Client capabilities unknown - discovery needed',
                'confidence': confidence,
                'recommendation': 'Test client capabilities with neighbor reports and BSS transitions'
            }

    def get_client_capability_summary(self) -> Dict[str, Any]:
        """Get summary of all client 802.11k/v capabilities detected."""
        summary = {
            'total_clients': len(self.client_stats),
            'k_capable': 0,
            'v_capable': 0,
            'both_capable': 0,
            'legacy_only': 0,
            'unknown': 0,
            'high_confidence': 0,  # confidence > 0.8
            'medium_confidence': 0,  # confidence 0.5-0.8
            'low_confidence': 0,  # confidence < 0.5
            'capability_distribution': {}
        }
        
        for mac, stats in self.client_stats.items():
            supports_k = stats.get('supports_11k')
            supports_v = stats.get('supports_11v')
            confidence = stats.get('capability_confidence', 0.0)
            
            # Capability counts
            if supports_k and supports_v:
                summary['both_capable'] += 1
                capability_type = 'both_k_v'
            elif supports_k:
                summary['k_capable'] += 1
                capability_type = 'k_only'
            elif supports_v:
                summary['v_capable'] += 1
                capability_type = 'v_only'
            elif supports_k is False and supports_v is False:
                summary['legacy_only'] += 1
                capability_type = 'legacy'
            else:
                summary['unknown'] += 1
                capability_type = 'unknown'
            
            # Confidence distribution
            if confidence > 0.8:
                summary['high_confidence'] += 1
            elif confidence > 0.5:
                summary['medium_confidence'] += 1
            else:
                summary['low_confidence'] += 1
            
            # Capability distribution
            summary['capability_distribution'][capability_type] = summary['capability_distribution'].get(capability_type, 0) + 1
        
        return summary

    def get_detailed_client_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed capability information for all clients."""
        detailed_caps = {}
        
        for mac, stats in self.client_stats.items():
            strategy = self.get_steering_strategy_recommendation(mac)
            
            detailed_caps[mac] = {
                'supports_11k': stats.get('supports_11k'),
                'supports_11v': stats.get('supports_11v'),
                'capability_confidence': stats.get('capability_confidence', 0.0),
                'first_seen': stats.get('first_seen'),
                'last_seen': stats.get('last_seen'),
                'steering_attempts': stats.get('steering_attempts', 0),
                'steering_successes': stats.get('steering_successes', 0),
                'steering_failures': stats.get('steering_failures', 0),
                'recommended_strategy': strategy,
                'evidence_summary': self._summarize_capability_evidence(stats)
            }
        
        return detailed_caps
    
    def _summarize_capability_evidence(self, client_stat: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize capability evidence for a client."""
        if 'k_v_evidence' not in client_stat:
            return {'total_evidence': 0, 'evidence_types': []}
        
        evidence = client_stat['k_v_evidence']
        evidence_types = []
        
        for exp in evidence.get('explicit_capabilities', []):
            evidence_types.append(f"Explicit: {exp['type']} = {exp['value']}")
        
        for behav in evidence.get('behavioral_indicators', []):
            evidence_types.append(f"Behavioral: {behav['type']}")
        
        for fail in evidence.get('failure_indicators', []):
            evidence_types.append(f"Failure: {fail['type']}")
        
        return {
            'total_evidence': len(evidence_types),
            'evidence_types': evidence_types,
            'explicit_count': len(evidence.get('explicit_capabilities', [])),
            'behavioral_count': len(evidence.get('behavioral_indicators', [])),
            'failure_count': len(evidence.get('failure_indicators', []))
        }
