"""
Anomaly Detection Module

This module provides machine learning-based anomaly detection for log analysis.
It uses various algorithms to identify unusual patterns in log data.
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
import joblib
import os

from ..models.core import TimeSeriesData, AnomalyResult, AnomalyType
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class AnomalyAlgorithm(Enum):
    """Supported anomaly detection algorithms"""
    ISOLATION_FOREST = "isolation_forest"
    DBSCAN = "dbscan"
    STATISTICAL = "statistical"
    PCA = "pca"

@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection"""
    algorithm: AnomalyAlgorithm
    contamination: float = 0.1
    n_estimators: int = 100
    random_state: int = 42
    eps: float = 0.5
    min_samples: int = 5
    threshold_std: float = 2.0
    window_size: int = 10
    min_anomaly_score: float = 0.5

class AnomalyDetector:
    """
    Machine learning-based anomaly detection for log analysis.
    
    Supports multiple algorithms:
    - Isolation Forest: Tree-based anomaly detection
    - DBSCAN: Density-based clustering for outlier detection
    - Statistical: Z-score and IQR based detection
    - PCA: Principal Component Analysis for dimensionality reduction
    """
    
    def __init__(self, config: Optional[AnomalyConfig] = None):
        """Initialize the anomaly detector"""
        self.config = config or AnomalyConfig(algorithm=AnomalyAlgorithm.ISOLATION_FOREST)
        self.models = {}
        self.scalers = {}
        self.is_fitted = False
        
        # Create models directory
        os.makedirs("models", exist_ok=True)
        
    def _prepare_features(self, time_series_data: List[TimeSeriesData]) -> pd.DataFrame:
        """Prepare features for anomaly detection"""
        features = []
        
        for ts in time_series_data:
            # Extract time-based features
            timestamps = pd.to_datetime([point.timestamp for point in ts.data_points])
            
            # Time features
            hour_of_day = pd.Series(timestamps.hour)
            day_of_week = pd.Series(timestamps.dayofweek)
            is_weekend = pd.Series((day_of_week >= 5).astype(int))
            
            # Value features
            values = [point.value for point in ts.data_points]
            
            # Statistical features
            rolling_mean = pd.Series(values).rolling(window=self.config.window_size, min_periods=1).mean()
            rolling_std = pd.Series(values).rolling(window=self.config.window_size, min_periods=1).std()
            rolling_max = pd.Series(values).rolling(window=self.config.window_size, min_periods=1).max()
            rolling_min = pd.Series(values).rolling(window=self.config.window_size, min_periods=1).min()
            
            # Rate of change
            rate_of_change = pd.Series(values).diff().fillna(0)
            
            # Combine features
            for i, (timestamp, value) in enumerate(zip(timestamps, values)):
                feature_vector = {
                    'timestamp': timestamp,
                    'value': value,
                    'hour_of_day': hour_of_day[i] if i < len(hour_of_day) else 0,
                    'day_of_week': day_of_week[i] if i < len(day_of_week) else 0,
                    'is_weekend': is_weekend[i] if i < len(is_weekend) else 0,
                    'rolling_mean': rolling_mean.iloc[i] if i < len(rolling_mean) else value,
                    'rolling_std': rolling_std.iloc[i] if i < len(rolling_std) else 0,
                    'rolling_max': rolling_max.iloc[i] if i < len(rolling_max) else value,
                    'rolling_min': rolling_min.iloc[i] if i < len(rolling_min) else value,
                    'rate_of_change': rate_of_change.iloc[i] if i < len(rate_of_change) else 0,
                    'metric_name': ts.metric_name,
                    'application': ts.application
                }
                features.append(feature_vector)
        
        return pd.DataFrame(features)
    
    def _detect_statistical_anomalies(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """Detect anomalies using statistical methods (Z-score, IQR)"""
        anomalies = []
        
        for metric in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric]
            values = metric_data['value'].values
            
            if len(values) < 3:
                continue
                
            # Z-score method
            z_scores = np.abs((values - np.mean(values)) / np.std(values))
            z_anomalies = z_scores > self.config.threshold_std
            
            # IQR method
            Q1 = np.percentile(values, 25)
            Q3 = np.percentile(values, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            iqr_anomalies = (values < lower_bound) | (values > upper_bound)
            
            # Combine both methods
            combined_anomalies = z_anomalies | iqr_anomalies
            
            for i, is_anomaly in enumerate(combined_anomalies):
                if is_anomaly:
                    row = metric_data.iloc[i]
                    anomaly = AnomalyResult(
                        timestamp=row['timestamp'],
                        metric_name=metric,
                        application=row['application'],
                        anomaly_type=AnomalyType.STATISTICAL,
                        score=float(z_scores[i]),
                        severity="high" if z_scores[i] > 3 else "medium",
                        description=f"Statistical anomaly detected: Z-score={z_scores[i]:.2f}, "
                                  f"Value={row['value']:.2f}",
                        confidence=min(0.95, z_scores[i] / 5.0)
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_isolation_forest_anomalies(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """Detect anomalies using Isolation Forest"""
        anomalies = []
        
        # Prepare features for ML
        feature_columns = ['value', 'hour_of_day', 'day_of_week', 'is_weekend', 
                          'rolling_mean', 'rolling_std', 'rate_of_change']
        
        # Group by metric and application
        for (metric, app), group in df.groupby(['metric_name', 'application']):
            if len(group) < 10:  # Need minimum data points
                continue
                
            X = group[feature_columns].fillna(0).values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train Isolation Forest
            model = IsolationForest(
                contamination=self.config.contamination,
                n_estimators=self.config.n_estimators,
                random_state=self.config.random_state
            )
            
            # Predict anomalies (-1 for anomaly, 1 for normal)
            predictions = model.fit_predict(X_scaled)
            scores = model.score_samples(X_scaled)
            
            # Convert scores to anomaly scores (lower = more anomalous)
            anomaly_scores = -scores
            
            # Find anomalies
            anomaly_indices = np.where(predictions == -1)[0]
            
            for idx in anomaly_indices:
                if anomaly_scores[idx] > self.config.min_anomaly_score:
                    row = group.iloc[idx]
                    anomaly = AnomalyResult(
                        timestamp=row['timestamp'],
                        metric_name=metric,
                        application=app,
                        anomaly_type=AnomalyType.MACHINE_LEARNING,
                        score=float(anomaly_scores[idx]),
                        severity="high" if anomaly_scores[idx] > 0.8 else "medium",
                        description=f"Isolation Forest anomaly: Score={anomaly_scores[idx]:.3f}, "
                                  f"Value={row['value']:.2f}",
                        confidence=min(0.95, anomaly_scores[idx])
                    )
                    anomalies.append(anomaly)
            
            # Store model and scaler
            model_key = f"{metric}_{app}"
            self.models[model_key] = model
            self.scalers[model_key] = scaler
        
        return anomalies
    
    def _detect_dbscan_anomalies(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """Detect anomalies using DBSCAN clustering"""
        anomalies = []
        
        # Prepare features
        feature_columns = ['value', 'hour_of_day', 'day_of_week', 'rolling_mean', 'rate_of_change']
        
        for (metric, app), group in df.groupby(['metric_name', 'application']):
            if len(group) < 10:
                continue
                
            X = group[feature_columns].fillna(0).values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Apply DBSCAN
            dbscan = DBSCAN(eps=self.config.eps, min_samples=self.config.min_samples)
            clusters = dbscan.fit_predict(X_scaled)
            
            # Points with cluster label -1 are outliers
            outlier_indices = np.where(clusters == -1)[0]
            
            for idx in outlier_indices:
                row = group.iloc[idx]
                # Calculate distance to nearest cluster center
                distances = dbscan.components_ - X_scaled[idx] if len(dbscan.components_) > 0 else [0]
                min_distance = np.min(np.linalg.norm(distances, axis=1)) if len(distances) > 0 else 1.0
                
                anomaly = AnomalyResult(
                    timestamp=row['timestamp'],
                    metric_name=metric,
                    application=app,
                    anomaly_type=AnomalyType.MACHINE_LEARNING,
                    score=float(min_distance),
                    severity="high" if min_distance > 2.0 else "medium",
                    description=f"DBSCAN outlier: Distance={min_distance:.3f}, "
                              f"Value={row['value']:.2f}",
                    confidence=min(0.95, min_distance / 3.0)
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_pca_anomalies(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """Detect anomalies using PCA reconstruction error"""
        anomalies = []
        
        feature_columns = ['value', 'hour_of_day', 'day_of_week', 'rolling_mean', 
                          'rolling_std', 'rate_of_change']
        
        for (metric, app), group in df.groupby(['metric_name', 'application']):
            if len(group) < 10:
                continue
                
            X = group[feature_columns].fillna(0).values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Apply PCA
            n_components = min(3, len(feature_columns))
            pca = PCA(n_components=n_components)
            X_pca = pca.fit_transform(X_scaled)
            X_reconstructed = pca.inverse_transform(X_pca)
            
            # Calculate reconstruction error
            reconstruction_errors = np.mean((X_scaled - X_reconstructed) ** 2, axis=1)
            
            # Find points with high reconstruction error
            threshold = np.percentile(reconstruction_errors, 95)  # Top 5% as anomalies
            
            anomaly_indices = np.where(reconstruction_errors > threshold)[0]
            
            for idx in anomaly_indices:
                row = group.iloc[idx]
                error = reconstruction_errors[idx]
                
                anomaly = AnomalyResult(
                    timestamp=row['timestamp'],
                    metric_name=metric,
                    application=app,
                    anomaly_type=AnomalyType.MACHINE_LEARNING,
                    score=float(error),
                    severity="high" if error > threshold * 1.5 else "medium",
                    description=f"PCA reconstruction error: Error={error:.3f}, "
                              f"Value={row['value']:.2f}",
                    confidence=min(0.95, error / (threshold * 2))
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def detect_anomalies(self, time_series_data: List[TimeSeriesData]) -> List[AnomalyResult]:
        """
        Detect anomalies in time series data using the configured algorithm.
        
        Args:
            time_series_data: List of time series data to analyze
            
        Returns:
            List of detected anomalies
        """
        logger.info(f"Starting anomaly detection with algorithm: {self.config.algorithm.value}")
        
        if not time_series_data:
            logger.warning("No time series data provided for anomaly detection")
            return []
        
        # Prepare features
        df = self._prepare_features(time_series_data)
        
        if df.empty:
            logger.warning("No features extracted from time series data")
            return []
        
        # Detect anomalies based on algorithm
        if self.config.algorithm == AnomalyAlgorithm.STATISTICAL:
            anomalies = self._detect_statistical_anomalies(df)
        elif self.config.algorithm == AnomalyAlgorithm.ISOLATION_FOREST:
            anomalies = self._detect_isolation_forest_anomalies(df)
        elif self.config.algorithm == AnomalyAlgorithm.DBSCAN:
            anomalies = self._detect_dbscan_anomalies(df)
        elif self.config.algorithm == AnomalyAlgorithm.PCA:
            anomalies = self._detect_pca_anomalies(df)
        else:
            raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")
        
        # Sort by timestamp
        anomalies.sort(key=lambda x: x.timestamp)
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def save_models(self, project_name: str):
        """Save trained models to disk"""
        if not self.models:
            logger.warning("No models to save")
            return
        
        models_dir = f"models/{project_name}"
        os.makedirs(models_dir, exist_ok=True)
        
        for model_key, model in self.models.items():
            model_path = f"{models_dir}/{model_key}_model.pkl"
            scaler_path = f"{models_dir}/{model_key}_scaler.pkl"
            
            joblib.dump(model, model_path)
            if model_key in self.scalers:
                joblib.dump(self.scalers[model_key], scaler_path)
        
        logger.info(f"Saved {len(self.models)} models to {models_dir}")
    
    def load_models(self, project_name: str):
        """Load trained models from disk"""
        models_dir = f"models/{project_name}"
        
        if not os.path.exists(models_dir):
            logger.warning(f"Models directory not found: {models_dir}")
            return
        
        for file in os.listdir(models_dir):
            if file.endswith("_model.pkl"):
                model_key = file.replace("_model.pkl", "")
                model_path = f"{models_dir}/{file}"
                scaler_path = f"{models_dir}/{model_key}_scaler.pkl"
                
                self.models[model_key] = joblib.load(model_path)
                if os.path.exists(scaler_path):
                    self.scalers[model_key] = joblib.load(scaler_path)
        
        self.is_fitted = True
        logger.info(f"Loaded {len(self.models)} models from {models_dir}")
    
    def get_anomaly_summary(self, anomalies: List[AnomalyResult]) -> Dict[str, Any]:
        """Generate summary statistics for detected anomalies"""
        if not anomalies:
            return {
                "total_anomalies": 0,
                "anomaly_types": {},
                "severity_distribution": {},
                "applications_affected": set(),
                "metrics_affected": set()
            }
        
        # Count by type
        type_counts = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.anomaly_type.value
            type_counts[anomaly_type] = type_counts.get(anomaly_type, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for anomaly in anomalies:
            severity = anomaly.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Get affected applications and metrics
        applications = set(anomaly.application for anomaly in anomalies)
        metrics = set(anomaly.metric_name for anomaly in anomalies)
        
        # Calculate average confidence
        avg_confidence = sum(anomaly.confidence for anomaly in anomalies) / len(anomalies)
        
        return {
            "total_anomalies": len(anomalies),
            "anomaly_types": type_counts,
            "severity_distribution": severity_counts,
            "applications_affected": list(applications),
            "metrics_affected": list(metrics),
            "average_confidence": avg_confidence,
            "high_severity_count": severity_counts.get("high", 0),
            "medium_severity_count": severity_counts.get("medium", 0)
        }

class AnomalyAlgorithm(Enum):
    """Supported anomaly detection algorithms"""
    ISOLATION_FOREST = "isolation_forest"
    DBSCAN = "dbscan"
    STATISTICAL = "statistical"
    PCA = "pca"

@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection"""
    algorithm: AnomalyAlgorithm
    contamination: float = 0.1
    n_estimators: int = 100
    random_state: int = 42
    eps: float = 0.5
    min_samples: int = 5
    threshold_std: float = 2.0
    window_size: int = 10
    min_anomaly_score: float = 0.5

class AnomalyDetector:
    """
    Machine learning-based anomaly detection for log analysis.
    
    Supports multiple algorithms:
    - Isolation Forest: Tree-based anomaly detection
    - DBSCAN: Density-based clustering for outlier detection
    - Statistical: Z-score and IQR based detection
    - PCA: Principal Component Analysis for dimensionality reduction
    """
    
    def __init__(self, config: Optional[AnomalyConfig] = None):
        """Initialize the anomaly detector"""
        self.config = config or AnomalyConfig(algorithm=AnomalyAlgorithm.ISOLATION_FOREST)
        self.models = {}
        self.scalers = {}
        self.is_fitted = False
        
        # Create models directory
        os.makedirs("models", exist_ok=True)
        
    def _prepare_features(self, time_series_data: List[TimeSeriesData]) -> pd.DataFrame:
        """Prepare features for anomaly detection"""
        features = []
        
        for ts in time_series_data:
            # Extract time-based features
            timestamps = pd.to_datetime([point.timestamp for point in ts.data_points])
            
            # Time features
            hour_of_day = timestamps.hour
            day_of_week = timestamps.dayofweek
            is_weekend = (day_of_week >= 5).astype(int)
            
            # Value features
            values = [point.value for point in ts.data_points]
            
            # Statistical features
            rolling_mean = pd.Series(values).rolling(window=self.config.window_size, min_periods=1).mean()
            rolling_std = pd.Series(values).rolling(window=self.config.window_size, min_periods=1).std()
            rolling_max = pd.Series(values).rolling(window=self.config.window_size, min_periods=1).max()
            rolling_min = pd.Series(values).rolling(window=self.config.window_size, min_periods=1).min()
            
            # Rate of change
            rate_of_change = pd.Series(values).diff().fillna(0)
            
            # Combine features
            for i, (timestamp, value) in enumerate(zip(timestamps, values)):
                feature_vector = {
                    'timestamp': timestamp,
                    'value': value,
                    'hour_of_day': hour_of_day[i] if i < len(hour_of_day) else 0,
                    'day_of_week': day_of_week[i] if i < len(day_of_week) else 0,
                    'is_weekend': is_weekend[i] if i < len(is_weekend) else 0,
                    'rolling_mean': rolling_mean.iloc[i] if i < len(rolling_mean) else value,
                    'rolling_std': rolling_std.iloc[i] if i < len(rolling_std) else 0,
                    'rolling_max': rolling_max.iloc[i] if i < len(rolling_max) else value,
                    'rolling_min': rolling_min.iloc[i] if i < len(rolling_min) else value,
                    'rate_of_change': rate_of_change.iloc[i] if i < len(rate_of_change) else 0,
                    'metric_name': ts.metric_name,
                    'application': ts.application
                }
                features.append(feature_vector)
        
        return pd.DataFrame(features)
    
    def _detect_statistical_anomalies(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """Detect anomalies using statistical methods (Z-score, IQR)"""
        anomalies = []
        
        for metric in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric]
            values = metric_data['value'].values
            
            if len(values) < 3:
                continue
                
            # Z-score method
            z_scores = np.abs((values - np.mean(values)) / np.std(values))
            z_anomalies = z_scores > self.config.threshold_std
            
            # IQR method
            Q1 = np.percentile(values, 25)
            Q3 = np.percentile(values, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            iqr_anomalies = (values < lower_bound) | (values > upper_bound)
            
            # Combine both methods
            combined_anomalies = z_anomalies | iqr_anomalies
            
            for i, is_anomaly in enumerate(combined_anomalies):
                if is_anomaly:
                    row = metric_data.iloc[i]
                    anomaly = AnomalyResult(
                        timestamp=row['timestamp'],
                        metric_name=metric,
                        application=row['application'],
                        anomaly_type=AnomalyType.STATISTICAL,
                        score=float(z_scores[i]),
                        severity="high" if z_scores[i] > 3 else "medium",
                        description=f"Statistical anomaly detected: Z-score={z_scores[i]:.2f}, "
                                  f"Value={row['value']:.2f}",
                        confidence=min(0.95, z_scores[i] / 5.0)
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_isolation_forest_anomalies(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """Detect anomalies using Isolation Forest"""
        anomalies = []
        
        # Prepare features for ML
        feature_columns = ['value', 'hour_of_day', 'day_of_week', 'is_weekend', 
                          'rolling_mean', 'rolling_std', 'rate_of_change']
        
        # Group by metric and application
        for (metric, app), group in df.groupby(['metric_name', 'application']):
            if len(group) < 10:  # Need minimum data points
                continue
                
            X = group[feature_columns].fillna(0).values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train Isolation Forest
            model = IsolationForest(
                contamination=self.config.contamination,
                n_estimators=self.config.n_estimators,
                random_state=self.config.random_state
            )
            
            # Predict anomalies (-1 for anomaly, 1 for normal)
            predictions = model.fit_predict(X_scaled)
            scores = model.score_samples(X_scaled)
            
            # Convert scores to anomaly scores (lower = more anomalous)
            anomaly_scores = -scores
            
            # Find anomalies
            anomaly_indices = np.where(predictions == -1)[0]
            
            for idx in anomaly_indices:
                if anomaly_scores[idx] > self.config.min_anomaly_score:
                    row = group.iloc[idx]
                    anomaly = AnomalyResult(
                        timestamp=row['timestamp'],
                        metric_name=metric,
                        application=app,
                        anomaly_type=AnomalyType.MACHINE_LEARNING,
                        score=float(anomaly_scores[idx]),
                        severity="high" if anomaly_scores[idx] > 0.8 else "medium",
                        description=f"Isolation Forest anomaly: Score={anomaly_scores[idx]:.3f}, "
                                  f"Value={row['value']:.2f}",
                        confidence=min(0.95, anomaly_scores[idx])
                    )
                    anomalies.append(anomaly)
            
            # Store model and scaler
            model_key = f"{metric}_{app}"
            self.models[model_key] = model
            self.scalers[model_key] = scaler
        
        return anomalies
    
    def _detect_dbscan_anomalies(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """Detect anomalies using DBSCAN clustering"""
        anomalies = []
        
        # Prepare features
        feature_columns = ['value', 'hour_of_day', 'day_of_week', 'rolling_mean', 'rate_of_change']
        
        for (metric, app), group in df.groupby(['metric_name', 'application']):
            if len(group) < 10:
                continue
                
            X = group[feature_columns].fillna(0).values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Apply DBSCAN
            dbscan = DBSCAN(eps=self.config.eps, min_samples=self.config.min_samples)
            clusters = dbscan.fit_predict(X_scaled)
            
            # Points with cluster label -1 are outliers
            outlier_indices = np.where(clusters == -1)[0]
            
            for idx in outlier_indices:
                row = group.iloc[idx]
                # Calculate distance to nearest cluster center
                distances = dbscan.components_ - X_scaled[idx] if len(dbscan.components_) > 0 else [0]
                min_distance = np.min(np.linalg.norm(distances, axis=1)) if len(distances) > 0 else 1.0
                
                anomaly = AnomalyResult(
                    timestamp=row['timestamp'],
                    metric_name=metric,
                    application=app,
                    anomaly_type=AnomalyType.MACHINE_LEARNING,
                    score=float(min_distance),
                    severity="high" if min_distance > 2.0 else "medium",
                    description=f"DBSCAN outlier: Distance={min_distance:.3f}, "
                              f"Value={row['value']:.2f}",
                    confidence=min(0.95, min_distance / 3.0)
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_pca_anomalies(self, df: pd.DataFrame) -> List[AnomalyResult]:
        """Detect anomalies using PCA reconstruction error"""
        anomalies = []
        
        feature_columns = ['value', 'hour_of_day', 'day_of_week', 'rolling_mean', 
                          'rolling_std', 'rate_of_change']
        
        for (metric, app), group in df.groupby(['metric_name', 'application']):
            if len(group) < 10:
                continue
                
            X = group[feature_columns].fillna(0).values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Apply PCA
            n_components = min(3, len(feature_columns))
            pca = PCA(n_components=n_components)
            X_pca = pca.fit_transform(X_scaled)
            X_reconstructed = pca.inverse_transform(X_pca)
            
            # Calculate reconstruction error
            reconstruction_errors = np.mean((X_scaled - X_reconstructed) ** 2, axis=1)
            
            # Find points with high reconstruction error
            threshold = np.percentile(reconstruction_errors, 95)  # Top 5% as anomalies
            
            anomaly_indices = np.where(reconstruction_errors > threshold)[0]
            
            for idx in anomaly_indices:
                row = group.iloc[idx]
                error = reconstruction_errors[idx]
                
                anomaly = AnomalyResult(
                    timestamp=row['timestamp'],
                    metric_name=metric,
                    application=app,
                    anomaly_type=AnomalyType.MACHINE_LEARNING,
                    score=float(error),
                    severity="high" if error > threshold * 1.5 else "medium",
                    description=f"PCA reconstruction error: Error={error:.3f}, "
                              f"Value={row['value']:.2f}",
                    confidence=min(0.95, error / (threshold * 2))
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def detect_anomalies(self, time_series_data: List[TimeSeriesData]) -> List[AnomalyResult]:
        """
        Detect anomalies in time series data using the configured algorithm.
        
        Args:
            time_series_data: List of time series data to analyze
            
        Returns:
            List of detected anomalies
        """
        logger.info(f"Starting anomaly detection with algorithm: {self.config.algorithm.value}")
        
        if not time_series_data:
            logger.warning("No time series data provided for anomaly detection")
            return []
        
        # Prepare features
        df = self._prepare_features(time_series_data)
        
        if df.empty:
            logger.warning("No features extracted from time series data")
            return []
        
        # Detect anomalies based on algorithm
        if self.config.algorithm == AnomalyAlgorithm.STATISTICAL:
            anomalies = self._detect_statistical_anomalies(df)
        elif self.config.algorithm == AnomalyAlgorithm.ISOLATION_FOREST:
            anomalies = self._detect_isolation_forest_anomalies(df)
        elif self.config.algorithm == AnomalyAlgorithm.DBSCAN:
            anomalies = self._detect_dbscan_anomalies(df)
        elif self.config.algorithm == AnomalyAlgorithm.PCA:
            anomalies = self._detect_pca_anomalies(df)
        else:
            raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")
        
        # Sort by timestamp
        anomalies.sort(key=lambda x: x.timestamp)
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def save_models(self, project_name: str):
        """Save trained models to disk"""
        if not self.models:
            logger.warning("No models to save")
            return
        
        models_dir = f"models/{project_name}"
        os.makedirs(models_dir, exist_ok=True)
        
        for model_key, model in self.models.items():
            model_path = f"{models_dir}/{model_key}_model.pkl"
            scaler_path = f"{models_dir}/{model_key}_scaler.pkl"
            
            joblib.dump(model, model_path)
            if model_key in self.scalers:
                joblib.dump(self.scalers[model_key], scaler_path)
        
        logger.info(f"Saved {len(self.models)} models to {models_dir}")
    
    def load_models(self, project_name: str):
        """Load trained models from disk"""
        models_dir = f"models/{project_name}"
        
        if not os.path.exists(models_dir):
            logger.warning(f"Models directory not found: {models_dir}")
            return
        
        for file in os.listdir(models_dir):
            if file.endswith("_model.pkl"):
                model_key = file.replace("_model.pkl", "")
                model_path = f"{models_dir}/{file}"
                scaler_path = f"{models_dir}/{model_key}_scaler.pkl"
                
                self.models[model_key] = joblib.load(model_path)
                if os.path.exists(scaler_path):
                    self.scalers[model_key] = joblib.load(scaler_path)
        
        self.is_fitted = True
        logger.info(f"Loaded {len(self.models)} models from {models_dir}")
    
    def get_anomaly_summary(self, anomalies: List[AnomalyResult]) -> Dict[str, Any]:
        """Generate summary statistics for detected anomalies"""
        if not anomalies:
            return {
                "total_anomalies": 0,
                "anomaly_types": {},
                "severity_distribution": {},
                "applications_affected": set(),
                "metrics_affected": set()
            }
        
        # Count by type
        type_counts = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.anomaly_type.value
            type_counts[anomaly_type] = type_counts.get(anomaly_type, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for anomaly in anomalies:
            severity = anomaly.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Get affected applications and metrics
        applications = set(anomaly.application for anomaly in anomalies)
        metrics = set(anomaly.metric_name for anomaly in anomalies)
        
        # Calculate average confidence
        avg_confidence = sum(anomaly.confidence for anomaly in anomalies) / len(anomalies)
        
        return {
            "total_anomalies": len(anomalies),
            "anomaly_types": type_counts,
            "severity_distribution": severity_counts,
            "applications_affected": list(applications),
            "metrics_affected": list(metrics),
            "average_confidence": avg_confidence,
            "high_severity_count": severity_counts.get("high", 0),
            "medium_severity_count": severity_counts.get("medium", 0)
        }
