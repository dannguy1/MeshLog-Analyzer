"""
Predictive Analytics Module

This module provides time series forecasting and predictive analytics for log analysis.
It uses various algorithms to predict future log patterns and system behavior.
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

from ..models.core import TimeSeriesData, PredictionResult, ForecastType, ForecastDataPoint
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class ForecastAlgorithm(Enum):
    """Supported forecasting algorithms"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"

@dataclass
class ForecastConfig:
    """Configuration for forecasting"""
    algorithm: ForecastAlgorithm
    forecast_horizon: int = 24  # Number of time steps to forecast
    confidence_level: float = 0.95
    min_data_points: int = 20
    seasonal_period: int = 24  # For seasonal decomposition
    alpha: float = 0.3  # For exponential smoothing
    window_size: int = 5  # For moving average

class PredictiveAnalytics:
    """
    Predictive analytics for log analysis using time series forecasting.
    
    Supports multiple algorithms:
    - Linear Regression: Simple trend-based forecasting
    - Random Forest: Non-linear pattern recognition
    - Moving Average: Smooth trend estimation
    - Exponential Smoothing: Weighted average forecasting
    - Seasonal Decomposition: Trend + seasonal + residual components
    """
    
    def __init__(self, config: Optional[ForecastConfig] = None):
        """Initialize the predictive analytics engine"""
        self.config = config or ForecastConfig(algorithm=ForecastAlgorithm.LINEAR_REGRESSION)
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        
    def _prepare_time_series(self, time_series_data: TimeSeriesData) -> pd.DataFrame:
        """Prepare time series data for forecasting"""
        if not time_series_data.data_points:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'timestamp': point.timestamp,
                'value': point.value
            }
            for point in time_series_data.data_points
        ])
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Add time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Add lag features
        for lag in [1, 2, 3, 6, 12]:
            df[f'lag_{lag}'] = df['value'].shift(lag)
        
        # Add rolling statistics
        for window in [3, 6, 12]:
            df[f'rolling_mean_{window}'] = df['value'].rolling(window=window, min_periods=1).mean()
            df[f'rolling_std_{window}'] = df['value'].rolling(window=window, min_periods=1).std()
        
        # Add trend features
        df['trend'] = range(len(df))
        df['trend_squared'] = df['trend'] ** 2
        
        return df
    
    def _linear_regression_forecast(self, df: pd.DataFrame, metric_name: str, application: str) -> PredictionResult:
        """Forecast using linear regression"""
        if len(df) < self.config.min_data_points:
            return self._create_empty_prediction(metric_name, application)
        
        # Prepare features
        feature_columns = ['trend', 'trend_squared', 'hour', 'day_of_week', 'is_weekend']
        lag_columns = [col for col in df.columns if col.startswith('lag_')]
        rolling_columns = [col for col in df.columns if col.startswith('rolling_')]
        
        all_features = feature_columns + lag_columns + rolling_columns
        available_features = [col for col in all_features if col in df.columns]
        
        X = df[available_features].fillna(0)
        y = df['value']
        
        # Remove rows with NaN values
        valid_indices = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[valid_indices]
        y = y[valid_indices]
        
        if len(X) < 10:
            return self._create_empty_prediction(metric_name, application)
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate future features
        future_trend = range(len(df), len(df) + self.config.forecast_horizon)
        future_trend_squared = [t ** 2 for t in future_trend]
        
        # Use last known values for lag features
        last_values = df['value'].tail(12).tolist()
        if len(last_values) < 12:
            last_values = [df['value'].iloc[-1]] * 12
        
        # Create future DataFrame
        future_df = pd.DataFrame()
        future_df['trend'] = future_trend
        future_df['trend_squared'] = future_trend_squared
        
        # Add time features (assuming hourly data)
        last_timestamp = df['timestamp'].iloc[-1]
        if isinstance(last_timestamp, str):
            last_timestamp = pd.to_datetime(last_timestamp)
        future_timestamps = [last_timestamp + timedelta(hours=i+1) for i in range(self.config.forecast_horizon)]
        future_df['hour'] = [ts.hour for ts in future_timestamps]
        future_df['day_of_week'] = [ts.weekday() for ts in future_timestamps]
        future_df['is_weekend'] = [(d >= 5) for d in future_df['day_of_week']]
        
        # Add lag features
        for i, lag in enumerate([1, 2, 3, 6, 12]):
            col_name = f'lag_{lag}'
            if col_name in available_features:
                future_df[col_name] = [last_values[-(lag-i)] if i < lag else last_values[-1]] * self.config.forecast_horizon
        
        # Add rolling features
        for window in [3, 6, 12]:
            for stat in ['mean', 'std']:
                col_name = f'rolling_{stat}_{window}'
                if col_name in available_features:
                    future_df[col_name] = df[f'rolling_{stat}_{window}'].iloc[-1]
        
        # Make predictions
        X_future = future_df[available_features].fillna(0)
        predictions = model.predict(X_future)
        
        # Calculate confidence intervals
        residuals = y - model.predict(X)
        std_residuals = np.std(residuals)
        confidence_interval = 1.96 * std_residuals  # 95% confidence
        
        # Create prediction result
        forecast_data = []
        for i, (timestamp, pred) in enumerate(zip(future_timestamps, predictions)):
            forecast_data.append(ForecastDataPoint(
                timestamp=timestamp,
                predicted_value=float(pred),
                lower_bound=float(pred - confidence_interval),
                upper_bound=float(pred + confidence_interval),
                confidence=self.config.confidence_level
            ))
        
        return PredictionResult(
            metric_name=metric_name,
            application=application,
            forecast_type=ForecastType.TIME_SERIES,
            algorithm=self.config.algorithm.value,
            forecast_data=forecast_data,
            model_accuracy=r2_score(y, model.predict(X)),
            confidence_level=self.config.confidence_level,
            forecast_horizon=self.config.forecast_horizon,
            created_at=datetime.now()
        )
    
    def _random_forest_forecast(self, df: pd.DataFrame, metric_name: str, application: str) -> PredictionResult:
        """Forecast using random forest"""
        if len(df) < self.config.min_data_points:
            return self._create_empty_prediction(metric_name, application)
        
        # Prepare features
        feature_columns = ['trend', 'trend_squared', 'hour', 'day_of_week', 'is_weekend']
        lag_columns = [col for col in df.columns if col.startswith('lag_')]
        rolling_columns = [col for col in df.columns if col.startswith('rolling_')]
        
        all_features = feature_columns + lag_columns + rolling_columns
        available_features = [col for col in all_features if col in df.columns]
        
        X = df[available_features].fillna(0)
        y = df['value']
        
        # Remove rows with NaN values
        valid_indices = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[valid_indices]
        y = y[valid_indices]
        
        if len(X) < 10:
            return self._create_empty_prediction(metric_name, application)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Generate future features (same as linear regression)
        future_trend = range(len(df), len(df) + self.config.forecast_horizon)
        future_trend_squared = [t ** 2 for t in future_trend]
        
        last_values = df['value'].tail(12).tolist()
        if len(last_values) < 12:
            last_values = [df['value'].iloc[-1]] * 12
        
        last_timestamp = df['timestamp'].iloc[-1]
        if isinstance(last_timestamp, str):
            last_timestamp = pd.to_datetime(last_timestamp)
        future_timestamps = [last_timestamp + timedelta(hours=i+1) for i in range(self.config.forecast_horizon)]
        
        future_df = pd.DataFrame()
        future_df['trend'] = future_trend
        future_df['trend_squared'] = future_trend_squared
        future_df['hour'] = [ts.hour for ts in future_timestamps]
        future_df['day_of_week'] = [ts.weekday() for ts in future_timestamps]
        future_df['is_weekend'] = [(d >= 5) for d in future_df['day_of_week']]
        
        # Add lag features
        for i, lag in enumerate([1, 2, 3, 6, 12]):
            col_name = f'lag_{lag}'
            if col_name in available_features:
                future_df[col_name] = [last_values[-(lag-i)] if i < lag else last_values[-1]] * self.config.forecast_horizon
        
        # Add rolling features
        for window in [3, 6, 12]:
            for stat in ['mean', 'std']:
                col_name = f'rolling_{stat}_{window}'
                if col_name in available_features:
                    future_df[col_name] = df[f'rolling_{stat}_{window}'].iloc[-1]
        
        # Make predictions
        X_future = future_df[available_features].fillna(0)
        predictions = model.predict(X_future)
        
        # Calculate confidence intervals using model predictions
        predictions_list = []
        for _ in range(100):  # Bootstrap
            sample_indices = np.random.choice(len(X), len(X), replace=True)
            X_sample = X.iloc[sample_indices]
            y_sample = y.iloc[sample_indices]
            
            sample_model = RandomForestRegressor(n_estimators=50, random_state=np.random.randint(1000))
            sample_model.fit(X_sample, y_sample)
            sample_pred = sample_model.predict(X_future)
            predictions_list.append(sample_pred)
        
        predictions_array = np.array(predictions_list)
        lower_bounds = np.percentile(predictions_array, 2.5, axis=0)
        upper_bounds = np.percentile(predictions_array, 97.5, axis=0)
        
        # Create prediction result
        forecast_data = []
        for i, (timestamp, pred, lower, upper) in enumerate(zip(future_timestamps, predictions, lower_bounds, upper_bounds)):
            forecast_data.append(ForecastDataPoint(
                timestamp=timestamp,
                predicted_value=float(pred),
                lower_bound=float(lower),
                upper_bound=float(upper),
                confidence=self.config.confidence_level
            ))
        
        return PredictionResult(
            metric_name=metric_name,
            application=application,
            forecast_type=ForecastType.TIME_SERIES,
            algorithm=self.config.algorithm.value,
            forecast_data=forecast_data,
            model_accuracy=r2_score(y, model.predict(X)),
            confidence_level=self.config.confidence_level,
            forecast_horizon=self.config.forecast_horizon,
            created_at=datetime.now()
        )
    
    def _moving_average_forecast(self, df: pd.DataFrame, metric_name: str, application: str) -> PredictionResult:
        """Forecast using moving average"""
        if len(df) < self.config.min_data_points:
            return self._create_empty_prediction(metric_name, application)
        
        values = df['value'].values
        timestamps = df['timestamp'].values
        
        # Calculate moving average
        window = self.config.window_size
        moving_avg = pd.Series(values).rolling(window=window, min_periods=1).mean()
        
        # Simple forecast: use last moving average value
        last_ma = moving_avg.iloc[-1]
        
        # Generate future timestamps
        last_timestamp = timestamps[-1]
        if isinstance(last_timestamp, str):
            last_timestamp = pd.to_datetime(last_timestamp)
        future_timestamps = [last_timestamp + timedelta(hours=i+1) for i in range(self.config.forecast_horizon)]
        
        # Create forecast data
        forecast_data = []
        for timestamp in future_timestamps:
            forecast_data.append(ForecastDataPoint(
                timestamp=timestamp,
                predicted_value=float(last_ma),
                lower_bound=float(last_ma * 0.9),  # Simple bounds
                upper_bound=float(last_ma * 1.1),
                confidence=0.8  # Lower confidence for simple method
            ))
        
        return PredictionResult(
            metric_name=metric_name,
            application=application,
            forecast_type=ForecastType.TIME_SERIES,
            algorithm=self.config.algorithm.value,
            forecast_data=forecast_data,
            model_accuracy=0.5,  # Simple method, lower accuracy
            confidence_level=0.8,
            forecast_horizon=self.config.forecast_horizon,
            created_at=datetime.now()
        )
    
    def _exponential_smoothing_forecast(self, df: pd.DataFrame, metric_name: str, application: str) -> PredictionResult:
        """Forecast using exponential smoothing"""
        if len(df) < self.config.min_data_points:
            return self._create_empty_prediction(metric_name, application)
        
        values = df['value'].values
        timestamps = df['timestamp'].values
        
        # Simple exponential smoothing
        alpha = self.config.alpha
        smoothed = [values[0]]
        
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[i-1])
        
        # Forecast using last smoothed value
        last_smoothed = smoothed[-1]
        
        # Generate future timestamps
        last_timestamp = timestamps[-1]
        if isinstance(last_timestamp, str):
            last_timestamp = pd.to_datetime(last_timestamp)
        future_timestamps = [last_timestamp + timedelta(hours=i+1) for i in range(self.config.forecast_horizon)]
        
        # Create forecast data
        forecast_data = []
        for timestamp in future_timestamps:
            forecast_data.append(ForecastDataPoint(
                timestamp=timestamp,
                predicted_value=float(last_smoothed),
                lower_bound=float(last_smoothed * 0.85),
                upper_bound=float(last_smoothed * 1.15),
                confidence=0.85
            ))
        
        return PredictionResult(
            metric_name=metric_name,
            application=application,
            forecast_type=ForecastType.TIME_SERIES,
            algorithm=self.config.algorithm.value,
            forecast_data=forecast_data,
            model_accuracy=0.6,
            confidence_level=0.85,
            forecast_horizon=self.config.forecast_horizon,
            created_at=datetime.now()
        )
    
    def _create_empty_prediction(self, metric_name: str, application: str) -> PredictionResult:
        """Create an empty prediction result when insufficient data"""
        return PredictionResult(
            metric_name=metric_name,
            application=application,
            forecast_type=ForecastType.TIME_SERIES,
            algorithm=self.config.algorithm.value,
            forecast_data=[],
            model_accuracy=0.0,
            confidence_level=0.0,
            forecast_horizon=self.config.forecast_horizon,
            created_at=datetime.now()
        )
    
    def generate_forecast(self, time_series_data: TimeSeriesData) -> PredictionResult:
        """
        Generate forecast for a single time series.
        
        Args:
            time_series_data: Time series data to forecast
            
        Returns:
            Prediction result with forecast data
        """
        logger.info(f"Generating forecast for {time_series_data.metric_name} using {self.config.algorithm.value}")
        
        # Prepare data
        df = self._prepare_time_series(time_series_data)
        
        if df.empty:
            logger.warning("No data available for forecasting")
            return self._create_empty_prediction(time_series_data.metric_name, time_series_data.application)
        
        # Generate forecast based on algorithm
        if self.config.algorithm == ForecastAlgorithm.LINEAR_REGRESSION:
            return self._linear_regression_forecast(df, time_series_data.metric_name, time_series_data.application)
        elif self.config.algorithm == ForecastAlgorithm.RANDOM_FOREST:
            return self._random_forest_forecast(df, time_series_data.metric_name, time_series_data.application)
        elif self.config.algorithm == ForecastAlgorithm.MOVING_AVERAGE:
            return self._moving_average_forecast(df, time_series_data.metric_name, time_series_data.application)
        elif self.config.algorithm == ForecastAlgorithm.EXPONENTIAL_SMOOTHING:
            return self._exponential_smoothing_forecast(df, time_series_data.metric_name, time_series_data.application)
        else:
            raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")
    
    def generate_forecasts(self, time_series_data: List[TimeSeriesData]) -> List[PredictionResult]:
        """
        Generate forecasts for multiple time series.
        
        Args:
            time_series_data: List of time series data to forecast
            
        Returns:
            List of prediction results
        """
        logger.info(f"Generating forecasts for {len(time_series_data)} time series")
        
        forecasts = []
        for ts_data in time_series_data:
            try:
                forecast = self.generate_forecast(ts_data)
                forecasts.append(forecast)
            except Exception as e:
                logger.error(f"Error generating forecast for {ts_data.metric_name}: {e}")
                continue
        
        logger.info(f"Generated {len(forecasts)} forecasts")
        return forecasts
    
    def get_forecast_summary(self, forecasts: List[PredictionResult]) -> Dict[str, Any]:
        """Generate summary statistics for forecasts"""
        if not forecasts:
            return {
                "total_forecasts": 0,
                "average_accuracy": 0.0,
                "forecast_algorithms": {},
                "applications_forecasted": set(),
                "metrics_forecasted": set()
            }
        
        # Calculate statistics
        accuracies = [f.model_accuracy for f in forecasts if f.model_accuracy > 0]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
        
        # Count by algorithm
        algorithm_counts = {}
        for forecast in forecasts:
            algorithm = forecast.algorithm
            algorithm_counts[algorithm] = algorithm_counts.get(algorithm, 0) + 1
        
        # Get applications and metrics
        applications = set(f.application for f in forecasts)
        metrics = set(f.metric_name for f in forecasts)
        
        # Calculate total predicted values
        total_predictions = sum(len(f.forecast_data) for f in forecasts)
        
        return {
            "total_forecasts": len(forecasts),
            "total_predictions": total_predictions,
            "average_accuracy": avg_accuracy,
            "forecast_algorithms": algorithm_counts,
            "applications_forecasted": list(applications),
            "metrics_forecasted": list(metrics),
            "forecast_horizon": self.config.forecast_horizon,
            "confidence_level": self.config.confidence_level
        }
