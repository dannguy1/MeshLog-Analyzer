# prplOS LCM Log Analysis System - Analysis Orchestrator

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

from app.models.core import (
    LogEntry, LogLevel, AnalysisResult, ApplicationAnalysisResult,
    CorrelationResult, PackageStructure, ContainerInfo
)
from app.analyzers.application_analyzer import ApplicationAnalyzer

logger = logging.getLogger(__name__)

class AnalysisOrchestrator:
    """Orchestrates application-specific analysis"""
    
    def __init__(self):
        self.supported_applications = [
            "wnc-steer",
            "wnc-acs", 
            "wnc-tpyopt",
            "otbr-agent"
        ]
    
    def analyze_project(self, project_name: str, package_structure: PackageStructure, log_entries: List[LogEntry]) -> AnalysisResult:
        """Analyze a project with application-specific analysis"""
        logger.info(f"Starting application-specific analysis for project: {project_name}")
        
        # Create analysis result
        analysis_result = AnalysisResult(
            analysis_id=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            project_name=project_name
        )
        
        # Group containers by application
        app_containers = self._group_containers_by_application(package_structure.containers)
        
        # Analyze each application separately
        for app_name, containers in app_containers.items():
            if app_name in self.supported_applications:
                app_analysis = self._analyze_application(app_name, containers, log_entries)
                analysis_result.application_analyses[app_name] = app_analysis
                logger.info(f"Completed analysis for {app_name}: {len(app_analysis.anomalies)} anomalies")
        
        # Generate cross-application correlations
        analysis_result.cross_application_correlations = self._generate_cross_application_correlations(
            analysis_result.application_analyses
        )
        
        # Generate system-level insights
        analysis_result.system_insights = self._generate_system_insights(
            analysis_result.application_analyses,
            package_structure
        )
        
        # Generate project summary
        analysis_result.summary = self._generate_project_summary(
            analysis_result.application_analyses,
            package_structure,
            log_entries
        )
        
        # Legacy fields for backward compatibility
        self._populate_legacy_fields(analysis_result)
        
        logger.info(f"Analysis completed for project {project_name}: {len(analysis_result.application_analyses)} applications")
        return analysis_result
    
    def _group_containers_by_application(self, containers: List[ContainerInfo]) -> Dict[str, List[ContainerInfo]]:
        """Group containers by application name"""
        app_containers = defaultdict(list)
        
        for container in containers:
            app_name = container.application_name
            app_containers[app_name].append(container)
        
        return dict(app_containers)
    
    def _analyze_application(self, app_name: str, containers: List[ContainerInfo], log_entries: List[LogEntry]) -> ApplicationAnalysisResult:
        """Analyze a specific application"""
        logger.info(f"Analyzing application: {app_name} with {len(containers)} containers")
        
        # Use the first container for the analysis (assuming same app = same container type)
        primary_container = containers[0]
        
        # Create application analyzer
        analyzer = ApplicationAnalyzer(
            application_name=app_name,
            container_id=primary_container.container_id,
            functional_domain=primary_container.functional_domain
        )
        
        # Analyze the application
        app_analysis = analyzer.analyze_application(log_entries)
        
        # Add time sequence preview
        app_logs = [log for log in log_entries if log.application == app_name]
        app_analysis.time_sequence_preview = analyzer.generate_time_sequence_preview(app_logs)
        
        # Update container-specific information
        app_analysis.container_id = primary_container.container_id
        app_analysis.functional_domain = primary_container.functional_domain
        
        return app_analysis
    
    def _generate_cross_application_correlations(self, app_analyses: Dict[str, ApplicationAnalysisResult]) -> List[CorrelationResult]:
        """Generate correlations between different applications"""
        correlations = []
        
        app_names = list(app_analyses.keys())
        
        for i in range(len(app_names)):
            for j in range(i + 1, len(app_names)):
                app1 = app_names[i]
                app2 = app_names[j]
                
                # Get error rates for correlation
                error_rate1 = app_analyses[app1].error_rate
                error_rate2 = app_analyses[app2].error_rate
                
                # Get health scores for correlation
                health1 = app_analyses[app1].health_score
                health2 = app_analyses[app2].health_score
                
                # Create correlation based on error rates
                if error_rate1 > 0 and error_rate2 > 0:
                    # Simple correlation: if both have high error rates, they might be related
                    correlation_strength = min(error_rate1, error_rate2) / max(error_rate1, error_rate2)
                    
                    if correlation_strength > 0.5:
                        correlations.append(CorrelationResult(
                            metric1=f"{app1}_error_rate",
                            metric2=f"{app2}_error_rate",
                            correlation_type="cross_application",
                            strength=correlation_strength,
                            confidence=0.6,
                            description=f"Error rate correlation between {app1} and {app2}"
                        ))
                
                # Create correlation based on health scores
                if health1 < 80 and health2 < 80:
                    # If both applications have poor health, they might be related
                    health_correlation = (100 - max(health1, health2)) / 100
                    
                    if health_correlation > 0.3:
                        correlations.append(CorrelationResult(
                            metric1=f"{app1}_health_score",
                            metric2=f"{app2}_health_score",
                            correlation_type="cross_application",
                            strength=health_correlation,
                            confidence=0.5,
                            description=f"Health score correlation between {app1} and {app2}"
                        ))
        
        return correlations
    
    def _generate_system_insights(self, app_analyses: Dict[str, ApplicationAnalysisResult], package_structure: PackageStructure) -> Dict[str, Any]:
        """Generate system-level insights"""
        insights = {
            'total_applications': len(app_analyses),
            'applications_analyzed': list(app_analyses.keys()),
            'overall_health_score': 0.0,
            'system_status': 'healthy',
            'critical_issues': [],
            'performance_summary': {},
            'recommendations': []
        }
        
        # Calculate overall health score
        total_health = 0.0
        app_count = 0
        
        for app_name, analysis in app_analyses.items():
            if analysis.health_score > 0:
                total_health += analysis.health_score
                app_count += 1
        
        if app_count > 0:
            insights['overall_health_score'] = total_health / app_count
        
        # Determine system status
        if insights['overall_health_score'] >= 80:
            insights['system_status'] = 'healthy'
        elif insights['overall_health_score'] >= 60:
            insights['system_status'] = 'degraded'
        else:
            insights['system_status'] = 'critical'
        
        # Identify critical issues
        for app_name, analysis in app_analyses.items():
            if analysis.error_rate > 0.2:
                insights['critical_issues'].append(f"High error rate in {app_name}: {analysis.error_rate:.1%}")
            
            if analysis.health_score < 50:
                insights['critical_issues'].append(f"Poor health in {app_name}: {analysis.health_score:.1f}/100")
        
        # Performance summary
        for app_name, analysis in app_analyses.items():
            insights['performance_summary'][app_name] = {
                'health_score': analysis.health_score,
                'error_rate': analysis.error_rate,
                'log_volume': analysis.log_volume,
                'anomaly_count': len(analysis.anomalies)
            }
        
        # System-level recommendations
        if insights['overall_health_score'] < 70:
            insights['recommendations'].append("Overall system health is below optimal. Review application configurations and check for system-wide issues.")
        
        if len(insights['critical_issues']) > 0:
            insights['recommendations'].append(f"Critical issues detected: {len(insights['critical_issues'])} applications need immediate attention.")
        
        return insights
    
    def _generate_project_summary(self, app_analyses: Dict[str, ApplicationAnalysisResult], package_structure: PackageStructure, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """Generate project-level summary"""
        summary = {
            'total_applications': len(app_analyses),
            'total_log_entries': len(log_entries),
            'time_range': {
                'start': log_entries[0].timestamp.isoformat() if log_entries else None,
                'end': log_entries[-1].timestamp.isoformat() if log_entries else None
            },
            'applications': list(app_analyses.keys()),
            'total_containers': len(package_structure.containers),
            'total_anomalies': sum(len(analysis.anomalies) for analysis in app_analyses.values()),
            'overall_error_rate': 0.0,
            'overall_health_score': 0.0
        }
        
        # Calculate overall metrics
        total_error_logs = 0
        total_health = 0.0
        app_count = 0
        
        for analysis in app_analyses.values():
            total_error_logs += int(analysis.error_rate * analysis.log_volume)
            if analysis.health_score > 0:
                total_health += analysis.health_score
                app_count += 1
        
        if len(log_entries) > 0:
            summary['overall_error_rate'] = total_error_logs / len(log_entries)
        
        if app_count > 0:
            summary['overall_health_score'] = total_health / app_count
        
        return summary
    
    def _populate_legacy_fields(self, analysis_result: AnalysisResult):
        """Populate legacy fields for backward compatibility"""
        # Combine all application data into legacy fields
        all_time_series = []
        all_anomalies = []
        all_predictions = []
        all_statistical_results = []
        all_correlations = []
        all_event_patterns = []
        all_recommendations = []
        
        for app_analysis in analysis_result.application_analyses.values():
            all_time_series.extend(app_analysis.time_series_data)
            all_anomalies.extend(app_analysis.anomalies)
            all_predictions.extend(app_analysis.predictions)
            all_statistical_results.extend(app_analysis.statistical_results)
            all_correlations.extend(app_analysis.correlations)
            all_event_patterns.extend(app_analysis.event_patterns)
            all_recommendations.extend(app_analysis.recommendations)
        
        # Add cross-application correlations
        all_correlations.extend(analysis_result.cross_application_correlations)
        
        # Populate legacy fields
        analysis_result.time_series_data = all_time_series
        analysis_result.anomalies = all_anomalies
        analysis_result.predictions = all_predictions
        analysis_result.statistical_results = all_statistical_results
        analysis_result.correlations = all_correlations
        analysis_result.event_patterns = all_event_patterns
        analysis_result.recommendations = all_recommendations
        
        # Populate application insights
        for app_name, app_analysis in analysis_result.application_analyses.items():
            analysis_result.application_insights[app_name] = {
                'health_score': app_analysis.health_score,
                'error_rate': app_analysis.error_rate,
                'log_volume': app_analysis.log_volume,
                'anomaly_count': len(app_analysis.anomalies),
                'functional_domain': app_analysis.functional_domain
            }
