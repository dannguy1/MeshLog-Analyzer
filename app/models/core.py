# prplOS LCM Log Analysis System - Core Data Models

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
import json

class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class PackageStatus(Enum):
    """Package processing status"""
    CREATED = "created"
    UPLOADING = "uploading"
    EXTRACTING = "extracting"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisStatus(Enum):
    """Analysis job status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Phase 3: Advanced Analytics Enums
class AnomalyType(Enum):
    """Types of anomalies"""
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"
    PATTERN_BASED = "pattern_based"
    THRESHOLD_BASED = "threshold_based"

class ForecastType(Enum):
    """Types of forecasting"""
    TIME_SERIES = "time_series"
    REGRESSION = "regression"
    CLASSIFICATION = "classification"

class DistributionType(Enum):
    """Types of statistical distributions"""
    NORMAL = "normal"
    POISSON = "poisson"
    EXPONENTIAL = "exponential"
    GAMMA = "gamma"
    UNIFORM = "uniform"
    UNKNOWN = "unknown"

@dataclass
class LogEntry:
    """Individual log entry from syslog"""
    timestamp: datetime
    container_id: str
    application: str
    log_level: LogLevel
    message: str
    message_type: Optional[str] = None  # Pre-categorized message type for fast filtering
    structured_data: Optional[Dict[str, Any]] = None
    raw_line: str = ""
    line_number: int = 0
    file_path: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "container_id": self.container_id,
            "application": self.application,
            "log_level": self.log_level.value,
            "message": self.message,
            "message_type": self.message_type,
            "structured_data": self.structured_data,
            "raw_line": self.raw_line,
            "line_number": self.line_number,
            "file_path": self.file_path
        }

@dataclass
class PackageMetadata:
    """Metadata for containerized syslog package"""
    package_id: UUID = field(default_factory=uuid4)
    original_filename: str = ""
    file_size_bytes: int = 0
    upload_timestamp: datetime = field(default_factory=datetime.now)
    extraction_path: str = ""
    total_containers: int = 0
    total_log_files: int = 0
    total_log_size_bytes: int = 0
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    applications_detected: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "package_id": str(self.package_id),
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "upload_timestamp": self.upload_timestamp.isoformat(),
            "extraction_path": self.extraction_path,
            "total_containers": self.total_containers,
            "total_log_files": self.total_log_files,
            "total_log_size_bytes": self.total_log_size_bytes,
            "time_range_start": self.time_range_start.isoformat() if self.time_range_start else None,
            "time_range_end": self.time_range_end.isoformat() if self.time_range_end else None,
            "applications_detected": self.applications_detected
        }

@dataclass
class ContainerInfo:
    """Information about a container in the package"""
    container_id: str
    application_name: str
    functional_domain: str
    relative_path: str
    log_file_count: int = 0
    total_log_size_bytes: int = 0
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    confidence_score: float = 0.0
    log_files: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "container_id": self.container_id,
            "application_name": self.application_name,
            "functional_domain": self.functional_domain,
            "relative_path": self.relative_path,
            "log_file_count": self.log_file_count,
            "total_log_size_bytes": self.total_log_size_bytes,
            "time_range_start": self.time_range_start.isoformat() if self.time_range_start else None,
            "time_range_end": self.time_range_end.isoformat() if self.time_range_end else None,
            "confidence_score": self.confidence_score,
            "log_files": self.log_files
        }

@dataclass
class PackageStructure:
    """Complete structure of a containerized syslog package"""
    metadata: PackageMetadata
    containers: List[ContainerInfo]
    status: PackageStatus
    validation_errors: List[str] = field(default_factory=list)
    processing_errors: List[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Check if package structure is valid"""
        return len(self.validation_errors) == 0
    
    @property
    def total_log_entries(self) -> int:
        """Calculate total log entries across all containers"""
        return sum(container.log_file_count for container in self.containers)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "metadata": self.metadata.to_dict(),
            "containers": [container.to_dict() for container in self.containers],
            "status": self.status.value,
            "validation_errors": self.validation_errors,
            "processing_errors": self.processing_errors,
            "is_valid": self.is_valid,
            "total_log_entries": self.total_log_entries
        }

@dataclass
class ApplicationInfo:
    """Detailed information about a detected application"""
    application_name: str
    container_id: str
    functional_domain: str
    description: str
    version: Optional[str] = None
    configuration_files: List[str] = field(default_factory=list)
    log_patterns: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "application_name": self.application_name,
            "container_id": self.container_id,
            "functional_domain": self.functional_domain,
            "description": self.description,
            "version": self.version,
            "configuration_files": self.configuration_files,
            "log_patterns": self.log_patterns,
            "dependencies": self.dependencies,
            "metrics": self.metrics
        }

# Phase 3: Advanced Analytics Models
@dataclass
class TimeSeriesDataPoint:
    """A single data point in a time series"""
    timestamp: datetime
    value: float
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "metadata": self.metadata
        }

@dataclass
class TimeSeriesData:
    """Time series data for a specific metric"""
    metric_name: str
    application: str
    data_points: List[TimeSeriesDataPoint]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "metric_name": self.metric_name,
            "application": self.application,
            "data_points": [point.to_dict() for point in self.data_points],
            "metadata": self.metadata
        }

@dataclass
class EventPattern:
    """Pattern of events detected in logs"""
    pattern_type: str
    confidence: float
    events: List[Dict[str, Any]]
    time_window: Optional[datetime] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "pattern_type": self.pattern_type,
            "confidence": self.confidence,
            "events": self.events,
            "time_window": self.time_window.isoformat() if self.time_window else None,
            "description": self.description
        }

@dataclass
class CorrelationResult:
    """Correlation between two metrics"""
    metric1: str
    metric2: str
    correlation_type: str
    strength: float
    confidence: float
    p_value: Optional[float] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "metric1": self.metric1,
            "metric2": self.metric2,
            "correlation_type": self.correlation_type,
            "strength": self.strength,
            "confidence": self.confidence,
            "p_value": self.p_value,
            "description": self.description
        }

@dataclass
class AnomalyResult:
    """Result of anomaly detection"""
    timestamp: datetime
    metric_name: str
    application: str
    anomaly_type: AnomalyType
    score: float
    severity: str  # "low", "medium", "high"
    description: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_name": self.metric_name,
            "application": self.application,
            "anomaly_type": self.anomaly_type.value,
            "score": self.score,
            "severity": self.severity,
            "description": self.description,
            "confidence": self.confidence,
            "metadata": self.metadata
        }

@dataclass
class ForecastDataPoint:
    """A single forecast data point"""
    timestamp: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "predicted_value": self.predicted_value,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "confidence": self.confidence
        }

@dataclass
class PredictionResult:
    """Result of predictive analytics"""
    metric_name: str
    application: str
    forecast_type: ForecastType
    algorithm: str
    forecast_data: List[ForecastDataPoint]
    model_accuracy: float
    confidence_level: float
    forecast_horizon: int
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "metric_name": self.metric_name,
            "application": self.application,
            "forecast_type": self.forecast_type.value,
            "algorithm": self.algorithm,
            "forecast_data": [point.to_dict() for point in self.forecast_data],
            "model_accuracy": self.model_accuracy,
            "confidence_level": self.confidence_level,
            "forecast_horizon": self.forecast_horizon,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class StatisticalResult:
    """Result of statistical analysis"""
    metric_name: str
    application: str
    descriptive_statistics: Dict[str, Any]
    distribution_analysis: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    outlier_analysis: Dict[str, Any]
    seasonality_analysis: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "metric_name": self.metric_name,
            "application": self.application,
            "descriptive_statistics": self.descriptive_statistics,
            "distribution_analysis": self.distribution_analysis,
            "trend_analysis": self.trend_analysis,
            "outlier_analysis": self.outlier_analysis,
            "seasonality_analysis": self.seasonality_analysis,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }

# NEW: Application-Specific Analysis Models
@dataclass
class ApplicationAnalysisMetadata:
    """Metadata for application-specific analysis results"""
    application_name: str
    analysis_id: str
    project_id: str
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    status: str = "completed"  # completed, failed, in_progress
    log_volume: int = 0
    error_rate: float = 0.0
    health_score: float = 0.0
    analysis_config_hash: str = ""  # Hash of analysis configuration to detect changes
    data_hash: str = ""  # Hash of source data to detect changes
    result_file_path: str = ""  # Path to the detailed analysis results
    metadata_file_path: str = ""  # Path to this metadata file
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "application_name": self.application_name,
            "analysis_id": self.analysis_id,
            "project_id": self.project_id,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "status": self.status,
            "log_volume": self.log_volume,
            "error_rate": self.error_rate,
            "health_score": self.health_score,
            "analysis_config_hash": self.analysis_config_hash,
            "data_hash": self.data_hash,
            "result_file_path": self.result_file_path,
            "metadata_file_path": self.metadata_file_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApplicationAnalysisMetadata':
        """Create from dictionary"""
        return cls(
            application_name=data["application_name"],
            analysis_id=data["analysis_id"],
            project_id=data["project_id"],
            analysis_timestamp=datetime.fromisoformat(data["analysis_timestamp"]),
            status=data["status"],
            log_volume=data["log_volume"],
            error_rate=data["error_rate"],
            health_score=data["health_score"],
            analysis_config_hash=data["analysis_config_hash"],
            data_hash=data["data_hash"],
            result_file_path=data["result_file_path"],
            metadata_file_path=data["metadata_file_path"]
        )

@dataclass
class ApplicationAnalysisResult:
    """Result of analysis for a specific application"""
    application_name: str
    container_id: str
    functional_domain: str
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    # Application-specific metrics and insights
    log_volume: int = 0
    error_rate: float = 0.0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    health_score: float = 0.0
    
    # Time series data specific to this application
    time_series_data: List[TimeSeriesData] = field(default_factory=list)
    
    # Application-specific patterns
    event_patterns: List[EventPattern] = field(default_factory=list)
    
    # Application-specific anomalies
    anomalies: List[AnomalyResult] = field(default_factory=list)
    
    # Application-specific predictions
    predictions: List[PredictionResult] = field(default_factory=list)
    
    # Application-specific statistics
    statistical_results: List[StatisticalResult] = field(default_factory=list)
    
    # Application-specific correlations (within the app)
    correlations: List[CorrelationResult] = field(default_factory=list)
    
    # Application-specific insights
    insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    # Time sequence preview for UI
    time_sequence_preview: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "application_name": self.application_name,
            "container_id": self.container_id,
            "functional_domain": self.functional_domain,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "log_volume": self.log_volume,
            "error_rate": self.error_rate,
            "performance_metrics": self.performance_metrics,
            "health_score": self.health_score,
            "time_series_data": [ts.to_dict() if hasattr(ts, 'to_dict') else ts for ts in self.time_series_data],
            "event_patterns": [pattern.to_dict() if hasattr(pattern, 'to_dict') else pattern for pattern in self.event_patterns],
            "anomalies": [anomaly.to_dict() if hasattr(anomaly, 'to_dict') else anomaly for anomaly in self.anomalies],
            "predictions": [pred.to_dict() if hasattr(pred, 'to_dict') else pred for pred in self.predictions],
            "statistical_results": [stat.to_dict() if hasattr(stat, 'to_dict') else stat for stat in self.statistical_results],
            "correlations": [corr.to_dict() if hasattr(corr, 'to_dict') else corr for corr in self.correlations],
            "insights": self.insights,
            "recommendations": self.recommendations,
            "time_sequence_preview": self.time_sequence_preview
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApplicationAnalysisResult':
        """Create ApplicationAnalysisResult instance from dictionary"""
        # Handle timestamp conversion
        analysis_timestamp = data.get("analysis_timestamp")
        if isinstance(analysis_timestamp, str):
            analysis_timestamp = datetime.fromisoformat(analysis_timestamp)
        elif analysis_timestamp is None:
            analysis_timestamp = datetime.now()
        
        # Convert time_series_data
        time_series_data = []
        if "time_series_data" in data and isinstance(data["time_series_data"], list):
            for ts_data in data["time_series_data"]:
                if isinstance(ts_data, dict):
                    try:
                        # Convert data_points
                        data_points = []
                        if "data_points" in ts_data and isinstance(ts_data["data_points"], list):
                            for dp in ts_data["data_points"]:
                                if isinstance(dp, dict):
                                    data_points.append(TimeSeriesDataPoint(
                                        timestamp=datetime.fromisoformat(dp["timestamp"]) if isinstance(dp.get("timestamp"), str) else dp.get("timestamp"),
                                        value=dp.get("value", 0.0),
                                        metadata=dp.get("metadata")
                                    ))
                        
                        time_series_data.append(TimeSeriesData(
                            metric_name=ts_data.get("metric_name", ""),
                            application=ts_data.get("application", ""),
                            data_points=data_points,
                            metadata=ts_data.get("metadata")
                        ))
                    except Exception as e:
                        print(f"Warning: Failed to convert time series data: {e}")
                        continue
        
        # Convert event_patterns
        event_patterns = []
        if "event_patterns" in data and isinstance(data["event_patterns"], list):
            for pattern_data in data["event_patterns"]:
                if isinstance(pattern_data, dict):
                    try:
                        event_patterns.append(EventPattern(
                            pattern_type=pattern_data.get("pattern_type", ""),
                            confidence=pattern_data.get("confidence", 0.0),
                            events=pattern_data.get("events", []),
                            time_window=datetime.fromisoformat(pattern_data["time_window"]) if pattern_data.get("time_window") and isinstance(pattern_data["time_window"], str) else pattern_data.get("time_window"),
                            description=pattern_data.get("description")
                        ))
                    except Exception as e:
                        print(f"Warning: Failed to convert event pattern: {e}")
                        continue
        
        # Convert anomalies
        anomalies = []
        if "anomalies" in data and isinstance(data["anomalies"], list):
            for anomaly_data in data["anomalies"]:
                if isinstance(anomaly_data, dict):
                    try:
                        anomalies.append(AnomalyResult(
                            timestamp=datetime.fromisoformat(anomaly_data["timestamp"]) if isinstance(anomaly_data.get("timestamp"), str) else anomaly_data.get("timestamp"),
                            metric_name=anomaly_data.get("metric_name", ""),
                            application=anomaly_data.get("application", ""),
                            anomaly_type=AnomalyType(anomaly_data.get("anomaly_type", "pattern_based")),
                            score=anomaly_data.get("score", 0.0),
                            severity=anomaly_data.get("severity", "low"),
                            description=anomaly_data.get("description", ""),
                            confidence=anomaly_data.get("confidence", 0.0),
                            metadata=anomaly_data.get("metadata")
                        ))
                    except Exception as e:
                        print(f"Warning: Failed to convert anomaly: {e}")
                        continue
        
        # Convert predictions
        predictions = []
        if "predictions" in data and isinstance(data["predictions"], list):
            for pred_data in data["predictions"]:
                if isinstance(pred_data, dict):
                    try:
                        # Convert forecast_data
                        forecast_data = []
                        if "forecast_data" in pred_data and isinstance(pred_data["forecast_data"], list):
                            for fd in pred_data["forecast_data"]:
                                if isinstance(fd, dict):
                                    forecast_data.append(ForecastDataPoint(
                                        timestamp=datetime.fromisoformat(fd["timestamp"]) if isinstance(fd.get("timestamp"), str) else fd.get("timestamp"),
                                        predicted_value=fd.get("predicted_value", 0.0),
                                        lower_bound=fd.get("lower_bound", 0.0),
                                        upper_bound=fd.get("upper_bound", 0.0),
                                        confidence=fd.get("confidence", 0.0)
                                    ))
                        
                        predictions.append(PredictionResult(
                            metric_name=pred_data.get("metric_name", ""),
                            application=pred_data.get("application", ""),
                            forecast_type=ForecastType(pred_data.get("forecast_type", "time_series")),
                            algorithm=pred_data.get("algorithm", ""),
                            forecast_data=forecast_data,
                            model_accuracy=pred_data.get("model_accuracy", 0.0),
                            confidence_level=pred_data.get("confidence_level", 0.0),
                            forecast_horizon=pred_data.get("forecast_horizon", 0),
                            created_at=datetime.fromisoformat(pred_data["created_at"]) if pred_data.get("created_at") and isinstance(pred_data["created_at"], str) else pred_data.get("created_at"),
                            metadata=pred_data.get("metadata")
                        ))
                    except Exception as e:
                        print(f"Warning: Failed to convert prediction: {e}")
                        continue
        
        # Convert statistical_results
        statistical_results = []
        if "statistical_results" in data and isinstance(data["statistical_results"], list):
            for stat_data in data["statistical_results"]:
                if isinstance(stat_data, dict):
                    try:
                        statistical_results.append(StatisticalResult(
                            metric_name=stat_data.get("metric_name", ""),
                            application=stat_data.get("application", ""),
                            descriptive_statistics=stat_data.get("descriptive_statistics", {}),
                            distribution_analysis=stat_data.get("distribution_analysis", {}),
                            trend_analysis=stat_data.get("trend_analysis", {}),
                            outlier_analysis=stat_data.get("outlier_analysis", {}),
                            seasonality_analysis=stat_data.get("seasonality_analysis", {}),
                            created_at=datetime.fromisoformat(stat_data["created_at"]) if stat_data.get("created_at") and isinstance(stat_data["created_at"], str) else stat_data.get("created_at"),
                            metadata=stat_data.get("metadata")
                        ))
                    except Exception as e:
                        print(f"Warning: Failed to convert statistical result: {e}")
                        continue
        
        # Convert correlations
        correlations = []
        if "correlations" in data and isinstance(data["correlations"], list):
            for corr_data in data["correlations"]:
                if isinstance(corr_data, dict):
                    try:
                        correlations.append(CorrelationResult(
                            metric1=corr_data.get("metric1", ""),
                            metric2=corr_data.get("metric2", ""),
                            correlation_type=corr_data.get("correlation_type", ""),
                            strength=corr_data.get("strength", 0.0),
                            confidence=corr_data.get("confidence", 0.0),
                            p_value=corr_data.get("p_value"),
                            description=corr_data.get("description")
                        ))
                    except Exception as e:
                        print(f"Warning: Failed to convert correlation: {e}")
                        continue
        
        return cls(
            application_name=data.get("application_name", ""),
            container_id=data.get("container_id", ""),
            functional_domain=data.get("functional_domain", ""),
            analysis_timestamp=analysis_timestamp,
            log_volume=data.get("log_volume", 0),
            error_rate=data.get("error_rate", 0.0),
            performance_metrics=data.get("performance_metrics", {}),
            health_score=data.get("health_score", 0.0),
            time_series_data=time_series_data,
            event_patterns=event_patterns,
            anomalies=anomalies,
            predictions=predictions,
            statistical_results=statistical_results,
            correlations=correlations,
            insights=data.get("insights", {}),
            recommendations=data.get("recommendations", []),
            time_sequence_preview=data.get("time_sequence_preview", {})
        )

@dataclass
class AnalysisResult:
    """Result of log analysis - now application-specific"""
    analysis_id: str
    project_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Project-level summary
    summary: Dict[str, Any] = field(default_factory=dict)
    
    # Application-specific analysis results
    application_analyses: Dict[str, ApplicationAnalysisResult] = field(default_factory=dict)
    
    # Cross-application correlations and insights
    cross_application_correlations: List[CorrelationResult] = field(default_factory=list)
    system_insights: Dict[str, Any] = field(default_factory=dict)
    
    # Legacy fields for backward compatibility
    time_series_data: List[TimeSeriesData] = field(default_factory=list)
    event_patterns: List[EventPattern] = field(default_factory=list)
    correlations: List[CorrelationResult] = field(default_factory=list)
    anomalies: List[AnomalyResult] = field(default_factory=list)
    predictions: List[PredictionResult] = field(default_factory=list)
    statistical_results: List[StatisticalResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    application_insights: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "analysis_id": self.analysis_id,
            "project_name": self.project_name,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "application_analyses": {
                app_name: app_analysis.to_dict() if hasattr(app_analysis, 'to_dict') else app_analysis
                for app_name, app_analysis in self.application_analyses.items()
            },
            "cross_application_correlations": [corr.to_dict() if hasattr(corr, 'to_dict') else corr for corr in self.cross_application_correlations],
            "system_insights": self.system_insights,
            # Legacy fields
            "time_series_data": [ts.to_dict() if hasattr(ts, 'to_dict') else ts for ts in self.time_series_data],
            "event_patterns": [pattern.to_dict() if hasattr(pattern, 'to_dict') else pattern for pattern in self.event_patterns],
            "correlations": [corr.to_dict() if hasattr(corr, 'to_dict') else corr for corr in self.correlations],
            "anomalies": [anomaly.to_dict() if hasattr(anomaly, 'to_dict') else anomaly for anomaly in self.anomalies],
            "predictions": [pred.to_dict() if hasattr(pred, 'to_dict') else pred for pred in self.predictions],
            "statistical_results": [stat.to_dict() if hasattr(stat, 'to_dict') else stat for stat in self.statistical_results],
            "recommendations": self.recommendations,
            "application_insights": self.application_insights,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Create AnalysisResult instance from dictionary"""
        # Handle timestamp conversion
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        # Handle application_analyses conversion
        application_analyses = {}
        if "application_analyses" in data and isinstance(data["application_analyses"], dict):
            for app_name, app_data in data["application_analyses"].items():
                if isinstance(app_data, dict):
                    try:
                        application_analyses[app_name] = ApplicationAnalysisResult.from_dict(app_data)
                    except Exception:
                        # If conversion fails, keep as dict for now
                        application_analyses[app_name] = app_data
        
        return cls(
            analysis_id=data.get("analysis_id", ""),
            project_name=data.get("project_name", ""),
            timestamp=timestamp,
            summary=data.get("summary", {}),
            application_analyses=application_analyses,
            cross_application_correlations=data.get("cross_application_correlations", []),
            system_insights=data.get("system_insights", {}),
            time_series_data=data.get("time_series_data", []),
            event_patterns=data.get("event_patterns", []),
            correlations=data.get("correlations", []),
            anomalies=data.get("anomalies", []),
            predictions=data.get("predictions", []),
            statistical_results=data.get("statistical_results", []),
            recommendations=data.get("recommendations", []),
            application_insights=data.get("application_insights", {}),
            metadata=data.get("metadata")
        )
    
    @property
    def total_applications(self) -> int:
        """Get total number of applications analyzed"""
        return len(self.application_analyses)
    
    @property
    def applications_list(self) -> List[str]:
        """Get list of application names"""
        return list(self.application_analyses.keys())
    
    def get_application_analysis(self, application_name: str) -> Optional[ApplicationAnalysisResult]:
        """Get analysis result for a specific application"""
        return self.application_analyses.get(application_name)
    
    def get_application_anomalies(self, application_name: str) -> List[AnomalyResult]:
        """Get anomalies for a specific application"""
        app_analysis = self.get_application_analysis(application_name)
        return app_analysis.anomalies if app_analysis else []
    
    def get_application_time_series(self, application_name: str) -> List[TimeSeriesData]:
        """Get time series data for a specific application"""
        app_analysis = self.get_application_analysis(application_name)
        return app_analysis.time_series_data if app_analysis else []

# Extraction Reuse Architecture Models (must be defined before Project class)

@dataclass
class ApplicationDiscoveryResult:
    """Result of application discovery in package"""
    container_id: str
    application_name: str
    functional_domain: str
    relative_path: str
    log_file_count: int
    total_log_size_bytes: int
    time_range: Optional[Dict[str, datetime]] = None
    confidence_score: float = 0.0
    discovery_method: str = "pattern_match"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "container_id": self.container_id,
            "application_name": self.application_name,
            "functional_domain": self.functional_domain,
            "relative_path": self.relative_path,
            "log_file_count": self.log_file_count,
            "total_log_size_bytes": self.total_log_size_bytes,
            "time_range": self.time_range,
            "confidence_score": self.confidence_score,
            "discovery_method": self.discovery_method
        }

@dataclass
class PackageStructureMetadata:
    """Persistent metadata for package structure"""
    project_id: str
    extraction_path: str
    original_filename: str
    extraction_timestamp: datetime
    package_hash: str
    total_containers: int
    total_log_files: int
    total_log_size_bytes: int
    applications_detected: List[str]
    extraction_integrity_hash: str
    
    def validate_integrity(self) -> bool:
        """Validate extraction integrity"""
        # Check if extraction directory exists and is complete
        # Verify file counts and sizes match metadata
        # Validate application discovery results
        return True  # Placeholder implementation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project_id": self.project_id,
            "extraction_path": self.extraction_path,
            "original_filename": self.original_filename,
            "extraction_timestamp": self.extraction_timestamp.isoformat(),
            "package_hash": self.package_hash,
            "total_containers": self.total_containers,
            "total_log_files": self.total_log_files,
            "total_log_size_bytes": self.total_log_size_bytes,
            "applications_detected": self.applications_detected,
            "extraction_integrity_hash": self.extraction_integrity_hash
        }

@dataclass
class ApplicationDiscoveryMetadata:
    """Persistent metadata for application discovery"""
    project_id: str
    discovery_timestamp: datetime
    applications: List[ApplicationDiscoveryResult]
    discovery_methods_used: List[str]
    confidence_scores: Dict[str, float]
    validation_status: str
    
    def get_application_info(self, app_name: str) -> Optional[ApplicationDiscoveryResult]:
        """Get cached application information"""
        for app in self.applications:
            if app.application_name == app_name:
                return app
        return None
    
    def update_application_info(self, app_info: ApplicationDiscoveryResult):
        """Update cached application information"""
        # Update or add application information
        for i, existing_app in enumerate(self.applications):
            if existing_app.application_name == app_info.application_name:
                self.applications[i] = app_info
                return
        self.applications.append(app_info)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project_id": self.project_id,
            "discovery_timestamp": self.discovery_timestamp.isoformat(),
            "applications": [app.to_dict() for app in self.applications],
            "discovery_methods_used": self.discovery_methods_used,
            "confidence_scores": self.confidence_scores,
            "validation_status": self.validation_status
        }

@dataclass
class ContainerMappingMetadata:
    """Persistent metadata for container-to-application mapping"""
    project_id: str
    mapping_timestamp: datetime
    container_mappings: Dict[str, 'ContainerMapping']
    
    @dataclass
    class ContainerMapping:
        container_id: str
        application_name: str
        functional_domain: str
        relative_path: str
        log_files: List[str]
        confidence_score: float
        discovery_method: str
        
        def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary for serialization"""
            return {
                "container_id": self.container_id,
                "application_name": self.application_name,
                "functional_domain": self.functional_domain,
                "relative_path": self.relative_path,
                "log_files": self.log_files,
                "confidence_score": self.confidence_score,
                "discovery_method": self.discovery_method
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project_id": self.project_id,
            "mapping_timestamp": self.mapping_timestamp.isoformat(),
            "container_mappings": {
                k: v.to_dict() for k, v in self.container_mappings.items()
            }
        }

# Database Models
@dataclass
class Project:
    """Project database model with extraction reuse support"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: Optional[str] = None
    original_filename: str = ""
    file_size_bytes: int = 0
    upload_timestamp: datetime = field(default_factory=datetime.now)
    extraction_path: str = ""
    status: str = "created"
    created_by: Optional[str] = None
    last_modified: datetime = field(default_factory=datetime.now)
    analysis_count: int = 0
    last_analysis_timestamp: Optional[datetime] = None
    
    # New fields for extraction reuse
    extraction_metadata_path: str = ""
    project_root_path: str = ""  # Absolute path to project root directory
    package_structure_metadata: Optional[PackageStructureMetadata] = None
    application_discovery_metadata: Optional[ApplicationDiscoveryMetadata] = None
    
    def get_project_root_path(self) -> str:
        """Get absolute project root path, normalized to current DATA_DIR if needed"""
        from app.core.config import get_settings
        settings = get_settings()
        expected_path = os.path.join(settings.DATA_DIR, "projects", str(self.id))
        
        # If no path set or path doesn't match current DATA_DIR, use expected path
        if not self.project_root_path:
            self.project_root_path = expected_path
        elif not self.project_root_path.startswith(settings.DATA_DIR):
            # Path is from different machine's DATA_DIR, normalize it
            if not os.path.exists(self.project_root_path):
                # Old path doesn't exist, use new one
                self.project_root_path = expected_path
            # else: keep old path if it exists (might be on shared storage)
        
        return self.project_root_path
    
    def get_extraction_path(self) -> str:
        """Get absolute project-based extraction path"""
        if not self.extraction_path:
            self.extraction_path = os.path.join(self.get_project_root_path(), "extracted")
        return os.path.abspath(self.extraction_path)
    
    def get_metadata_path(self) -> str:
        """Get absolute metadata directory path"""
        if not self.extraction_metadata_path:
            self.extraction_metadata_path = os.path.join(self.get_extraction_path(), "metadata")
        return os.path.abspath(self.extraction_metadata_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "upload_timestamp": self.upload_timestamp.isoformat(),
            "extraction_path": self.extraction_path,
            "status": self.status,
            "created_by": self.created_by,
            "last_modified": self.last_modified.isoformat(),
            "analysis_count": self.analysis_count,
            "last_analysis_timestamp": self.last_analysis_timestamp.isoformat() if self.last_analysis_timestamp else None,
            "extraction_metadata_path": self.extraction_metadata_path,
            "project_root_path": self.project_root_path,
            "package_structure_metadata": self.package_structure_metadata.to_dict() if self.package_structure_metadata and hasattr(self.package_structure_metadata, 'to_dict') else self.package_structure_metadata,
            "application_discovery_metadata": self.application_discovery_metadata.to_dict() if self.application_discovery_metadata and hasattr(self.application_discovery_metadata, 'to_dict') else self.application_discovery_metadata
        }

@dataclass
class Analysis:
    """Analysis job database model"""
    project_id: UUID
    id: UUID = field(default_factory=uuid4)
    configuration: Dict[str, Any] = field(default_factory=dict)
    status: str = "queued"
    created_timestamp: datetime = field(default_factory=datetime.now)
    started_timestamp: Optional[datetime] = None
    completed_timestamp: Optional[datetime] = None
    progress_percentage: float = 0.0
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    result_path: Optional[str] = None
    result: Optional[Any] = None  # Store the actual analysis result
    application_focus: Optional[str] = None  # Focus on specific application
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "configuration": self.configuration,
            "status": self.status,
            "created_timestamp": self.created_timestamp.isoformat(),
            "started_timestamp": self.started_timestamp.isoformat() if self.started_timestamp else None,
            "completed_timestamp": self.completed_timestamp.isoformat() if self.completed_timestamp else None,
            "progress_percentage": self.progress_percentage,
            "current_stage": self.current_stage,
            "error_message": self.error_message,
            "result_path": self.result_path,
            "result": self.result.to_dict() if self.result and hasattr(self.result, 'to_dict') else (self.result if self.result else None),
            "application_focus": self.application_focus
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Analysis':
        """Create Analysis instance from dictionary"""
        # Handle result field - convert dict to AnalysisResult if it exists
        result = data.get("result")
        if result and isinstance(result, dict):
            try:
                result = AnalysisResult.from_dict(result)
            except Exception as e:
                # If conversion fails, keep as dict for now
                print(f"Warning: Failed to convert result to AnalysisResult for analysis {data.get('id', 'unknown')}: {e}")
                print(f"Result type: {type(result)}, Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                pass
        
        return cls(
            id=UUID(data["id"]),
            project_id=UUID(data["project_id"]),
            configuration=data.get("configuration", {}),
            status=data.get("status", "queued"),
            created_timestamp=datetime.fromisoformat(data["created_timestamp"]),
            started_timestamp=datetime.fromisoformat(data["started_timestamp"]) if data.get("started_timestamp") else None,
            completed_timestamp=datetime.fromisoformat(data["completed_timestamp"]) if data.get("completed_timestamp") else None,
            progress_percentage=data.get("progress_percentage", 0.0),
            current_stage=data.get("current_stage"),
            error_message=data.get("error_message"),
            result_path=data.get("result_path"),
            result=result,
            application_focus=data.get("application_focus")
        )

@dataclass
class Application:
    """Application database model"""
    project_id: UUID
    container_id: str
    application_name: str
    id: UUID = field(default_factory=uuid4)
    functional_domain: Optional[str] = None
    relative_path: str = ""
    log_file_count: int = 0
    total_log_size_bytes: int = 0
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "container_id": self.container_id,
            "application_name": self.application_name,
            "functional_domain": self.functional_domain,
            "relative_path": self.relative_path,
            "log_file_count": self.log_file_count,
            "total_log_size_bytes": self.total_log_size_bytes,
            "time_range_start": self.time_range_start.isoformat() if self.time_range_start else None,
            "time_range_end": self.time_range_end.isoformat() if self.time_range_end else None,
            "confidence_score": self.confidence_score
        }

