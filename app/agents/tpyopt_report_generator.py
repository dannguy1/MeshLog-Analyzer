"""
WNC TPYOPT HTML Report Generator Module

This module generates comprehensive HTML reports for WNC Topology Optimization analysis,
including optimization cycles, device roaming analysis, and actionable insights.
"""

from typing import Dict, List, Any
from datetime import datetime

class TPYOPTReportGenerator:
    """Generates HTML reports for TPYOPT analysis with enhanced visualizations and interactive features"""
    
    @staticmethod
    def generate_html_report(results: dict) -> str:
        """Generate comprehensive HTML report with TPYOPT optimization analysis and detailed insights"""
        analysis_data = results['analysis_data']
        summary = analysis_data.get('summary', {})
        metrics = analysis_data.get('metrics', {})
        insights = analysis_data.get('insights', [])
        metadata = results.get('metadata', {})
        
        # Get TPYOPT-specific data
        optimization_cycles = analysis_data.get('optimization_cycles', {})
        roaming_commands = analysis_data.get('roaming_commands', {})
        device_analysis = analysis_data.get('device_analysis', {})
        failure_analysis = analysis_data.get('failure_analysis', {})
        recommendations = analysis_data.get('recommendations', [])
        fsm_transitions = analysis_data.get('fsm_transitions', {})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>WNC TPYOPT Analysis Report - Comprehensive Topology Optimization Analysis</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%); color: white; border-radius: 8px; }}
        .summary {{ background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff; }}
        .metrics {{ background: #f0f8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .insights {{ background: #fff8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .tpyopt-section {{ background: #f0f2ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #6366f1; }}
        .failure-section {{ background: #ffeaea; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f44336; }}
        .insight {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #007acc; }}
        .metric {{ margin: 5px 0; }}
        .success {{ color: #28a745; font-weight: bold; }}
        .warning {{ color: #ffc107; font-weight: bold; }}
        .error {{ color: #dc3545; font-weight: bold; }}
        .info {{ color: #17a2b8; font-weight: bold; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        
        /* Accordion styles */
        .accordion {{ margin: 10px 0; }}
        .accordion-header {{ 
            background: #f8f9fa; 
            border: 1px solid #dee2e6; 
            padding: 12px 15px; 
            cursor: pointer; 
            border-radius: 5px 5px 0 0;
            font-weight: bold;
            transition: background-color 0.3s;
        }}
        .accordion-header:hover {{ background: #e9ecef; }}
        .accordion-header.active {{ background: #e3f2fd; border-color: #2196f3; }}
        .accordion-content {{ 
            border: 1px solid #dee2e6; 
            border-top: none; 
            padding: 15px; 
            display: none; 
            border-radius: 0 0 5px 5px;
            background: #fff;
        }}
        .accordion-content.active {{ display: block; }}
        
        /* TPYOPT-specific styles */
        .optimization-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .optimization-card {{ 
            text-align: center; 
            padding: 15px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .optimization-card.overview {{ background: #e3f2fd; }}
        .optimization-card.successful {{ background: #e8f5e8; }}
        .optimization-card.failed {{ background: #ffebee; }}
        .optimization-card.roaming {{ background: #f3e5f5; }}
        
        .device-analysis {{ max-height: 400px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; }}
        .device-item {{ 
            padding: 12px; 
            border-bottom: 1px solid #eee; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }}
        .device-item:last-child {{ border-bottom: none; }}
        .device-mac {{ font-family: monospace; font-weight: bold; }}
        .device-stats {{ font-size: 0.9em; color: #666; }}
        
        .roaming-command {{ 
            display: inline-block; 
            margin: 5px; 
            padding: 8px 12px; 
            background: #e3f2fd; 
            border-radius: 15px; 
            font-size: 0.9em;
        }}
        
        .recommendation {{ 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px; 
            border-left: 4px solid #28a745;
        }}
        .recommendation.high {{ background: #ffebee; border-left-color: #f44336; }}
        .recommendation.medium {{ background: #fff3e0; border-left-color: #ff9800; }}
        .recommendation.low {{ background: #e8f5e8; border-left-color: #4caf50; }}
        
        .failure-incident {{ 
            background: #fff5f5; 
            border: 1px solid #fed7d7; 
            padding: 12px; 
            margin: 8px 0; 
            border-radius: 5px; 
        }}
        .failure-incident.critical {{ border-left: 4px solid #f56565; }}
        .failure-incident.warning {{ border-left: 4px solid #ed8936; }}
    </style>
    <script>
        function toggleAccordion(element) {{
            element.classList.toggle('active');
            var content = element.nextElementSibling;
            content.classList.toggle('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WNC Topology Optimization Analysis Report</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Agent Version: {metadata.get('version', 'Unknown')} | Analysis Type: {metadata.get('agent_type', 'wnc-tpyopt')}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Analysis Summary</h2>
            <div class="metric"><strong>Total Events Processed:</strong> {summary.get('total_events', 0):,}</div>
            <div class="metric"><strong>Devices Analyzed:</strong> {summary.get('devices_analyzed', 0)}</div>
            <div class="metric"><strong>Optimization Cycles:</strong> {summary.get('optimization_cycles', 0)}</div>
            <div class="metric"><strong>Roaming Commands:</strong> {summary.get('roaming_commands', 0)}</div>
            <div class="metric"><strong>FSM Transitions:</strong> {summary.get('fsm_transitions', 0)}</div>
            <div class="metric"><strong>Analysis Period:</strong> {summary.get('time_range', 'Unknown')}</div>
            <div class="metric"><strong>Processing Time:</strong> {summary.get('processing_time', 0):.2f} seconds</div>
            <div class="metric"><strong>Status:</strong> <span class="success">{summary.get('status', 'completed')}</span></div>
        </div>
        
        <div class="metrics">
            <h2>📈 Performance Metrics</h2>
            <div class="optimization-stats">
                <div class="optimization-card overview">
                    <h3>Optimization Success Rate</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #1976d2;">
                        {metrics.get('optimization_success_rate', 0):.1%}
                    </div>
                </div>
                <div class="optimization-card successful">
                    <h3>Successful Optimizations</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #388e3c;">
                        {metrics.get('successful_optimizations', 0)}
                    </div>
                </div>
                <div class="optimization-card failed">
                    <h3>Failed Optimizations</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #d32f2f;">
                        {metrics.get('failed_optimizations', 0)}
                    </div>
                </div>
                <div class="optimization-card roaming">
                    <h3>Roaming Commands</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #7b1fa2;">
                        {metrics.get('total_roaming_commands', 0)}
                    </div>
                </div>
            </div>
            
            <div class="metric"><strong>Events per Second:</strong> {metrics.get('events_per_second', 0):.1f}</div>
            <div class="metric"><strong>Average Processing Time:</strong> {metrics.get('avg_processing_time', 0):.3f}s</div>
            <div class="metric"><strong>Average Optimization Duration:</strong> {metrics.get('avg_optimization_duration', 0):.1f}s</div>
            <div class="metric"><strong>Device Roaming Success Rate:</strong> {metrics.get('roaming_success_rate', 0):.1%}</div>
        </div>"""
        
        # Add Optimization Cycles Analysis Section
        if optimization_cycles:
            html += TPYOPTReportGenerator._generate_optimization_cycles_section(optimization_cycles)
        
        # Add Device Analysis Section
        if device_analysis:
            html += TPYOPTReportGenerator._generate_device_analysis_section(device_analysis)
        
        # Add Roaming Commands Section
        if roaming_commands:
            html += TPYOPTReportGenerator._generate_roaming_commands_section(roaming_commands)
        
        # Add Failure Analysis Section
        if failure_analysis:
            html += TPYOPTReportGenerator._generate_failure_analysis_section(failure_analysis)
        
        # Add FSM Transitions Section
        if fsm_transitions:
            html += TPYOPTReportGenerator._generate_fsm_section(fsm_transitions)
        
        # Add Insights Section
        if insights:
            html += f"""
        <div class="insights">
            <h2>🔍 Analysis Insights</h2>
            {''.join(f'<div class="insight">{insight}</div>' for insight in insights)}
        </div>"""
        
        # Add Recommendations Section
        if recommendations:
            html += TPYOPTReportGenerator._generate_recommendations_section(recommendations)
        
        html += """
    </div>
</body>
</html>"""
        return html
    
    @staticmethod
    def _generate_optimization_cycles_section(optimization_cycles: dict) -> str:
        """Generate optimization cycles analysis section with accordion interface"""
        cycles_summary = optimization_cycles.get('summary', {})
        cycles_by_type = optimization_cycles.get('by_type', {})
        
        html = f"""
        <div class="tpyopt-section">
            <h2>🔄 Optimization Cycles Analysis</h2>
            <div class="metric"><strong>Total Cycles:</strong> {cycles_summary.get('total_cycles', 0)}</div>
            <div class="metric"><strong>Successful Cycles:</strong> {cycles_summary.get('successful_cycles', 0)}</div>
            <div class="metric"><strong>Average Duration:</strong> {cycles_summary.get('average_duration', 0):.2f} seconds</div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    🔧 Optimization Cycle Details
                </div>
                <div class="accordion-content">"""
        
        for cycle_type, type_data in cycles_by_type.items():
            count = type_data.get('count', 0)
            success_rate = type_data.get('success_rate', 0)
            
            html += f"""
                    <div class="metric">
                        <strong>{cycle_type.replace('_', ' ').title()}:</strong> 
                        {count} cycles | Success Rate: {success_rate:.1%}
                    </div>"""
        
        html += """
                </div>
            </div>
        </div>"""
        
        return html
    
    @staticmethod
    def _generate_device_analysis_section(device_analysis: dict) -> str:
        """Generate device analysis section"""
        html = f"""
        <div class="tpyopt-section">
            <h2>📱 Device Performance Analysis</h2>
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    Device Performance Details ({len(device_analysis)} Devices)
                </div>
                <div class="accordion-content">
                    <div class="device-analysis">"""
        
        for device_mac, device_data in device_analysis.items():
            roaming_count = device_data.get('roaming_commands', 0)
            success_rate = device_data.get('success_rate', 0)
            avg_rssi = device_data.get('average_rssi', 0)
            
            html += f"""
                        <div class="device-item">
                            <div>
                                <div class="device-mac">{device_mac}</div>
                                <div class="device-stats">
                                    Roaming: {roaming_count} | Success: {success_rate:.1%} | 
                                    Avg RSSI: {avg_rssi:.1f} dBm
                                </div>
                            </div>
                        </div>"""
        
        html += """
                    </div>
                </div>
            </div>
        </div>"""
        
        return html
    
    @staticmethod
    def _generate_roaming_commands_section(roaming_commands: dict) -> str:
        """Generate roaming commands section"""
        command_summary = roaming_commands.get('summary', {})
        command_types = roaming_commands.get('by_type', {})
        
        html = f"""
        <div class="tpyopt-section">
            <h2>🔀 Roaming Commands Analysis</h2>
            <div class="metric"><strong>Total Commands:</strong> {command_summary.get('total_commands', 0)}</div>
            <div class="metric"><strong>Success Rate:</strong> {command_summary.get('success_rate', 0):.1%}</div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    Roaming Command Types
                </div>
                <div class="accordion-content">"""
        
        for cmd_type, cmd_data in command_types.items():
            count = cmd_data.get('count', 0)
            success_rate = cmd_data.get('success_rate', 0)
            
            html += f'<span class="roaming-command">{cmd_type}: {count} ({success_rate:.1%} success)</span>'
        
        html += """
                </div>
            </div>
        </div>"""
        
        return html
    
    @staticmethod
    def _generate_failure_analysis_section(failure_analysis: dict) -> str:
        """Generate failure analysis section"""
        failure_summary = failure_analysis.get('summary', {})
        failure_incidents = failure_analysis.get('incidents', [])
        failure_patterns = failure_analysis.get('patterns', {})
        
        html = f"""
        <div class="failure-section">
            <h2>⚠️ Failure Analysis</h2>
            <div class="metric"><strong>Total Failures:</strong> {failure_summary.get('total_failures', 0)}</div>
            <div class="metric"><strong>Failure Rate:</strong> {failure_summary.get('failure_rate', 0):.1%}</div>
            <div class="metric"><strong>Critical Incidents:</strong> {failure_summary.get('critical_incidents', 0)}</div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    🚨 Recent Failure Incidents ({len(failure_incidents)} incidents)
                </div>
                <div class="accordion-content">"""
        
        for incident in failure_incidents[:10]:  # Show top 10 recent incidents
            severity = incident.get('severity', 'warning').lower()
            html += f"""
                    <div class="failure-incident {severity}">
                        <strong>{incident.get('timestamp', 'Unknown Time')}:</strong> 
                        {incident.get('description', 'No description available')}
                        <br><small>Device: {incident.get('device_mac', 'Unknown')} | 
                        Type: {incident.get('failure_type', 'Unknown')}</small>
                    </div>"""
        
        html += """
                </div>
            </div>
        </div>"""
        
        return html
    
    @staticmethod
    def _generate_fsm_section(fsm_transitions: dict) -> str:
        """Generate FSM transitions section"""
        transition_counts = fsm_transitions.get('transition_counts', {})
        state_summary = fsm_transitions.get('state_summary', {})
        
        html = f"""
        <div class="tpyopt-section">
            <h2>🔄 FSM State Transitions</h2>
            <div class="metric"><strong>Total Transitions:</strong> {sum(transition_counts.values())}</div>
            <div class="metric"><strong>Unique States:</strong> {len(state_summary)}</div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    State Transition Details
                </div>
                <div class="accordion-content">
                    <h4>Most Common Transitions:</h4>"""
        
        sorted_transitions = sorted(transition_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for transition, count in sorted_transitions:
            html += f'<div class="metric">• {transition}: {count} times</div>'
        
        html += """
                </div>
            </div>
        </div>"""
        
        return html
    
    @staticmethod
    def _generate_recommendations_section(recommendations: list) -> str:
        """Generate recommendations section"""
        html = """
        <div class="tpyopt-section">
            <h2>💡 Recommendations</h2>"""
        
        for rec in recommendations:
            priority = rec.get('priority', 'low').lower()
            html += f"""
            <div class="recommendation {priority}">
                <strong>[{rec.get('priority', 'LOW').upper()}]</strong> {rec.get('recommendation', '')}
                {f"<br><small><strong>Rationale:</strong> {rec.get('rationale', '')}</small>" if rec.get('rationale') else ''}
            </div>"""
        
        html += "</div>"
        return html
