"""
Enhanced WNC ACS Agent for MeshLog Integrated Agent System

This agent provides comprehensive analysis of WNC Auto Channel Selection (ACS) behavior,
tracking FSM state transitions, channel selection cycles, and radio optimization decisions.
Features enhanced pattern recognition, cycle detection, and performance analysis.
"""

import re
import csv
import json
import logging
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
import statistics

from app.core.agent_interface import AgentInterface
from app.core.pattern_recognition import PatternRegistry, AgentPatternInterface
from .acs_report_generator import ACSReportGenerator
from .acs_modules import (
    ACSLogParser, ACSAnalysisEngine, ACSCycleDetector,
    ACSFailureAnalyzer, ACSMetricsCalculator, ACSChannelAnalyzer
)

class WNCAcsAgent(AgentInterface):
    """Enhanced WNC ACS Analysis Agent with modular architecture"""
    
    @property
    def agent_type(self) -> str:
        return "wnc-acs"
    
    @property
    def version(self) -> str:
        return "2.2.0-modular"
    
    def __init__(self):
        # Initialize pattern recognition framework
        self.pattern_registry = PatternRegistry()
        self.pattern_interface = AgentPatternInterface("wnc-acs", self.pattern_registry)
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize modular components
        self.log_parser = ACSLogParser(self.pattern_interface, self.logger)
        self.analysis_engine = ACSAnalysisEngine(self.logger)
        self.cycle_detector = ACSCycleDetector(self.logger)
        self.failure_analyzer = ACSFailureAnalyzer(self.logger)
        self.metrics_calculator = ACSMetricsCalculator(self.logger)
        self.channel_analyzer = ACSChannelAnalyzer(self.logger)
        self.report_generator = ACSReportGenerator()
        
        # Enhanced capabilities
        self.capabilities = [
            "acs_analysis", 
            "fsm_transition_tracking", 
            "cycle_detection",
            "channel_preference_analysis",
            "multi_radio_support",
            "performance_metrics",
            "actionable_recommendations",
            "multi_file_processing",
            "modular_architecture"
        ]
        
        self.description = "Enhanced WNC ACS analysis with FSM transition tracking, cycle detection, and channel optimization insights"
        
        # Enhanced input schema
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
                        "radio_filter": {"type": "string"},
                        "metrics": {"type": "array", "items": {"type": "string"}},
                        "enable_enhanced_insights": {"type": "boolean", "default": True},
                        "merge_rotation_files": {"type": "boolean", "default": True},
                        "max_rotation_files": {"type": "integer", "default": 20},
                        "cycle_timeout_minutes": {"type": "integer", "default": 30},
                        "generate_html_report": {"type": "boolean", "default": True},
                        "include_raw_data": {"type": "boolean", "default": False},
                        "detailed_timeline": {"type": "boolean", "default": True}
                    }
                }
            }
        }
        
        # Enhanced output schema
        self.output_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "analysis_data": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "object"},
                        "timeline": {"type": "array"},
                        "metrics": {"type": "object"},
                        "insights": {"type": "array"},
                        "acs_cycles": {"type": "object"},
                        "fsm_transitions": {"type": "object"},
                        "channel_analysis": {"type": "object"},
                        "recommendations": {"type": "array"}
                    }
                },
                "metadata": {"type": "object"}
            }
        }
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, log_paths: list, output_path: str, analysis_config: dict = None) -> dict:
        """Enhanced modular ACS analysis"""
        start_time = time.time()
        config = analysis_config or {}
        
        try:
            self.logger.info(f"Starting modular ACS analysis of {len(log_paths)} files")
            
            # Ensure output directory exists
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Reset all modular components
            self._reset_analysis_state()
            
            # Phase 1: Log Parsing
            self.logger.info("Phase 1: Parsing log files")
            events = self._parse_log_files(log_paths, config)
            
            # Phase 2: Core Analysis
            self.logger.info("Phase 2: Analyzing events and patterns")
            analysis_data = self._perform_core_analysis(events)
            
            # Phase 3: Cycle Detection
            self.logger.info("Phase 3: Detecting ACS cycles")
            cycle_data = self._detect_cycles(events, analysis_data)
            
            # Phase 4: Failure Analysis
            self.logger.info("Phase 4: Analyzing failures")
            failure_data = self._analyze_failures(events, cycle_data)
            
            # Phase 5: Channel Analysis
            self.logger.info("Phase 5: Analyzing channel patterns")
            channel_data = self._analyze_channels(events, cycle_data, analysis_data)
            
            # Phase 6: Metrics Calculation
            self.logger.info("Phase 6: Calculating metrics")
            metrics_data = self._calculate_metrics(events, cycle_data, analysis_data, failure_data)
            
            # Phase 7: Generate Comprehensive Results
            self.logger.info("Phase 7: Generating results")
            results = self._generate_comprehensive_results(
                events, analysis_data, cycle_data, failure_data, 
                channel_data, metrics_data, start_time, config
            )
            
            # Phase 8: Write Results
            self.logger.info("Phase 8: Writing results to files")
            self._write_results_to_files(results, output_dir, config)
            
            return {
                "status": "completed",
                "message": f"Modular ACS analysis completed, results written to {output_path}",
                "files_created": [
                    "agent_report.html", 
                    "agent_data.json", 
                    "agent_data.csv"
                ],
                "statistics": {
                    "total_events": len(events),
                    "files_processed": len(log_paths),
                    "processing_time": time.time() - start_time
                }
            }
            
        except Exception as e:
            self.logger.error(f"ACS analysis failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _reset_analysis_state(self):
        """Reset all modular components for new analysis"""
        self.log_parser.reset()
        # Other components don't need explicit reset as they're stateless for each analysis
    
    def _parse_log_files(self, log_paths: list, config: dict) -> list:
        """Parse log files using modular log parser"""
        all_events = []
        
        for log_file in log_paths:
            try:
                lines_processed, lines_matched = self.log_parser.process_log_file(log_file)
                self.logger.info(f"Processed {log_file}: {lines_processed} lines, {lines_matched} matched")
            except Exception as e:
                self.logger.warning(f"Error processing {log_file}: {e}")
        
        return self.log_parser.get_events()
    
    def _perform_core_analysis(self, events: list) -> dict:
        """Perform core analysis using analysis engine"""
        return self.analysis_engine.analyze_events(events)
    
    def _detect_cycles(self, events: list, analysis_data: dict) -> dict:
        """Detect ACS cycles using cycle detector"""
        radio_states = analysis_data.get('radio_analysis', {})
        return self.cycle_detector.detect_cycles(events, radio_states)
    
    def _analyze_failures(self, events: list, cycle_data: dict) -> dict:
        """Analyze failures using failure analyzer"""
        cycles = cycle_data.get('cycle_details', [])
        return self.failure_analyzer.analyze_failures(events, cycles)
    
    def _analyze_channels(self, events: list, cycle_data: dict, analysis_data: dict) -> dict:
        """Analyze channels using channel analyzer"""
        cycles = cycle_data.get('cycle_details', [])
        radio_states = analysis_data.get('radio_analysis', {})
        return self.channel_analyzer.analyze_channels(events, cycles, radio_states)
    
    def _calculate_metrics(self, events: list, cycle_data: dict, analysis_data: dict, failure_data: dict) -> dict:
        """Calculate metrics using metrics calculator"""
        cycles = cycle_data.get('cycle_details', [])
        failures = failure_data.get('failure_incidents', [])
        return self.metrics_calculator.calculate_metrics(events, cycles, analysis_data, failures)
    
    def _generate_comprehensive_results(self, events: list, analysis_data: dict, cycle_data: dict, 
                                      failure_data: dict, channel_data: dict, metrics_data: dict,
                                      start_time: float, config: dict) -> dict:
        """Generate comprehensive analysis results"""
        
        # Generate summary
        summary = self._generate_summary(events, analysis_data, cycle_data, metrics_data)
        
        # Generate timeline (last 100 events for performance)
        timeline = events[-100:] if len(events) > 100 else events
        
        # Generate insights
        insights = self._generate_insights(analysis_data, cycle_data, failure_data, channel_data, metrics_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(cycle_data, failure_data, channel_data, metrics_data)
        
        return {
            "status": "completed",
            "analysis_id": f"acs_modular_{int(time.time())}",
            "analysis_data": {
                "summary": summary,
                "timeline": timeline,
                "metrics": metrics_data,
                "insights": insights,
                "acs_cycles": cycle_data,
                "fsm_analysis": analysis_data.get('fsm_analysis', {}),
                "channel_analysis": channel_data,
                "failure_analysis": failure_data,
                "radio_analysis": analysis_data.get('radio_analysis', {}),
                "recommendations": recommendations
            },
            "metadata": {
                "agent_type": self.agent_type,
                "version": self.version,
                "processing_time": time.time() - start_time,
                "modular_components": {
                    "log_parser": True,
                    "analysis_engine": True,
                    "cycle_detector": True,
                    "failure_analyzer": True,
                    "metrics_calculator": True,
                    "channel_analyzer": True
                },
                "pattern_framework_enabled": True,
                "events_processed": len(events)
            }
        }
    
    def _generate_summary(self, events: list, analysis_data: dict, cycle_data: dict, metrics_data: dict) -> dict:
        """Generate analysis summary"""
        cycle_summary = cycle_data.get('cycle_summary', {})
        radio_analysis = analysis_data.get('radio_analysis', {})
        performance_metrics = metrics_data.get('performance_metrics', {})
        
        return {
            'total_events': len(events),
            'total_radios': radio_analysis.get('total_radios', 0),
            'active_radios': radio_analysis.get('active_radios', 0),
            'total_cycles': cycle_summary.get('total_cycles', 0),
            'completed_cycles': cycle_summary.get('completed_cycles', 0),
            'cycle_success_rate': cycle_summary.get('success_rate', 0),
            'average_cycle_duration': cycle_summary.get('average_duration_seconds', 0),
            'time_range': analysis_data.get('timeline_analysis', {}).get('time_range', 'Unknown'),
            'analysis_status': 'completed'
        }
    
    def _generate_insights(self, analysis_data: dict, cycle_data: dict, failure_data: dict, 
                          channel_data: dict, metrics_data: dict) -> list:
        """Generate analysis insights"""
        insights = []
        
        # Cycle insights
        cycle_summary = cycle_data.get('cycle_summary', {})
        success_rate = cycle_summary.get('success_rate', 0)
        
        if success_rate > 80:
            insights.append("Excellent ACS cycle success rate - system performing well")
        elif success_rate > 60:
            insights.append("Good ACS cycle success rate with room for optimization")
        else:
            insights.append("Low ACS cycle success rate - investigate configuration")
        
        # Channel insights
        channel_insights = channel_data.get('optimization_insights', [])
        insights.extend(channel_insights[:3])  # Add top 3 channel insights
        
        # Failure insights
        failure_summary = failure_data.get('failure_summary', {})
        total_failures = failure_summary.get('total_failures', 0)
        
        if total_failures > 10:
            insights.append(f"High failure count ({total_failures}) detected - review system configuration")
        
        # Performance insights
        performance_metrics = metrics_data.get('performance_metrics', {})
        avg_duration = performance_metrics.get('average_cycle_duration', 0)
        
        if avg_duration > 300:
            insights.append("Long average cycle duration - consider optimizing scan parameters")
        
        return insights
    
    def _generate_recommendations(self, cycle_data: dict, failure_data: dict, 
                                channel_data: dict, metrics_data: dict) -> list:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Add cycle recommendations
        cycle_recommendations = cycle_data.get('recommendations', [])
        recommendations.extend(cycle_recommendations[:2])
        
        # Add failure recommendations
        failure_recommendations = failure_data.get('recommendations', [])
        recommendations.extend(failure_recommendations[:2])
        
        # Add channel recommendations
        channel_recommendations = channel_data.get('recommendations', [])
        recommendations.extend(channel_recommendations[:2])
        
        # Add KPI recommendations
        kpi_data = metrics_data.get('kpi_dashboard', {})
        attention_areas = kpi_data.get('health_indicators', {}).get('attention_required', [])
        
        for area in attention_areas[:2]:
            if area != 'System Operating Normally':
                recommendations.append(f"Address {area.lower()} for improved performance")
        
        return recommendations if recommendations else ['System operating normally - no specific recommendations']
    
    def _write_results_to_files(self, results: dict, output_dir: Path, config: dict) -> None:
        """Write analysis results to files"""
        
        # Write agent_data.json
        json_file = output_dir / "agent_data.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Write agent_data.csv
        csv_file = output_dir / "agent_data.csv"
        self._write_csv_timeline(results['analysis_data']['timeline'], csv_file)
        
        # Write agent_report.html using modular report generator
        html_file = output_dir / "agent_report.html"
        if config.get('generate_html_report', True):
            html_content = self.report_generator.generate_html_report(results)
            with open(html_file, 'w') as f:
                f.write(html_content)
    
    def _write_csv_timeline(self, timeline: list, csv_file: Path) -> None:
        """Write timeline data to CSV"""
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Timestamp', 'Event Type', 'Radio', 'Channel', 'FSM State', 'Details'])
            
            # Write timeline data
            for event in timeline:
                writer.writerow([
                    event.get('timestamp', ''),
                    event.get('event_type', ''),
                    event.get('radio', ''),
                    event.get('channel', ''),
                    event.get('fsm_state', ''),
                    event.get('reason', '')
                ])
    
    def get_metadata(self) -> dict:
        """Get agent metadata"""
        return {
            'agent_type': self.agent_type,
            'name': self.agent_type,
            'version': self.version,
            'capabilities': self.capabilities,
            'description': self.description,
            'modular_architecture': True,
            'components': {
                'log_parser': 'ACSLogParser',
                'analysis_engine': 'ACSAnalysisEngine',
                'cycle_detector': 'ACSCycleDetector',
                'failure_analyzer': 'ACSFailureAnalyzer',
                'metrics_calculator': 'ACSMetricsCalculator',
                'channel_analyzer': 'ACSChannelAnalyzer',
                'report_generator': 'ACSReportGenerator'
            }
        }
        
        # Expand log files if rotation merging is enabled
        all_files = self._expand_log_files(log_paths, config)
        
        # Parse ACS logs using pattern recognition framework
        acs_events = self._parse_acs_logs_enhanced(all_files, config)
        
        # Detect ACS cycles
        acs_cycles = self._detect_acs_cycles()
        
        # Analyze FSM transitions
        fsm_transitions = self._analyze_fsm_transitions()
        
        # Analyze channel selection
        channel_analysis = self._analyze_channel_selection()
        
        # Generate actionable recommendations
        recommendations = self._generate_actionable_recommendations()
        
        # Generate comprehensive analysis
        summary = self._generate_enhanced_summary(acs_events, acs_cycles, fsm_transitions)
        timeline = self._generate_enhanced_timeline(acs_events)
        metrics = self._calculate_enhanced_metrics(acs_events, acs_cycles, fsm_transitions)
        insights = self._generate_enhanced_insights(acs_events, acs_cycles, fsm_transitions, recommendations)
        
        return {
            "summary": summary,
            "timeline": timeline,
            "metrics": metrics,
            "insights": insights,
            "acs_cycles": acs_cycles,
            "fsm_transitions": fsm_transitions,
            "channel_analysis": channel_analysis,
            "recommendations": recommendations,
            "files_processed": len(all_files)
        }
    
    def _expand_log_files(self, log_paths: list, config: dict) -> list:
        """Expand log files to include rotation files"""
        if not config.get("merge_rotation_files", True):
            return log_paths
        
        expanded_files = []
        max_files = config.get("max_rotation_files", 20)
        
        for log_path in log_paths:
            expanded_files.append(log_path)
            
            # Add rotation files
            base_path = Path(log_path)
            for i in range(1, max_files + 1):
                # Check for numbered rotation files
                rotated_file = base_path.parent / f"{base_path.name}.{i}"
                if rotated_file.exists():
                    expanded_files.append(str(rotated_file))
                
                # Check for compressed rotation files
                compressed_file = base_path.parent / f"{base_path.name}.{i}.gz"
                if compressed_file.exists():
                    expanded_files.append(str(compressed_file))
        
        return expanded_files
    
    def _parse_acs_logs_enhanced(self, files: List[str], config: dict) -> List[Dict[str, Any]]:
        """Parse ACS logs using pattern recognition framework"""
        events = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Use pattern recognition framework
                        result = self.pattern_interface.parse_log_line(line, line_num)
                        
                        if result['status'] == 'matched':
                            event = self._process_pattern_match(result, line)
                            if event:
                                events.append(event)
                                self._update_radio_data(event)
                                
            except Exception as e:
                self.logger.warning(f"Could not process file {file_path}: {e}")
        
        return events
    
    def _process_pattern_match(self, result: dict, line: str) -> Optional[Dict[str, Any]]:
        """Process a pattern match result into a structured event"""
        pattern_name = result['pattern_name']
        match_data = result['match_data']
        confidence = result['confidence']
        
        # Extract timestamp
        timestamp = self._extract_timestamp(line)
        
        # Create event based on pattern type
        event = {
            'timestamp': timestamp,
            'pattern_name': pattern_name,
            'confidence': confidence,
            'raw_line': line,
            'match_data': match_data
        }
        
        # Add pattern-specific data
        if 'mac' in match_data:
            event['radio_mac'] = match_data['mac']
        
        if 'from_state' in match_data and 'to_state' in match_data:
            event['from_state'] = match_data['from_state']
            event['to_state'] = match_data['to_state']
        
        if 'reason' in match_data:
            event['reason'] = match_data['reason']
        
        if 'channel' in match_data:
            event['channel'] = int(match_data['channel'])
        
        if 'freq' in match_data:
            event['frequency'] = match_data['freq']
        
        if 'bandwidth' in match_data:
            event['bandwidth'] = match_data['bandwidth']
        
        return event
    
    def _extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line"""
        # Use pattern recognition for timestamp extraction
        timestamp_result = self.pattern_interface.parse_log_line(line)
        
        if timestamp_result['status'] == 'matched' and 'timestamp' in timestamp_result['pattern_name']:
            match_data = timestamp_result['match_data']
            if all(key in match_data for key in ['year', 'month', 'day', 'hour', 'minute', 'second']):
                return f"{match_data['year']} {match_data['month']} {match_data['day']} {match_data['hour']}:{match_data['minute']}:{match_data['second']}"
        
        return ""
    
    def _update_radio_data(self, event: Dict[str, Any]) -> None:
        """Update radio data with new event"""
        if 'radio_mac' not in event:
            return
        
        radio_mac = event['radio_mac']
        radio_info = self.radio_data[radio_mac]
        
        # Add event to radio timeline
        radio_info['events'].append(event)
        
        # Update time spans
        timestamp = event.get('timestamp', '')
        if timestamp:
            if not radio_info['first_seen'] or timestamp < radio_info['first_seen']:
                radio_info['first_seen'] = timestamp
            if not radio_info['last_seen'] or timestamp > radio_info['last_seen']:
                radio_info['last_seen'] = timestamp
        
        # Update FSM state
        pattern_name = event.get('pattern_name', '')
        
        if 'fsm_transition' in pattern_name:
            radio_info['fsm_transitions'].append(event)
            radio_info['current_state'] = event.get('to_state', 'UNKNOWN')
        
        # Track channel information
        if 'channel' in event:
            radio_info['channel_history'].append({
                'timestamp': timestamp,
                'channel': event['channel'],
                'event_type': pattern_name
            })
        
        if 'frequency' in event:
            radio_info['frequency_history'].append({
                'timestamp': timestamp,
                'frequency': event['frequency'],
                'event_type': pattern_name
            })
        
        if 'bandwidth' in event:
            radio_info['bandwidth_history'].append({
                'timestamp': timestamp,
                'bandwidth': event['bandwidth'],
                'event_type': pattern_name
            })
    
    def _detect_acs_cycles(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detect ACS cycles for each radio"""
        cycles = {}
        
        for radio_mac, radio_info in self.radio_data.items():
            radio_cycles = []
            events = radio_info['events']
            
            # Find cycle start events (SERVING -> CHECKING transitions)
            cycle_starts = []
            for i, event in enumerate(events):
                if (event.get('pattern_name') == 'acs_fsm_transition' and 
                    event.get('from_state') == 'SERVING' and 
                    event.get('to_state') == 'CHECKING'):
                    cycle_starts.append(i)
            
            # Build cycles
            for start_idx in cycle_starts:
                cycle = {
                    'cycle_id': f"{radio_mac}_cycle_{len(radio_cycles)}",
                    'start_time': events[start_idx]['timestamp'],
                    'start_event': events[start_idx],
                    'events': [events[start_idx]],
                    'status': 'active',
                    'duration_seconds': 0
                }
                
                # Find cycle end (CHECKING -> SERVING transition)
                for i in range(start_idx + 1, len(events)):
                    event = events[i]
                    cycle['events'].append(event)
                    
                    if (event.get('pattern_name') == 'acs_fsm_transition' and 
                        event.get('from_state') == 'CHECKING' and 
                        event.get('to_state') == 'SERVING'):
                        cycle['status'] = 'completed'
                        cycle['end_time'] = event['timestamp']
                        cycle['end_event'] = event
                        break
                
                # Calculate duration
                if cycle['status'] == 'completed':
                    try:
                        start_dt = datetime.strptime(cycle['start_time'], '%Y %b %d %H:%M:%S')
                        end_dt = datetime.strptime(cycle['end_time'], '%Y %b %d %H:%M:%S')
                        cycle['duration_seconds'] = (end_dt - start_dt).total_seconds()
                    except:
                        pass
                
                radio_cycles.append(cycle)
            
            cycles[radio_mac] = radio_cycles
        
        return cycles
    
    def _analyze_fsm_transitions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze FSM transitions for each radio"""
        transitions = {}
        
        for radio_mac, radio_info in self.radio_data.items():
            radio_transitions = []
            
            for event in radio_info['events']:
                if event.get('pattern_name') == 'acs_fsm_transition':
                    transition = {
                        'timestamp': event['timestamp'],
                        'from_state': event.get('from_state', 'UNKNOWN'),
                        'to_state': event.get('to_state', 'UNKNOWN'),
                        'radio_mac': radio_mac,
                        'event': event
                    }
                    radio_transitions.append(transition)
            
            transitions[radio_mac] = radio_transitions
        
        return transitions
    
    def _analyze_channel_selection(self) -> Dict[str, Any]:
        """Analyze channel selection patterns"""
        analysis = {
            'channel_usage': defaultdict(int),
            'frequency_usage': defaultdict(int),
            'bandwidth_usage': defaultdict(int),
            'radio_channel_history': {},
            'channel_changes': {}
        }
        
        for radio_mac, radio_info in self.radio_data.items():
            # Track channel history
            analysis['radio_channel_history'][radio_mac] = radio_info['channel_history']
            
            # Count channel changes
            channel_changes = 0
            last_channel = None
            
            for channel_event in radio_info['channel_history']:
                current_channel = channel_event['channel']
                if last_channel is not None and current_channel != last_channel:
                    channel_changes += 1
                last_channel = current_channel
            
            analysis['channel_changes'][radio_mac] = channel_changes
            
            # Aggregate usage statistics
            for channel_event in radio_info['channel_history']:
                analysis['channel_usage'][channel_event['channel']] += 1
            
            for freq_event in radio_info['frequency_history']:
                analysis['frequency_usage'][freq_event['frequency']] += 1
            
            for bw_event in radio_info['bandwidth_history']:
                analysis['bandwidth_usage'][bw_event['bandwidth']] += 1
        
        return analysis
    
    def _analyze_acs_failures(self) -> Dict[str, Any]:
        """Analyze ACS failures and root causes with DFS monitoring"""
        failure_analysis = {
            'total_failures': 0,
            'failure_reasons': defaultdict(int),
            'failed_cycles': [],
            'failure_trends': defaultdict(list),
            'problematic_radios': defaultdict(int),
            'dfs_events': [],
            'blacklisted_channels': defaultdict(int),
            'algorithm_decisions': [],
            'recommendations': []
        }
        
        for radio_mac, radio_info in self.radio_data.items():
            cycles = radio_info.get('cycles', [])
            events = radio_info['events']
            radio_failures = 0
            
            # Analyze cycles
            for cycle in cycles:
                if cycle.get('status') == 'failed':
                    failure_analysis['total_failures'] += 1
                    radio_failures += 1
                    
                    reason = cycle.get('failure_reason', 'unknown')
                    failure_analysis['failure_reasons'][reason] += 1
                    
                    failure_analysis['failed_cycles'].append({
                        'radio_mac': radio_mac,
                        'cycle_id': cycle['cycle_id'],
                        'reason': reason,
                        'timestamp': cycle['start_time'],
                        'duration': cycle.get('duration_seconds', 0)
                    })
            
            # Analyze DFS events
            for event in events:
                pattern_name = event.get('pattern_name', '')
                
                if pattern_name == 'acs_dfs_radar_detected':
                    failure_analysis['dfs_events'].append({
                        'radio_mac': radio_mac,
                        'detected_channel': event.get('channel'),
                        'switched_channel': event.get('new_channel'),
                        'timestamp': event.get('timestamp', ''),
                        'type': 'radar_detection'
                    })
                
                elif pattern_name == 'acs_dfs_channel_available':
                    failure_analysis['dfs_events'].append({
                        'radio_mac': radio_mac,
                        'channel': event.get('channel'),
                        'wait_time_minutes': event.get('minutes'),
                        'timestamp': event.get('timestamp', ''),
                        'type': 'channel_available'
                    })
                
                elif pattern_name == 'acs_channel_blacklisted':
                    channel = event.get('channel')
                    reason = event.get('reason')
                    failure_analysis['blacklisted_channels'][f"{channel}:{reason}"] += 1
                
                elif pattern_name == 'acs_algorithm_decision':
                    failure_analysis['algorithm_decisions'].append({
                        'radio_mac': radio_mac,
                        'selected_channel': event.get('channel'),
                        'score': event.get('score'),
                        'criteria': event.get('criteria'),
                        'timestamp': event.get('timestamp', '')
                    })
            
            if radio_failures > 0:
                failure_analysis['problematic_radios'][radio_mac] = radio_failures
        
        # Generate enhanced recommendations
        failure_analysis['recommendations'] = self._generate_enhanced_failure_recommendations(failure_analysis)
        
        return failure_analysis

    def _generate_enhanced_failure_recommendations(self, failure_analysis: Dict[str, Any]) -> List[str]:
        """Generate enhanced actionable recommendations based on comprehensive failure analysis"""
        recommendations = []
        
        total_failures = failure_analysis['total_failures']
        if total_failures == 0:
            recommendations.append("No ACS failures detected - system operating normally")
            return recommendations
        
        failure_reasons = failure_analysis['failure_reasons']
        dfs_events = failure_analysis['dfs_events']
        blacklisted_channels = failure_analysis['blacklisted_channels']
        
        # DFS-specific recommendations
        radar_detections = [e for e in dfs_events if e['type'] == 'radar_detection']
        if radar_detections:
            recommendations.append(f"DFS radar detected {len(radar_detections)} times - ensure proper DFS configuration and consider non-DFS channels")
        
        # Blacklisted channel recommendations
        if blacklisted_channels:
            high_interference_channels = [k for k in blacklisted_channels.keys() if 'HIGH_INTERFERENCE' in k]
            if high_interference_channels:
                recommendations.append(f"Channels {[k.split(':')[0] for k in high_interference_channels]} frequently blacklisted for interference - investigate interference sources")
        
        # Algorithm decision recommendations
        algorithm_decisions = failure_analysis['algorithm_decisions']
        if algorithm_decisions:
            low_score_decisions = [d for d in algorithm_decisions if int(d['score']) < 70]
            if low_score_decisions:
                recommendations.append(f"{len(low_score_decisions)} channel selections with low scores - consider manual channel planning")
        
        # Existing failure reason recommendations
        if 'POLICY_BLOCKED' in failure_reasons:
            policy_failures = failure_reasons['POLICY_BLOCKED']
            recommendations.append(f"Policy constraints blocking {policy_failures} ACS operations - review ACS policies")
        
        if 'INTERFERENCE_TOO_HIGH' in failure_reasons:
            interference_failures = failure_reasons['INTERFERENCE_TOO_HIGH']
            recommendations.append(f"High interference preventing {interference_failures} channel changes - consider interference mitigation")
        
        return recommendations

    def _analyze_advanced_channel_quality(self) -> Dict[str, Any]:
        """Analyze channel quality with advanced interference detection"""
        channel_analysis = {
            'interference_levels': defaultdict(list),
            'channel_utilization': defaultdict(list),
            'quality_scores': defaultdict(list),
            'problematic_channels': [],
            'recommended_channels': [],
            'interference_trends': defaultdict(list),
            'utilization_trends': defaultdict(list),
            'dfs_channel_status': defaultdict(dict),
            'co_channel_interference': defaultdict(list),
            'adjacent_channel_interference': defaultdict(list),
            'interference_sources': defaultdict(list)
        }
        
        for radio_mac, radio_info in self.radio_data.items():
            events = radio_info['events']
            for event in events:
                pattern_name = event.get('pattern_name', '')
                
                if pattern_name == 'acs_interference_detected':
                    channel = event.get('channel')
                    level = event.get('level')
                    source = event.get('source', 'UNKNOWN')
                    
                    if channel and level:
                        channel_analysis['interference_levels'][channel].append({
                            'level': int(level),
                            'source': source,
                            'timestamp': event.get('timestamp', ''),
                            'radio_mac': radio_mac
                        })
                        channel_analysis['interference_sources'][source].append({
                            'channel': channel,
                            'level': int(level),
                            'timestamp': event.get('timestamp', '')
                        })
                
                elif pattern_name == 'acs_channel_scan_result':
                    channel = event.get('channel')
                    rssi = event.get('rssi')
                    noise = event.get('noise')
                    util = event.get('util')
                    bss_count = event.get('bss_count')
                    
                    if channel and rssi and noise and util and bss_count:
                        snr = int(rssi) - int(noise)
                        channel_analysis['channel_utilization'][channel].append({
                            'utilization': int(util),
                            'rssi': int(rssi),
                            'noise': int(noise),
                            'snr': snr,
                            'bss_count': int(bss_count),
                            'timestamp': event.get('timestamp', ''),
                            'radio_mac': radio_mac
                        })
                
                elif pattern_name == 'acs_co_channel_interference':
                    channel = event.get('channel')
                    interfering_aps = event.get('interfering_aps')
                    if channel and interfering_aps:
                        channel_analysis['co_channel_interference'][channel].append({
                            'interfering_aps': int(interfering_aps),
                            'timestamp': event.get('timestamp', ''),
                            'radio_mac': radio_mac
                        })
                
                elif pattern_name == 'acs_adjacent_channel_interference':
                    channel = event.get('channel')
                    adjacent_channel = event.get('adjacent_channel')
                    if channel and adjacent_channel:
                        channel_analysis['adjacent_channel_interference'][channel].append({
                            'adjacent_channel': adjacent_channel,
                            'timestamp': event.get('timestamp', ''),
                            'radio_mac': radio_mac
                        })
        
        # Enhanced channel analysis
        channel_analysis['problematic_channels'] = self._identify_advanced_problematic_channels(channel_analysis)
        channel_analysis['recommended_channels'] = self._identify_advanced_recommended_channels(channel_analysis)
        channel_analysis['dfs_channel_status'] = self._analyze_dfs_channel_status(channel_analysis)
        
        return channel_analysis

    def _identify_advanced_problematic_channels(self, channel_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify channels with advanced problem detection"""
        problematic = []
        
        # Check interference levels with source analysis
        for channel, interference_data in channel_analysis['interference_levels'].items():
            if interference_data:
                avg_interference = statistics.mean([d['level'] for d in interference_data])
                sources = [d['source'] for d in interference_data]
                source_counts = {source: sources.count(source) for source in set(sources)}
                
                if avg_interference > -60:  # High interference threshold
                    problematic.append({
                        'channel': channel,
                        'issue': 'high_interference',
                        'avg_interference': avg_interference,
                        'interference_sources': source_counts,
                        'measurements': len(interference_data)
                    })
        
        # Check co-channel interference
        for channel, co_channel_data in channel_analysis['co_channel_interference'].items():
            if co_channel_data:
                avg_interfering_aps = statistics.mean([d['interfering_aps'] for d in co_channel_data])
                if avg_interfering_aps > 2:  # High co-channel interference threshold
                    problematic.append({
                        'channel': channel,
                        'issue': 'co_channel_interference',
                        'avg_interfering_aps': avg_interfering_aps,
                        'measurements': len(co_channel_data)
                    })
        
        # Check utilization with BSS count
        for channel, util_data in channel_analysis['channel_utilization'].items():
            if util_data:
                avg_utilization = statistics.mean([d['utilization'] for d in util_data])
                avg_bss_count = statistics.mean([d['bss_count'] for d in util_data])
                
                if avg_utilization > 70 or avg_bss_count > 5:  # High utilization or BSS count
                    problematic.append({
                        'channel': channel,
                        'issue': 'high_utilization_or_bss',
                        'avg_utilization': avg_utilization,
                        'avg_bss_count': avg_bss_count,
                        'measurements': len(util_data)
                    })
        
        return problematic

    def _identify_advanced_recommended_channels(self, channel_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify channels with good quality metrics"""
        recommended = []
        
        for channel, util_data in channel_analysis['channel_utilization'].items():
            if util_data:
                avg_utilization = statistics.mean([d['utilization'] for d in util_data])
                avg_snr = statistics.mean([d['snr'] for d in util_data])
                
                # Good channel criteria: low utilization, high SNR
                if avg_utilization < 30 and avg_snr > 20:
                    recommended.append({
                        'channel': channel,
                        'avg_utilization': avg_utilization,
                        'avg_snr': avg_snr,
                        'measurements': len(util_data),
                        'quality_score': (100 - avg_utilization) + avg_snr
                    })
        
        # Sort by quality score
        recommended.sort(key=lambda x: x['quality_score'], reverse=True)
        return recommended[:5]  # Top 5 recommended channels

    def _analyze_dfs_channel_status(self, channel_analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Analyze DFS channel availability and radar detection patterns"""
        dfs_status = {}
        
        # DFS channels in 5GHz band
        dfs_channels = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144]
        
        for channel in dfs_channels:
            dfs_status[str(channel)] = {
                'is_dfs': True,
                'radar_detections': 0,
                'availability_percentage': 100.0,
                'avg_unavailable_time': 0,
                'last_radar_detection': None
            }
        
        return dfs_status

    def _analyze_multi_radio_coordination(self) -> Dict[str, Any]:
        """Analyze multi-radio ACS coordination and conflicts"""
        coordination_analysis = {
            'cluster_coordination': defaultdict(list),
            'channel_conflicts': [],
            'coordination_failures': [],
            'radio_isolation': [],
            'cluster_performance': defaultdict(dict),
            'recommendations': []
        }
        
        for radio_mac, radio_info in self.radio_data.items():
            events = radio_info['events']
            
            for event in events:
                pattern_name = event.get('pattern_name', '')
                
                if pattern_name == 'acs_cluster_coordination':
                    cluster_size = event.get('cluster_size')
                    coordination_analysis['cluster_coordination'][radio_mac].append({
                        'cluster_size': int(cluster_size),
                        'timestamp': event.get('timestamp', ''),
                        'coordination_success': True
                    })
                
                elif pattern_name == 'acs_channel_conflict':
                    radio1 = event.get('radio1')
                    radio2 = event.get('radio2')
                    channel = event.get('channel')
                    
                    coordination_analysis['channel_conflicts'].append({
                        'radio1': radio1,
                        'radio2': radio2,
                        'conflict_channel': channel,
                        'timestamp': event.get('timestamp', ''),
                        'severity': 'high'
                    })
                
                elif pattern_name == 'acs_coordination_failure':
                    coordination_analysis['coordination_failures'].append({
                        'radio_mac': radio_mac,
                        'timestamp': event.get('timestamp', ''),
                        'failure_type': 'coordination_unavailable'
                    })
        
        # Analyze radio isolation
        coordination_analysis['radio_isolation'] = self._identify_isolated_radios(coordination_analysis)
        
        # Generate coordination recommendations
        coordination_analysis['recommendations'] = self._generate_coordination_recommendations(coordination_analysis)
        
        return coordination_analysis

    def _identify_isolated_radios(self, coordination_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify radios that are not participating in cluster coordination"""
        isolated_radios = []
        
        for radio_mac in self.radio_data.keys():
            coordination_events = coordination_analysis['cluster_coordination'].get(radio_mac, [])
            if not coordination_events:
                isolated_radios.append({
                    'radio_mac': radio_mac,
                    'isolation_reason': 'no_coordination_events',
                    'recommendation': 'Check radio connectivity and cluster configuration'
                })
        
        return isolated_radios

    def _generate_coordination_recommendations(self, coordination_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for multi-radio coordination issues"""
        recommendations = []
        
        # Channel conflict recommendations
        if coordination_analysis['channel_conflicts']:
            recommendations.append(f"Detected {len(coordination_analysis['channel_conflicts'])} channel conflicts - review cluster coordination settings")
        
        # Coordination failure recommendations
        if coordination_analysis['coordination_failures']:
            recommendations.append(f"ACS coordination failed {len(coordination_analysis['coordination_failures'])} times - check cluster connectivity")
        
        # Radio isolation recommendations
        if coordination_analysis['radio_isolation']:
            isolated_count = len(coordination_analysis['radio_isolation'])
            recommendations.append(f"{isolated_count} radios not participating in cluster coordination - investigate connectivity")
        
        return recommendations

    def _analyze_predictive_patterns(self) -> Dict[str, Any]:
        """Analyze predictive patterns and automated optimization"""
        predictive_analysis = {
            'predictions': [],
            'automated_optimizations': [],
            'prediction_accuracy': defaultdict(list),
            'optimization_effectiveness': defaultdict(list),
            'trend_analysis': defaultdict(list),
            'recommendations': []
        }
        
        for radio_mac, radio_info in self.radio_data.items():
            events = radio_info['events']
            
            for event in events:
                pattern_name = event.get('pattern_name', '')
                
                if pattern_name == 'acs_predictive_analysis':
                    predictive_analysis['predictions'].append({
                        'radio_mac': radio_mac,
                        'channel': event.get('channel'),
                        'prediction': event.get('prediction'),
                        'timeframe': event.get('timeframe'),
                        'timestamp': event.get('timestamp', '')
                    })
                
                elif pattern_name == 'acs_automated_optimization':
                    predictive_analysis['automated_optimizations'].append({
                        'radio_mac': radio_mac,
                        'optimization': event.get('optimization'),
                        'timestamp': event.get('timestamp', '')
                    })
        
        return predictive_analysis
    
    def _generate_actionable_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable ACS recommendations"""
        recommendations = []
        
        for radio_mac, radio_info in self.radio_data.items():
            cycles = self._detect_acs_cycles().get(radio_mac, [])
            transitions = self._analyze_fsm_transitions().get(radio_mac, [])
            
            # Analyze cycle performance
            completed_cycles = [c for c in cycles if c['status'] == 'completed']
            avg_cycle_duration = statistics.mean([c['duration_seconds'] for c in completed_cycles]) if completed_cycles else 0
            
            # Analyze transition patterns
            serving_to_checking = len([t for t in transitions if t['from_state'] == 'SERVING' and t['to_state'] == 'CHECKING'])
            checking_to_serving = len([t for t in transitions if t['from_state'] == 'CHECKING' and t['to_state'] == 'SERVING'])
            
            # Generate recommendations based on analysis
            if avg_cycle_duration > 300:  # 5 minutes
                recommendation = "acs_cycles_too_long_optimize_scanning"
                priority = "high"
                reasoning = f"ACS cycles averaging {avg_cycle_duration:.1f} seconds, consider optimizing scanning parameters"
            elif serving_to_checking > checking_to_serving * 1.5:
                recommendation = "acs_frequent_triggers_review_thresholds"
                priority = "medium"
                reasoning = f"Frequent ACS triggers ({serving_to_checking}) vs completions ({checking_to_serving}), review trigger thresholds"
            elif len(completed_cycles) == 0:
                recommendation = "acs_no_completed_cycles_investigate"
                priority = "high"
                reasoning = "No completed ACS cycles detected, investigate system configuration"
            else:
                recommendation = "acs_performance_acceptable_monitor"
                priority = "low"
                reasoning = f"ACS performance appears acceptable with {len(completed_cycles)} completed cycles"
            
            recommendations.append({
                'radio_mac': radio_mac,
                'recommendation': recommendation,
                'priority': priority,
                'reasoning': reasoning,
                'cycles_count': len(cycles),
                'completed_cycles': len(completed_cycles),
                'avg_cycle_duration': avg_cycle_duration,
                'transitions_count': len(transitions)
            })
        
        return recommendations
    
    def _generate_enhanced_summary(self, events: List[Dict[str, Any]], acs_cycles: Dict[str, List[Dict[str, Any]]], fsm_transitions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate enhanced analysis summary"""
        if not events:
            return {
                "total_events": 0,
                "time_range": "No data",
                "status": "No ACS events found",
                "radios_analyzed": 0,
                "total_cycles": 0,
                "total_transitions": 0
            }
        
        timestamps = [event.get("timestamp", "") for event in events if event.get("timestamp")]
        
        return {
            "total_events": len(events),
            "time_range": f"{min(timestamps)} to {max(timestamps)}" if timestamps else "Unknown",
            "status": "Enhanced analysis completed",
            "radios_analyzed": len(self.radio_data),
            "total_cycles": sum(len(cycles) for cycles in acs_cycles.values()),
            "total_transitions": sum(len(transitions) for transitions in fsm_transitions.values()),
            "pattern_framework_enabled": True,
            "enhanced_features": [
                "fsm_transition_tracking",
                "acs_cycle_detection", 
                "channel_selection_analysis",
                "performance_metrics",
                "actionable_recommendations",
                "multi_file_processing"
            ]
        }
    
    def _generate_enhanced_timeline(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate enhanced timeline of events"""
        timeline = []
        
        for event in events:
            timeline.append({
                "timestamp": event.get("timestamp", ""),
                "pattern_name": event.get("pattern_name", "unknown"),
                "radio_mac": event.get("radio_mac", ""),
                "confidence": event.get("confidence", 0.0),
                "description": self._get_event_description(event),
                "from_state": event.get("from_state"),
                "to_state": event.get("to_state"),
                "channel": event.get("channel"),
                "frequency": event.get("frequency"),
                "bandwidth": event.get("bandwidth")
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x.get("timestamp", ""))
        
        return timeline
    
    def _get_event_description(self, event: Dict[str, Any]) -> str:
        """Get human-readable description of event"""
        pattern_name = event.get("pattern_name", "")
        radio_mac = event.get("radio_mac", "")
        
        descriptions = {
            "acs_fsm_transition": f"FSM transition: {event.get('from_state', 'UNKNOWN')} → {event.get('to_state', 'UNKNOWN')} for radio {radio_mac}",
            "acs_trigger_event": f"ACS triggered for radio {radio_mac}, reason: {event.get('reason', 'unknown')}",
            "acs_countdown": f"Countdown message for radio {radio_mac}",
            "acs_preference_query": f"Channel preference query for radio {radio_mac}",
            "acs_selection_trigger": f"Channel selection request for radio {radio_mac}",
            "acs_radio_info": f"Radio info: channel {event.get('channel', 'unknown')}, freq {event.get('frequency', 'unknown')}, bandwidth {event.get('bandwidth', 'unknown')}"
        }
        
        return descriptions.get(pattern_name, f"ACS event: {pattern_name}")
    
    def _calculate_enhanced_metrics(self, events: List[Dict[str, Any]], acs_cycles: Dict[str, List[Dict[str, Any]]], fsm_transitions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate enhanced performance metrics"""
        if not events:
            return {"error": "No events to analyze"}
        
        # Basic metrics
        total_events = len(events)
        unique_radios = len(self.radio_data)
        
        # Cycle metrics
        total_cycles = sum(len(cycles) for cycles in acs_cycles.values())
        completed_cycles = sum(len([c for c in cycles if c['status'] == 'completed']) for cycles in acs_cycles.values())
        cycle_success_rate = completed_cycles / total_cycles if total_cycles > 0 else 0
        
        # Transition metrics
        total_transitions = sum(len(transitions) for transitions in fsm_transitions.values())
        
        # Duration metrics
        cycle_durations = []
        for cycles in acs_cycles.values():
            for cycle in cycles:
                if cycle['status'] == 'completed' and cycle['duration_seconds'] > 0:
                    cycle_durations.append(cycle['duration_seconds'])
        
        avg_cycle_duration = statistics.mean(cycle_durations) if cycle_durations else 0
        
        # Pattern matching metrics
        pattern_matches = len([e for e in events if e.get("confidence", 0) > 0])
        avg_confidence = statistics.mean([e.get("confidence", 0) for e in events if e.get("confidence", 0) > 0]) if events else 0
        
        return {
            "total_events": total_events,
            "unique_radios": unique_radios,
            "total_acs_cycles": total_cycles,
            "completed_cycles": completed_cycles,
            "cycle_success_rate": cycle_success_rate,
            "total_fsm_transitions": total_transitions,
            "average_cycle_duration_seconds": avg_cycle_duration,
            "pattern_matches": pattern_matches,
            "pattern_match_rate": pattern_matches / total_events if total_events > 0 else 0,
            "average_confidence": avg_confidence
        }
    
    def _generate_enhanced_insights(self, events: List[Dict[str, Any]], acs_cycles: Dict[str, List[Dict[str, Any]]], fsm_transitions: Dict[str, List[Dict[str, Any]]], recommendations: List[Dict[str, Any]]) -> List[str]:
        """Generate enhanced insights from analysis"""
        insights = []
        
        if not events:
            insights.append("No ACS events found in the provided data")
            return insights
        
        # Basic insights
        insights.append(f"Analyzed {len(events)} ACS events across {len(self.radio_data)} radios")
        
        # Cycle insights
        total_cycles = sum(len(cycles) for cycles in acs_cycles.values())
        completed_cycles = sum(len([c for c in cycles if c['status'] == 'completed']) for cycles in acs_cycles.values())
        
        if total_cycles > 0:
            success_rate = completed_cycles / total_cycles
            insights.append(f"Detected {total_cycles} ACS cycles with {success_rate:.1%} completion rate")
            
            if success_rate >= 0.8:
                insights.append("ACS system shows excellent cycle completion performance")
            elif success_rate >= 0.6:
                insights.append("ACS system shows good cycle completion performance")
            elif success_rate >= 0.3:
                insights.append("ACS system shows moderate cycle completion performance - consider optimization")
            else:
                insights.append("ACS system shows poor cycle completion performance - immediate attention needed")
        
        # Transition insights
        total_transitions = sum(len(transitions) for transitions in fsm_transitions.values())
        insights.append(f"Tracked {total_transitions} FSM state transitions")
        
        # Recommendation insights
        high_priority_recommendations = [r for r in recommendations if r.get("priority") == "high"]
        if high_priority_recommendations:
            insights.append(f"{len(high_priority_recommendations)} radios require high-priority attention for ACS optimization")
        
        # Pattern recognition insights
        pattern_matches = len([e for e in events if e.get("confidence", 0) > 0])
        match_rate = pattern_matches / len(events) if events else 0
        insights.append(f"Pattern recognition framework achieved {match_rate:.1%} match rate with high confidence")
        
        insights.append("Enhanced ACS analysis completed successfully with comprehensive insights")
        
        return insights
    
    def render_components(self, analysis_data: dict) -> dict:
        """Provide pre-rendered UI components"""
        return {
            "summary_card": self._render_summary_card(analysis_data.get("summary", {})),
            "timeline_chart": self._render_timeline_chart(analysis_data.get("timeline", [])),
            "metrics_dashboard": self._render_metrics_dashboard(analysis_data.get("metrics", {}))
        }
    
    def _render_summary_card(self, summary_data: dict) -> str:
        """Render HTML summary card"""
        return f"""
        <div class="acs-summary-card">
            <h3>WNC ACS Analysis Summary</h3>
            <p><strong>Total Events:</strong> {summary_data.get('total_events', 0)}</p>
            <p><strong>Radios Analyzed:</strong> {summary_data.get('radios_analyzed', 0)}</p>
            <p><strong>ACS Cycles:</strong> {summary_data.get('total_cycles', 0)}</p>
            <p><strong>FSM Transitions:</strong> {summary_data.get('total_transitions', 0)}</p>
            <p><strong>Time Range:</strong> {summary_data.get('time_range', 'Unknown')}</p>
            <p><strong>Status:</strong> {summary_data.get('status', 'Unknown')}</p>
        </div>
        """
    
    def _render_timeline_chart(self, timeline_data: list) -> dict:
        """Render timeline chart configuration"""
        return {
            "type": "timeline",
            "data": timeline_data,
            "options": {
                "title": "ACS Events Timeline",
                "height": 400
            }
        }
    
    def _render_metrics_dashboard(self, metrics_data: dict) -> dict:
        """Render metrics dashboard configuration"""
        return {
            "type": "dashboard",
            "metrics": metrics_data,
            "layout": "grid"
        }
    
    def _write_enhanced_results_to_files(self, results: dict, output_dir: Path, config: dict) -> None:
        """Write enhanced analysis results to comprehensive files"""
        
        # Write main JSON file
        json_file = output_dir / "agent_data.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Write ACS-specific CSV files
        self._write_acs_timeline_csv(results, output_dir)
        self._write_acs_cycles_csv(results, output_dir)
        self._write_acs_metrics_json(results, output_dir)
        
        # Write enhanced HTML report
        if config.get("generate_html_report", True):
            html_file = output_dir / "agent_report.html"
            html_content = self._generate_html_report(results)
            with open(html_file, 'w') as f:
                f.write(html_content)
        
        # Write raw data if requested
        if config.get("include_raw_data", False):
            raw_file = output_dir / "acs_raw_data.json"
            with open(raw_file, 'w') as f:
                json.dump(self.radio_data, f, indent=2, default=str)
    
    def _write_acs_timeline_csv(self, results: dict, output_dir: Path) -> None:
        """Write ACS events timeline CSV"""
        csv_file = output_dir / "acs_events_timeline.csv"
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Pattern Name', 'Radio MAC', 'Confidence', 'Description', 'From State', 'To State', 'Channel', 'Frequency', 'Bandwidth'])
            
            timeline = results.get('analysis_data', {}).get('timeline', [])
            for event in timeline:
                writer.writerow([
                    event.get('timestamp', ''),
                    event.get('pattern_name', ''),
                    event.get('radio_mac', ''),
                    event.get('confidence', 0.0),
                    event.get('description', ''),
                    event.get('from_state', ''),
                    event.get('to_state', ''),
                    event.get('channel', ''),
                    event.get('frequency', ''),
                    event.get('bandwidth', '')
                ])
    
    def _write_acs_cycles_csv(self, results: dict, output_dir: Path) -> None:
        """Write ACS cycles summary CSV"""
        csv_file = output_dir / "acs_cycles_summary.csv"
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Radio MAC', 'Cycle ID', 'Start Time', 'End Time', 'Status', 'Duration (seconds)', 'Events Count'
            ])
            
            acs_cycles = results.get('analysis_data', {}).get('acs_cycles', {})
            
            for radio_mac, cycles in acs_cycles.items():
                for cycle in cycles:
                    writer.writerow([
                        radio_mac,
                        cycle.get('cycle_id', ''),
                        cycle.get('start_time', ''),
                        cycle.get('end_time', ''),
                        cycle.get('status', ''),
                        cycle.get('duration_seconds', 0),
                        len(cycle.get('events', []))
                    ])
    
    def _write_acs_metrics_json(self, results: dict, output_dir: Path) -> None:
        """Write ACS metrics JSON"""
        metrics_file = output_dir / "acs_metrics.json"
        
        metrics_data = {
            "overall_metrics": results.get('analysis_data', {}).get('metrics', {}),
            "acs_cycles": results.get('analysis_data', {}).get('acs_cycles', {}),
            "fsm_transitions": results.get('analysis_data', {}).get('fsm_transitions', {}),
            "channel_analysis": results.get('analysis_data', {}).get('channel_analysis', {}),
            "recommendations_summary": {
                "total_recommendations": len(results.get('analysis_data', {}).get('recommendations', [])),
                "high_priority": len([r for r in results.get('analysis_data', {}).get('recommendations', []) if r.get('priority') == 'high']),
                "medium_priority": len([r for r in results.get('analysis_data', {}).get('recommendations', []) if r.get('priority') == 'medium']),
                "low_priority": len([r for r in results.get('analysis_data', {}).get('recommendations', []) if r.get('priority') == 'low'])
            },
            "analysis_metadata": results.get('metadata', {})
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2, default=str)
    
    def _generate_html_report(self, results: dict) -> str:
        """Generate HTML report using the modular report generator"""
        analysis_data = results['analysis_data']
        summary = analysis_data.get('summary', {})
        metrics = analysis_data.get('metrics', {})
        insights = analysis_data.get('insights', [])
        
        # Use the modular report generator if available
        if self.report_generator:
            try:
                # Enhance results structure for the report generator
                enhanced_results = {
                    'analysis_data': {
                        'summary': summary,
                        'metrics': metrics,
                        'insights': insights,
                        'acs_cycles': analysis_data.get('acs_cycles', {}),
                        'fsm_transitions': analysis_data.get('fsm_transitions', {}),
                        'radio_analysis': analysis_data.get('radio_analysis', {}),
                        'channel_preferences': analysis_data.get('channel_analysis', {}),
                        'recommendations': analysis_data.get('recommendations', [])
                    },
                    'metadata': results.get('metadata', {})
                }
                return self.report_generator.generate_html_report(enhanced_results)
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
            <title>WNC ACS Analysis Report</title>
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
                <h1>WNC ACS Analysis Report</h1>
                <p><strong>Agent Version:</strong> {self.version}</p>
                <p><strong>Agent Type:</strong> {self.agent_type}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <div class="metric"><strong>Total Events:</strong> {summary.get('total_events', 0)}</div>
                <div class="metric"><strong>Radios Analyzed:</strong> {summary.get('radios_analyzed', 0)}</div>
                <div class="metric"><strong>Processing Time:</strong> {summary.get('processing_time', 0):.2f} seconds</div>
                <div class="metric"><strong>Status:</strong> <span class="success">{summary.get('status', 'completed')}</span></div>
            </div>
            
            <div class="metrics">
                <h2>Performance Metrics</h2>
                <div class="metric"><strong>Events per Second:</strong> {metrics.get('events_per_second', 0):.1f}</div>
                <div class="metric"><strong>Cycle Success Rate:</strong> {metrics.get('cycle_success_rate', 0):.1%}</div>
            </div>
            
            <div class="insights">
                <h2>Analysis Insights</h2>
                {''.join(f'<div style="margin: 10px 0;">{insight}</div>' for insight in insights)}
            </div>
        </body>
        </html>
        """
        return html
