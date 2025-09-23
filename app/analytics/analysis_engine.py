# prplOS LCM Log Analysis System - Analysis Engine

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, Counter

from app.models.core import LogEntry, LogLevel, ApplicationInfo
from app.analytics.time_series_processor import TimeSeriesProcessor, EventCorrelator, TimeSeriesData, EventPattern, CorrelationResult

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Analysis result structure"""
    analysis_id: str
    project_id: str
    timestamp: datetime
    summary: Dict[str, Any]
    time_series_data: List[TimeSeriesData]
    event_patterns: List[EventPattern]
    correlations: List[CorrelationResult]
    application_insights: List[Dict[str, Any]]
    system_insights: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "analysis_id": self.analysis_id,
            "project_id": self.project_id,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "time_series_data": [ts.to_dict() for ts in self.time_series_data],
            "event_patterns": [ep.to_dict() for ep in self.event_patterns],
            "correlations": [c.to_dict() for c in self.correlations],
            "application_insights": self.application_insights,
            "system_insights": self.system_insights,
            "recommendations": self.recommendations,
            "metadata": self.metadata
        }

@dataclass
class Summary:
    """Analysis summary structure"""
    total_log_entries: int
    time_range: Dict[str, str]
    applications: List[str]
    log_level_distribution: Dict[str, int]
    error_rate: float
    warning_rate: float
    top_issues: List[str]
    system_health_score: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "total_log_entries": self.total_log_entries,
            "time_range": self.time_range,
            "applications": self.applications,
            "log_level_distribution": self.log_level_distribution,
            "error_rate": self.error_rate,
            "warning_rate": self.warning_rate,
            "top_issues": self.top_issues,
            "system_health_score": self.system_health_score,
            "metadata": self.metadata
        }

class AnalysisEngine:
    """Main analysis engine for log processing"""
    
    def __init__(self):
        self.time_series_processor = TimeSeriesProcessor()
        self.event_correlator = EventCorrelator()
        
    def analyze_logs(self, log_entries: List[LogEntry], 
                    project_id: str,
                    analysis_config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Perform comprehensive log analysis"""
        logger.info(f"Starting analysis for project: {project_id}")
        
        if not log_entries:
            logger.warning("No log entries provided for analysis")
            return self._create_empty_analysis(project_id)
        
        # Generate analysis ID
        analysis_id = f"analysis_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Perform analysis steps
        summary = self._generate_summary(log_entries)
        time_series_data = self._generate_time_series(log_entries, analysis_config)
        event_patterns = self._find_event_patterns(log_entries, analysis_config)
        correlations = self._find_correlations(log_entries, analysis_config)
        application_insights = self._generate_application_insights(log_entries)
        system_insights = self._generate_system_insights(log_entries, summary)
        recommendations = self._generate_recommendations(log_entries, summary, event_patterns)
        
        # Create analysis result
        result = AnalysisResult(
            analysis_id=analysis_id,
            project_id=project_id,
            timestamp=datetime.now(),
            summary=summary.to_dict(),
            time_series_data=time_series_data,
            event_patterns=event_patterns,
            correlations=correlations,
            application_insights=application_insights,
            system_insights=system_insights,
            recommendations=recommendations,
            metadata={
                "analysis_config": analysis_config or {},
                "processing_time": datetime.now().isoformat(),
                "total_entries_processed": len(log_entries)
            }
        )
        
        logger.info(f"Analysis completed: {analysis_id}")
        return result
    
    def _create_empty_analysis(self, project_id: str) -> AnalysisResult:
        """Create empty analysis result"""
        return AnalysisResult(
            analysis_id=f"empty_analysis_{project_id}",
            project_id=project_id,
            timestamp=datetime.now(),
            summary={},
            time_series_data=[],
            event_patterns=[],
            correlations=[],
            application_insights=[],
            system_insights={},
            recommendations=["No log entries found for analysis"],
            metadata={"empty": True}
        )
    
    def _generate_summary(self, log_entries: List[LogEntry]) -> Summary:
        """Generate analysis summary"""
        logger.info("Generating analysis summary")
        
        # Basic statistics
        total_entries = len(log_entries)
        
        # Time range
        timestamps = [entry.timestamp for entry in log_entries]
        time_range = {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat(),
            "duration_hours": (max(timestamps) - min(timestamps)).total_seconds() / 3600
        }
        
        # Applications
        applications = list(set(entry.application for entry in log_entries))
        
        # Log level distribution
        level_counts = Counter(entry.log_level.value for entry in log_entries)
        log_level_distribution = dict(level_counts)
        
        # Error and warning rates
        error_count = level_counts.get("error", 0) + level_counts.get("critical", 0)
        warning_count = level_counts.get("warning", 0)
        
        error_rate = (error_count / total_entries) * 100 if total_entries > 0 else 0
        warning_rate = (warning_count / total_entries) * 100 if total_entries > 0 else 0
        
        # Top issues
        top_issues = self._identify_top_issues(log_entries)
        
        # System health score (0-100)
        health_score = self._calculate_health_score(log_entries, error_rate, warning_rate)
        
        return Summary(
            total_log_entries=total_entries,
            time_range=time_range,
            applications=applications,
            log_level_distribution=log_level_distribution,
            error_rate=error_rate,
            warning_rate=warning_rate,
            top_issues=top_issues,
            system_health_score=health_score,
            metadata={
                "unique_applications": len(applications),
                "analysis_timestamp": datetime.now().isoformat()
            }
        )
    
    def _generate_time_series(self, log_entries: List[LogEntry], 
                            analysis_config: Optional[Dict[str, Any]]) -> List[TimeSeriesData]:
        """Generate time series data"""
        logger.info("Generating time series data")
        
        time_series_data = []
        
        # Create different time series metrics
        metrics = ["count", "error_count", "warning_count", "unique_applications"]
        
        for metric in metrics:
            time_series = self.time_series_processor.create_time_series(log_entries, metric)
            time_series_data.append(time_series)
        
        # Create application-specific time series
        app_entries = defaultdict(list)
        for entry in log_entries:
            app_entries[entry.application].append(entry)
        
        for app_name, entries in app_entries.items():
            if len(entries) > 10:  # Only create time series for apps with sufficient data
                app_time_series = self.time_series_processor.create_time_series(
                    entries, "count"
                )
                app_time_series.metadata["application"] = app_name
                time_series_data.append(app_time_series)
        
        return time_series_data
    
    def _find_event_patterns(self, log_entries: List[LogEntry], 
                             analysis_config: Optional[Dict[str, Any]]) -> List[EventPattern]:
        """Find event patterns in log entries"""
        logger.info("Finding event patterns")
        
        # Use default time window or from config
        time_window = timedelta(minutes=5)
        if analysis_config and "pattern_time_window_minutes" in analysis_config:
            time_window = timedelta(minutes=analysis_config["pattern_time_window_minutes"])
        
        return self.event_correlator.find_event_patterns(log_entries, time_window)
    
    def _find_correlations(self, log_entries: List[LogEntry], 
                           analysis_config: Optional[Dict[str, Any]]) -> List[CorrelationResult]:
        """Find event correlations"""
        logger.info("Finding event correlations")
        
        return self.event_correlator.correlate_events(log_entries)
    
    def _generate_application_insights(self, log_entries: List[LogEntry]) -> List[Dict[str, Any]]:
        """Generate insights for each application"""
        logger.info("Generating application insights")
        
        insights = []
        app_entries = defaultdict(list)
        
        for entry in log_entries:
            app_entries[entry.application].append(entry)
        
        for app_name, entries in app_entries.items():
            insight = self._analyze_application(app_name, entries)
            insights.append(insight)
        
        return insights
    
    def _analyze_application(self, app_name: str, entries: List[LogEntry]) -> Dict[str, Any]:
        """Analyze a single application"""
        # Sort entries by timestamp
        sorted_entries = sorted(entries, key=lambda x: x.timestamp)
        
        # Basic statistics
        total_entries = len(entries)
        error_count = sum(1 for e in entries if e.log_level in [LogLevel.ERROR, LogLevel.CRITICAL])
        warning_count = sum(1 for e in entries if e.log_level == LogLevel.WARNING)
        
        # Time range
        timestamps = [e.timestamp for e in entries]
        time_range = {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat(),
            "duration_hours": (max(timestamps) - min(timestamps)).total_seconds() / 3600
        }
        
        # Log level distribution
        level_distribution = Counter(e.log_level.value for e in entries)
        
        # Error rate
        error_rate = (error_count / total_entries) * 100 if total_entries > 0 else 0
        
        # Common patterns
        common_patterns = self._find_common_patterns(entries)
        
        # Health assessment
        health_status = self._assess_application_health(error_rate, warning_count, total_entries)
        
        return {
            "application": app_name,
            "total_entries": total_entries,
            "time_range": time_range,
            "error_count": error_count,
            "warning_count": warning_count,
            "error_rate": error_rate,
            "log_level_distribution": dict(level_distribution),
            "common_patterns": common_patterns,
            "health_status": health_status,
            "insights": self._generate_application_insights_text(app_name, error_rate, common_patterns)
        }
    
    def _generate_system_insights(self, log_entries: List[LogEntry], 
                                 summary: Summary) -> Dict[str, Any]:
        """Generate system-wide insights"""
        logger.info("Generating system insights")
        
        # System health assessment
        health_assessment = self._assess_system_health(summary)
        
        # Performance metrics
        performance_metrics = self._calculate_performance_metrics(log_entries)
        
        # Security insights
        security_insights = self._analyze_security_events(log_entries)
        
        # Operational insights
        operational_insights = self._analyze_operational_patterns(log_entries)
        
        return {
            "health_assessment": health_assessment,
            "performance_metrics": performance_metrics,
            "security_insights": security_insights,
            "operational_insights": operational_insights,
            "overall_assessment": self._generate_overall_assessment(summary, health_assessment)
        }
    
    def _generate_recommendations(self, log_entries: List[LogEntry], 
                                 summary: Summary, 
                                 event_patterns: List[EventPattern]) -> List[str]:
        """Generate recommendations based on analysis"""
        logger.info("Generating recommendations")
        
        recommendations = []
        
        # Error rate recommendations
        if summary.error_rate > 5.0:
            recommendations.append("High error rate detected. Review application configurations and dependencies.")
        
        if summary.error_rate > 10.0:
            recommendations.append("Critical error rate. Immediate investigation required.")
        
        # Pattern-based recommendations
        for pattern in event_patterns:
            if "error" in pattern.name.lower() and pattern.confidence > 0.7:
                recommendations.append(f"Address recurring error pattern: {pattern.name}")
        
        # Application-specific recommendations
        app_entries = defaultdict(list)
        for entry in log_entries:
            app_entries[entry.application].append(entry)
        
        for app_name, entries in app_entries.items():
            error_count = sum(1 for e in entries if e.log_level in [LogLevel.ERROR, LogLevel.CRITICAL])
            if error_count > 10:
                recommendations.append(f"Investigate error patterns in {app_name} application")
        
        # System health recommendations
        if summary.system_health_score < 70:
            recommendations.append("System health below optimal levels. Review overall system configuration.")
        
        if summary.system_health_score < 50:
            recommendations.append("Critical system health issues detected. Immediate system review required.")
        
        # Add general recommendations if none specific
        if not recommendations:
            recommendations.append("System appears healthy. Continue monitoring for any emerging issues.")
        
        return recommendations
    
    def _identify_top_issues(self, log_entries: List[LogEntry]) -> List[str]:
        """Identify top issues from log entries"""
        # Count error messages
        error_messages = [e.message for e in log_entries 
                         if e.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        
        # Find most common error patterns
        error_patterns = Counter()
        for message in error_messages:
            # Extract key parts of error messages
            words = message.lower().split()
            if len(words) > 2:
                pattern = " ".join(words[:3])
                error_patterns[pattern] += 1
        
        # Return top 5 issues
        top_issues = []
        for pattern, count in error_patterns.most_common(5):
            if count > 1:  # Only include patterns that occur multiple times
                top_issues.append(f"{pattern} (occurred {count} times)")
        
        return top_issues
    
    def _calculate_health_score(self, log_entries: List[LogEntry], 
                               error_rate: float, 
                               warning_rate: float) -> float:
        """Calculate system health score (0-100)"""
        base_score = 100.0
        
        # Deduct points for errors
        if error_rate > 0:
            base_score -= min(error_rate * 2, 50)  # Max 50 points deduction for errors
        
        # Deduct points for warnings
        if warning_rate > 0:
            base_score -= min(warning_rate, 20)  # Max 20 points deduction for warnings
        
        # Bonus for good patterns
        info_count = sum(1 for e in log_entries if e.log_level == LogLevel.INFO)
        total_entries = len(log_entries)
        if total_entries > 0:
            info_rate = (info_count / total_entries) * 100
            if info_rate > 80:
                base_score += 10  # Bonus for high info rate
        
        return max(0, min(100, base_score))
    
    def _find_common_patterns(self, entries: List[LogEntry]) -> List[str]:
        """Find common patterns in log messages"""
        patterns = Counter()
        
        for entry in entries:
            # Extract common patterns from messages
            message = entry.message.lower()
            words = message.split()
            
            if len(words) >= 2:
                # Look for common prefixes
                prefix = " ".join(words[:2])
                patterns[prefix] += 1
        
        # Return top patterns
        return [pattern for pattern, count in patterns.most_common(5) if count > 1]
    
    def _assess_application_health(self, error_rate: float, 
                                  warning_count: int, 
                                  total_entries: int) -> str:
        """Assess application health status"""
        if error_rate > 10.0 or (warning_count > 50 and total_entries > 1000):
            return "critical"
        elif error_rate > 5.0 or warning_count > 20:
            return "warning"
        elif error_rate > 1.0:
            return "attention"
        else:
            return "healthy"
    
    def _assess_system_health(self, summary: Summary) -> Dict[str, Any]:
        """Assess overall system health"""
        return {
            "overall_score": summary.system_health_score,
            "status": "healthy" if summary.system_health_score >= 80 else 
                     "warning" if summary.system_health_score >= 60 else "critical",
            "error_rate": summary.error_rate,
            "warning_rate": summary.warning_rate,
            "applications_healthy": len([app for app in summary.applications if app != "unknown"])
        }
    
    def _calculate_performance_metrics(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        # This is a simplified implementation
        # In a real system, you'd extract performance data from structured logs
        
        return {
            "total_entries_per_hour": len(log_entries) / max(1, (log_entries[-1].timestamp - log_entries[0].timestamp).total_seconds() / 3600),
            "average_message_length": sum(len(e.message) for e in log_entries) / len(log_entries) if log_entries else 0,
            "structured_data_usage": sum(1 for e in log_entries if e.structured_data) / len(log_entries) if log_entries else 0
        }
    
    def _analyze_security_events(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """Analyze security-related events"""
        security_keywords = ["auth", "login", "password", "security", "access", "permission", "denied"]
        security_events = []
        
        for entry in log_entries:
            message_lower = entry.message.lower()
            if any(keyword in message_lower for keyword in security_keywords):
                security_events.append({
                    "timestamp": entry.timestamp.isoformat(),
                    "application": entry.application,
                    "level": entry.log_level.value,
                    "message": entry.message[:100]
                })
        
        return {
            "security_events_count": len(security_events),
            "security_events": security_events[:10],  # Top 10 security events
            "high_severity_security_events": len([e for e in security_events if e["level"] in ["error", "critical"]])
        }
    
    def _analyze_operational_patterns(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """Analyze operational patterns"""
        # Group by hour to find operational patterns
        hourly_distribution = defaultdict(int)
        
        for entry in log_entries:
            hour = entry.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_distribution[hour] += 1
        
        return {
            "peak_hours": [h.isoformat() for h, count in sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:3]],
            "quiet_hours": [h.isoformat() for h, count in sorted(hourly_distribution.items(), key=lambda x: x[1])[:3]],
            "hourly_distribution": {h.isoformat(): count for h, count in hourly_distribution.items()}
        }
    
    def _generate_overall_assessment(self, summary: Summary, 
                                     health_assessment: Dict[str, Any]) -> str:
        """Generate overall system assessment"""
        if health_assessment["status"] == "healthy":
            return "System is operating normally with good health indicators."
        elif health_assessment["status"] == "warning":
            return "System shows some warning signs that should be monitored."
        else:
            return "System has critical issues that require immediate attention."
    
    def _generate_application_insights_text(self, app_name: str, 
                                             error_rate: float, 
                                             common_patterns: List[str]) -> str:
        """Generate text insights for an application"""
        if error_rate == 0:
            return f"{app_name} is operating normally with no errors detected."
        elif error_rate < 5:
            return f"{app_name} has low error rate ({error_rate:.1f}%). Monitor for any emerging patterns."
        else:
            return f"{app_name} has elevated error rate ({error_rate:.1f}%). Investigation recommended."
    
    def generate_summary(self, analysis_result: AnalysisResult) -> Summary:
        """Generate analysis summary"""
        return Summary(
            total_log_entries=analysis_result.summary["total_log_entries"],
            time_range=analysis_result.summary["time_range"],
            applications=analysis_result.summary["applications"],
            log_level_distribution=analysis_result.summary["log_level_distribution"],
            error_rate=analysis_result.summary["error_rate"],
            warning_rate=analysis_result.summary["warning_rate"],
            top_issues=analysis_result.summary["top_issues"],
            system_health_score=analysis_result.summary["system_health_score"],
            metadata=analysis_result.summary.get("metadata", {})
        )
