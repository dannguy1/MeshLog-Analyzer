"""
Enhanced WNC TPYOPT Agent for MeshLog Integrated Agent System

This agent analyzes WNC Topology Optimization behavior, tracking FSM state transitions,
optimization cycles, and device roaming decisions.
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
from .tpyopt_report_generator import TPYOPTReportGenerator

class WNCTpyoptAgent(AgentInterface):
    """Enhanced WNC TPYOPT Analysis Agent"""
    
    @property
    def agent_type(self) -> str:
        return "wnc-tpyopt"
    
    @property
    def version(self) -> str:
        return "2.1.0-enterprise"
    
    def __init__(self):
        # Initialize pattern recognition framework
        self.pattern_registry = PatternRegistry()
        self.pattern_interface = AgentPatternInterface("wnc-tpyopt", self.pattern_registry)
        
        self.capabilities = [
            "tpyopt_analysis", 
            "fsm_transition_tracking", 
            "optimization_cycle_detection",
            "roaming_command_tracking",
            "packet_loss_monitoring",
            "performance_metrics",
            "multi_file_processing",
            "enterprise_failure_analysis",
            "optimization_quality_assessment",
            "device_coordination_analysis"
        ]
        
        self.description = "Enterprise-grade WNC TPYOPT analysis with advanced failure analysis, optimization quality assessment, and device coordination tracking"
        
        # Enhanced configuration schemas
        self.input_schema = {
            "type": "object",
            "properties": {
                "analysis_config": {
                    "type": "object",
                    "properties": {
                        "device_filter": {
                            "type": "string",
                            "description": "MAC address pattern to filter devices (e.g., 'aa:bb:*' or specific MAC)"
                        },
                        "cycle_timeout_minutes": {
                            "type": "integer",
                            "default": 5,
                            "description": "Timeout for incomplete optimization cycles"
                        },
                        "merge_rotation_files": {
                            "type": "boolean",
                            "default": True,
                            "description": "Automatically discover and merge log rotation files"
                        },
                        "max_rotation_files": {
                            "type": "integer",
                            "default": 10,
                            "description": "Maximum number of rotation files to process"
                        },
                        "enable_enhanced_insights": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable advanced failure analysis and optimization insights"
                        },
                        "include_raw_data": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include raw log lines in output for debugging"
                        },
                        "detailed_timeline": {
                            "type": "boolean",
                            "default": True,
                            "description": "Generate detailed event timeline with all FSM transitions"
                        },
                        "failure_analysis_depth": {
                            "type": "string",
                            "enum": ["basic", "detailed", "comprehensive"],
                            "default": "detailed",
                            "description": "Depth of failure analysis"
                        },
                        "optimization_quality_threshold": {
                            "type": "number",
                            "default": 0.7,
                            "description": "Quality threshold for optimization effectiveness (0.0-1.0)"
                        }
                    }
                }
            }
        }
        
        self.output_schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "object"},
                "timeline": {"type": "array"},
                "metrics": {"type": "object"},
                "insights": {"type": "object"},
                "optimization_cycles": {"type": "array"},
                "fsm_transitions": {"type": "array"},
                "roaming_analysis": {"type": "object"},
                "failure_analysis": {"type": "object"},
                "optimization_quality": {"type": "object"},
                "device_coordination": {"type": "object"},
                "metadata": {"type": "object"}
            }
        }
        
        # Initialize analysis state
        self.device_data = defaultdict(lambda: {
            'events': [],
            'fsm_transitions': [],
            'optimization_cycles': [],
            'roaming_commands': [],
            'packet_loss_events': [],
            'first_seen': None,
            'last_seen': None
        })
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize modular report generator
        self.report_generator = TPYOPTReportGenerator()
    
    def analyze(self, log_paths: list, output_path: str, analysis_config: dict = None) -> dict:
        """Enhanced TPYOPT analysis with enterprise features"""
        start_time = time.time()
        config = analysis_config or {}
        
        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.device_data.clear()
            
            # Expand log files to include rotation files if enabled
            expanded_log_paths = self._expand_log_files(log_paths, config)
            
            # Process log files with enhanced capabilities
            tpyopt_analysis = self._process_log_files_enhanced(expanded_log_paths, config)
            
            # Create comprehensive results
            results = {
                "status": "completed",
                "analysis_id": f"tpyopt_enterprise_{int(time.time())}",
                "analysis_data": tpyopt_analysis,
                "metadata": {
                    "agent_type": self.agent_type,
                    "version": self.version,
                    "processing_time": time.time() - start_time,
                    "input_files": len(log_paths),
                    "expanded_files": len(expanded_log_paths),
                    "pattern_framework_enabled": True,
                    "enterprise_features_enabled": config.get('enable_enhanced_insights', True),
                    "configuration": config
                }
            }
            
            # Write enhanced results
            file_outputs = self._write_enhanced_results_to_files(results, output_dir, config)
            
            return {
                "status": "completed",
                "message": f"Enterprise TPYOPT analysis completed, results written to {output_path}",
                "files_created": list(file_outputs.keys()),
                "file_paths": {k: str(v) for k, v in file_outputs.items()},
                "analysis_summary": {
                    "total_cycles": len(tpyopt_analysis.get('optimization_cycles', [])),
                    "total_events": len(tpyopt_analysis.get('timeline', [])),
                    "processing_time": time.time() - start_time
                }
            }
            
        except Exception as e:
            self.logger.error(f"TPYOPT analysis failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_log_files_enhanced(self, log_paths: list, config: dict) -> dict:
        """Enhanced TPYOPT log processing with enterprise modules"""
        
        # Parse TPYOPT logs
        tpyopt_events = self._parse_tpyopt_logs_enhanced(log_paths, config)
        
        # Detect optimization cycles
        optimization_cycles = self._detect_optimization_cycles()
        
        # Analyze FSM transitions
        fsm_transitions = self._analyze_fsm_transitions()
        
        # Analyze roaming commands
        roaming_analysis = self._analyze_roaming_commands()
        
        # Enterprise analysis modules
        failure_analysis = {}
        optimization_quality = {}
        device_coordination = {}
        
        if config.get('enable_enhanced_insights', True):
            # Priority 1: Enterprise failure analysis
            failure_analysis = self._analyze_tpyopt_failures()
            
            # Priority 2: Optimization quality assessment
            optimization_quality = self._analyze_optimization_quality()
            
            # Priority 2: Device coordination analysis
            device_coordination = self._analyze_device_coordination()
        
        # Generate enhanced analysis
        summary = self._generate_enhanced_summary(tpyopt_events, optimization_cycles, fsm_transitions)
        timeline = self._generate_enhanced_timeline(tpyopt_events)
        metrics = self._calculate_enhanced_metrics(tpyopt_events, optimization_cycles, fsm_transitions)
        insights = self._generate_enhanced_insights(tpyopt_events, optimization_cycles, fsm_transitions)
        
        return {
            "summary": summary,
            "timeline": timeline,
            "metrics": metrics,
            "insights": insights,
            "optimization_cycles": optimization_cycles,
            "fsm_transitions": fsm_transitions,
            "roaming_analysis": roaming_analysis,
            "failure_analysis": failure_analysis,
            "optimization_quality": optimization_quality,
            "device_coordination": device_coordination
        }
    
    def _parse_tpyopt_logs_enhanced(self, files: List[str], config: dict) -> List[Dict[str, Any]]:
        """Parse TPYOPT logs using pattern recognition framework"""
        events = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        result = self.pattern_interface.parse_log_line(line, line_num)
                        
                        if result['status'] == 'matched':
                            event = self._process_pattern_match(result, line)
                            if event:
                                events.append(event)
                                self._update_device_data(event)
                                
            except Exception as e:
                self.logger.warning(f"Could not process file {file_path}: {e}")
        
        return events
    
    def _process_pattern_match(self, result: dict, line: str) -> Optional[Dict[str, Any]]:
        """Process pattern match result"""
        pattern_name = result['pattern_name']
        match_data = result['match_data']
        
        timestamp = self._extract_timestamp(line)
        
        event = {
            'timestamp': timestamp,
            'pattern_name': pattern_name,
            'confidence': result['confidence'],
            'raw_line': line,
            'match_data': match_data
        }
        
        # Add pattern-specific data
        if 'mac' in match_data:
            event['device_mac'] = match_data['mac']
        if 'from_state' in match_data and 'to_state' in match_data:
            event['from_state'] = match_data['from_state']
            event['to_state'] = match_data['to_state']
        if 'from_mac' in match_data and 'to_mac' in match_data:
            event['from_mac'] = match_data['from_mac']
            event['to_mac'] = match_data['to_mac']
        
        return event
    
    def _extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line"""
        timestamp_result = self.pattern_interface.parse_log_line(line)
        
        if timestamp_result['status'] == 'matched' and 'timestamp' in timestamp_result['pattern_name']:
            match_data = timestamp_result['match_data']
            if all(key in match_data for key in ['year', 'month', 'day', 'hour', 'minute', 'second']):
                return f"{match_data['year']} {match_data['month']} {match_data['day']} {match_data['hour']}:{match_data['minute']}:{match_data['second']}"
        
        return ""
    
    def _update_device_data(self, event: Dict[str, Any]) -> None:
        """Update device data with new event"""
        if 'device_mac' not in event:
            return
        
        device_mac = event['device_mac']
        device_info = self.device_data[device_mac]
        
        device_info['events'].append(event)
        
        timestamp = event.get('timestamp', '')
        if timestamp:
            if not device_info['first_seen'] or timestamp < device_info['first_seen']:
                device_info['first_seen'] = timestamp
            if not device_info['last_seen'] or timestamp > device_info['last_seen']:
                device_info['last_seen'] = timestamp
        
        pattern_name = event.get('pattern_name', '')
        
        if 'fsm_transition' in pattern_name:
            device_info['fsm_transitions'].append(event)
        elif 'roaming_command' in pattern_name:
            device_info['roaming_commands'].append(event)
        elif 'packet_loss' in pattern_name:
            device_info['packet_loss_events'].append(event)
    
    def _detect_optimization_cycles(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detect optimization cycles"""
        cycles = {}
        
        for device_mac, device_info in self.device_data.items():
            device_cycles = []
            events = device_info['events']
            
            # Find cycle triggers (WaitTrigger -> SendScan)
            for i, event in enumerate(events):
                if (event.get('pattern_name') == 'tpyopt_fsm_transition' and 
                    event.get('from_state') == 'WaitTrigger' and 
                    event.get('to_state') == 'SendScan'):
                    
                    cycle = {
                        'cycle_id': f"{device_mac}_cycle_{len(device_cycles)}",
                        'start_time': event['timestamp'],
                        'start_event': event,
                        'events': [event],
                        'status': 'active'
                    }
                    
                    # Find cycle completion
                    for j in range(i + 1, len(events)):
                        next_event = events[j]
                        cycle['events'].append(next_event)
                        
                        if (next_event.get('pattern_name') == 'tpyopt_fsm_transition' and 
                            next_event.get('to_state') == 'WaitTrigger'):
                            cycle['status'] = 'completed'
                            cycle['end_time'] = next_event['timestamp']
                            break
                    
                    device_cycles.append(cycle)
            
            cycles[device_mac] = device_cycles
        
        return cycles
    
    def _analyze_fsm_transitions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze FSM transitions"""
        transitions = {}
        
        for device_mac, device_info in self.device_data.items():
            device_transitions = []
            
            for event in device_info['events']:
                if event.get('pattern_name') == 'tpyopt_fsm_transition':
                    transition = {
                        'timestamp': event['timestamp'],
                        'from_state': event.get('from_state', 'UNKNOWN'),
                        'to_state': event.get('to_state', 'UNKNOWN'),
                        'device_mac': device_mac
                    }
                    device_transitions.append(transition)
            
            transitions[device_mac] = device_transitions
        
        return transitions
    
    def _analyze_roaming_commands(self) -> Dict[str, Any]:
        """Analyze roaming commands"""
        analysis = {
            'total_commands': 0,
            'roaming_pairs': defaultdict(int),
            'device_roaming_activity': {}
        }
        
        for device_mac, device_info in self.device_data.items():
            roaming_commands = device_info['roaming_commands']
            analysis['total_commands'] += len(roaming_commands)
            analysis['device_roaming_activity'][device_mac] = len(roaming_commands)
            
            for command in roaming_commands:
                from_mac = command.get('from_mac', '')
                to_mac = command.get('to_mac', '')
                if from_mac and to_mac:
                    analysis['roaming_pairs'][f"{from_mac} -> {to_mac}"] += 1
        
        return analysis
    
    def _generate_enhanced_summary(self, events: List[Dict[str, Any]], optimization_cycles: Dict, fsm_transitions: Dict) -> Dict[str, Any]:
        """Generate enhanced analysis summary"""
        if not events:
            return {
                "total_events": 0,
                "time_range": "No data",
                "status": "No TPYOPT events found"
            }
        
        timestamps = [event.get("timestamp", "") for event in events if event.get("timestamp")]
        
        return {
            "total_events": len(events),
            "time_range": f"{min(timestamps)} to {max(timestamps)}" if timestamps else "Unknown",
            "status": "Enhanced analysis completed",
            "devices_analyzed": len(self.device_data),
            "total_cycles": sum(len(cycles) for cycles in optimization_cycles.values()),
            "total_transitions": sum(len(transitions) for transitions in fsm_transitions.values()),
            "pattern_framework_enabled": True
        }
    
    def _generate_enhanced_timeline(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate enhanced timeline"""
        timeline = []
        
        for event in events:
            timeline.append({
                "timestamp": event.get("timestamp", ""),
                "pattern_name": event.get("pattern_name", "unknown"),
                "device_mac": event.get("device_mac", ""),
                "confidence": event.get("confidence", 0.0),
                "description": self._get_event_description(event)
            })
        
        timeline.sort(key=lambda x: x.get("timestamp", ""))
        return timeline
    
    def _get_event_description(self, event: Dict[str, Any]) -> str:
        """Get human-readable event description"""
        pattern_name = event.get("pattern_name", "")
        device_mac = event.get("device_mac", "")
        
        descriptions = {
            "tpyopt_fsm_transition": f"FSM transition: {event.get('from_state', 'UNKNOWN')} → {event.get('to_state', 'UNKNOWN')}",
            "tpyopt_optimization_trigger": "Topology optimization triggered",
            "tpyopt_roaming_command": f"Roaming command: {event.get('from_mac', '')} → {event.get('to_mac', '')}",
            "tpyopt_packet_loss": "Packet loss detected",
            "tpyopt_build_topology_success": "Topology build successful",
            "tpyopt_build_topology_fail": "Topology build failed"
        }
        
        return descriptions.get(pattern_name, f"TPYOPT event: {pattern_name}")
    
    def _calculate_enhanced_metrics(self, events: List[Dict[str, Any]], optimization_cycles: Dict, fsm_transitions: Dict) -> Dict[str, Any]:
        """Calculate enhanced metrics"""
        if not events:
            return {"error": "No events to analyze"}
        
        total_cycles = sum(len(cycles) for cycles in optimization_cycles.values())
        completed_cycles = sum(len([c for c in cycles if c['status'] == 'completed']) for cycles in optimization_cycles.values())
        cycle_success_rate = completed_cycles / total_cycles if total_cycles > 0 else 0
        
        pattern_matches = len([e for e in events if e.get("confidence", 0) > 0])
        avg_confidence = statistics.mean([e.get("confidence", 0) for e in events if e.get("confidence", 0) > 0]) if events else 0
        
        return {
            "total_events": len(events),
            "unique_devices": len(self.device_data),
            "total_optimization_cycles": total_cycles,
            "completed_cycles": completed_cycles,
            "cycle_success_rate": cycle_success_rate,
            "total_fsm_transitions": sum(len(transitions) for transitions in fsm_transitions.values()),
            "pattern_matches": pattern_matches,
            "pattern_match_rate": pattern_matches / len(events),
            "average_confidence": avg_confidence
        }
    
    def _generate_enhanced_insights(self, events: List[Dict[str, Any]], optimization_cycles: Dict, fsm_transitions: Dict) -> List[str]:
        """Generate enhanced insights"""
        insights = []
        
        if not events:
            insights.append("No TPYOPT events found in the provided data")
            return insights
        
        insights.append(f"Analyzed {len(events)} TPYOPT events across {len(self.device_data)} devices")
        
        total_cycles = sum(len(cycles) for cycles in optimization_cycles.values())
        completed_cycles = sum(len([c for c in cycles if c['status'] == 'completed']) for cycles in optimization_cycles.values())
        
        if total_cycles > 0:
            success_rate = completed_cycles / total_cycles
            insights.append(f"Detected {total_cycles} optimization cycles with {success_rate:.1%} completion rate")
        
        total_transitions = sum(len(transitions) for transitions in fsm_transitions.values())
        insights.append(f"Tracked {total_transitions} FSM state transitions")
        
        insights.append("Enhanced TPYOPT analysis completed successfully")
        
        return insights
    
    def _write_results_to_files(self, results: dict, output_dir: Path, config: dict) -> None:
        """Write results to files"""
        # Write main JSON file
        json_file = output_dir / "agent_data.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Write metrics JSON
        metrics_file = output_dir / "tpyopt_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(results.get('analysis_data', {}), f, indent=2, default=str)
        
        # Write HTML report
        html_file = output_dir / "agent_report.html"
        html_content = self._generate_html_report(results)
        with open(html_file, 'w') as f:
            f.write(html_content)
    
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
                        'optimization_cycles': analysis_data.get('optimization_cycles', {}),
                        'roaming_commands': analysis_data.get('roaming_commands', {}),
                        'device_analysis': analysis_data.get('device_analysis', {}),
                        'failure_analysis': analysis_data.get('failure_analysis', {}),
                        'fsm_transitions': analysis_data.get('fsm_transitions', {}),
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
            <title>WNC TPYOPT Analysis Report</title>
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
                <h1>WNC TPYOPT Analysis Report</h1>
                <p><strong>Agent Version:</strong> {self.version}</p>
                <p><strong>Agent Type:</strong> {self.agent_type}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <div class="metric"><strong>Total Events:</strong> {summary.get('total_events', 0)}</div>
                <div class="metric"><strong>Devices Analyzed:</strong> {summary.get('devices_analyzed', 0)}</div>
                <div class="metric"><strong>Processing Time:</strong> {summary.get('processing_time', 0):.2f} seconds</div>
                <div class="metric"><strong>Status:</strong> <span class="success">{summary.get('status', 'completed')}</span></div>
            </div>
            
            <div class="metrics">
                <h2>Performance Metrics</h2>
                <div class="metric"><strong>Events per Second:</strong> {metrics.get('events_per_second', 0):.1f}</div>
                <div class="metric"><strong>Optimization Success Rate:</strong> {metrics.get('optimization_success_rate', 0):.1%}</div>
            </div>
            
            <div class="insights">
                <h2>Analysis Insights</h2>
                {''.join(f'<div style="margin: 10px 0;">{insight}</div>' for insight in insights)}
            </div>
        </body>
        </html>
        """
        return html
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _expand_log_files(self, log_paths: list, config: dict) -> list:
        """Expand log files to include rotation files (.1, .2, .gz files)"""
        if not config.get('merge_rotation_files', True):
            return log_paths
        
        expanded_paths = []
        max_rotation_files = config.get('max_rotation_files', 10)
        
        for log_path in log_paths:
            path = Path(log_path)
            expanded_paths.append(str(path))
            
            # Look for rotation files
            for i in range(1, max_rotation_files + 1):
                rotation_path = Path(f"{path}.{i}")
                if rotation_path.exists():
                    expanded_paths.append(str(rotation_path))
                    self.logger.info(f"Found rotation file: {rotation_path}")
                
                # Check for compressed rotation files
                gz_path = Path(f"{path}.{i}.gz")
                if gz_path.exists():
                    expanded_paths.append(str(gz_path))
                    self.logger.info(f"Found compressed rotation file: {gz_path}")
        
        self.logger.info(f"Expanded {len(log_paths)} log files to {len(expanded_paths)} files")
        return expanded_paths
    
    def _analyze_tpyopt_failures(self) -> Dict[str, Any]:
        """Enterprise failure analysis for TPYOPT optimization failures"""
        failure_analysis = {
            'total_failures': 0,
            'failure_reasons': defaultdict(int),
            'failed_cycles': [],
            'topology_build_failures': [],
            'roaming_command_failures': [],
            'algorithm_decisions': [],
            'recommendations': []
        }
        
        # Analyze failures across all devices
        for device_mac, device_data in self.device_data.items():
            cycles = device_data.get('optimization_cycles', [])
            events = device_data.get('events', [])
            
            for cycle in cycles:
                if cycle.get('status') == 'failed':
                    failure_analysis['total_failures'] += 1
                    failure_reason = cycle.get('failure_reason', 'unknown')
                    failure_analysis['failure_reasons'][failure_reason] += 1
                    
                    failure_analysis['failed_cycles'].append({
                        'device_mac': device_mac,
                        'cycle_id': cycle.get('cycle_id'),
                        'start_time': cycle.get('start_time'),
                        'failure_reason': failure_reason,
                        'events_in_cycle': len(cycle.get('events', []))
                    })
            
            # Analyze topology build failures
            topology_failures = [e for e in events if e.get('pattern_name') == 'tpyopt_build_topology_fail']
            for failure in topology_failures:
                failure_analysis['topology_build_failures'].append({
                    'device_mac': device_mac,
                    'timestamp': failure.get('timestamp'),
                    'context': failure.get('raw_line', '')
                })
            
            # Analyze roaming command failures (implicit from packet loss events)
            packet_loss_events = [e for e in events if e.get('pattern_name') == 'tpyopt_packet_loss']
            for event in packet_loss_events:
                if event.get('rx_error_percent', 0) > 20:  # High packet loss threshold
                    failure_analysis['roaming_command_failures'].append({
                        'device_mac': device_mac,
                        'timestamp': event.get('timestamp'),
                        'packet_loss_percent': event.get('rx_error_percent'),
                        'severity': 'high' if event.get('rx_error_percent', 0) > 30 else 'medium'
                    })
        
        # Generate recommendations based on failure analysis
        if failure_analysis['total_failures'] > 0:
            failure_analysis['recommendations'].extend([
                f"Detected {failure_analysis['total_failures']} optimization failures",
                "Review topology build algorithm for stability improvements",
                "Consider adjusting optimization trigger thresholds"
            ])
        
        if len(failure_analysis['topology_build_failures']) > 0:
            failure_analysis['recommendations'].append(
                f"{len(failure_analysis['topology_build_failures'])} topology build failures detected - investigate network topology constraints"
            )
        
        if len(failure_analysis['roaming_command_failures']) > 0:
            failure_analysis['recommendations'].append(
                f"{len(failure_analysis['roaming_command_failures'])} high packet loss events detected - review RF environment and interference"
            )
        
        return failure_analysis
    
    def _analyze_optimization_quality(self) -> Dict[str, Any]:
        """Analyze optimization quality and effectiveness"""
        quality_analysis = {
            'optimization_effectiveness': defaultdict(list),
            'topology_quality_scores': defaultdict(list),
            'problematic_topologies': [],
            'recommended_optimizations': [],
            'performance_trends': defaultdict(list)
        }
        
        # Analyze optimization effectiveness per device
        for device_mac, device_data in self.device_data.items():
            cycles = device_data.get('optimization_cycles', [])
            events = device_data.get('events', [])
            
            for cycle in cycles:
                if cycle.get('status') == 'completed':
                    # Calculate effectiveness score
                    start_time = cycle.get('start_time')
                    end_time = cycle.get('end_time')
                    duration = self._calculate_time_difference(start_time, end_time)
                    
                    # Quality factors
                    has_roaming = len([e for e in cycle.get('events', []) if e.get('pattern_name') == 'tpyopt_roaming_command']) > 0
                    has_packet_loss = len([e for e in cycle.get('events', []) if e.get('pattern_name') == 'tpyopt_packet_loss']) > 0
                    topology_success = len([e for e in cycle.get('events', []) if e.get('pattern_name') == 'tpyopt_build_topology_success']) > 0
                    
                    # Calculate quality score (0.0 - 1.0)
                    quality_score = 0.0
                    if topology_success:
                        quality_score += 0.4
                    if has_roaming:
                        quality_score += 0.3
                    if not has_packet_loss:
                        quality_score += 0.2
                    if duration < 60:  # Quick optimization is better
                        quality_score += 0.1
                    
                    quality_analysis['optimization_effectiveness'][device_mac].append({
                        'cycle_id': cycle.get('cycle_id'),
                        'quality_score': quality_score,
                        'duration': duration,
                        'has_roaming': has_roaming,
                        'topology_success': topology_success
                    })
                    
                    quality_analysis['topology_quality_scores'][device_mac].append(quality_score)
                    
                    # Identify problematic topologies
                    if quality_score < 0.3:
                        quality_analysis['problematic_topologies'].append({
                            'device_mac': device_mac,
                            'cycle_id': cycle.get('cycle_id'),
                            'quality_score': quality_score,
                            'issues': self._identify_topology_issues(cycle)
                        })
        
        # Generate optimization recommendations
        avg_quality_scores = {}
        for device_mac, scores in quality_analysis['topology_quality_scores'].items():
            if scores:
                avg_quality_scores[device_mac] = statistics.mean(scores)
        
        if avg_quality_scores:
            overall_quality = statistics.mean(avg_quality_scores.values())
            quality_analysis['overall_quality_score'] = overall_quality
            
            if overall_quality < 0.5:
                quality_analysis['recommended_optimizations'].extend([
                    "Overall optimization quality is below threshold",
                    "Consider reviewing topology optimization algorithms",
                    "Investigate RF environment for interference sources"
                ])
            elif overall_quality > 0.8:
                quality_analysis['recommended_optimizations'].append(
                    "Optimization quality is excellent - current configuration is performing well"
                )
        
        return quality_analysis
    
    def _analyze_device_coordination(self) -> Dict[str, Any]:
        """Analyze multi-device coordination patterns"""
        coordination_analysis = {
            'device_clusters': [],
            'coordination_conflicts': [],
            'roaming_patterns': [],
            'topology_conflicts': [],
            'device_isolation_events': []
        }
        
        # Analyze device clusters and coordination
        device_macs = list(self.device_data.keys())
        
        # Find devices that have overlapping optimization cycles (potential conflicts)
        for i, device1 in enumerate(device_macs):
            for j, device2 in enumerate(device_macs[i+1:], i+1):
                device1_cycles = self.device_data[device1].get('optimization_cycles', [])
                device2_cycles = self.device_data[device2].get('optimization_cycles', [])
                
                # Check for overlapping cycles
                for cycle1 in device1_cycles:
                    for cycle2 in device2_cycles:
                        if self._cycles_overlap(cycle1, cycle2):
                            coordination_analysis['coordination_conflicts'].append({
                                'device1': device1,
                                'device2': device2,
                                'cycle1_id': cycle1.get('cycle_id'),
                                'cycle2_id': cycle2.get('cycle_id'),
                                'overlap_period': self._calculate_overlap_period(cycle1, cycle2)
                            })
        
        # Analyze roaming patterns across devices
        all_roaming_events = []
        for device_mac, device_data in self.device_data.items():
            roaming_events = [e for e in device_data.get('events', []) if e.get('pattern_name') == 'tpyopt_roaming_command']
            for event in roaming_events:
                all_roaming_events.append({
                    'device_mac': device_mac,
                    'timestamp': event.get('timestamp'),
                    'from_mac': event.get('from_mac'),
                    'to_mac': event.get('to_mac')
                })
        
        # Group roaming events by time windows to identify patterns
        roaming_patterns = self._group_roaming_by_time_windows(all_roaming_events)
        coordination_analysis['roaming_patterns'] = roaming_patterns
        
        # Identify device isolation events (devices with no coordination)
        isolated_devices = []
        for device_mac, device_data in self.device_data.items():
            cycles = device_data.get('optimization_cycles', [])
            if len(cycles) == 0:
                coordination_analysis['device_isolation_events'].append({
                    'device_mac': device_mac,
                    'reason': 'no_optimization_cycles',
                    'event_count': len(device_data.get('events', []))
                })
        
        return coordination_analysis
    
    def _write_enhanced_results_to_files(self, results: dict, output_dir: Path, config: dict) -> Dict[str, Path]:
        """Write enhanced results with comprehensive multi-format output"""
        file_outputs = {}
        analysis_data = results.get('analysis_data', {})
        
        # 1. Main JSON file with all analysis data
        json_file = output_dir / "tpyopt_analysis_complete.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        file_outputs['complete_analysis'] = json_file
        
        # 2. Timeline CSV file
        timeline_file = output_dir / "tpyopt_timeline.csv"
        timeline_data = analysis_data.get('timeline', [])
        with open(timeline_file, 'w', newline='', encoding='utf-8') as f:
            if timeline_data:
                writer = csv.DictWriter(f, fieldnames=timeline_data[0].keys())
                writer.writeheader()
                writer.writerows(timeline_data)
        file_outputs['timeline'] = timeline_file
        
        # 3. Optimization cycles CSV
        cycles_file = output_dir / "tpyopt_optimization_cycles.csv"
        all_cycles = []
        for device_mac, cycles in analysis_data.get('optimization_cycles', {}).items():
            for cycle in cycles:
                cycle_data = cycle.copy()
                cycle_data['device_mac'] = device_mac
                all_cycles.append(cycle_data)
        
        if all_cycles:
            with open(cycles_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_cycles[0].keys())
                writer.writeheader()
                writer.writerows(all_cycles)
        file_outputs['optimization_cycles'] = cycles_file
        
        # 4. Failure analysis JSON
        failure_file = output_dir / "tpyopt_failure_analysis.json"
        with open(failure_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data.get('failure_analysis', {}), f, indent=2, default=str)
        file_outputs['failure_analysis'] = failure_file
        
        # 5. Quality assessment JSON
        quality_file = output_dir / "tpyopt_quality_assessment.json"
        with open(quality_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data.get('optimization_quality', {}), f, indent=2, default=str)
        file_outputs['quality_assessment'] = quality_file
        
        # 6. Device coordination JSON
        coordination_file = output_dir / "tpyopt_device_coordination.json"
        with open(coordination_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data.get('device_coordination', {}), f, indent=2, default=str)
        file_outputs['device_coordination'] = coordination_file
        
        # 7. Enhanced HTML report
        html_file = output_dir / "tpyopt_enterprise_report.html"
        html_content = self._generate_html_report(results)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        file_outputs['enterprise_report'] = html_file
        
        # 8. Metrics summary JSON
        metrics_file = output_dir / "tpyopt_metrics_summary.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data.get('metrics', {}), f, indent=2, default=str)
        file_outputs['metrics_summary'] = metrics_file
        
        # 9. Raw data export (if enabled)
        if config.get('include_raw_data', False):
            raw_file = output_dir / "tpyopt_raw_data.json"
            raw_data = {
                'device_data': dict(self.device_data),
                'configuration': config,
                'metadata': results.get('metadata', {})
            }
            with open(raw_file, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, default=str)
            file_outputs['raw_data'] = raw_file
        
        return file_outputs
    
    
    # Helper methods for enterprise analysis
    def _calculate_time_difference(self, start_time: str, end_time: str) -> float:
        """Calculate time difference in seconds"""
        try:
            if not start_time or not end_time:
                return 0.0
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            return (end - start).total_seconds()
        except (ValueError, TypeError):
            return 0.0
    
    def _identify_topology_issues(self, cycle: Dict[str, Any]) -> List[str]:
        """Identify issues in a topology optimization cycle"""
        issues = []
        events = cycle.get('events', [])
        
        if not events:
            issues.append("No events recorded in cycle")
            return issues
        
        has_topology_success = any(e.get('pattern_name') == 'tpyopt_build_topology_success' for e in events)
        has_topology_failure = any(e.get('pattern_name') == 'tpyopt_build_topology_fail' for e in events)
        has_packet_loss = any(e.get('pattern_name') == 'tpyopt_packet_loss' for e in events)
        has_roaming = any(e.get('pattern_name') == 'tpyopt_roaming_command' for e in events)
        
        if has_topology_failure:
            issues.append("Topology build failed")
        if not has_topology_success:
            issues.append("No topology build success")
        if has_packet_loss:
            issues.append("Packet loss detected during optimization")
        if not has_roaming:
            issues.append("No roaming commands issued")
        
        return issues
    
    def _cycles_overlap(self, cycle1: Dict[str, Any], cycle2: Dict[str, Any]) -> bool:
        """Check if two optimization cycles overlap in time"""
        try:
            start1 = cycle1.get('start_time')
            end1 = cycle1.get('end_time')
            start2 = cycle2.get('start_time')
            end2 = cycle2.get('end_time')
            
            if not all([start1, end1, start2, end2]):
                return False
            
            start1_dt = datetime.fromisoformat(start1.replace('Z', '+00:00'))
            end1_dt = datetime.fromisoformat(end1.replace('Z', '+00:00'))
            start2_dt = datetime.fromisoformat(start2.replace('Z', '+00:00'))
            end2_dt = datetime.fromisoformat(end2.replace('Z', '+00:00'))
            
            return not (end1_dt < start2_dt or end2_dt < start1_dt)
        except (ValueError, TypeError):
            return False
    
    def _calculate_overlap_period(self, cycle1: Dict[str, Any], cycle2: Dict[str, Any]) -> str:
        """Calculate the overlap period between two cycles"""
        try:
            start1 = datetime.fromisoformat(cycle1.get('start_time', '').replace('Z', '+00:00'))
            end1 = datetime.fromisoformat(cycle1.get('end_time', '').replace('Z', '+00:00'))
            start2 = datetime.fromisoformat(cycle2.get('start_time', '').replace('Z', '+00:00'))
            end2 = datetime.fromisoformat(cycle2.get('end_time', '').replace('Z', '+00:00'))
            
            overlap_start = max(start1, start2)
            overlap_end = min(end1, end2)
            
            if overlap_end > overlap_start:
                duration = (overlap_end - overlap_start).total_seconds()
                return f"{duration:.1f} seconds"
            return "No overlap"
        except (ValueError, TypeError):
            return "Unknown"
    
    def _group_roaming_by_time_windows(self, roaming_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group roaming events by time windows to identify patterns"""
        if not roaming_events:
            return []
        
        # Sort events by timestamp
        sorted_events = sorted(roaming_events, key=lambda x: x.get('timestamp', ''))
        
        patterns = []
        current_window = []
        window_duration = 60  # 60 seconds window
        
        for event in sorted_events:
            if not current_window:
                current_window.append(event)
                continue
            
            # Check if event is within the current window
            last_time = current_window[-1].get('timestamp', '')
            current_time = event.get('timestamp', '')
            
            try:
                last_dt = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                current_dt = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                
                if (current_dt - last_dt).total_seconds() <= window_duration:
                    current_window.append(event)
                else:
                    # Close current window and start new one
                    if len(current_window) > 1:
                        patterns.append({
                            'window_start': current_window[0].get('timestamp'),
                            'window_end': current_window[-1].get('timestamp'),
                            'event_count': len(current_window),
                            'devices_involved': len(set(e.get('device_mac') for e in current_window)),
                            'events': current_window
                        })
                    current_window = [event]
            except (ValueError, TypeError):
                current_window = [event]
        
        # Handle last window
        if len(current_window) > 1:
            patterns.append({
                'window_start': current_window[0].get('timestamp'),
                'window_end': current_window[-1].get('timestamp'),
                'event_count': len(current_window),
                'devices_involved': len(set(e.get('device_mac') for e in current_window)),
                'events': current_window
            })
        
        return patterns
