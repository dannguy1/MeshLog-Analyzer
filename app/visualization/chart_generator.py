"""
Chart Generator Module

This module provides comprehensive chart generation capabilities for the prplOS LCM Log Analysis System.
It creates interactive visualizations for time series data, anomalies, predictions, and statistical analysis.
"""

import logging
import json
import base64
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dataclasses import dataclass
from enum import Enum

from ..models.core import (
    TimeSeriesData, AnomalyResult, PredictionResult, StatisticalResult,
    AnalysisResult, AnomalyType, ForecastType
)

logger = logging.getLogger(__name__)

class ChartType(Enum):
    """Supported chart types"""
    TIME_SERIES = "time_series"
    ANOMALY_CHART = "anomaly_chart"
    PREDICTION_CHART = "prediction_chart"
    STATISTICAL_CHART = "statistical_chart"
    CORRELATION_HEATMAP = "correlation_heatmap"
    DISTRIBUTION_PLOT = "distribution_plot"
    SEASONALITY_PLOT = "seasonality_plot"
    DASHBOARD = "dashboard"

@dataclass
class ChartConfig:
    """Configuration for chart generation"""
    chart_type: ChartType
    title: str = ""
    width: int = 800
    height: int = 600
    theme: str = "plotly_white"
    show_legend: bool = True
    interactive: bool = True
    export_format: str = "html"  # html, png, svg, json

class ChartGenerator:
    """
    Advanced chart generator for log analysis visualizations.
    
    Supports multiple chart types:
    - Time series charts with annotations
    - Anomaly detection visualizations
    - Prediction charts with confidence intervals
    - Statistical analysis plots
    - Interactive dashboards
    """
    
    def __init__(self, config: Optional[ChartConfig] = None):
        """Initialize the chart generator"""
        self.config = config or ChartConfig(chart_type=ChartType.TIME_SERIES)
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#8c564b',
            'dark': '#e377c2'
        }
        
    def create_time_series_chart(self, time_series_data: List[TimeSeriesData], 
                                anomalies: Optional[List[AnomalyResult]] = None,
                                predictions: Optional[List[PredictionResult]] = None) -> Dict[str, Any]:
        """Create comprehensive time series chart with anomalies and predictions"""
        logger.info("Creating time series chart")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Time Series Data', 'Anomalies', 'Predictions'),
            row_heights=[0.6, 0.2, 0.2]
        )
        
        # Plot time series data
        for ts in time_series_data:
            timestamps = [point.timestamp for point in ts.data_points]
            values = [point.value for point in ts.data_points]
            
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines+markers',
                    name=f"{ts.metric_name} ({ts.application})",
                    line=dict(width=2),
                    marker=dict(size=4)
                ),
                row=1, col=1
            )
        
        # Add anomalies if provided
        if anomalies:
            anomaly_timestamps = [anomaly.timestamp for anomaly in anomalies]
            anomaly_values = [anomaly.score for anomaly in anomalies]
            anomaly_colors = ['red' if anomaly.severity == 'high' else 'orange' 
                             for anomaly in anomalies]
            
            fig.add_trace(
                go.Scatter(
                    x=anomaly_timestamps,
                    y=anomaly_values,
                    mode='markers',
                    name='Anomalies',
                    marker=dict(
                        size=8,
                        color=anomaly_colors,
                        symbol='diamond'
                    ),
                    hovertemplate='<b>Anomaly</b><br>' +
                                'Time: %{x}<br>' +
                                'Score: %{y:.2f}<br>' +
                                '<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Add predictions if provided
        if predictions:
            for prediction in predictions:
                if prediction.forecast_data:
                    pred_timestamps = [point.timestamp for point in prediction.forecast_data]
                    pred_values = [point.predicted_value for point in prediction.forecast_data]
                    lower_bounds = [point.lower_bound for point in prediction.forecast_data]
                    upper_bounds = [point.upper_bound for point in prediction.forecast_data]
                    
                    # Add confidence interval
                    fig.add_trace(
                        go.Scatter(
                            x=pred_timestamps,
                            y=upper_bounds,
                            mode='lines',
                            line=dict(width=0),
                            showlegend=False,
                            hoverinfo='skip'
                        ),
                        row=3, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=pred_timestamps,
                            y=lower_bounds,
                            mode='lines',
                            line=dict(width=0),
                            fill='tonexty',
                            fillcolor='rgba(31, 119, 180, 0.2)',
                            showlegend=False,
                            hoverinfo='skip'
                        ),
                        row=3, col=1
                    )
                    
                    # Add prediction line
                    fig.add_trace(
                        go.Scatter(
                            x=pred_timestamps,
                            y=pred_values,
                            mode='lines+markers',
                            name=f"Prediction ({prediction.algorithm})",
                            line=dict(dash='dash', width=2),
                            marker=dict(size=4)
                        ),
                        row=3, col=1
                    )
        
        # Update layout
        fig.update_layout(
            title=self.config.title or "Time Series Analysis",
            width=self.config.width,
            height=self.config.height,
            template=self.config.theme,
            showlegend=self.config.show_legend,
            hovermode='x unified'
        )
        
        # Update axes
        fig.update_xaxes(title_text="Time", row=3, col=1)
        fig.update_yaxes(title_text="Value", row=1, col=1)
        fig.update_yaxes(title_text="Anomaly Score", row=2, col=1)
        fig.update_yaxes(title_text="Predicted Value", row=3, col=1)
        
        return self._format_chart_output(fig)
    
    def create_anomaly_chart(self, anomalies: List[AnomalyResult]) -> Dict[str, Any]:
        """Create specialized anomaly visualization"""
        logger.info("Creating anomaly chart")
        
        # Handle empty anomalies case
        if not anomalies:
            fig = go.Figure()
            fig.add_annotation(
                text="No anomalies detected",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title="Anomaly Detection Results",
                width=self.config.width,
                height=self.config.height,
                template=self.config.theme,
                showlegend=False
            )
            return self._format_chart_output(fig)
        
        # Group anomalies by type
        anomaly_types = {}
        for anomaly in anomalies:
            if anomaly.anomaly_type.value not in anomaly_types:
                anomaly_types[anomaly.anomaly_type.value] = []
            anomaly_types[anomaly.anomaly_type.value].append(anomaly)
        
        # Create subplots for different anomaly types
        n_types = len(anomaly_types)
        fig = make_subplots(
            rows=n_types, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=list(anomaly_types.keys())
        )
        
        colors = ['red', 'orange', 'yellow', 'purple']
        
        for i, (anomaly_type, anomaly_list) in enumerate(anomaly_types.items()):
            timestamps = [anomaly.timestamp for anomaly in anomaly_list]
            scores = [anomaly.score for anomaly in anomaly_list]
            severities = [anomaly.severity for anomaly in anomaly_list]
            
            # Color by severity
            color_map = {'high': 'red', 'medium': 'orange', 'low': 'yellow'}
            colors = [color_map.get(severity, 'blue') for severity in severities]
            
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=scores,
                    mode='markers',
                    name=anomaly_type,
                    marker=dict(
                        size=10,
                        color=colors,
                        symbol='diamond'
                    ),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                'Time: %{x}<br>' +
                                'Score: %{y:.2f}<br>' +
                                'Severity: %{marker.color}<br>' +
                                '<extra></extra>'
                ),
                row=i+1, col=1
            )
        
        fig.update_layout(
            title="Anomaly Detection Results",
            width=self.config.width,
            height=self.config.height,
            template=self.config.theme,
            showlegend=self.config.show_legend
        )
        
        return self._format_chart_output(fig)
    
    def create_prediction_chart(self, predictions: List[PredictionResult]) -> Dict[str, Any]:
        """Create prediction visualization with confidence intervals"""
        logger.info("Creating prediction chart")
        
        # Handle empty predictions case
        if not predictions:
            fig = go.Figure()
            fig.add_annotation(
                text="No predictions available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title="Prediction Results",
                width=self.config.width,
                height=self.config.height,
                template=self.config.theme,
                showlegend=False
            )
            return self._format_chart_output(fig)
        
        fig = go.Figure()
        
        for prediction in predictions:
            if prediction.forecast_data:
                timestamps = [point.timestamp for point in prediction.forecast_data]
                values = [point.predicted_value for point in prediction.forecast_data]
                lower_bounds = [point.lower_bound for point in prediction.forecast_data]
                upper_bounds = [point.upper_bound for point in prediction.forecast_data]
                
                # Add confidence interval
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=upper_bounds,
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo='skip'
                    )
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=lower_bounds,
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor=f'rgba(31, 119, 180, 0.2)',
                        showlegend=False,
                        hoverinfo='skip'
                    )
                )
                
                # Add prediction line
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=values,
                        mode='lines+markers',
                        name=f"{prediction.metric_name} ({prediction.algorithm})",
                        line=dict(dash='dash', width=2),
                        marker=dict(size=4)
                    )
                )
        
        fig.update_layout(
            title="Predictive Analytics Results",
            xaxis_title="Time",
            yaxis_title="Predicted Value",
            width=self.config.width,
            height=self.config.height,
            template=self.config.theme,
            showlegend=self.config.show_legend,
            hovermode='x unified'
        )
        
        return self._format_chart_output(fig)
    
    def create_statistical_chart(self, statistical_results: List[StatisticalResult]) -> Dict[str, Any]:
        """Create statistical analysis visualizations"""
        logger.info("Creating statistical chart")
        
        # Handle empty statistical results case
        if not statistical_results:
            fig = go.Figure()
            fig.add_annotation(
                text="No statistical data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title="Statistical Analysis Results",
                width=self.config.width,
                height=self.config.height,
                template=self.config.theme,
                showlegend=False
            )
            return self._format_chart_output(fig)
        
        # Create subplots for different statistical aspects
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribution', 'Trend Analysis', 'Outliers', 'Seasonality'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        for result in statistical_results:
            # Distribution plot
            if 'distribution_analysis' in result.descriptive_statistics:
                desc_stats = result.descriptive_statistics
                fig.add_trace(
                    go.Histogram(
                        x=desc_stats.get('sample_data', []),
                        name=f"{result.metric_name} Distribution",
                        nbinsx=20,
                        opacity=0.7
                    ),
                    row=1, col=1
                )
            
            # Trend analysis
            if 'trend_analysis' in result.trend_analysis:
                trend_data = result.trend_analysis
                if 'trend_line' in trend_data:
                    fig.add_trace(
                        go.Scatter(
                            x=trend_data.get('x_values', []),
                            y=trend_data.get('trend_line', []),
                            mode='lines',
                            name=f"{result.metric_name} Trend",
                            line=dict(width=2)
                        ),
                        row=1, col=2
                    )
            
            # Outliers
            if 'outlier_analysis' in result.outlier_analysis:
                outliers = result.outlier_analysis.get('outliers', [])
                if outliers:
                    fig.add_trace(
                        go.Scatter(
                            x=range(len(outliers)),
                            y=outliers,
                            mode='markers',
                            name=f"{result.metric_name} Outliers",
                            marker=dict(color='red', size=8, symbol='diamond')
                        ),
                        row=2, col=1
                    )
            
            # Seasonality
            if 'seasonality_analysis' in result.seasonality_analysis:
                seasonality = result.seasonality_analysis.get('seasonal_patterns', {})
                if 'hourly' in seasonality:
                    hourly_pattern = seasonality['hourly']
                    fig.add_trace(
                        go.Scatter(
                            x=list(hourly_pattern.keys()),
                            y=list(hourly_pattern.values()),
                            mode='lines+markers',
                            name=f"{result.metric_name} Hourly Pattern",
                            line=dict(width=2)
                        ),
                        row=2, col=2
                    )
        
        fig.update_layout(
            title="Statistical Analysis Results",
            width=self.config.width,
            height=self.config.height,
            template=self.config.theme,
            showlegend=self.config.show_legend
        )
        
        return self._format_chart_output(fig)
    
    def create_correlation_heatmap(self, correlations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create correlation heatmap visualization"""
        logger.info("Creating correlation heatmap")
        
        # Extract correlation data
        metrics = set()
        for corr in correlations:
            metrics.add(corr.get('metric1', ''))
            metrics.add(corr.get('metric2', ''))
        
        metrics = sorted(list(metrics))
        correlation_matrix = np.zeros((len(metrics), len(metrics)))
        
        # Fill correlation matrix
        for corr in correlations:
            metric1 = corr.get('metric1', '')
            metric2 = corr.get('metric2', '')
            correlation = corr.get('correlation', 0)
            
            if metric1 in metrics and metric2 in metrics:
                i = metrics.index(metric1)
                j = metrics.index(metric2)
                correlation_matrix[i][j] = correlation
                correlation_matrix[j][i] = correlation  # Symmetric
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=metrics,
            y=metrics,
            colorscale='RdBu',
            zmid=0,
            text=np.round(correlation_matrix, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Metric Correlations",
            xaxis_title="Metrics",
            yaxis_title="Metrics",
            width=self.config.width,
            height=self.config.height,
            template=self.config.theme
        )
        
        return self._format_chart_output(fig)
    
    def create_dashboard(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Create comprehensive dashboard with multiple charts"""
        logger.info("Creating analysis dashboard")
        
        # Create dashboard layout
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Time Series Overview', 'Anomaly Distribution',
                'Predictions', 'Statistical Summary',
                'Application Performance', 'System Health'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Time Series Overview
        if analysis_result.time_series_data:
            for ts in analysis_result.time_series_data[:3]:  # Show first 3 series
                timestamps = [point.timestamp for point in ts.data_points]
                values = [point.value for point in ts.data_points]
                
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=values,
                        mode='lines',
                        name=f"{ts.metric_name} ({ts.application})",
                        line=dict(width=1)
                    ),
                    row=1, col=1
                )
        
        # Anomaly Distribution
        if analysis_result.anomalies:
            anomaly_types = {}
            for anomaly in analysis_result.anomalies:
                anomaly_type = anomaly.anomaly_type.value
                if anomaly_type not in anomaly_types:
                    anomaly_types[anomaly_type] = 0
                anomaly_types[anomaly_type] += 1
            
            fig.add_trace(
                go.Bar(
                    x=list(anomaly_types.keys()),
                    y=list(anomaly_types.values()),
                    name="Anomalies by Type"
                ),
                row=1, col=2
            )
        
        # Predictions
        if analysis_result.predictions:
            for prediction in analysis_result.predictions[:2]:  # Show first 2 predictions
                if prediction.forecast_data:
                    timestamps = [point.timestamp for point in prediction.forecast_data]
                    values = [point.predicted_value for point in prediction.forecast_data]
                    
                    fig.add_trace(
                        go.Scatter(
                            x=timestamps,
                            y=values,
                            mode='lines+markers',
                            name=f"Prediction ({prediction.algorithm})",
                            line=dict(dash='dash')
                        ),
                        row=2, col=1
                    )
        
        # Statistical Summary
        if analysis_result.statistical_results:
            metrics = []
            means = []
            for result in analysis_result.statistical_results:
                metrics.append(result.metric_name)
                means.append(result.descriptive_statistics.get('mean', 0))
            
            fig.add_trace(
                go.Bar(
                    x=metrics,
                    y=means,
                    name="Mean Values"
                ),
                row=2, col=2
            )
        
        # Application Performance
        if analysis_result.application_insights:
            apps = list(analysis_result.application_insights.keys())[:5]  # Top 5 apps
            error_rates = []
            for app in apps:
                insights = analysis_result.application_insights[app]
                error_rate = insights.get('error_rate', 0)
                error_rates.append(error_rate)
            
            fig.add_trace(
                go.Bar(
                    x=apps,
                    y=error_rates,
                    name="Error Rates"
                ),
                row=3, col=1
            )
        
        # System Health (summary metrics)
        summary = analysis_result.summary
        health_metrics = ['total_entries', 'unique_applications', 'error_count']
        health_values = [summary.get(metric, 0) for metric in health_metrics]
        
        fig.add_trace(
                go.Bar(
                    x=health_metrics,
                    y=health_values,
                    name="System Metrics"
                ),
                row=3, col=2
            )
        
        fig.update_layout(
            title=f"Analysis Dashboard - {analysis_result.project_name}",
            width=self.config.width,
            height=self.config.height * 1.5,  # Larger for dashboard
            template=self.config.theme,
            showlegend=True
        )
        
        return self._format_chart_output(fig)
    
    def _format_chart_output(self, fig) -> Dict[str, Any]:
        """Format chart output based on configuration"""
        if self.config.export_format == "html":
            return {
                "type": "html",
                "data": fig.to_html(include_plotlyjs=True, full_html=False),
                "config": {
                    "responsive": True,
                    "displayModeBar": self.config.interactive
                }
            }
        elif self.config.export_format == "json":
            return {
                "type": "json",
                "data": fig.to_json(),
                "config": {
                    "responsive": True,
                    "displayModeBar": self.config.interactive
                }
            }
        elif self.config.export_format == "png":
            img_bytes = fig.to_image(format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            return {
                "type": "png",
                "data": f"data:image/png;base64,{img_base64}",
                "config": {
                    "width": self.config.width,
                    "height": self.config.height
                }
            }
        else:
            return {
                "type": "html",
                "data": fig.to_html(include_plotlyjs=True, full_html=False),
                "config": {
                    "responsive": True,
                    "displayModeBar": self.config.interactive
                }
            }
    
    def generate_all_charts(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Generate all chart types for an analysis result"""
        logger.info("Generating all charts for analysis result")
        
        charts = {}
        
        # Time series chart
        if analysis_result.time_series_data:
            charts['time_series'] = self.create_time_series_chart(
                analysis_result.time_series_data,
                analysis_result.anomalies,
                analysis_result.predictions
            )
        
        # Anomaly chart
        if analysis_result.anomalies:
            charts['anomalies'] = self.create_anomaly_chart(analysis_result.anomalies)
        
        # Prediction chart
        if analysis_result.predictions:
            charts['predictions'] = self.create_prediction_chart(analysis_result.predictions)
        
        # Statistical chart
        if analysis_result.statistical_results:
            charts['statistics'] = self.create_statistical_chart(analysis_result.statistical_results)
        
        # Dashboard
        charts['dashboard'] = self.create_dashboard(analysis_result)
        
        return {
            "analysis_id": analysis_result.analysis_id,
            "project_name": analysis_result.project_name,
            "charts": charts,
            "metadata": {
                "total_charts": len(charts),
                "generated_at": datetime.now().isoformat(),
                "chart_types": list(charts.keys())
            }
        }
