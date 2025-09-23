"""
Enhanced WNC ACS Agent for MeshLog Integrated Agent System

This agent provides comprehensive analysis of WNC Auto Channel Selection (ACS) behavior,
tracking FSM state transitions, channel selection cycles, and radio optimization decisions.
Features modular architecture with separate components for parsing, analysis, and reporting.
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
        
        self.description = "Enhanced WNC ACS analysis with modular architecture, FSM transition tracking, cycle detection, and channel optimization insights"
        
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
