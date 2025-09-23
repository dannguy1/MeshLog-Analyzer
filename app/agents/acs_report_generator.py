"""
WNC ACS HTML Report Generator Module

This module generates comprehensive HTML reports for WNC Auto Channel Selection analysis,
including cycle analysis, FSM transitions, and actionable insights with interactive features.
"""

from typing import Dict, List, Any
from datetime import datetime

class ACSReportGenerator:
    """Generates HTML reports for ACS analysis with enhanced visualizations and interactive features"""
    
    @staticmethod
    def generate_html_report(results: dict) -> str:
        """Generate comprehensive HTML report with ACS cycle analysis and detailed insights"""
        analysis_data = results['analysis_data']
        summary = analysis_data.get('summary', {})
        metrics = analysis_data.get('metrics', {})
        insights = analysis_data.get('insights', [])
        metadata = results.get('metadata', {})
        
        # Get ACS-specific data
        acs_cycles = analysis_data.get('acs_cycles', {})
        fsm_transitions = analysis_data.get('fsm_transitions', {})
        recommendations = analysis_data.get('recommendations', [])
        radio_analysis = analysis_data.get('radio_analysis', {})
        channel_preferences = analysis_data.get('channel_preferences', {})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>WNC ACS Analysis Report - Comprehensive Channel Selection Analysis</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; }}
        .summary {{ background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff; }}
        .metrics {{ background: #f0f8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .insights {{ background: #fff8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .acs-section {{ background: #f3e5f5; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #9c27b0; }}
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
        
        /* ACS-specific styles */
        .cycle-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .cycle-card {{ 
            text-align: center; 
            padding: 15px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .cycle-card.overview {{ background: #e3f2fd; }}
        .cycle-card.successful {{ background: #e8f5e8; }}
        .cycle-card.failed {{ background: #ffebee; }}
        .cycle-card.ongoing {{ background: #fff3e0; }}
        
        .radio-analysis {{ max-height: 400px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; }}
        .radio-item {{ 
            padding: 12px; 
            border-bottom: 1px solid #eee; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }}
        .radio-item:last-child {{ border-bottom: none; }}
        .radio-id {{ font-family: monospace; font-weight: bold; }}
        .radio-stats {{ font-size: 0.9em; color: #666; }}
        
        .channel-preference {{ 
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
            <h1>WNC Auto Channel Selection Analysis Report</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Agent Version: {metadata.get('version', 'Unknown')} | Analysis Type: {metadata.get('agent_type', 'wnc-acs')}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Analysis Summary</h2>
            <div class="metric"><strong>Total Events Processed:</strong> {summary.get('total_events', 0):,}</div>
            <div class="metric"><strong>Radios Analyzed:</strong> {summary.get('radios_analyzed', 0)}</div>
            <div class="metric"><strong>ACS Cycles Detected:</strong> {summary.get('total_cycles', 0)}</div>
            <div class="metric"><strong>FSM Transitions:</strong> {summary.get('total_transitions', 0)}</div>
            <div class="metric"><strong>Analysis Period:</strong> {summary.get('time_range', 'Unknown')}</div>
            <div class="metric"><strong>Processing Time:</strong> {summary.get('processing_time', 0):.2f} seconds</div>
            <div class="metric"><strong>Status:</strong> <span class="success">{summary.get('status', 'completed')}</span></div>
        </div>
        
        <div class="metrics">
            <h2>📈 Performance Metrics</h2>
            <div class="cycle-stats">
                <div class="cycle-card overview">
                    <h3>Overall Success Rate</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #1976d2;">
                        {metrics.get('cycle_success_rate', 0):.1%}
                    </div>
                </div>
                <div class="cycle-card successful">
                    <h3>Successful Cycles</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #388e3c;">
                        {metrics.get('successful_cycles', 0)}
                    </div>
                </div>
                <div class="cycle-card failed">
                    <h3>Failed Cycles</h3>
                    <div style="font-size: 2em; font-weight: bold; color: #d32f2f;">
                        {metrics.get('failed_cycles', 0)}
                    </div>
                </div>
                <div class="cycle-card ongoing">
                    <h3>Average Duration</h3>
                    <div style="font-size: 1.5em; font-weight: bold; color: #f57c00;">
                        {metrics.get('average_cycle_duration', 0):.1f}s
                    </div>
                </div>
            </div>
            
            <div class="metric"><strong>Events per Second:</strong> {metrics.get('events_per_second', 0):.1f}</div>
            <div class="metric"><strong>Average Processing Time:</strong> {metrics.get('avg_processing_time', 0):.3f}s</div>
            <div class="metric"><strong>Peak Channel Switches:</strong> {metrics.get('peak_channel_switches', 0)}</div>
        </div>"""
        
        # Add ACS Cycles Analysis Section
        if acs_cycles:
            html += ACSReportGenerator._generate_cycles_section(acs_cycles)
        
        # Add Radio Analysis Section
        if radio_analysis:
            html += ACSReportGenerator._generate_radio_analysis_section(radio_analysis)
        
        # Add Channel Preferences Section
        if channel_preferences:
            html += ACSReportGenerator._generate_channel_preferences_section(channel_preferences)
        
        # Add FSM Transitions Section
        if fsm_transitions:
            html += ACSReportGenerator._generate_fsm_section(fsm_transitions)
        
        # Add Insights Section
        if insights:
            html += f"""
        <div class="insights">
            <h2>🔍 Analysis Insights</h2>
            {''.join(f'<div class="insight">{insight}</div>' for insight in insights)}
        </div>"""
        
        # Add Recommendations Section
        if recommendations:
            html += ACSReportGenerator._generate_recommendations_section(recommendations)
        
        html += """
    </div>
</body>
</html>"""
        return html
    
    @staticmethod
    def _generate_cycles_section(acs_cycles: dict) -> str:
        """Generate ACS cycles analysis section with accordion interface"""
        cycles_by_radio = acs_cycles.get('by_radio', {})
        cycle_summary = acs_cycles.get('summary', {})
        
        html = f"""
        <div class="acs-section">
            <h2>🔄 ACS Cycles Analysis</h2>
            <div class="metric"><strong>Total Cycles:</strong> {cycle_summary.get('total_cycles', 0)}</div>
            <div class="metric"><strong>Successful Cycles:</strong> {cycle_summary.get('successful_cycles', 0)}</div>
            <div class="metric"><strong>Average Duration:</strong> {cycle_summary.get('average_duration', 0):.2f} seconds</div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    📡 Detailed Radio Cycles ({len(cycles_by_radio)} Radios)
                </div>
                <div class="accordion-content">
                    <div class="radio-analysis">"""
        
        for radio_id, radio_cycles in cycles_by_radio.items():
            total_cycles = len(radio_cycles.get('cycles', []))
            successful = sum(1 for cycle in radio_cycles.get('cycles', []) if cycle.get('status') == 'completed')
            
            html += f"""
                        <div class="radio-item">
                            <div>
                                <div class="radio-id">Radio {radio_id}</div>
                                <div class="radio-stats">
                                    Cycles: {total_cycles} | Success: {successful} | 
                                    Success Rate: {(successful/total_cycles*100) if total_cycles > 0 else 0:.1f}%
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
    def _generate_radio_analysis_section(radio_analysis: dict) -> str:
        """Generate radio analysis section"""
        html = f"""
        <div class="acs-section">
            <h2>📡 Radio Performance Analysis</h2>
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    Radio Performance Details ({len(radio_analysis)} Radios)
                </div>
                <div class="accordion-content">
                    <div class="radio-analysis">"""
        
        for radio_id, radio_data in radio_analysis.items():
            performance = radio_data.get('performance', {})
            html += f"""
                        <div class="radio-item">
                            <div>
                                <div class="radio-id">Radio {radio_id}</div>
                                <div class="radio-stats">
                                    Events: {performance.get('total_events', 0)} | 
                                    Cycles: {performance.get('cycle_count', 0)} | 
                                    Avg Duration: {performance.get('avg_cycle_duration', 0):.1f}s
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
    def _generate_channel_preferences_section(channel_preferences: dict) -> str:
        """Generate channel preferences section"""
        html = f"""
        <div class="acs-section">
            <h2>📶 Channel Preferences Analysis</h2>
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion(this)">
                    Channel Usage Patterns
                </div>
                <div class="accordion-content">"""
        
        for band, channels in channel_preferences.items():
            html += f"""
                    <h4>{band.upper()} Band Preferences:</h4>
                    <div style="margin: 10px 0;">"""
            
            for channel, count in sorted(channels.items(), key=lambda x: x[1], reverse=True)[:10]:
                html += f'<span class="channel-preference">Ch {channel}: {count} uses</span>'
            
            html += "</div>"
        
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
        <div class="acs-section">
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
        <div class="acs-section">
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
