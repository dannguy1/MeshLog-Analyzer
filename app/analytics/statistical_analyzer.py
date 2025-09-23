"""
Statistical Analysis Module

This module provides comprehensive statistical analysis for log data.
It includes descriptive statistics, trend analysis, distribution analysis, and more.
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from scipy import stats
from scipy.stats import norm, poisson, expon, gamma
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

from ..models.core import TimeSeriesData, StatisticalResult, DistributionType
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class StatisticType(Enum):
    """Types of statistical analysis"""
    DESCRIPTIVE = "descriptive"
    DISTRIBUTION = "distribution"
    TREND = "trend"
    CORRELATION = "correlation"
    OUTLIER = "outlier"
    SEASONALITY = "seasonality"

@dataclass
class StatisticalConfig:
    """Configuration for statistical analysis"""
    confidence_level: float = 0.95
    outlier_threshold: float = 3.0  # Z-score threshold
    min_data_points: int = 10
    seasonal_period: int = 24  # For seasonality analysis
    correlation_threshold: float = 0.5
    distribution_test_method: str = "ks"  # Kolmogorov-Smirnov test

class StatisticalAnalyzer:
    """
    Comprehensive statistical analysis for log data.
    
    Provides:
    - Descriptive statistics
    - Distribution analysis
    - Trend analysis
    - Correlation analysis
    - Outlier detection
    - Seasonality analysis
    """
    
    def __init__(self, config: Optional[StatisticalConfig] = None):
        """Initialize the statistical analyzer"""
        self.config = config or StatisticalConfig()
        
    def _prepare_data(self, time_series_data: TimeSeriesData) -> pd.DataFrame:
        """Prepare data for statistical analysis"""
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
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        
        return df
    
    def analyze_descriptive_statistics(self, time_series_data: TimeSeriesData) -> Dict[str, Any]:
        """Calculate descriptive statistics"""
        df = self._prepare_data(time_series_data)
        
        if df.empty:
            return {}
        
        values = df['value'].values
        
        # Basic statistics
        stats_dict = {
            'count': len(values),
            'mean': float(np.mean(values)),
            'median': float(np.median(values)),
            'std': float(np.std(values)),
            'variance': float(np.var(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'range': float(np.max(values) - np.min(values)),
            'q1': float(np.percentile(values, 25)),
            'q3': float(np.percentile(values, 75)),
            'iqr': float(np.percentile(values, 75) - np.percentile(values, 25)),
            'skewness': float(stats.skew(values)),
            'kurtosis': float(stats.kurtosis(values)),
            'coefficient_of_variation': float(np.std(values) / np.mean(values)) if np.mean(values) != 0 else 0.0
        }
        
        # Confidence intervals
        if len(values) > 1:
            confidence_interval = stats.t.interval(
                self.config.confidence_level, 
                len(values) - 1, 
                loc=np.mean(values), 
                scale=stats.sem(values)
            )
            stats_dict['confidence_interval'] = {
                'lower': float(confidence_interval[0]),
                'upper': float(confidence_interval[1]),
                'level': self.config.confidence_level
            }
        
        return stats_dict
    
    def analyze_distribution(self, time_series_data: TimeSeriesData) -> Dict[str, Any]:
        """Analyze the distribution of values"""
        df = self._prepare_data(time_series_data)
        
        if df.empty:
            return {}
        
        values = df['value'].values
        
        # Test different distributions
        distributions = {
            'normal': norm,
            'poisson': poisson,
            'exponential': expon,
            'gamma': gamma
        }
        
        best_fit = None
        best_p_value = 0
        best_params = None
        
        for dist_name, dist in distributions.items():
            try:
                # Fit distribution
                params = dist.fit(values)
                
                # Perform Kolmogorov-Smirnov test
                ks_statistic, p_value = stats.kstest(values, dist_name, params)
                
                if p_value > best_p_value:
                    best_fit = dist_name
                    best_p_value = p_value
                    best_params = params
                    
            except Exception as e:
                logger.debug(f"Could not fit {dist_name} distribution: {e}")
                continue
        
        # Calculate distribution statistics
        distribution_stats = {
            'best_fit': best_fit,
            'p_value': float(best_p_value) if best_p_value else 0.0,
            'is_normal': bool(best_fit == 'normal' and best_p_value > 0.05),
            'is_uniform': float(stats.kstest(values, 'uniform', (np.min(values), np.max(values)))[1]),
            'is_exponential': float(stats.kstest(values, 'expon', (0, np.mean(values)))[1])
        }
        
        # Add fitted parameters
        if best_params:
            distribution_stats['fitted_params'] = [float(p) for p in best_params]
        
        return distribution_stats
    
    def analyze_trend(self, time_series_data: TimeSeriesData) -> Dict[str, Any]:
        """Analyze trends in the time series"""
        df = self._prepare_data(time_series_data)
        
        if df.empty or len(df) < self.config.min_data_points:
            return {}
        
        values = df['value'].values
        timestamps = df['timestamp'].values
        
        # Linear trend
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Mann-Kendall trend test
        try:
            mk_statistic, mk_p_value = stats.kendalltau(x, values)
        except:
            mk_statistic, mk_p_value = 0, 1
        
        # Calculate trend strength
        trend_strength = abs(r_value)
        
        # Determine trend direction
        if p_value < 0.05:
            if slope > 0:
                trend_direction = "increasing"
            else:
                trend_direction = "decreasing"
        else:
            trend_direction = "no_significant_trend"
        
        # Calculate rate of change
        rate_of_change = np.diff(values)
        avg_rate_of_change = float(np.mean(rate_of_change)) if len(rate_of_change) > 0 else 0.0
        
        trend_stats = {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'std_error': float(std_err),
            'trend_direction': trend_direction,
            'trend_strength': float(trend_strength),
            'mann_kendall_statistic': float(mk_statistic),
            'mann_kendall_p_value': float(mk_p_value),
            'avg_rate_of_change': avg_rate_of_change,
            'is_significant': bool(p_value < 0.05)
        }
        
        return trend_stats
    
    def analyze_correlation(self, time_series_data: List[TimeSeriesData]) -> Dict[str, Any]:
        """Analyze correlations between multiple time series"""
        if len(time_series_data) < 2:
            return {}
        
        # Prepare data for correlation analysis
        correlation_data = {}
        
        for ts in time_series_data:
            df = self._prepare_data(ts)
            if not df.empty:
                correlation_data[f"{ts.application}_{ts.metric_name}"] = df['value'].values
        
        if len(correlation_data) < 2:
            return {}
        
        # Create correlation matrix
        df_corr = pd.DataFrame(correlation_data)
        
        # Calculate correlations
        pearson_corr = df_corr.corr(method='pearson')
        spearman_corr = df_corr.corr(method='spearman')
        kendall_corr = df_corr.corr(method='kendall')
        
        # Find significant correlations
        significant_correlations = []
        
        for i in range(len(pearson_corr.columns)):
            for j in range(i+1, len(pearson_corr.columns)):
                col1 = pearson_corr.columns[i]
                col2 = pearson_corr.columns[j]
                
                pearson_val = pearson_corr.iloc[i, j]
                spearman_val = spearman_corr.iloc[i, j]
                kendall_val = kendall_corr.iloc[i, j]
                
                if abs(pearson_val) > self.config.correlation_threshold:
                    significant_correlations.append({
                        'series1': col1,
                        'series2': col2,
                        'pearson': float(pearson_val),
                        'spearman': float(spearman_val),
                        'kendall': float(kendall_val),
                        'strength': 'strong' if abs(pearson_val) > 0.7 else 'moderate' if abs(pearson_val) > 0.5 else 'weak'
                    })
        
        return {
            'pearson_correlation': pearson_corr.to_dict(),
            'spearman_correlation': spearman_corr.to_dict(),
            'kendall_correlation': kendall_corr.to_dict(),
            'significant_correlations': significant_correlations,
            'total_correlations': len(significant_correlations)
        }
    
    def detect_outliers(self, time_series_data: TimeSeriesData) -> Dict[str, Any]:
        """Detect outliers using multiple methods"""
        df = self._prepare_data(time_series_data)
        
        if df.empty:
            return {}
        
        values = df['value'].values
        
        # Z-score method
        z_scores = np.abs(stats.zscore(values))
        z_outliers = z_scores > self.config.outlier_threshold
        
        # IQR method
        Q1 = np.percentile(values, 25)
        Q3 = np.percentile(values, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        iqr_outliers = (values < lower_bound) | (values > upper_bound)
        
        # Modified Z-score method (more robust)
        median = np.median(values)
        mad = np.median(np.abs(values - median))
        modified_z_scores = 0.6745 * (values - median) / mad
        modified_z_outliers = np.abs(modified_z_scores) > self.config.outlier_threshold
        
        # Combine methods
        combined_outliers = z_outliers | iqr_outliers | modified_z_outliers
        
        outlier_indices = np.where(combined_outliers)[0]
        outlier_values = values[outlier_indices]
        outlier_timestamps = df['timestamp'].iloc[outlier_indices].tolist()
        
        return {
            'total_outliers': int(np.sum(combined_outliers)),
            'outlier_percentage': float(np.sum(combined_outliers) / len(values) * 100),
            'z_score_outliers': int(np.sum(z_outliers)),
            'iqr_outliers': int(np.sum(iqr_outliers)),
            'modified_z_outliers': int(np.sum(modified_z_outliers)),
            'outlier_values': [float(v) for v in outlier_values],
            'outlier_timestamps': outlier_timestamps,
            'outlier_indices': [int(i) for i in outlier_indices],
            'thresholds': {
                'z_score': self.config.outlier_threshold,
                'iqr_lower': float(lower_bound),
                'iqr_upper': float(upper_bound)
            }
        }
    
    def analyze_seasonality(self, time_series_data: TimeSeriesData) -> Dict[str, Any]:
        """Analyze seasonality patterns"""
        df = self._prepare_data(time_series_data)
        
        if df.empty or len(df) < self.config.seasonal_period:
            return {}
        
        values = df['value'].values
        
        # Hourly patterns
        hourly_means = df.groupby('hour')['value'].mean()
        hourly_std = df.groupby('hour')['value'].std()
        
        # Daily patterns
        daily_means = df.groupby('day_of_week')['value'].mean()
        daily_std = df.groupby('day_of_week')['value'].std()
        
        # Monthly patterns
        monthly_means = df.groupby('month')['value'].mean()
        monthly_std = df.groupby('month')['value'].std()
        
        # Calculate seasonality strength
        overall_mean = np.mean(values)
        hourly_variance = np.var(hourly_means)
        daily_variance = np.var(daily_means)
        monthly_variance = np.var(monthly_means)
        
        total_variance = np.var(values)
        
        hourly_seasonality = hourly_variance / total_variance if total_variance > 0 else 0
        daily_seasonality = daily_variance / total_variance if total_variance > 0 else 0
        monthly_seasonality = monthly_variance / total_variance if total_variance > 0 else 0
        
        return {
            'hourly_patterns': {
                'means': hourly_means.to_dict(),
                'std': hourly_std.to_dict(),
                'seasonality_strength': float(hourly_seasonality)
            },
            'daily_patterns': {
                'means': daily_means.to_dict(),
                'std': daily_std.to_dict(),
                'seasonality_strength': float(daily_seasonality)
            },
            'monthly_patterns': {
                'means': monthly_means.to_dict(),
                'std': monthly_std.to_dict(),
                'seasonality_strength': float(monthly_seasonality)
            },
            'overall_seasonality': {
                'hourly': float(hourly_seasonality),
                'daily': float(daily_seasonality),
                'monthly': float(monthly_seasonality),
                'strongest_pattern': max(['hourly', 'daily', 'monthly'], 
                                      key=lambda x: [hourly_seasonality, daily_seasonality, monthly_seasonality][['hourly', 'daily', 'monthly'].index(x)])
            }
        }
    
    def comprehensive_analysis(self, time_series_data: TimeSeriesData) -> StatisticalResult:
        """Perform comprehensive statistical analysis"""
        logger.info(f"Performing comprehensive statistical analysis for {time_series_data.metric_name}")
        
        # Perform all analyses
        descriptive = self.analyze_descriptive_statistics(time_series_data)
        distribution = self.analyze_distribution(time_series_data)
        trend = self.analyze_trend(time_series_data)
        outliers = self.detect_outliers(time_series_data)
        seasonality = self.analyze_seasonality(time_series_data)
        
        # Create comprehensive result
        result = StatisticalResult(
            metric_name=time_series_data.metric_name,
            application=time_series_data.application,
            descriptive_statistics=descriptive,
            distribution_analysis=distribution,
            trend_analysis=trend,
            outlier_analysis=outliers,
            seasonality_analysis=seasonality,
            created_at=datetime.now()
        )
        
        return result
    
    def analyze_multiple_series(self, time_series_data: List[TimeSeriesData]) -> Dict[str, Any]:
        """Analyze multiple time series and their relationships"""
        logger.info(f"Analyzing {len(time_series_data)} time series")
        
        # Individual analyses
        individual_results = []
        for ts_data in time_series_data:
            try:
                result = self.comprehensive_analysis(ts_data)
                individual_results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {ts_data.metric_name}: {e}")
                continue
        
        # Correlation analysis
        correlation_results = self.analyze_correlation(time_series_data)
        
        # Summary statistics
        summary = {
            'total_series_analyzed': len(individual_results),
            'total_data_points': sum(len(ts.data_points) for ts in time_series_data),
            'applications_analyzed': list(set(ts.application for ts in time_series_data)),
            'metrics_analyzed': list(set(ts.metric_name for ts in time_series_data)),
            'correlation_analysis': correlation_results,
            'individual_results': individual_results
        }
        
        return summary
