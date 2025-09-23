"""
Real-time Monitoring Dashboard

This module provides real-time monitoring capabilities for the prplOS LCM Log Analysis System.
It includes live data streaming, alert management, and real-time visualization updates.
"""

import logging
import asyncio
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import websockets
from websockets.server import serve
import threading
import time

from ..models.core import AnalysisResult, AnomalyResult, LogLevel
from .chart_generator import ChartGenerator, ChartConfig, ChartType

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """Real-time alert"""
    id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    source: str
    metric_name: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

@dataclass
class MonitoringConfig:
    """Configuration for real-time monitoring"""
    update_interval: int = 5  # seconds
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    max_alerts: int = 100
    websocket_port: int = 8765
    enable_notifications: bool = True
    chart_update_interval: int = 10  # seconds

class RealTimeMonitor:
    """
    Real-time monitoring system for log analysis.
    
    Features:
    - Live data streaming
    - Real-time alert generation
    - WebSocket-based updates
    - Dynamic chart updates
    - Alert management
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        """Initialize the real-time monitor"""
        self.config = config or MonitoringConfig()
        self.chart_generator = ChartGenerator()
        self.connected_clients: List[websockets.WebSocketServerProtocol] = []
        self.alerts: List[Alert] = []
        self.current_analysis: Optional[AnalysisResult] = None
        self.monitoring_active = False
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
    async def start_monitoring(self, analysis_result: AnalysisResult):
        """Start real-time monitoring for an analysis result"""
        logger.info("Starting real-time monitoring")
        
        self.current_analysis = analysis_result
        self.monitoring_active = True
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_data())
        asyncio.create_task(self._update_charts())
        asyncio.create_task(self._check_alerts())
        
        logger.info("Real-time monitoring started")
    
    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        logger.info("Stopping real-time monitoring")
        self.monitoring_active = False
        self.current_analysis = None
        
        # Clear alerts
        self.alerts.clear()
        
        logger.info("Real-time monitoring stopped")
    
    async def _monitor_data(self):
        """Monitor data for changes and generate alerts"""
        while self.monitoring_active:
            try:
                if self.current_analysis:
                    # Check for new anomalies
                    await self._check_anomaly_alerts()
                    
                    # Check for threshold violations
                    await self._check_threshold_alerts()
                    
                    # Check for system health
                    await self._check_system_health()
                
                await asyncio.sleep(self.config.update_interval)
                
            except Exception as e:
                logger.error(f"Error in data monitoring: {e}")
                await asyncio.sleep(self.config.update_interval)
    
    async def _check_anomaly_alerts(self):
        """Check for new anomalies and generate alerts"""
        if not self.current_analysis or not self.current_analysis.anomalies:
            return
        
        # Check for high-severity anomalies
        for anomaly in self.current_analysis.anomalies:
            if anomaly.severity in ['high', 'critical']:
                alert = Alert(
                    id=f"anomaly_{anomaly.timestamp.strftime('%Y%m%d_%H%M%S')}",
                    severity=AlertSeverity.ERROR if anomaly.severity == 'high' else AlertSeverity.CRITICAL,
                    message=f"Anomaly detected: {anomaly.description}",
                    timestamp=anomaly.timestamp,
                    source="anomaly_detection",
                    metric_name=anomaly.metric_name,
                    value=anomaly.score,
                    threshold=3.0  # Default threshold
                )
                
                await self._add_alert(alert)
    
    async def _check_threshold_alerts(self):
        """Check for threshold violations"""
        if not self.current_analysis or not self.current_analysis.time_series_data:
            return
        
        for ts in self.current_analysis.time_series_data:
            if not ts.data_points:
                continue
            
            # Get latest value
            latest_point = ts.data_points[-1]
            metric_name = ts.metric_name
            
            # Check against configured thresholds
            if metric_name in self.config.alert_thresholds:
                threshold = self.config.alert_thresholds[metric_name]
                
                if latest_point.value > threshold:
                    alert = Alert(
                        id=f"threshold_{metric_name}_{latest_point.timestamp.strftime('%Y%m%d_%H%M%S')}",
                        severity=AlertSeverity.WARNING,
                        message=f"Threshold exceeded for {metric_name}: {latest_point.value:.2f} > {threshold}",
                        timestamp=latest_point.timestamp,
                        source="threshold_monitoring",
                        metric_name=metric_name,
                        value=latest_point.value,
                        threshold=threshold
                    )
                    
                    await self._add_alert(alert)
    
    async def _check_system_health(self):
        """Check overall system health"""
        if not self.current_analysis:
            return
        
        summary = self.current_analysis.summary
        
        # Check error rate
        total_entries = summary.get('total_entries', 0)
        error_count = summary.get('error_count', 0)
        
        if total_entries > 0:
            error_rate = error_count / total_entries
            
            if error_rate > 0.1:  # 10% error rate threshold
                alert = Alert(
                    id=f"system_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    severity=AlertSeverity.WARNING,
                    message=f"High error rate detected: {error_rate:.2%}",
                    timestamp=datetime.now(),
                    source="system_health",
                    value=error_rate,
                    threshold=0.1
                )
                
                await self._add_alert(alert)
    
    async def _add_alert(self, alert: Alert):
        """Add a new alert"""
        # Check if alert already exists
        existing_alert = next((a for a in self.alerts if a.id == alert.id), None)
        if existing_alert:
            return
        
        # Add alert
        self.alerts.append(alert)
        
        # Limit number of alerts
        if len(self.alerts) > self.config.max_alerts:
            self.alerts.pop(0)  # Remove oldest alert
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        # Broadcast to connected clients
        await self._broadcast_alert(alert)
        
        logger.info(f"New alert: {alert.severity.value} - {alert.message}")
    
    async def _update_charts(self):
        """Update charts periodically"""
        while self.monitoring_active:
            try:
                if self.current_analysis:
                    # Generate updated charts
                    charts = self.chart_generator.generate_all_charts(self.current_analysis)
                    
                    # Broadcast chart updates
                    await self._broadcast_charts(charts)
                
                await asyncio.sleep(self.config.chart_update_interval)
                
            except Exception as e:
                logger.error(f"Error updating charts: {e}")
                await asyncio.sleep(self.config.chart_update_interval)
    
    async def _broadcast_alert(self, alert: Alert):
        """Broadcast alert to connected clients"""
        message = {
            "type": "alert",
            "data": {
                "id": alert.id,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "source": alert.source,
                "metric_name": alert.metric_name,
                "value": alert.value,
                "threshold": alert.threshold
            }
        }
        
        await self._broadcast_message(message)
    
    async def _broadcast_charts(self, charts: Dict[str, Any]):
        """Broadcast chart updates to connected clients"""
        message = {
            "type": "charts_update",
            "data": charts
        }
        
        await self._broadcast_message(message)
    
    async def _broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.connected_clients:
            return
        
        message_json = json.dumps(message)
        disconnected_clients = []
        
        for client in self.connected_clients:
            try:
                await client.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.connected_clients.remove(client)
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        logger.info("New WebSocket client connected")
        self.connected_clients.append(websocket)
        
        try:
            # Send initial data
            if self.current_analysis:
                charts = self.chart_generator.generate_all_charts(self.current_analysis)
                initial_message = {
                    "type": "initial_data",
                    "data": {
                        "analysis": self.current_analysis.to_dict(),
                        "charts": charts,
                        "alerts": [alert.__dict__ for alert in self.alerts[-10:]]  # Last 10 alerts
                    }
                }
                await websocket.send(json.dumps(initial_message))
            
            # Handle client messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON message received")
                except Exception as e:
                    logger.error(f"Error handling client message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket client disconnected")
        finally:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
    
    async def _handle_client_message(self, websocket, data: Dict[str, Any]):
        """Handle messages from WebSocket clients"""
        message_type = data.get("type")
        
        if message_type == "acknowledge_alert":
            alert_id = data.get("alert_id")
            user = data.get("user", "unknown")
            await self._acknowledge_alert(alert_id, user)
            
        elif message_type == "request_chart":
            chart_type = data.get("chart_type")
            await self._send_chart(websocket, chart_type)
            
        elif message_type == "update_config":
            config_data = data.get("config", {})
            await self._update_config(config_data)
    
    async def _acknowledge_alert(self, alert_id: str, user: str):
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.acknowledged:
                alert.acknowledged = True
                alert.acknowledged_by = user
                alert.acknowledged_at = datetime.now()
                
                # Broadcast acknowledgment
                message = {
                    "type": "alert_acknowledged",
                    "data": {
                        "alert_id": alert_id,
                        "acknowledged_by": user,
                        "acknowledged_at": alert.acknowledged_at.isoformat()
                    }
                }
                await self._broadcast_message(message)
                break
    
    async def _send_chart(self, websocket, chart_type: str):
        """Send specific chart to client"""
        if not self.current_analysis:
            return
        
        try:
            if chart_type == "time_series":
                chart = self.chart_generator.create_time_series_chart(
                    self.current_analysis.time_series_data,
                    self.current_analysis.anomalies,
                    self.current_analysis.predictions
                )
            elif chart_type == "anomalies":
                chart = self.chart_generator.create_anomaly_chart(self.current_analysis.anomalies)
            elif chart_type == "predictions":
                chart = self.chart_generator.create_prediction_chart(self.current_analysis.predictions)
            elif chart_type == "dashboard":
                chart = self.chart_generator.create_dashboard(self.current_analysis)
            else:
                return
            
            message = {
                "type": "chart_response",
                "data": {
                    "chart_type": chart_type,
                    "chart": chart
                }
            }
            
            await websocket.send(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Error sending chart {chart_type}: {e}")
    
    async def _update_config(self, config_data: Dict[str, Any]):
        """Update monitoring configuration"""
        if "alert_thresholds" in config_data:
            self.config.alert_thresholds.update(config_data["alert_thresholds"])
        
        if "update_interval" in config_data:
            self.config.update_interval = config_data["update_interval"]
        
        if "chart_update_interval" in config_data:
            self.config.chart_update_interval = config_data["chart_update_interval"]
        
        logger.info("Monitoring configuration updated")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback for new alerts"""
        self.alert_callbacks.append(callback)
    
    def get_alerts(self, severity: Optional[AlertSeverity] = None, 
                   acknowledged: Optional[bool] = None) -> List[Alert]:
        """Get alerts with optional filtering"""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]
        
        return alerts
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        total_alerts = len(self.alerts)
        unacknowledged = len([a for a in self.alerts if not a.acknowledged])
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([a for a in self.alerts if a.severity == severity])
        
        return {
            "total_alerts": total_alerts,
            "unacknowledged_alerts": unacknowledged,
            "severity_distribution": severity_counts,
            "latest_alert": self.alerts[-1].__dict__ if self.alerts else None
        }
    
    async def start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        logger.info(f"Starting WebSocket server on port {self.config.websocket_port}")
        
        async with serve(self.handle_websocket_connection, "localhost", self.config.websocket_port):
            await asyncio.Future()  # Run forever
