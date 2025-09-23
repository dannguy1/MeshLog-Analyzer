"""
WNC Steering HTML Report Generator Module

This module generates comprehensive HTML reports for WNC steering analysis,
including failure analysis, client performance, and actionable insights.
"""

from typing import Dict, List, Any

class SteeringReportGenerator:
    """Generates HTML reports for steering analysis with enhanced failure reporting"""
    
    @staticmethod
    def generate_html_report(results: dict) -> str:
        """Generate comprehensive HTML report with failure analysis and detailed client capabilities"""
        analysis_data = results['analysis_data']
        summary = analysis_data['summary']
        metrics = analysis_data['metrics']
        insights = analysis_data['insights']
        metadata = results['metadata']
        
        # Get failure analysis data if available
        failure_analysis = analysis_data.get('failure_analysis', {})
        failure_incidents = analysis_data.get('failure_incidents', [])
        
        # Get client capabilities data if available
        client_capabilities = analysis_data.get('client_capabilities', {})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>WNC Steering Analysis Report - Enhanced with Failure Analysis</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .summary {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .failure-section {{ background: #ffeaea; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f44336; }}
        .metrics {{ background: #f0f8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .insights {{ background: #fff8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .capabilities-section {{ background: #f3e5f5; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #9c27b0; }}
        .insight {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #007acc; }}
        .metric {{ margin: 5px 0; }}
        .success {{ color: #28a745; font-weight: bold; }}
        .warning {{ color: #ffc107; font-weight: bold; }}
        .error {{ color: #dc3545; font-weight: bold; }}
        .info {{ color: #17a2b8; font-weight: bold; }}
        .failure-incident {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .chart {{ margin: 15px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; }}
        
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
        
        /* Client capability cards */
        .capability-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .capability-card {{ 
            text-align: center; 
            padding: 15px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .capability-card.overview {{ background: #e3f2fd; }}
        .capability-card.k-support {{ background: #e8f5e8; }}
        .capability-card.v-support {{ background: #fff3e0; }}
        .capability-card.fully-capable {{ background: #f3e5f5; }}
        
        .client-list {{ max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; }}
        .client-item {{ 
            padding: 8px 12px; 
            border-bottom: 1px solid #eee; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }}
        .client-item:last-child {{ border-bottom: none; }}
        .client-mac {{ font-family: monospace; font-weight: bold; }}
        .client-capabilities {{ font-size: 0.9em; color: #666; }}
    </style>
    <script>
        function toggleAccordion(element) {{
            element.classList.toggle('active');
            const content = element.nextElementSibling;
            content.classList.toggle('active');
        }}
    </script>
</head>
<body>
    <div class="header">
        <h1>🔄 WNC Steering Analysis Report - Enhanced with Failure Analysis</h1>
        <p><strong>Agent Version:</strong> {metadata['version']}</p>
        <p><strong>Analysis ID:</strong> {results['analysis_id']}</p>
        <p><strong>Processing Time:</strong> {metadata['processing_time']:.2f} seconds</p>
        <p><strong>Files Processed:</strong> {metadata['input_files']}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Executive Summary</h2>
        <div class="metric"><strong>Total Events:</strong> {summary['total_events']}</div>
        <div class="metric"><strong>Unique Clients:</strong> {summary['total_clients']}</div>
        <div class="metric"><strong>Steering Attempts:</strong> {summary['total_steering_attempts']}</div>
        <div class="metric"><strong>Steering Successes:</strong> <span class="success">{summary['total_steering_successes']}</span></div>"""
        
        # Add failure data if available
        if 'total_steering_failures' in summary:
            html += f"""
        <div class="metric"><strong>Steering Failures:</strong> <span class="error">{summary['total_steering_failures']}</span></div>"""
        
        html += f"""
        <div class="metric"><strong>Success Rate:</strong> <span class="{'success' if summary['success_rate_percent'] > 70 else 'warning' if summary['success_rate_percent'] > 40 else 'error'}">{summary['success_rate_percent']}%</span></div>"""
        
        if 'failure_incidents_count' in summary:
            html += f"""
        <div class="metric"><strong>Failure Incidents:</strong> <span class="error">{summary['failure_incidents_count']}</span></div>"""
        
        html += f"""
        <div class="metric"><strong>Time Range:</strong> {summary['time_range']}</div>
    </div>"""
        
        # Add failure analysis section if there are failures
        if failure_analysis.get('total_failures', 0) > 0:
            html += SteeringReportGenerator._generate_failure_section(failure_analysis, failure_incidents)
        
        # Add comprehensive client capabilities section
        if client_capabilities:
            html += SteeringReportGenerator._generate_capabilities_section(client_capabilities)
        
        html += f"""
    
    <div class="insights">
        <h2>💡 Actionable Insights & Recommendations</h2>"""
        
        for insight in insights:
            html += f'<div class="insight">{insight}</div>'
        
        html += f"""
    </div>
    
    <div style="margin-top: 30px; padding: 10px; background: #f8f9fa; border-radius: 5px; text-align: center;">
        <small>Report generated by WNC Steering Agent v{metadata['version']} | Analysis ID: {results['analysis_id']}</small>
    </div>
</body>
</html>"""
        
        return html        # Add failure data if available
        if 'total_steering_failures' in summary:
            html += f"""
        <div class="metric"><strong>Steering Failures:</strong> <span class="error">{summary['total_steering_failures']}</span></div>"""
        
        html += f"""
        <div class="metric"><strong>Success Rate:</strong> <span class="{'success' if summary['success_rate_percent'] > 70 else 'warning' if summary['success_rate_percent'] > 40 else 'error'}">{summary['success_rate_percent']}%</span></div>"""
        
        if 'failure_incidents_count' in summary:
            html += f"""
        <div class="metric"><strong>Failure Incidents:</strong> <span class="error">{summary['failure_incidents_count']}</span></div>"""
        
        html += f"""
        <div class="metric"><strong>Time Range:</strong> {summary['time_range']}</div>
    </div>"""
        
        # Add failure analysis section if there are failures
        if failure_analysis.get('total_failures', 0) > 0:
            html += SteeringReportGenerator._generate_failure_section(failure_analysis, failure_incidents)
        
        # Client capabilities section
        html += f"""
    
    <div class="metrics">
        <h2>📱 Client Capabilities</h2>
        <div class="metric"><strong>802.11k Support:</strong> {metrics['client_capability_distribution']['802.11k_support_percentage']}% ({summary['clients_supporting_11k']} clients)</div>
        <div class="metric"><strong>802.11v Support:</strong> {metrics['client_capability_distribution']['802.11v_support_percentage']}% ({summary['clients_supporting_11v']} clients)</div>
        <div class="metric"><strong>Average Attempts per Client:</strong> {metrics['steering_effectiveness']['avg_attempts_per_client']}</div>
    </div>
    
    <div class="insights">
        <h2>💡 Actionable Insights & Recommendations</h2>"""
        
        for insight in insights:
            html += f'<div class="insight">{insight}</div>'
        
        html += f"""
    </div>
    
    <div class="metrics">
        <h2>🔧 Processing Statistics</h2>
        <div class="metric"><strong>Lines Processed:</strong> {metadata['total_lines_processed']:,}</div>
        <div class="metric"><strong>Lines Matched:</strong> {metadata['matched_lines']:,}</div>
        <div class="metric"><strong>Events Extracted:</strong> {metadata['events_extracted']}</div>
        <div class="metric"><strong>Processing Efficiency:</strong> {round((metadata['matched_lines'] / metadata['total_lines_processed'] * 100) if metadata['total_lines_processed'] > 0 else 0, 2)}%</div>
    </div>
    
    <div class="summary">
        <h2>📋 Analysis Notes</h2>
        <p>This enhanced analysis provides comprehensive monitoring of WNC steering operations:</p>
        <ul>
            <li><strong>Steering Effectiveness:</strong> Success/failure rates and patterns</li>
            <li><strong>Client Behavior:</strong> Individual client steering performance</li>
            <li><strong>Capability Assessment:</strong> 802.11k/v support analysis</li>"""
        
        if failure_analysis.get('total_failures', 0) > 0:
            html += """
            <li><strong>Failure Analysis:</strong> Detailed incident tracking with specific failure types</li>
            <li><strong>Performance Optimization:</strong> Actionable insights based on failure patterns</li>"""
        
        html += """
        </ul>
    </div>
</body>
</html>"""
        
        return html
    
    @staticmethod
    def _generate_failure_section(failure_analysis: dict, failure_incidents: list) -> str:
        """Generate the failure analysis section of the HTML report"""
        html = f"""
    
    <div class="failure-section">
        <h2>❌ Detailed Failure Analysis</h2>
        <div class="metric"><strong>Total Failure Incidents:</strong> {failure_analysis['total_failures']}</div>
        
        <h3>Failure Types Breakdown:</h3>
        <div class="chart">
            <ul>"""
        
        for failure_type, count in failure_analysis.get('failure_types', {}).items():
            percentage = round((count / failure_analysis['total_failures'] * 100), 1)
            html += f"""
                <li><strong>{failure_type.replace('_', ' ').title()}:</strong> {count} incidents ({percentage}%)</li>"""
        
        html += """
            </ul>
        </div>
        
        <h3>Top Failing Clients:</h3>
        <div class="chart">
            <ul>"""
        
        for client_mac, count in failure_analysis.get('top_failing_clients', []):
            html += f"""
                <li><strong>{client_mac}:</strong> {count} failures</li>"""
        
        html += """
            </ul>
        </div>"""
        
        # Performance metrics breakdown
        if 'performance_metrics' in failure_analysis:
            metrics = failure_analysis['performance_metrics']
            html += f"""
        
        <h3>Performance Metrics:</h3>
        <div class="chart">
            <div class="metric"><strong>BTM Failures:</strong> {metrics.get('btm_failures', 0)}</div>
            <div class="metric"><strong>Timeout Failures:</strong> {metrics.get('timeout_failures', 0)}</div>
            <div class="metric"><strong>Client Rejections:</strong> {metrics.get('rejection_failures', 0)}</div>
            <div class="metric"><strong>Target Selection Failures:</strong> {metrics.get('target_selection_failures', 0)}</div>
            <div class="metric"><strong>RSSI-related Failures:</strong> {metrics.get('rssi_failures', 0)}</div>
        </div>"""
        
        # Recent failure incidents
        if failure_incidents:
            recent_failures = failure_incidents[-10:] if len(failure_incidents) > 10 else failure_incidents
            html += """
        
        <h3>Recent Failure Incidents (Last 10):</h3>"""
            
            for incident in recent_failures:
                html += f"""
        <div class="failure-incident">
            <strong>Time:</strong> {incident['timestamp']}<br>
            <strong>Client:</strong> {incident['client_mac']}<br>
            <strong>Type:</strong> {incident['failure_type']}<br>
            <strong>Reason:</strong> {incident['failure_reason'] or 'Not specified'}<br>
            <strong>Raw Log:</strong> <code>{incident['raw_line'][:100]}...</code>
        </div>"""
        
        html += """
    </div>"""
        
        return html
    
    @staticmethod
    def _generate_capabilities_section(client_capabilities: dict) -> str:
        """Generate detailed client capabilities section with accordion interface"""
        overview = client_capabilities.get('overview', {})
        client_breakdown = client_capabilities.get('client_breakdown', {})
        
        html = f"""
    <div class="capabilities-section">
        <h2>📡 802.11k/v Capability Analysis - Detailed Breakdown</h2>
        
        <!-- Capability Overview Cards -->
        <div class="capability-stats">
            <div class="capability-card overview">
                <h3>{overview.get('total_clients_analyzed', 0)}</h3>
                <p>Total Clients Analyzed</p>
            </div>
            <div class="capability-card k-support">
                <h3 class="success">{overview.get('k_support_percentage', 0):.1f}%</h3>
                <p>802.11k Support</p>
            </div>
            <div class="capability-card v-support">
                <h3 class="warning">{overview.get('v_support_percentage', 0):.1f}%</h3>
                <p>802.11v Support</p>
            </div>
            <div class="capability-card fully-capable">
                <h3 class="info">{overview.get('fully_capable_percentage', 0):.1f}%</h3>
                <p>Fully Capable</p>
            </div>
        </div>"""
        
        # Fully Capable Clients
        fully_capable = client_breakdown.get('fully_capable_clients', {})
        if fully_capable.get('count', 0) > 0:
            html += f"""
        <div class="accordion">
            <div class="accordion-header" onclick="toggleAccordion(this)">
                ✅ Fully Capable Clients ({fully_capable['count']}) - Supports both 802.11k and 802.11v
            </div>
            <div class="accordion-content">
                <p><strong>These clients support both 802.11k neighbor reports and 802.11v BSS transition management, enabling the most effective steering strategies.</strong></p>
                <div class="client-list">"""
            
            for client in fully_capable.get('clients', [])[:50]:  # Limit to first 50 for performance
                mac = client.get('mac_address', 'Unknown')
                k_support = "✓" if client.get('supports_802_11k', False) else "✗"
                v_support = "✓" if client.get('supports_802_11v', False) else "✗"
                html += f"""
                    <div class="client-item">
                        <span class="client-mac">{mac}</span>
                        <span class="client-capabilities">802.11k: {k_support} | 802.11v: {v_support}</span>
                    </div>"""
            
            if len(fully_capable.get('clients', [])) > 50:
                html += f"""
                    <div class="client-item" style="text-align: center; font-style: italic; color: #666;">
                        ... and {len(fully_capable.get('clients', [])) - 50} more clients
                    </div>"""
            
            html += """
                </div>
                <p><em>Recommended Strategy: Use 802.11v BSS Transition requests with 802.11k neighbor reports for optimal steering performance.</em></p>
            </div>
        </div>"""
        
        # 802.11k Only Clients
        k_only = client_breakdown.get('k_only_clients', {})
        if k_only.get('count', 0) > 0:
            html += f"""
        <div class="accordion">
            <div class="accordion-header" onclick="toggleAccordion(this)">
                📶 802.11k Only Clients ({k_only['count']}) - Neighbor reports only
            </div>
            <div class="accordion-content">
                <p><strong>These clients support 802.11k neighbor reports but not 802.11v BSS transition management.</strong></p>
                <div class="client-list">"""
            
            for client in k_only.get('clients', [])[:50]:
                mac = client.get('mac_address', 'Unknown')
                html += f"""
                    <div class="client-item">
                        <span class="client-mac">{mac}</span>
                        <span class="client-capabilities">Supports 802.11k neighbor reports</span>
                    </div>"""
            
            if len(k_only.get('clients', [])) > 50:
                html += f"""
                    <div class="client-item" style="text-align: center; font-style: italic; color: #666;">
                        ... and {len(k_only.get('clients', [])) - 50} more clients
                    </div>"""
            
            html += """
                </div>
                <p><em>Recommended Strategy: Use 802.11k neighbor reports with legacy steering methods. Consider signal strength based steering.</em></p>
            </div>
        </div>"""
        
        # 802.11v Only Clients  
        v_only = client_breakdown.get('v_only_clients', {})
        if v_only.get('count', 0) > 0:
            html += f"""
        <div class="accordion">
            <div class="accordion-header" onclick="toggleAccordion(this)">
                🔄 802.11v Only Clients ({v_only['count']}) - BSS transition only
            </div>
            <div class="accordion-content">
                <p><strong>These clients support 802.11v BSS transition management but not 802.11k neighbor reports.</strong></p>
                <div class="client-list">"""
            
            for client in v_only.get('clients', [])[:50]:
                mac = client.get('mac_address', 'Unknown')
                html += f"""
                    <div class="client-item">
                        <span class="client-mac">{mac}</span>
                        <span class="client-capabilities">Supports 802.11v BSS transition</span>
                    </div>"""
            
            if len(v_only.get('clients', [])) > 50:
                html += f"""
                    <div class="client-item" style="text-align: center; font-style: italic; color: #666;">
                        ... and {len(v_only.get('clients', [])) - 50} more clients
                    </div>"""
            
            html += """
                </div>
                <p><em>Recommended Strategy: Use 802.11v BSS Transition requests without neighbor reports. Pre-configure target AP information.</em></p>
            </div>
        </div>"""
        
        # Legacy Clients
        legacy = client_breakdown.get('legacy_clients', {})
        if legacy.get('count', 0) > 0:
            html += f"""
        <div class="accordion">
            <div class="accordion-header" onclick="toggleAccordion(this)">
                ⚠️ Legacy Clients ({legacy['count']}) - No 802.11k/v capabilities
            </div>
            <div class="accordion-content">
                <p><strong>These clients do not support 802.11k neighbor reports or 802.11v BSS transition management.</strong></p>
                <div class="client-list">"""
            
            for client in legacy.get('clients', [])[:50]:
                mac = client.get('mac_address', 'Unknown')
                html += f"""
                    <div class="client-item">
                        <span class="client-mac">{mac}</span>
                        <span class="client-capabilities" style="color: #dc3545;">No 802.11k/v capabilities detected</span>
                    </div>"""
            
            if len(legacy.get('clients', [])) > 50:
                html += f"""
                    <div class="client-item" style="text-align: center; font-style: italic; color: #666;">
                        ... and {len(legacy.get('clients', [])) - 50} more clients
                    </div>"""
            
            html += """
                </div>
                <p><em>Recommended Strategy: Use legacy steering methods such as deauthentication, disassociation, or signal strength manipulation. Monitor for negative user experience.</em></p>
            </div>
        </div>"""
        
        html += """
    </div>"""
        
        return html
