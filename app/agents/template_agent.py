"""
Template Agent for MeshLog Integrated Agent System

This is a simple template agent that can be used as a starting point
for developing new agents or for testing the agent system.
"""

import time
from typing import Dict, Any
from pathlib import Path

from app.core.agent_interface import AgentInterface

class TemplateAgent(AgentInterface):
    """Template Agent for development and testing"""
    
    @property
    def agent_type(self) -> str:
        return "template-agent"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def __init__(self):
        self.capabilities = ["generic_analysis", "template_processing"]
        self.description = "Template agent for development and testing"
        self.input_schema = {
            "type": "object",
            "properties": {
                "log_data": {
                    "type": "object",
                    "description": "Any log data structure"
                },
                "analysis_config": {
                    "type": "object",
                    "description": "Analysis configuration"
                }
            }
        }
        self.output_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "analysis_data": {"type": "object"},
                "metadata": {"type": "object"}
            }
        }
    
    def analyze(self, log_paths: list, output_path: str, analysis_config: dict = None) -> dict:
        """Generic analysis template following the standard agent interface"""
        start_time = time.time()
        
        try:
            # Ensure output directory exists
            from pathlib import Path
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process log files (basic template processing)
            total_lines = 0
            total_files = len(log_paths)
            
            # Simple log file processing
            for log_file in log_paths:
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                except Exception as e:
                    print(f"Warning: Could not read {log_file}: {e}")
            
            # Create analysis results
            analysis_data = {
                "summary": {
                    "total_files_processed": total_files,
                    "total_lines_processed": total_lines,
                    "analysis_type": "template",
                    "status": "completed"
                },
                "metrics": {
                    "processing_time": time.time() - start_time,
                    "files_per_second": total_files / max(time.time() - start_time, 0.001),
                    "lines_per_second": total_lines / max(time.time() - start_time, 0.001)
                },
                "insights": [
                    f"Processed {total_files} log files successfully",
                    f"Analyzed {total_lines} lines of log data",
                    "Template agent analysis completed without errors"
                ]
            }
            
            # Create results structure matching other agents
            results = {
                "status": "completed",
                "analysis_id": f"template_{int(time.time())}",
                "analysis_data": analysis_data,
                "metadata": {
                    "agent_type": self.agent_type,
                    "version": self.version,
                    "processing_time": time.time() - start_time,
                    "input_files": total_files,
                    "total_lines_processed": total_lines
                }
            }
            
            # Write results to files (following standard pattern)
            self._write_results_to_files(results, output_dir)
            
            return results
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def _write_results_to_files(self, results: dict, output_dir: Path) -> None:
        """Write analysis results to standard files"""
        import json
        
        # Write agent_data.json
        json_file = output_dir / "agent_data.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Write agent_report.html
        html_file = output_dir / "agent_report.html"
        html_content = self._generate_html_report(results)
        with open(html_file, 'w') as f:
            f.write(html_content)
    
    def _generate_html_report(self, results: dict) -> str:
        """Generate HTML report for template agent"""
        analysis_data = results['analysis_data']
        summary = analysis_data['summary']
        metrics = analysis_data['metrics']
        insights = analysis_data['insights']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Template Agent Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .summary {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .metrics {{ background: #f0f8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .insights {{ background: #fff8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .metric {{ margin: 5px 0; }}
                .success {{ color: #28a745; }}
                .info {{ color: #17a2b8; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Template Agent Analysis Report</h1>
                <p><strong>Agent Version:</strong> {self.version}</p>
                <p><strong>Agent Type:</strong> {self.agent_type}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <div class="metric"><strong>Files Processed:</strong> {summary['total_files_processed']}</div>
                <div class="metric"><strong>Lines Processed:</strong> {summary['total_lines_processed']}</div>
                <div class="metric"><strong>Analysis Status:</strong> <span class="success">{summary['status']}</span></div>
            </div>
            
            <div class="metrics">
                <h2>Performance Metrics</h2>
                <div class="metric"><strong>Processing Time:</strong> {metrics['processing_time']:.2f} seconds</div>
                <div class="metric"><strong>Files per Second:</strong> {metrics['files_per_second']:.2f}</div>
                <div class="metric"><strong>Lines per Second:</strong> {metrics['lines_per_second']:.0f}</div>
            </div>
            
            <div class="insights">
                <h2>Analysis Insights</h2>
                {''.join(f'<div style="margin: 10px 0;" class="info">{insight}</div>' for insight in insights)}
            </div>
        </body>
        </html>
        """
        return html