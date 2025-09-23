# prplOS LCM Log Analysis System - Report Generator

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

from app.analytics.analysis_engine import AnalysisResult, Summary
from app.models.core import LogEntry, ApplicationInfo

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate analysis reports in various formats"""
    
    def __init__(self):
        self.report_templates = {
            "summary": self._generate_summary_report,
            "detailed": self._generate_detailed_report,
            "executive": self._generate_executive_report,
            "technical": self._generate_technical_report
        }
    
    def generate_report(self, analysis_result: AnalysisResult, 
                       report_type: str = "summary",
                       output_format: str = "json",
                       output_path: Optional[str] = None) -> str:
        """Generate a report based on analysis results"""
        logger.info(f"Generating {report_type} report in {output_format} format")
        
        # Generate report content
        if report_type not in self.report_templates:
            logger.warning(f"Unknown report type: {report_type}. Using summary.")
            report_type = "summary"
        
        report_content = self.report_templates[report_type](analysis_result)
        
        # Format report
        if output_format == "json":
            formatted_report = self._format_json_report(report_content)
        elif output_format == "html":
            formatted_report = self._format_html_report(report_content, report_type)
        elif output_format == "markdown":
            formatted_report = self._format_markdown_report(report_content, report_type)
        else:
            logger.warning(f"Unknown output format: {output_format}. Using JSON.")
            formatted_report = self._format_json_report(report_content)
        
        # Save report if output path provided
        if output_path:
            self._save_report(formatted_report, output_path, output_format)
        
        return formatted_report
    
    def _generate_summary_report(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Generate summary report"""
        summary = analysis_result.summary
        
        return {
            "report_type": "summary",
            "generated_at": datetime.now().isoformat(),
            "analysis_id": analysis_result.analysis_id,
            "project_id": analysis_result.project_id,
            "overview": {
                "total_log_entries": summary["total_log_entries"],
                "time_range": summary["time_range"],
                "applications": summary["applications"],
                "system_health_score": summary["system_health_score"]
            },
            "key_metrics": {
                "error_rate": summary["error_rate"],
                "warning_rate": summary["warning_rate"],
                "log_level_distribution": summary["log_level_distribution"]
            },
            "top_issues": summary["top_issues"][:5],
            "recommendations": analysis_result.recommendations[:3],
            "system_status": self._get_system_status(summary["system_health_score"])
        }
    
    def _generate_detailed_report(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Generate detailed report"""
        summary = analysis_result.summary
        
        return {
            "report_type": "detailed",
            "generated_at": datetime.now().isoformat(),
            "analysis_id": analysis_result.analysis_id,
            "project_id": analysis_result.project_id,
            "executive_summary": {
                "overview": self._generate_summary_report(analysis_result),
                "key_findings": self._extract_key_findings(analysis_result),
                "risk_assessment": self._assess_risks(analysis_result)
            },
            "detailed_analysis": {
                "time_series_summary": self._summarize_time_series(analysis_result.time_series_data),
                "event_patterns": self._summarize_event_patterns(analysis_result.event_patterns),
                "correlations": self._summarize_correlations(analysis_result.correlations),
                "application_insights": analysis_result.application_insights,
                "system_insights": analysis_result.system_insights
            },
            "recommendations": {
                "immediate_actions": self._get_immediate_actions(analysis_result),
                "short_term_actions": self._get_short_term_actions(analysis_result),
                "long_term_actions": self._get_long_term_actions(analysis_result)
            },
            "appendix": {
                "analysis_configuration": analysis_result.metadata.get("analysis_config", {}),
                "processing_details": analysis_result.metadata
            }
        }
    
    def _generate_executive_report(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Generate executive report"""
        summary = analysis_result.summary
        
        return {
            "report_type": "executive",
            "generated_at": datetime.now().isoformat(),
            "analysis_id": analysis_result.analysis_id,
            "project_id": analysis_result.project_id,
            "executive_summary": {
                "system_health": {
                    "score": summary["system_health_score"],
                    "status": self._get_system_status(summary["system_health_score"]),
                    "trend": "stable"  # Would be calculated from historical data
                },
                "key_metrics": {
                    "total_log_entries": summary["total_log_entries"],
                    "error_rate": f"{summary['error_rate']:.1f}%",
                    "warning_rate": f"{summary['warning_rate']:.1f}%",
                    "applications_monitored": len(summary["applications"])
                },
                "business_impact": self._assess_business_impact(analysis_result),
                "risk_level": self._assess_risk_level(summary["system_health_score"])
            },
            "recommendations": {
                "priority_1": self._get_priority_recommendations(analysis_result, 1),
                "priority_2": self._get_priority_recommendations(analysis_result, 2),
                "priority_3": self._get_priority_recommendations(analysis_result, 3)
            },
            "next_steps": self._get_executive_next_steps(analysis_result)
        }
    
    def _generate_technical_report(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Generate technical report"""
        return {
            "report_type": "technical",
            "generated_at": datetime.now().isoformat(),
            "analysis_id": analysis_result.analysis_id,
            "project_id": analysis_result.project_id,
            "technical_details": {
                "time_series_data": [ts.to_dict() for ts in analysis_result.time_series_data],
                "event_patterns": [ep.to_dict() for ep in analysis_result.event_patterns],
                "correlations": [c.to_dict() for c in analysis_result.correlations],
                "raw_statistics": analysis_result.summary
            },
            "analysis_methodology": {
                "time_series_analysis": "Aggregated log entries by time bins",
                "pattern_detection": "Identified recurring event sequences",
                "correlation_analysis": "Found temporal relationships between events",
                "health_scoring": "Calculated system health based on error rates and patterns"
            },
            "data_quality": {
                "total_entries_processed": analysis_result.metadata.get("total_entries_processed", 0),
                "processing_time": analysis_result.metadata.get("processing_time", ""),
                "analysis_configuration": analysis_result.metadata.get("analysis_config", {})
            }
        }
    
    def _format_json_report(self, report_content: Dict[str, Any]) -> str:
        """Format report as JSON"""
        return json.dumps(report_content, indent=2, default=str)
    
    def _format_html_report(self, report_content: Dict[str, Any], report_type: str) -> str:
        """Format report as HTML"""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>prplOS LCM Log Analysis Report - {report_type.title()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
        .health-score {{ font-size: 24px; font-weight: bold; }}
        .healthy {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .critical {{ color: #dc3545; }}
        .recommendation {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>prplOS LCM Log Analysis Report</h1>
        <p><strong>Report Type:</strong> {report_type.title()}</p>
        <p><strong>Generated:</strong> {report_content.get('generated_at', 'N/A')}</p>
        <p><strong>Analysis ID:</strong> {report_content.get('analysis_id', 'N/A')}</p>
    </div>
    
    {self._generate_html_content(report_content, report_type)}
</body>
</html>
        """
        return html_template
    
    def _generate_html_content(self, report_content: Dict[str, Any], report_type: str) -> str:
        """Generate HTML content based on report type"""
        if report_type == "summary":
            return self._generate_summary_html(report_content)
        elif report_type == "executive":
            return self._generate_executive_html(report_content)
        else:
            return self._generate_detailed_html(report_content)
    
    def _generate_summary_html(self, report_content: Dict[str, Any]) -> str:
        """Generate HTML for summary report"""
        overview = report_content.get("overview", {})
        key_metrics = report_content.get("key_metrics", {})
        
        health_score = overview.get("system_health_score", 0)
        health_class = "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical"
        
        return f"""
    <div class="section">
        <h2>System Overview</h2>
        <div class="metric">
            <div class="health-score {health_class}">{health_score:.1f}</div>
            <div>System Health Score</div>
        </div>
        <div class="metric">
            <div class="health-score">{overview.get('total_log_entries', 0):,}</div>
            <div>Total Log Entries</div>
        </div>
        <div class="metric">
            <div class="health-score">{len(overview.get('applications', []))}</div>
            <div>Applications</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Key Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Error Rate</td><td>{key_metrics.get('error_rate', 0):.1f}%</td></tr>
            <tr><td>Warning Rate</td><td>{key_metrics.get('warning_rate', 0):.1f}%</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Top Issues</h2>
        <ul>
            {''.join(f'<li>{issue}</li>' for issue in report_content.get('top_issues', []))}
        </ul>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        {''.join(f'<div class="recommendation">{rec}</div>' for rec in report_content.get('recommendations', []))}
    </div>
        """
    
    def _generate_executive_html(self, report_content: Dict[str, Any]) -> str:
        """Generate HTML for executive report"""
        exec_summary = report_content.get("executive_summary", {})
        system_health = exec_summary.get("system_health", {})
        key_metrics = exec_summary.get("key_metrics", {})
        
        health_score = system_health.get("score", 0)
        health_class = "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical"
        
        return f"""
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <div class="health-score {health_class}">{health_score:.1f}</div>
            <div>System Health Score</div>
        </div>
        <p><strong>Status:</strong> {system_health.get('status', 'Unknown')}</p>
        <p><strong>Risk Level:</strong> {exec_summary.get('risk_level', 'Unknown')}</p>
    </div>
    
    <div class="section">
        <h2>Key Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Log Entries</td><td>{key_metrics.get('total_log_entries', 0):,}</td></tr>
            <tr><td>Error Rate</td><td>{key_metrics.get('error_rate', 'N/A')}</td></tr>
            <tr><td>Warning Rate</td><td>{key_metrics.get('warning_rate', 'N/A')}</td></tr>
            <tr><td>Applications Monitored</td><td>{key_metrics.get('applications_monitored', 0)}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Business Impact</h2>
        <p>{exec_summary.get('business_impact', 'No significant business impact detected.')}</p>
    </div>
    
    <div class="section">
        <h2>Priority Recommendations</h2>
        <h3>Priority 1 (Immediate)</h3>
        <ul>
            {''.join(f'<li>{rec}</li>' for rec in report_content.get('recommendations', {}).get('priority_1', []))}
        </ul>
        <h3>Priority 2 (Short-term)</h3>
        <ul>
            {''.join(f'<li>{rec}</li>' for rec in report_content.get('recommendations', {}).get('priority_2', []))}
        </ul>
    </div>
        """
    
    def _generate_detailed_html(self, report_content: Dict[str, Any]) -> str:
        """Generate HTML for detailed report"""
        return """
    <div class="section">
        <h2>Detailed Analysis Report</h2>
        <p>This is a comprehensive technical report with detailed analysis results.</p>
        <p>Please refer to the JSON or technical report format for complete details.</p>
    </div>
        """
    
    def _format_markdown_report(self, report_content: Dict[str, Any], report_type: str) -> str:
        """Format report as Markdown"""
        if report_type == "summary":
            return self._generate_summary_markdown(report_content)
        elif report_type == "executive":
            return self._generate_executive_markdown(report_content)
        else:
            return self._generate_detailed_markdown(report_content)
    
    def _generate_summary_markdown(self, report_content: Dict[str, Any]) -> str:
        """Generate Markdown for summary report"""
        overview = report_content.get("overview", {})
        key_metrics = report_content.get("key_metrics", {})
        
        return f"""# prplOS LCM Log Analysis Report - Summary

**Generated:** {report_content.get('generated_at', 'N/A')}  
**Analysis ID:** {report_content.get('analysis_id', 'N/A')}  
**Project ID:** {report_content.get('project_id', 'N/A')}

## System Overview

- **System Health Score:** {overview.get('system_health_score', 0):.1f}
- **Total Log Entries:** {overview.get('total_log_entries', 0):,}
- **Applications:** {len(overview.get('applications', []))}
- **Time Range:** {overview.get('time_range', {}).get('start', 'N/A')} to {overview.get('time_range', {}).get('end', 'N/A')}

## Key Metrics

| Metric | Value |
|--------|-------|
| Error Rate | {key_metrics.get('error_rate', 0):.1f}% |
| Warning Rate | {key_metrics.get('warning_rate', 0):.1f}% |

## Top Issues

{chr(10).join(f'- {issue}' for issue in report_content.get('top_issues', []))}

## Recommendations

{chr(10).join(f'- {rec}' for rec in report_content.get('recommendations', []))}

## System Status

**Status:** {report_content.get('system_status', 'Unknown')}
        """
    
    def _generate_executive_markdown(self, report_content: Dict[str, Any]) -> str:
        """Generate Markdown for executive report"""
        exec_summary = report_content.get("executive_summary", {})
        system_health = exec_summary.get("system_health", {})
        key_metrics = exec_summary.get("key_metrics", {})
        
        return f"""# prplOS LCM Log Analysis Report - Executive Summary

**Generated:** {report_content.get('generated_at', 'N/A')}  
**Analysis ID:** {report_content.get('analysis_id', 'N/A')}

## Executive Summary

- **System Health Score:** {system_health.get('score', 0):.1f}
- **Status:** {system_health.get('status', 'Unknown')}
- **Risk Level:** {exec_summary.get('risk_level', 'Unknown')}

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Log Entries | {key_metrics.get('total_log_entries', 0):,} |
| Error Rate | {key_metrics.get('error_rate', 'N/A')} |
| Warning Rate | {key_metrics.get('warning_rate', 'N/A')} |
| Applications Monitored | {key_metrics.get('applications_monitored', 0)} |

## Business Impact

{exec_summary.get('business_impact', 'No significant business impact detected.')}

## Priority Recommendations

### Priority 1 (Immediate)
{chr(10).join(f'- {rec}' for rec in report_content.get('recommendations', {}).get('priority_1', []))}

### Priority 2 (Short-term)
{chr(10).join(f'- {rec}' for rec in report_content.get('recommendations', {}).get('priority_2', []))}

### Priority 3 (Long-term)
{chr(10).join(f'- {rec}' for rec in report_content.get('recommendations', {}).get('priority_3', []))}

## Next Steps

{chr(10).join(f'- {step}' for step in report_content.get('next_steps', []))}
        """
    
    def _generate_detailed_markdown(self, report_content: Dict[str, Any]) -> str:
        """Generate Markdown for detailed report"""
        return """# prplOS LCM Log Analysis Report - Detailed

This is a comprehensive technical report with detailed analysis results.

Please refer to the JSON or technical report format for complete details.
        """
    
    def _save_report(self, report_content: str, output_path: str, output_format: str):
        """Save report to file"""
        try:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Determine file extension
            if output_format == "html":
                extension = ".html"
            elif output_format == "markdown":
                extension = ".md"
            else:
                extension = ".json"
            
            # Add extension if not present
            if not output_path.endswith(extension):
                output_path += extension
            
            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Report saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    def _get_system_status(self, health_score: float) -> str:
        """Get system status based on health score"""
        if health_score >= 80:
            return "Healthy"
        elif health_score >= 60:
            return "Warning"
        else:
            return "Critical"
    
    def _extract_key_findings(self, analysis_result: AnalysisResult) -> List[str]:
        """Extract key findings from analysis"""
        findings = []
        summary = analysis_result.summary
        
        if summary["error_rate"] > 5:
            findings.append(f"High error rate detected: {summary['error_rate']:.1f}%")
        
        if summary["system_health_score"] < 70:
            findings.append(f"System health below optimal: {summary['system_health_score']:.1f}")
        
        if len(analysis_result.event_patterns) > 0:
            findings.append(f"Found {len(analysis_result.event_patterns)} event patterns")
        
        if len(analysis_result.correlations) > 0:
            findings.append(f"Identified {len(analysis_result.correlations)} event correlations")
        
        return findings
    
    def _assess_risks(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Assess risks based on analysis"""
        summary = analysis_result.summary
        
        risks = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        if summary["error_rate"] > 10:
            risks["high"].append("Critical error rate detected")
        elif summary["error_rate"] > 5:
            risks["medium"].append("Elevated error rate")
        
        if summary["system_health_score"] < 50:
            risks["high"].append("Critical system health issues")
        elif summary["system_health_score"] < 70:
            risks["medium"].append("System health below optimal")
        
        return risks
    
    def _summarize_time_series(self, time_series_data: List) -> Dict[str, Any]:
        """Summarize time series data"""
        return {
            "total_series": len(time_series_data),
            "metrics_analyzed": [ts.metadata.get("metric", "unknown") for ts in time_series_data],
            "time_range": time_series_data[0].metadata if time_series_data else {}
        }
    
    def _summarize_event_patterns(self, event_patterns: List) -> Dict[str, Any]:
        """Summarize event patterns"""
        return {
            "total_patterns": len(event_patterns),
            "high_confidence_patterns": len([p for p in event_patterns if p.confidence > 0.8]),
            "pattern_types": list(set(p.name.split(" (")[0] for p in event_patterns))
        }
    
    def _summarize_correlations(self, correlations: List) -> Dict[str, Any]:
        """Summarize correlations"""
        return {
            "total_correlations": len(correlations),
            "strong_correlations": len([c for c in correlations if c.strength > 0.7]),
            "correlation_types": list(set(c.correlation_type for c in correlations))
        }
    
    def _get_immediate_actions(self, analysis_result: AnalysisResult) -> List[str]:
        """Get immediate actions"""
        actions = []
        summary = analysis_result.summary
        
        if summary["error_rate"] > 10:
            actions.append("Immediately investigate critical error patterns")
        
        if summary["system_health_score"] < 50:
            actions.append("Review system configuration and dependencies")
        
        return actions
    
    def _get_short_term_actions(self, analysis_result: AnalysisResult) -> List[str]:
        """Get short-term actions"""
        actions = []
        summary = analysis_result.summary
        
        if summary["error_rate"] > 5:
            actions.append("Implement error monitoring and alerting")
        
        if len(analysis_result.event_patterns) > 0:
            actions.append("Analyze and address recurring event patterns")
        
        return actions
    
    def _get_long_term_actions(self, analysis_result: AnalysisResult) -> List[str]:
        """Get long-term actions"""
        return [
            "Implement comprehensive logging standards",
            "Set up automated analysis and reporting",
            "Establish baseline metrics and monitoring"
        ]
    
    def _assess_business_impact(self, analysis_result: AnalysisResult) -> str:
        """Assess business impact"""
        summary = analysis_result.summary
        
        if summary["error_rate"] > 10:
            return "High business impact: Critical error rates may affect system reliability and user experience."
        elif summary["error_rate"] > 5:
            return "Medium business impact: Elevated error rates should be monitored and addressed."
        else:
            return "Low business impact: System appears stable with minimal operational issues."
    
    def _assess_risk_level(self, health_score: float) -> str:
        """Assess risk level"""
        if health_score < 50:
            return "High"
        elif health_score < 70:
            return "Medium"
        else:
            return "Low"
    
    def _get_priority_recommendations(self, analysis_result: AnalysisResult, priority: int) -> List[str]:
        """Get recommendations by priority"""
        if priority == 1:
            return [rec for rec in analysis_result.recommendations if "immediate" in rec.lower() or "critical" in rec.lower()]
        elif priority == 2:
            return [rec for rec in analysis_result.recommendations if "investigate" in rec.lower() or "review" in rec.lower()]
        else:
            return [rec for rec in analysis_result.recommendations if rec not in self._get_priority_recommendations(analysis_result, 1) + self._get_priority_recommendations(analysis_result, 2)]
    
    def _get_executive_next_steps(self, analysis_result: AnalysisResult) -> List[str]:
        """Get executive next steps"""
        return [
            "Review analysis results with technical team",
            "Prioritize recommendations based on business impact",
            "Schedule follow-up analysis in 1-2 weeks",
            "Consider implementing automated monitoring"
        ]
