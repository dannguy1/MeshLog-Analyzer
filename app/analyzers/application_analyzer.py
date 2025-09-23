# prplOS LCM Log Analysis System - Application-Specific Analyzer

import os
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import json

from app.models.core import (
    LogEntry, LogLevel, AnomalyType, ForecastType, DistributionType,
    TimeSeriesData, TimeSeriesDataPoint, AnomalyResult, PredictionResult,
    StatisticalResult, CorrelationResult, EventPattern, ApplicationAnalysisResult,
    ForecastDataPoint
)

logger = logging.getLogger(__name__)

class ApplicationAnalyzer:
    """Analyzes logs for a specific application"""
    
    def __init__(self, application_name: str, container_id: str, functional_domain: str):
        self.application_name = application_name
        self.container_id = container_id
        self.functional_domain = functional_domain
        
        # Application-specific patterns and metrics
        self.metric_patterns = self._get_application_metrics()
        self.error_patterns = self._get_error_patterns()
        self.performance_patterns = self._get_performance_patterns()
    
    def _get_application_metrics(self) -> Dict[str, List[str]]:
        """Get application-specific metric patterns"""
        patterns = {
            "wnc-steer": {
                "client_count": [r"sta_info\.mac=([a-fA-F0-9:]+)", r"client=([a-fA-F0-9:]+)"],
                "rssi_values": [r"RSSI=(-?\d+)", r"rcpi=(\d+)"],
                "steering_events": [r"steer_info->enable=(\d+)", r"steering.*triggered"],
                "weak_signal_clients": [r"weak signal clients", r"RSSI.*low"]
            },
            "wnc-acs": {
                "channel_changes": [r"channelList.*(\d+)", r"opClass.*(\d+)"],
                "interference_detected": [r"interference.*detected", r"channel.*busy"],
                "scan_results": [r"scan.*result", r"channel.*quality"]
            },
            "wnc-tpyopt": {
                "topology_changes": [r"topology.*change", r"Build topology"],
                "scan_triggers": [r"State: WaitTrigger --> SendScan", r"scan.*triggered"],
                "optimization_events": [r"optimization.*event", r"topology.*optimize"]
            },
            "otbr-agent": {
                "mesh_messages": [r"MeshForwarder.*Sent", r"Mle.*Send"],
                "beacon_requests": [r"Beacon Request", r"beacon.*request"],
                "network_changes": [r"network.*change", r"topology.*update"]
            }
        }
        return patterns.get(self.application_name, {})
    
    def _get_error_patterns(self) -> List[str]:
        """Get application-specific error patterns"""
        patterns = {
            "wnc-steer": [
                r"steering.*failed", r"client.*disconnect", r"weak.*signal",
                r"steer_info.*error", r"sta_info.*error"
            ],
            "wnc-acs": [
                r"channel.*selection.*failed", r"interference.*high",
                r"scan.*failed", r"acs.*error"
            ],
            "wnc-tpyopt": [
                r"Build topology fail", r"optimization.*failed",
                r"scan.*timeout", r"topology.*error"
            ],
            "otbr-agent": [
                r"mesh.*error", r"beacon.*failed", r"network.*error",
                r"forwarder.*error", r"mle.*error"
            ]
        }
        return patterns.get(self.application_name, [])
    
    def _get_performance_patterns(self) -> Dict[str, List[str]]:
        """Get application-specific performance patterns"""
        patterns = {
            "wnc-steer": {
                "steering_latency": [r"steering.*latency.*(\d+)", r"steer.*time.*(\d+)"],
                "client_throughput": [r"throughput.*(\d+)", r"client.*rate.*(\d+)"]
            },
            "wnc-acs": {
                "channel_quality": [r"channel.*quality.*(\d+)", r"interference.*(\d+)"],
                "scan_duration": [r"scan.*duration.*(\d+)", r"scan.*time.*(\d+)"]
            },
            "wnc-tpyopt": {
                "optimization_time": [r"optimization.*time.*(\d+)", r"topology.*time.*(\d+)"],
                "scan_efficiency": [r"scan.*efficiency.*(\d+)", r"trigger.*rate.*(\d+)"]
            },
            "otbr-agent": {
                "message_latency": [r"message.*latency.*(\d+)", r"forward.*time.*(\d+)"],
                "network_health": [r"network.*health.*(\d+)", r"mesh.*quality.*(\d+)"]
            }
        }
        return patterns.get(self.application_name, {})
    
    def analyze_application(self, log_entries: List[LogEntry]) -> ApplicationAnalysisResult:
        """Analyze logs for a specific application
        
        NOTE: No time filtering is applied to keep analysis simple.
        All log entries for the application are included regardless of timestamp.
        """
        logger.info(f"Analyzing application: {self.application_name}")
        
        # Filter logs for this application only (no time filtering)
        app_logs = [log for log in log_entries if log.application == self.application_name]
        
        if not app_logs:
            logger.warning(f"No logs found for application: {self.application_name}")
            return self._create_empty_analysis()
        
        # Messages are already categorized during log extraction
        
        # Create application analysis result
        analysis = ApplicationAnalysisResult(
            application_name=self.application_name,
            container_id=self.container_id,
            functional_domain=self.functional_domain
        )
        
        # Analyze log volume and error rate
        analysis.log_volume = len(app_logs)
        analysis.error_rate = self._calculate_error_rate(app_logs)
        
        # Generate time series data
        analysis.time_series_data = self._generate_time_series(app_logs)
        
        # Detect anomalies
        analysis.anomalies = self._detect_anomalies(app_logs)
        
        # Generate predictions
        analysis.predictions = self._generate_predictions(app_logs)
        
        # Perform statistical analysis
        analysis.statistical_results = self._perform_statistical_analysis(app_logs)
        
        # Detect event patterns
        analysis.event_patterns = self._detect_event_patterns(app_logs)
        
        # Calculate correlations
        analysis.correlations = self._calculate_correlations(app_logs)
        
        # Generate insights and recommendations
        analysis.insights = self._generate_insights(app_logs)
        analysis.recommendations = self._generate_recommendations(app_logs)
        
        # Calculate health score
        analysis.health_score = self._calculate_health_score(app_logs)
        
        # Calculate performance metrics
        analysis.performance_metrics = self._calculate_performance_metrics(app_logs)
        
        logger.info(f"Analysis completed for {self.application_name}: {len(app_logs)} logs, {len(analysis.anomalies)} anomalies")
        return analysis
    
    def generate_time_sequence_preview(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """Generate time sequence preview for UI"""
        if not log_entries:
            return {
                "recentEvents": [],
                "eventCount": 0,
                "timeRange": {"start": None, "end": None}
            }
        
        # Ensure logs are sorted by timestamp for accurate time range calculation
        sorted_logs = sorted(log_entries, key=lambda x: x.timestamp)
        
        recent_events = []
        for i, entry in enumerate(sorted_logs[-10:]):  # Last 10 events
            recent_events.append({
                "id": f"{self.application_name}_{i}_{entry.timestamp.isoformat()}",
                "timestamp": entry.timestamp.isoformat(),
                "eventType": self._categorize_event(entry),
                "category": self._categorize_event(entry),  # Use same as eventType for now
                "severity": entry.log_level.value,
                "message": entry.message[:100],  # Truncate
                "metadata": {
                    "container_id": entry.container_id,
                    "application": entry.application,
                    "log_level": entry.log_level.value
                },
                "source": entry.application
            })
        
        return {
            "events": recent_events,  # Changed from "recentEvents" to "events"
            "eventCount": len(log_entries),
            "timeRange": {
                "start": sorted_logs[0].timestamp.isoformat() if sorted_logs else None,
                "end": sorted_logs[-1].timestamp.isoformat() if sorted_logs else None
            }
        }
    
    def _categorize_messages(self, log_entries: List[LogEntry]) -> None:
        """Pre-categorize messages for fast filtering"""
        for entry in log_entries:
            if entry.message_type is None:  # Only categorize if not already done
                entry.message_type = self._categorize_event(entry)
    
    def save_categorized_logs(self, log_entries: List[LogEntry], project_id: str) -> None:
        """Save logs with message_type field back to the filesystem"""
        logger.info(f"Saving categorized logs for {self.application_name}")
        
        # Get the logs file path
        logs_file = os.path.join(
            "data", "projects", project_id, "extracted", self.application_name, "logs.json"
        )
        
        if not os.path.exists(logs_file):
            logger.warning(f"Logs file not found: {logs_file}")
            return
        
        try:
            # Convert LogEntry objects to dictionaries with message_type
            logs_data = [entry.to_dict() for entry in log_entries]
            
            # Write back to the file
            with open(logs_file, 'w') as f:
                json.dump(logs_data, f, indent=2)
            
            logger.info(f"Saved {len(logs_data)} categorized logs to {logs_file}")
            
        except Exception as e:
            logger.error(f"Error saving categorized logs: {e}")
    
    def _categorize_event(self, entry: LogEntry) -> str:
        """Categorize event based on message content - matches frontend filter categories"""
        message = entry.message.lower()
        
        # Match frontend filter categories exactly
        if "steer" in message:
            if "request" in message or "enable" in message:
                return "steer-requests"
            elif "action" in message or "triggered" in message or "moved" in message:
                return "steer-actions"
            else:
                return "steer-requests"  # Default to steer-requests for any steering
        elif "rssi" in message or "rcpi" in message or "signal" in message or "weak" in message:
            return "monitoring"
        elif "load" in message or "balance" in message or "capacity" in message or "distribution" in message:
            return "optimization"
        elif "channel" in message:
            if "scan" in message:
                return "channel-scans"
            elif "change" in message:
                return "channel-changes"
            else:
                return "channel-management"
        elif "topology" in message:
            if "scan" in message:
                return "topology-scans"
            elif "change" in message:
                return "topology-changes"
            else:
                return "topology"
        elif "mesh" in message:
            return "mesh-messages"
        elif "beacon" in message:
            return "beacon-operations"
        elif "ipv6" in message:
            return "ipv6-traffic"
        
        return "general"
    
    def _create_empty_analysis(self) -> ApplicationAnalysisResult:
        """Create empty analysis result when no logs are found"""
        return ApplicationAnalysisResult(
            application_name=self.application_name,
            container_id=self.container_id,
            functional_domain=self.functional_domain
        )
    
    def _calculate_error_rate(self, logs: List[LogEntry]) -> float:
        """Calculate error rate for the application"""
        if not logs:
            return 0.0
        
        error_logs = [log for log in logs if log.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        return len(error_logs) / len(logs)
    
    def _generate_time_series(self, logs: List[LogEntry]) -> List[TimeSeriesData]:
        """Generate time series data for application-specific metrics"""
        time_series_data = []
        
        # Group logs by minute for time series analysis
        time_groups = defaultdict(list)
        for log in logs:
            # Round to minute for grouping
            minute_key = log.timestamp.replace(second=0, microsecond=0)
            time_groups[minute_key].append(log)
        
        # Generate time series for each metric pattern
        for metric_name, patterns in self.metric_patterns.items():
            data_points = []
            
            for timestamp, minute_logs in sorted(time_groups.items()):
                value = self._extract_metric_value(minute_logs, patterns)
                if value is not None:
                    data_points.append(TimeSeriesDataPoint(
                        timestamp=timestamp,
                        value=value
                    ))
            
            if data_points:
                time_series_data.append(TimeSeriesData(
                    metric_name=metric_name,
                    application=self.application_name,
                    data_points=data_points
                ))
        
        return time_series_data
    
    def _extract_metric_value(self, logs: List[LogEntry], patterns: List[str]) -> Optional[float]:
        """Extract metric value from logs using patterns"""
        for pattern in patterns:
            for log in logs:
                match = re.search(pattern, log.message, re.IGNORECASE)
                if match:
                    try:
                        # Try to extract numeric value
                        value_str = match.group(1) if match.groups() else match.group(0)
                        return float(value_str)
                    except (ValueError, IndexError):
                        # If not numeric, count occurrences
                        return 1.0
        return None
    
    def _detect_anomalies(self, logs: List[LogEntry]) -> List[AnomalyResult]:
        """Detect anomalies specific to this application"""
        anomalies = []
        
        # Error rate anomalies
        error_rate = self._calculate_error_rate(logs)
        if error_rate > 0.1:  # More than 10% errors
            anomalies.append(AnomalyResult(
                timestamp=logs[-1].timestamp if logs else datetime.now(),
                metric_name="error_rate",
                application=self.application_name,
                anomaly_type=AnomalyType.THRESHOLD_BASED,
                score=error_rate,
                severity="high" if error_rate > 0.2 else "medium",
                description=f"High error rate detected: {error_rate:.2%}",
                confidence=0.8
            ))
        
        # Pattern-based anomalies
        for error_pattern in self.error_patterns:
            error_count = sum(1 for log in logs if re.search(error_pattern, log.message, re.IGNORECASE))
            if error_count > 5:  # More than 5 errors of this type
                anomalies.append(AnomalyResult(
                    timestamp=logs[-1].timestamp if logs else datetime.now(),
                    metric_name="error_pattern",
                    application=self.application_name,
                    anomaly_type=AnomalyType.PATTERN_BASED,
                    score=error_count / len(logs),
                    severity="medium",
                    description=f"Multiple errors matching pattern: {error_pattern}",
                    confidence=0.7
                ))
        
        return anomalies
    
    def _generate_predictions(self, logs: List[LogEntry]) -> List[PredictionResult]:
        """Generate predictions for this application"""
        predictions = []
        
        # Simple trend-based predictions for key metrics
        for metric_name, patterns in self.metric_patterns.items():
            if len(logs) < 10:  # Need minimum data for predictions
                continue
            
            # Calculate trend
            recent_logs = logs[-10:]  # Last 10 logs
            trend = self._calculate_trend(recent_logs, patterns)
            
            if trend is not None:
                # Generate simple forecast
                forecast_data = []
                current_value = trend['current_value']
                
                for i in range(1, 6):  # 5 time steps ahead
                    predicted_value = current_value + (trend['slope'] * i)
                    forecast_data.append(ForecastDataPoint(
                        timestamp=logs[-1].timestamp + timedelta(minutes=i),
                        predicted_value=predicted_value,
                        lower_bound=predicted_value * 0.9,
                        upper_bound=predicted_value * 1.1,
                        confidence=0.6
                    ))
                
                predictions.append(PredictionResult(
                    metric_name=metric_name,
                    application=self.application_name,
                    forecast_type=ForecastType.TIME_SERIES,
                    algorithm="linear_trend",
                    forecast_data=forecast_data,
                    model_accuracy=0.6,
                    confidence_level=0.6,
                    forecast_horizon=5
                ))
        
        return predictions
    
    def _calculate_trend(self, logs: List[LogEntry], patterns: List[str]) -> Optional[Dict[str, float]]:
        """Calculate trend for a metric"""
        values = []
        for log in logs:
            value = self._extract_metric_value([log], patterns)
            if value is not None:
                values.append(value)
        
        if len(values) < 2:
            return None
        
        # Simple linear trend
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * val for i, val in enumerate(values))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        current_value = values[-1]
        
        return {
            'slope': slope,
            'current_value': current_value
        }
    
    def _perform_statistical_analysis(self, logs: List[LogEntry]) -> List[StatisticalResult]:
        """Perform statistical analysis for this application"""
        results = []
        
        for metric_name, patterns in self.metric_patterns.items():
            values = []
            for log in logs:
                value = self._extract_metric_value([log], patterns)
                if value is not None:
                    values.append(value)
            
            if len(values) < 3:  # Need minimum data for statistics
                continue
            
            # Calculate descriptive statistics
            mean_val = sum(values) / len(values)
            sorted_values = sorted(values)
            median_val = sorted_values[len(sorted_values) // 2]
            min_val = min(values)
            max_val = max(values)
            
            # Calculate variance and standard deviation
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            results.append(StatisticalResult(
                metric_name=metric_name,
                application=self.application_name,
                descriptive_statistics={
                    'mean': mean_val,
                    'median': median_val,
                    'min': min_val,
                    'max': max_val,
                    'std_dev': std_dev,
                    'variance': variance,
                    'count': len(values)
                },
                distribution_analysis={'type': 'unknown'},
                trend_analysis={'trend': 'stable'},
                outlier_analysis={'outliers': []},
                seasonality_analysis={'seasonal': False}
            ))
        
        return results
    
    def _detect_event_patterns(self, logs: List[LogEntry]) -> List[EventPattern]:
        """Detect event patterns specific to this application"""
        patterns = []
        
        # Look for repeated error patterns
        error_counts = Counter()
        for log in logs:
            if log.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                # Extract error type from message
                error_type = log.message.split()[0] if log.message else "unknown"
                error_counts[error_type] += 1
        
        # Create patterns for frequent errors
        for error_type, count in error_counts.most_common(3):
            if count > 2:  # More than 2 occurrences
                patterns.append(EventPattern(
                    pattern_type="error_repetition",
                    confidence=min(count / len(logs), 1.0),
                    events=[{'type': error_type, 'count': count}],
                    description=f"Repeated {error_type} errors: {count} occurrences"
                ))
        
        return patterns
    
    def _calculate_correlations(self, logs: List[LogEntry]) -> List[CorrelationResult]:
        """Calculate correlations between metrics for this application"""
        correlations = []
        
        # Get all metric values
        metric_values = {}
        for metric_name, patterns in self.metric_patterns.items():
            values = []
            for log in logs:
                value = self._extract_metric_value([log], patterns)
                if value is not None:
                    values.append(value)
            if len(values) > 1:
                metric_values[metric_name] = values
        
        # Calculate correlations between pairs of metrics
        metric_names = list(metric_values.keys())
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                metric1 = metric_names[i]
                metric2 = metric_names[j]
                
                # Simple correlation calculation
                correlation = self._calculate_correlation(
                    metric_values[metric1], 
                    metric_values[metric2]
                )
                
                if correlation is not None and abs(correlation) > 0.3:
                    correlations.append(CorrelationResult(
                        metric1=metric1,
                        metric2=metric2,
                        correlation_type="pearson",
                        strength=correlation,
                        confidence=0.7,
                        description=f"Correlation between {metric1} and {metric2}"
                    ))
        
        return correlations
    
    def _calculate_correlation(self, values1: List[float], values2: List[float]) -> Optional[float]:
        """Calculate Pearson correlation between two lists of values"""
        if len(values1) != len(values2) or len(values1) < 2:
            return None
        
        n = len(values1)
        sum1 = sum(values1)
        sum2 = sum(values2)
        sum1_sq = sum(x * x for x in values1)
        sum2_sq = sum(x * x for x in values2)
        sum_xy = sum(x * y for x, y in zip(values1, values2))
        
        numerator = n * sum_xy - sum1 * sum2
        denominator = ((n * sum1_sq - sum1 * sum1) * (n * sum2_sq - sum2 * sum2)) ** 0.5
        
        if denominator == 0:
            return None
        
        return numerator / denominator
    
    def _generate_insights(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Generate insights specific to this application"""
        # Ensure logs are sorted by timestamp for accurate time range calculation
        sorted_logs = sorted(logs, key=lambda x: x.timestamp)
        
        insights = {
            'log_volume': len(logs),
            'error_rate': self._calculate_error_rate(logs),
            'time_range': {
                'start': sorted_logs[0].timestamp.isoformat() if sorted_logs else None,
                'end': sorted_logs[-1].timestamp.isoformat() if sorted_logs else None
            },
            'log_level_distribution': self._get_log_level_distribution(logs),
            'peak_activity_hour': self._find_peak_activity_hour(logs)
        }
        
        return insights
    
    def _get_log_level_distribution(self, logs: List[LogEntry]) -> Dict[str, int]:
        """Get distribution of log levels"""
        distribution = defaultdict(int)
        for log in logs:
            distribution[log.log_level.value] += 1
        return dict(distribution)
    
    def _find_peak_activity_hour(self, logs: List[LogEntry]) -> Optional[int]:
        """Find hour with peak activity"""
        if not logs:
            return None
        
        hour_counts = defaultdict(int)
        for log in logs:
            hour_counts[log.timestamp.hour] += 1
        
        return max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None
    
    def _generate_recommendations(self, logs: List[LogEntry]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        error_rate = self._calculate_error_rate(logs)
        if error_rate > 0.1:
            recommendations.append(f"High error rate ({error_rate:.1%}) detected. Review application configuration and check for system issues.")
        
        if len(logs) < 100:
            recommendations.append("Limited log data available. Consider collecting more logs for better analysis.")
        
        # Application-specific recommendations
        if self.application_name == "wnc-steer":
            if any("weak signal" in log.message.lower() for log in logs):
                recommendations.append("Weak signal clients detected. Consider adjusting steering thresholds or improving signal coverage.")
        
        elif self.application_name == "wnc-acs":
            if any("interference" in log.message.lower() for log in logs):
                recommendations.append("Interference detected. Consider channel optimization or interference mitigation strategies.")
        
        elif self.application_name == "wnc-tpyopt":
            if any("Build topology fail" in log.message for log in logs):
                recommendations.append("Topology build failures detected. Review network topology and connectivity.")
        
        elif self.application_name == "otbr-agent":
            if any("mesh.*error" in log.message.lower() for log in logs):
                recommendations.append("Mesh network errors detected. Check mesh connectivity and node health.")
        
        return recommendations
    
    def _calculate_health_score(self, logs: List[LogEntry]) -> float:
        """Calculate overall health score for the application"""
        if not logs:
            return 0.0
        
        # Base score starts at 100
        score = 100.0
        
        # Deduct points for errors
        error_rate = self._calculate_error_rate(logs)
        score -= error_rate * 50  # Up to 50 points for errors
        
        # Deduct points for critical errors
        critical_count = sum(1 for log in logs if log.log_level == LogLevel.CRITICAL)
        score -= critical_count * 10  # 10 points per critical error
        
        # Deduct points for low log volume (might indicate issues)
        if len(logs) < 50:
            score -= 20
        
        return max(0.0, min(100.0, score))
    
    def _calculate_performance_metrics(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Calculate performance metrics for this application"""
        metrics = {}
        
        # Calculate metrics based on performance patterns
        for metric_name, patterns in self.performance_patterns.items():
            values = []
            for log in logs:
                value = self._extract_metric_value([log], patterns)
                if value is not None:
                    values.append(value)
            
            if values:
                metrics[metric_name] = {
                    'current': values[-1] if values else 0,
                    'average': sum(values) / len(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0
                }
        
        return metrics
