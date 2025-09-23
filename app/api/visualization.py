"""
Visualization API Endpoints

This module provides FastAPI endpoints for the visualization system,
including chart generation, real-time monitoring, and dashboard management.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime

from ..models.core import AnalysisResult
from ..visualization.chart_generator import ChartGenerator, ChartConfig, ChartType
from ..visualization.realtime_monitor import RealTimeMonitor, MonitoringConfig, AlertSeverity

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/visualization", tags=["visualization"])

# Global instances
chart_generator = ChartGenerator()
real_time_monitor = RealTimeMonitor()

class ChartRequest(BaseModel):
    """Request model for chart generation"""
    analysis_id: str
    chart_type: str
    config: Optional[Dict[str, Any]] = None

class DashboardRequest(BaseModel):
    """Request model for dashboard generation"""
    analysis_id: str
    include_charts: List[str] = ["time_series", "anomalies", "predictions", "statistics"]
    layout: Optional[Dict[str, Any]] = None

class MonitoringRequest(BaseModel):
    """Request model for monitoring configuration"""
    analysis_id: str
    alert_thresholds: Optional[Dict[str, float]] = None
    update_interval: Optional[int] = 5
    enable_notifications: bool = True

class AlertResponse(BaseModel):
    """Response model for alerts"""
    id: str
    severity: str
    message: str
    timestamp: str
    source: str
    metric_name: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None

@router.post("/charts/generate")
async def generate_chart(request: ChartRequest) -> Dict[str, Any]:
    """Generate a specific chart for an analysis"""
    try:
        logger.info(f"Generating chart {request.chart_type} for analysis {request.analysis_id}")
        
        # TODO: Load analysis result from database
        # For now, we'll return a mock response
        analysis_result = _get_mock_analysis_result(request.analysis_id)
        
        if not analysis_result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Create chart configuration (without ChartType conversion to avoid enum issues)
        chart_config = ChartConfig(
            chart_type=ChartType.TIME_SERIES,  # Default, not used in this flow
            **request.config or {}
        )
        
        # Generate chart
        if request.chart_type == "time_series":
            chart = chart_generator.create_time_series_chart(
                analysis_result.time_series_data,
                analysis_result.anomalies,
                analysis_result.predictions
            )
        elif request.chart_type == "anomalies":
            chart = chart_generator.create_anomaly_chart(analysis_result.anomalies)
        elif request.chart_type == "predictions":
            chart = chart_generator.create_prediction_chart(analysis_result.predictions)
        elif request.chart_type == "statistics":
            chart = chart_generator.create_statistical_chart(analysis_result.statistical_results)
        elif request.chart_type == "dashboard":
            chart = chart_generator.create_dashboard(analysis_result)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported chart type: {request.chart_type}")
        
        return {
            "success": True,
            "analysis_id": request.analysis_id,
            "chart_type": request.chart_type,
            "chart": chart,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")

@router.post("/dashboard/generate")
async def generate_dashboard(request: DashboardRequest) -> Dict[str, Any]:
    """Generate a comprehensive dashboard for an analysis"""
    try:
        logger.info(f"Generating dashboard for analysis {request.analysis_id}")
        
        # TODO: Load analysis result from database
        analysis_result = _get_mock_analysis_result(request.analysis_id)
        
        if not analysis_result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Generate all requested charts
        charts = {}
        
        for chart_type in request.include_charts:
            try:
                if chart_type == "time_series":
                    charts[chart_type] = chart_generator.create_time_series_chart(
                        analysis_result.time_series_data,
                        analysis_result.anomalies,
                        analysis_result.predictions
                    )
                elif chart_type == "anomalies":
                    charts[chart_type] = chart_generator.create_anomaly_chart(analysis_result.anomalies)
                elif chart_type == "predictions":
                    charts[chart_type] = chart_generator.create_prediction_chart(analysis_result.predictions)
                elif chart_type == "statistics":
                    charts[chart_type] = chart_generator.create_statistical_chart(analysis_result.statistical_results)
                elif chart_type == "dashboard":
                    charts[chart_type] = chart_generator.create_dashboard(analysis_result)
            except Exception as e:
                logger.warning(f"Error generating chart {chart_type}: {e}")
                charts[chart_type] = {"error": str(e)}
        
        return {
            "success": True,
            "analysis_id": request.analysis_id,
            "dashboard": {
                "charts": charts,
                "layout": request.layout or "default",
                "total_charts": len(charts),
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")

@router.post("/monitoring/start")
async def start_monitoring(request: MonitoringRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Start real-time monitoring for an analysis"""
    try:
        logger.info(f"Starting monitoring for analysis {request.analysis_id}")
        
        # TODO: Load analysis result from database
        analysis_result = _get_mock_analysis_result(request.analysis_id)
        
        if not analysis_result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Configure monitoring
        config = MonitoringConfig(
            alert_thresholds=request.alert_thresholds or {},
            update_interval=request.update_interval,
            enable_notifications=request.enable_notifications
        )
        
        # Start monitoring in background
        background_tasks.add_task(real_time_monitor.start_monitoring, analysis_result)
        
        return {
            "success": True,
            "analysis_id": request.analysis_id,
            "monitoring": {
                "status": "started",
                "websocket_port": real_time_monitor.config.websocket_port,
                "alert_thresholds": config.alert_thresholds,
                "update_interval": config.update_interval,
                "started_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting monitoring: {str(e)}")

@router.post("/monitoring/stop")
async def stop_monitoring(analysis_id: str) -> Dict[str, Any]:
    """Stop real-time monitoring for an analysis"""
    try:
        logger.info(f"Stopping monitoring for analysis {analysis_id}")
        
        await real_time_monitor.stop_monitoring()
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "monitoring": {
                "status": "stopped",
                "stopped_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Error stopping monitoring: {str(e)}")

@router.get("/monitoring/alerts")
async def get_alerts(
    analysis_id: str,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None
) -> List[AlertResponse]:
    """Get alerts for an analysis"""
    try:
        # Filter alerts
        alerts = real_time_monitor.get_alerts(
            severity=AlertSeverity(severity) if severity else None,
            acknowledged=acknowledged
        )
        
        # Convert to response format
        alert_responses = []
        for alert in alerts:
            alert_responses.append(AlertResponse(
                id=alert.id,
                severity=alert.severity.value,
                message=alert.message,
                timestamp=alert.timestamp.isoformat(),
                source=alert.source,
                metric_name=alert.metric_name,
                value=alert.value,
                threshold=alert.threshold,
                acknowledged=alert.acknowledged,
                acknowledged_by=alert.acknowledged_by,
                acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
            ))
        
        return alert_responses
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting alerts: {str(e)}")

@router.get("/monitoring/alerts/summary")
async def get_alert_summary(analysis_id: str) -> Dict[str, Any]:
    """Get alert summary statistics"""
    try:
        summary = real_time_monitor.get_alert_summary()
        
        return {
            "analysis_id": analysis_id,
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting alert summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting alert summary: {str(e)}")

@router.post("/monitoring/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user: str = "unknown") -> Dict[str, Any]:
    """Acknowledge an alert"""
    try:
        # Find and acknowledge alert
        for alert in real_time_monitor.alerts:
            if alert.id == alert_id and not alert.acknowledged:
                alert.acknowledged = True
                alert.acknowledged_by = user
                alert.acknowledged_at = datetime.now()
                
                return {
                    "success": True,
                    "alert_id": alert_id,
                    "acknowledged_by": user,
                    "acknowledged_at": alert.acknowledged_at.isoformat()
                }
        
        raise HTTPException(status_code=404, detail="Alert not found or already acknowledged")
        
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=f"Error acknowledging alert: {str(e)}")

@router.websocket("/ws/{analysis_id}")
async def websocket_endpoint(websocket: WebSocket, analysis_id: str):
    """WebSocket endpoint for real-time updates"""
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection established for analysis {analysis_id}")
        
        # Add to monitor's client list
        real_time_monitor.connected_clients.append(websocket)
        
        try:
            # Send initial data
            if real_time_monitor.current_analysis:
                charts = chart_generator.generate_all_charts(real_time_monitor.current_analysis)
                initial_message = {
                    "type": "initial_data",
                    "data": {
                        "analysis_id": analysis_id,
                        "charts": charts,
                        "alerts": [alert.__dict__ for alert in real_time_monitor.alerts[-10:]]
                    }
                }
                await websocket.send_text(str(initial_message))
            
            # Handle messages
            while True:
                message = await websocket.receive_text()
                # Handle client messages here
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for analysis {analysis_id}")
        finally:
            if websocket in real_time_monitor.connected_clients:
                real_time_monitor.connected_clients.remove(websocket)
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for visualization system"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "chart_generator": "active",
            "real_time_monitor": "active" if real_time_monitor.monitoring_active else "inactive",
            "websocket_server": "active"
        }
    }

def _get_mock_analysis_result(analysis_id: str) -> Optional[AnalysisResult]:
    """Get a mock analysis result for testing"""
    # This is a placeholder - in production, this would load from database
    from ..analytics.advanced_analysis_engine import AdvancedAnalysisEngine
    from ..analytics.anomaly_detector import AnomalyConfig, AnomalyAlgorithm
    from ..analytics.predictive_analytics import ForecastConfig, ForecastAlgorithm
    
    # Create mock analysis result
    analysis_result = AnalysisResult(
        analysis_id=analysis_id,
        project_name="test-project",
        summary={
            "total_entries": 200,
            "unique_applications": 4,
            "error_count": 20,
            "warning_count": 40
        },
        time_series_data=[],
        event_patterns=[],
        correlations=[],
        anomalies=[],
        predictions=[],
        statistical_results=[],
        recommendations=["System appears to be operating normally"],
        application_insights={},
        system_insights={}
    )
    
    return analysis_result
