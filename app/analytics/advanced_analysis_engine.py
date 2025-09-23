"""
Advanced Analysis Engine

This module provides comprehensive log analysis capabilities including
time series processing, event correlation, anomaly detection, predictive analytics,
and statistical analysis.
"""

import logging
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..models.core import (
    AnalysisResult, TimeSeriesData, EventPattern, CorrelationResult,
    AnomalyResult, PredictionResult, StatisticalResult, AnomalyType, ForecastType
)
from .time_series_processor import TimeSeriesProcessor
from .anomaly_detector import AnomalyDetector, AnomalyConfig, AnomalyAlgorithm
from .predictive_analytics import PredictiveAnalytics, ForecastConfig, ForecastAlgorithm
from .statistical_analyzer import StatisticalAnalyzer, StatisticalConfig
from ..core.config import get_settings

logger = logging.getLogger(__name__)

@dataclass
class AnalysisConfig:
    """Configuration for analysis engine"""
    # Time series configuration
    time_bin_size_minutes: int = 5
    metrics_to_analyze: List[str] = None
    
    # Anomaly detection configuration
    anomaly_algorithm: AnomalyAlgorithm = AnomalyAlgorithm.ISOLATION_FOREST
    anomaly_contamination: float = 0.1
    
    # Predictive analytics configuration
    forecast_algorithm: ForecastAlgorithm = ForecastAlgorithm.LINEAR_REGRESSION
    forecast_horizon: int = 24
    
    # Statistical analysis configuration
    confidence_level: float = 0.95
    outlier_threshold: float = 3.0
    
    def __post_init__(self):
        if self.metrics_to_analyze is None:
            self.metrics_to_analyze = ['count', 'error_count', 'warning_count', 'unique_applications']

class AdvancedAnalysisEngine:
    """
    Advanced analysis engine that integrates all analytics components.
    
    Provides:
    - Time series processing and analysis
    - Event correlation and pattern detection
    - Machine learning-based anomaly detection
    - Predictive analytics and forecasting
    - Comprehensive statistical analysis
    """
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize the advanced analysis engine"""
        self.config = config or AnalysisConfig()
        self.settings = get_settings()
        
        # Initialize components
        self.time_series_processor = TimeSeriesProcessor()
        
        # Phase 3: Advanced Analytics Components
        self.anomaly_detector = AnomalyDetector(
            AnomalyConfig(
                algorithm=self.config.anomaly_algorithm,
                contamination=self.config.anomaly_contamination
            )
        )
        
        self.predictive_analytics = PredictiveAnalytics(
            ForecastConfig(
                algorithm=self.config.forecast_algorithm,
                forecast_horizon=self.config.forecast_horizon
            )
        )
        
        self.statistical_analyzer = StatisticalAnalyzer(
            StatisticalConfig(
                confidence_level=self.config.confidence_level,
                outlier_threshold=self.config.outlier_threshold
            )
        )
        
        logger.info("Advanced Analysis Engine initialized with all components")
    
    def analyze_project(self, project_name: str, log_entries: List[Dict[str, Any]]) -> AnalysisResult:
        """
        Perform comprehensive analysis on a project.
        
        Args:
            project_name: Name of the project to analyze
            log_entries: List of log entries to analyze
            
        Returns:
            Complete analysis result
        """
        logger.info(f"Starting comprehensive analysis for project: {project_name}")
        
        # Generate analysis ID
        analysis_id = f"analysis_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Phase 1 & 2: Basic Analysis
            logger.info("Generating analysis summary")
            summary = self._generate_summary(log_entries)
            
            logger.info("Generating time series data")
            time_series_data = self._generate_time_series_data(log_entries)
            
            logger.info("Finding event patterns")
            event_patterns = self._find_event_patterns(log_entries)
            
            logger.info("Finding event correlations")
            correlations = self._find_event_correlations(time_series_data)
            
            # Phase 3: Advanced Analytics
            logger.info("Detecting anomalies")
            anomalies = self._detect_anomalies(time_series_data)
            
            logger.info("Generating predictions")
            predictions = self._generate_predictions(time_series_data)
            
            logger.info("Performing statistical analysis")
            statistical_results = self._perform_statistical_analysis(time_series_data)
            
            # Generate insights and recommendations
            logger.info("Generating application insights")
            application_insights = self._generate_application_insights(log_entries, anomalies, predictions)
            
            logger.info("Generating system insights")
            system_insights = self._generate_system_insights(summary, anomalies, predictions, statistical_results)
            
            logger.info("Generating recommendations")
            recommendations = self._generate_recommendations(anomalies, predictions, statistical_results)
            
            # Create analysis result
            result = AnalysisResult(
                analysis_id=analysis_id,
                project_name=project_name,
                summary=summary,
                time_series_data=time_series_data,
                event_patterns=event_patterns,
                correlations=correlations,
                anomalies=anomalies,
                predictions=predictions,
                statistical_results=statistical_results,
                recommendations=recommendations,
                application_insights=application_insights,
                system_insights=system_insights
            )
            
            # Save models for future use
            self.anomaly_detector.save_models(project_name)
            
            logger.info(f"Analysis completed: {analysis_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            raise
    
    def _generate_summary(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic summary statistics"""
        if not log_entries:
            return {}
        
        total_entries = len(log_entries)
        applications = set(entry.get('application', 'unknown') for entry in log_entries)
        
        # Count by log level
        level_counts = {}
        for entry in log_entries:
            level = entry.get('log_level', 'unknown')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Calculate error rate
        error_count = level_counts.get('error', 0) + level_counts.get('critical', 0)
        error_rate = (error_count / total_entries * 100) if total_entries > 0 else 0
        
        # Calculate system health score
        health_score = max(0, 100 - error_rate)
        
        return {
            'total_entries': total_entries,
            'unique_applications': len(applications),
            'applications': list(applications),
            'level_distribution': level_counts,
            'error_rate': error_rate,
            'system_health_score': health_score,
            'time_range': {
                'start': min(entry.get('timestamp', datetime.now()) for entry in log_entries),
                'end': max(entry.get('timestamp', datetime.now()) for entry in log_entries)
            }
        }
    
    def _generate_time_series_data(self, log_entries: List[Dict[str, Any]]) -> List[TimeSeriesData]:
        """Generate time series data for analysis"""
        if not log_entries:
            return []
        
        # Convert log entries to time series data
        time_series_data = []
        
        for metric in self.config.metrics_to_analyze:
            try:
                ts_data = self.time_series_processor.create_time_series(
                    log_entries, metric, "system"
                )
                if ts_data:
                    time_series_data.append(ts_data)
            except Exception as e:
                logger.error(f"Error creating time series for {metric}: {e}")
                continue
        
        return time_series_data
    
    def _find_event_patterns(self, log_entries: List[Dict[str, Any]]) -> List[EventPattern]:
        """Find patterns in log events"""
        if not log_entries:
            return []
        
        try:
            patterns = self.time_series_processor.find_event_patterns(log_entries)
            return patterns
        except Exception as e:
            logger.error(f"Error finding event patterns: {e}")
            return []
    
    def _find_event_correlations(self, time_series_data: List[TimeSeriesData]) -> List[CorrelationResult]:
        """Find correlations between different metrics"""
        if len(time_series_data) < 2:
            return []
        
        try:
            correlations = self.time_series_processor.find_event_correlations(time_series_data)
            return correlations
        except Exception as e:
            logger.error(f"Error finding correlations: {e}")
            return []
    
    def _detect_anomalies(self, time_series_data: List[TimeSeriesData]) -> List[AnomalyResult]:
        """Detect anomalies in time series data"""
        if not time_series_data:
            return []
        
        try:
            anomalies = self.anomaly_detector.detect_anomalies(time_series_data)
            return anomalies
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def _generate_predictions(self, time_series_data: List[TimeSeriesData]) -> List[PredictionResult]:
        """Generate predictions for time series data"""
        if not time_series_data:
            return []
        
        try:
            predictions = self.predictive_analytics.generate_forecasts(time_series_data)
            return predictions
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return []
    
    def _perform_statistical_analysis(self, time_series_data: List[TimeSeriesData]) -> List[StatisticalResult]:
        """Perform comprehensive statistical analysis"""
        if not time_series_data:
            return []
        
        try:
            # Analyze each time series individually
            statistical_results = []
            for ts_data in time_series_data:
                try:
                    result = self.statistical_analyzer.comprehensive_analysis(ts_data)
                    statistical_results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing {ts_data.metric_name}: {e}")
                    continue
            
            return statistical_results
        except Exception as e:
            logger.error(f"Error performing statistical analysis: {e}")
            return []
    
    def _generate_application_insights(self, log_entries: List[Dict[str, Any]], 
                                     anomalies: List[AnomalyResult],
                                     predictions: List[PredictionResult]) -> Dict[str, Dict[str, Any]]:
        """Generate insights for each application"""
        insights = {}
        
        # Group log entries by application
        app_entries = {}
        for entry in log_entries:
            app = entry.get('application', 'unknown')
            if app not in app_entries:
                app_entries[app] = []
            app_entries[app].append(entry)
        
        # Generate insights for each application
        for app, entries in app_entries.items():
            app_insights = {
                'total_entries': len(entries),
                'error_rate': 0.0,
                'anomaly_count': 0,
                'prediction_count': 0,
                'health_status': 'healthy'
            }
            
            # Calculate error rate
            error_count = sum(1 for entry in entries if entry.get('log_level') in ['error', 'critical'])
            app_insights['error_rate'] = (error_count / len(entries) * 100) if entries else 0
            
            # Count anomalies for this application
            app_anomalies = [a for a in anomalies if a.application == app]
            app_insights['anomaly_count'] = len(app_anomalies)
            
            # Count predictions for this application
            app_predictions = [p for p in predictions if p.application == app]
            app_insights['prediction_count'] = len(app_predictions)
            
            # Determine health status
            if app_insights['error_rate'] > 10 or app_insights['anomaly_count'] > 5:
                app_insights['health_status'] = 'warning'
            elif app_insights['error_rate'] > 20 or app_insights['anomaly_count'] > 10:
                app_insights['health_status'] = 'critical'
            
            insights[app] = app_insights
        
        return insights
    
    def _generate_system_insights(self, summary: Dict[str, Any], 
                                 anomalies: List[AnomalyResult],
                                 predictions: List[PredictionResult],
                                 statistical_results: List[StatisticalResult]) -> Dict[str, Any]:
        """Generate system-wide insights"""
        insights = {
            'overall_health': summary.get('system_health_score', 0),
            'anomaly_summary': {},
            'prediction_summary': {},
            'statistical_summary': {},
            'trends': {},
            'recommendations': []
        }
        
        # Anomaly summary
        if anomalies:
            anomaly_summary = self.anomaly_detector.get_anomaly_summary(anomalies)
            insights['anomaly_summary'] = anomaly_summary
        
        # Prediction summary
        if predictions:
            prediction_summary = self.predictive_analytics.get_forecast_summary(predictions)
            insights['prediction_summary'] = prediction_summary
        
        # Statistical summary
        if statistical_results:
            insights['statistical_summary'] = {
                'total_series_analyzed': len(statistical_results),
                'distributions_found': {},
                'trends_detected': {},
                'outliers_found': sum(len(stat.outlier_analysis.get('outlier_values', [])) 
                                    for stat in statistical_results)
            }
        
        return insights
    
    def _generate_recommendations(self, anomalies: List[AnomalyResult],
                                predictions: List[PredictionResult],
                                statistical_results: List[StatisticalResult]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Anomaly-based recommendations
        if anomalies:
            high_severity_anomalies = [a for a in anomalies if a.severity == 'high']
            if high_severity_anomalies:
                recommendations.append(
                    f"Investigate {len(high_severity_anomalies)} high-severity anomalies "
                    f"detected in the system"
                )
        
        # Prediction-based recommendations
        if predictions:
            avg_accuracy = sum(p.model_accuracy for p in predictions) / len(predictions)
            if avg_accuracy < 0.7:
                recommendations.append(
                    "Consider improving prediction models as average accuracy is below 70%"
                )
        
        # Statistical-based recommendations
        if statistical_results:
            for stat in statistical_results:
                trend = stat.trend_analysis.get('trend_direction', '')
                if trend == 'increasing' and stat.trend_analysis.get('is_significant', False):
                    recommendations.append(
                        f"Monitor {stat.metric_name} for {stat.application} as it shows "
                        f"a significant increasing trend"
                    )
        
        if not recommendations:
            recommendations.append("System appears to be operating normally")
        
        return recommendations
    
    def save_analysis_result(self, result: AnalysisResult, output_path: str):
        """Save analysis result to file"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Analysis result saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving analysis result: {e}")
            raise
    
    def load_analysis_result(self, file_path: str) -> AnalysisResult:
        """Load analysis result from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert back to AnalysisResult object
            # This is a simplified version - in practice, you'd need proper deserialization
            return AnalysisResult(**data)
            
        except Exception as e:
            logger.error(f"Error loading analysis result: {e}")
            raise
