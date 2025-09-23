"""
Agent Analysis API endpoints
Provides integration with wnc-log-agents service and future on-demand spawning
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Path, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import structlog
from app.core.agent_orchestrator import AgentOrchestrator
from app.services.agent_service_client import AgentServiceClient
from app.services.file_system_integration import FileSystemIntegration
from app.services.data_preparation_service import DataPreparationService
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

# Pydantic models for structured responses
class AnalysisRequest(BaseModel):
    agent_type: str
    analysis_config: Dict[str, Any] = {}

class AnalysisResponse(BaseModel):
    status: str
    analysis_id: Optional[str] = None
    agent_type: Optional[str] = None
    execution_mode: Optional[str] = None
    project_id: Optional[str] = None
    application_name: Optional[str] = None
    message: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class AgentMetadataResponse(BaseModel):
    agent_type: str
    execution_mode: str
    metadata: Dict[str, Any]
    available: bool = True

class HealthResponse(BaseModel):
    status: str
    total_agents: int
    agent_types: List[str]
    integrated_agents: Optional[int] = None
    integrated_agents_enabled: Optional[bool] = None
    execution_modes: Optional[Dict[str, int]] = None
    error: Optional[str] = None
router = APIRouter(prefix="/api/v1/projects/{project_id}/applications/{application_name}/agent-analysis", tags=["agent-analysis"])

# Initialize the orchestrator
orchestrator = AgentOrchestrator()

@router.get("/agents")
async def list_available_agents():
    """List available agents and their capabilities"""
    try:
        # Use orchestrator to get available agents (currently service-based)
        agents = orchestrator.get_available_agents()
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_agent_analysis(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name"),
    agent_type: str = Query(..., description="Agent type to use"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    config: Optional[Dict[str, Any]] = None
):
    """Start agent analysis using hybrid orchestrator (integrated or service-based)"""
    try:
        logger.info(f"Starting hybrid agent analysis: {agent_type} for {project_id}/{application_name}")
        
        # Use orchestrator to handle both integrated and service agents
        result = await orchestrator.analyze_logs(
            project_id=project_id,
            application_name=application_name,
            agent_type=agent_type,
            log_data={},  # Will be populated by orchestrator
            analysis_config=config or {}
        )
        
        return {
            "status": "initiated" if result.get("status") == "completed" else "processing",
            "analysis_id": result.get("analysis_id"),
            "agent_type": agent_type,
            "execution_mode": result.get("metadata", {}).get("execution_mode", "unknown"),
            "project_id": project_id,
            "application_name": application_name,
            "message": f"Agent analysis {'completed' if result.get('status') == 'completed' else 'started'}",
            "result": result if result.get("status") == "completed" else None
        }
        
    except Exception as e:
        logger.error(f"Agent analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        project_root_path = fs_integration.meshlog_data_path / "projects" / project_id
        
        if not project_root_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Project not found: {project_id}"
            )
        
        # Check if application discovery data exists
        discovery_file = project_root_path / "extracted" / "metadata" / "application_discovery.json"
        if not discovery_file.exists():
            raise HTTPException(
                status_code=400, 
                detail="No application discovery data found. Upload a log package first."
            )
        
        # Verify the application exists in discovery data
        import json
        with open(discovery_file, 'r') as f:
            discovery_data = json.load(f)
        
        app_containers = [
            app for app in discovery_data["applications"] 
            if app["application_name"] == application_name
        ]
        
        if not app_containers:
            raise HTTPException(
                status_code=400, 
                detail=f"Application {application_name} not found in discovery data"
            )
        
        # Initialize agent client
        client = AgentServiceClient()
        
        # Get original source log file paths (no copying)
        log_paths = fs_integration.prepare_application_specific_logs_for_agent(
            project_id, application_name, project_root_path
        )
        agent_output_path = fs_integration.get_agent_output_path(project_id, application_name)
        
        # Start agent analysis with original log paths
        analysis_response = await client.start_analysis(
            project_id=project_id,
            app_name=application_name,
            log_paths=log_paths,
            output_path=agent_output_path,
            agent_type=agent_type,
            config={**(config or {}), "raw_data_mode": True, "meshlog_raw_data": True}
        )
        
        # Start background task to monitor completion
        background_tasks.add_task(
            monitor_agent_analysis,
            analysis_response["analysis_id"],
            project_id,
            application_name,
            agent_output_path
        )
        
        await client.close()
        
        return {
            "status": "initiated",
            "analysis_id": analysis_response["analysis_id"],
            "agent_type": agent_type,
            "message": "Agent analysis started for application-specific log data",
            "application_specific_mode": True,
            "containers_processed": len(app_containers),
            "file_locations": {
                "input_path": log_paths[0] if log_paths else "N/A",
                "output_path": str(agent_output_path),
                "project_root": str(project_root_path)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start agent analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{analysis_id}")
async def get_agent_analysis_status(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name"),
    analysis_id: str = Path(..., description="Analysis ID")
):
    """Get agent analysis status"""
    try:
        # Use orchestrator for both integrated and service agents
        status = await orchestrator.get_analysis_status(analysis_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get analysis status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_agent_analysis_results(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name"),
    format: str = Query("html", description="Result format (html, json, csv)"),
    analysis_id: str = Query(None, description="Analysis ID for integrated agents")
):
    """Get agent analysis results from integrated agents or service-based files"""
    try:
        # Always check for file-based HTML report first (for enhanced presentation)
        fs_integration = FileSystemIntegration()
        meshlog_agent_path = (
            fs_integration.meshlog_data_path / "projects" / project_id / 
            "applications" / application_name / "agent-analysis"
        )
        
        # For HTML format, prefer the agent's own HTML file if it exists
        if format == "html" and meshlog_agent_path.exists():
            html_file = meshlog_agent_path / "agent_report.html"
            json_file = meshlog_agent_path / "agent_data.json"
            
            if html_file.exists():
                response = {"html_content": html_file.read_text(encoding='utf-8')}
                
                # Also include structured data if available for enhanced UI features
                if json_file.exists():
                    try:
                        import json
                        with open(json_file, 'r') as f:
                            structured_data = json.load(f)
                        response.update(structured_data)
                    except Exception as e:
                        logger.warning(f"Could not load structured data: {e}")
                
                return response
        
        # Try to get results from orchestrator (integrated agents)
        if analysis_id:
            try:
                result = await orchestrator.get_analysis_result(analysis_id)
                
                if format == "json":
                    return result
                elif format == "html":
                    # Use converted HTML as fallback if no file-based HTML exists
                    html_content = _convert_result_to_html(result)
                    # Return both HTML and structured data
                    response = {"html_content": html_content}
                    response.update(result)
                    return response
                elif format == "csv":
                    # Convert integrated agent result to CSV for display  
                    csv_content = _convert_result_to_csv(result)
                    return {"csv_content": csv_content}
                else:
                    raise HTTPException(status_code=400, detail="Invalid format. Use html, json, or csv")
                    
            except ValueError as e:
                # Analysis not found in orchestrator, fall through to file-based approach
                logger.warning(f"Analysis {analysis_id} not found in orchestrator: {e}")
        
        # Fall back to other file-based results (for non-HTML or when HTML file doesn't exist)
        if not meshlog_agent_path.exists():
            raise HTTPException(status_code=404, detail="No agent analysis results found")
        
        if format == "html":
            # This should only be reached if HTML file doesn't exist
            raise HTTPException(status_code=404, detail="HTML report not found")
        
        elif format == "json":
            json_file = meshlog_agent_path / "agent_data.json"
            if json_file.exists():
                import json
                return json.loads(json_file.read_text(encoding='utf-8'))
            else:
                raise HTTPException(status_code=404, detail="JSON data not found")
        
        elif format == "csv":
            csv_file = meshlog_agent_path / "agent_data.csv"
            if csv_file.exists():
                return {"csv_content": csv_file.read_text(encoding='utf-8')}
            else:
                raise HTTPException(status_code=404, detail="CSV data not found")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use html, json, or csv")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-applications")
async def get_available_applications(
    project_id: str = Path(..., description="Project ID")
):
    """Get applications available for agent analysis from raw log data"""
    try:
        fs_integration = FileSystemIntegration()
        data_preparation = DataPreparationService()
        
        # Get project root path
        project_root_path = fs_integration.meshlog_data_path / "projects" / project_id
        
        if not project_root_path.exists():
            raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
        
        # Read application discovery data
        discovery_file = project_root_path / "extracted" / "metadata" / "application_discovery.json"
        
        if not discovery_file.exists():
            raise HTTPException(status_code=404, detail="Application discovery data not found")
        
        import json
        with open(discovery_file, 'r') as f:
            discovery_data = json.load(f)
        
        # Create application info with agent mapping
        applications = []
        for app_info in discovery_data["applications"]:
            app_name = app_info["application_name"]
            agent_type = data_preparation._determine_agent_type(app_name)
            
            # Only add unique applications
            if not any(app["application_name"] == app_name for app in applications):
                applications.append({
                    "application_name": app_name,
                    "agent_type": agent_type,
                    "has_discovery_data": True,
                    "ready_for_analysis": True,
                    "container_count": len([a for a in discovery_data["applications"] if a["application_name"] == app_name]),
                    "total_log_size_bytes": sum(a["total_log_size_bytes"] for a in discovery_data["applications"] if a["application_name"] == app_name)
                })
        
        return {
            "project_id": project_id,
            "applications": applications,
            "total_applications": len(applications),
            "raw_data_path": str(project_root_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get available applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def monitor_agent_analysis(
    analysis_id: str,
    project_id: str,
    application_name: str,
    agent_output_path: Path
):
    """Background task to monitor agent analysis completion"""
    try:
        client = AgentServiceClient()
        fs_integration = FileSystemIntegration()
        
        logger.info(f"Starting background monitoring for analysis {analysis_id}")
        logger.info(f"Agent output path: {agent_output_path}")
        
        # Wait for completion
        final_status = await client.wait_for_completion(analysis_id)
        logger.info(f"Agent analysis {analysis_id} final status: {final_status}")
        
        if final_status["status"] == "completed":
            logger.info(f"Reading results from: {agent_output_path}")
            # Read results from agent output directory (no copying needed)
            agent_results = fs_integration.read_agent_results(agent_output_path)
            logger.info(f"Agent results: {list(agent_results.keys())}")
            
            # Ensure directory exists (agent should have created it, but just in case)
            fs_integration.ensure_agent_directory(project_id, application_name)
            
            logger.info(f"Agent analysis {analysis_id} completed successfully")
        else:
            logger.error(f"Agent analysis {analysis_id} failed: {final_status.get('error')}")
        
        await client.close()
        
    except Exception as e:
        logger.error(f"Error monitoring agent analysis {analysis_id}: {e}")
    finally:
        # Ensure client is closed even if there's an error
        try:
            await client.close()
        except Exception:
            pass

@router.get("/agents/{agent_type}/metadata", response_model=AgentMetadataResponse)
async def get_agent_metadata(
    agent_type: str = Path(..., description="Agent type"),
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name")
):
    """Get metadata for a specific agent"""
    try:
        # Use orchestrator to get agent information
        agents = orchestrator.get_available_agents()
        agent_metadata = next((agent for agent in agents if agent.get("agent_type") == agent_type), None)
        
        if not agent_metadata:
            raise HTTPException(status_code=404, detail=f"Agent {agent_type} not found")
        
        # Get execution mode from orchestrator
        try:
            execution_mode = orchestrator.agent_registry.get_agent_execution_mode(agent_type)
        except Exception:
            execution_mode = "service"  # fallback
        
        return AgentMetadataResponse(
            agent_type=agent_type,
            execution_mode=execution_mode,
            metadata=agent_metadata,
            available=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check for the agent analysis system"""
    try:
        # Get available agents from orchestrator
        agents = orchestrator.get_available_agents()
        
        # Get registry status if integrated agents are enabled
        registry_status = None
        try:
            registry_status = orchestrator.agent_registry.get_registry_status()
        except Exception as e:
            logger.warning(f"Could not get registry status: {e}")
        
        return HealthResponse(
            status="healthy",
            total_agents=len(agents),
            agent_types=[agent.get("agent_type", "unknown") for agent in agents],
            integrated_agents=registry_status.get("total_agents", 0) if registry_status else 0,
            integrated_agents_enabled=registry_status.get("enabled", False) if registry_status else False,
            execution_modes={
                "integrated": len([a for a in agents if orchestrator.agent_registry.get_agent_execution_mode(a.get("agent_type", "")) == "integrated"]),
                "service": len([a for a in agents if orchestrator.agent_registry.get_agent_execution_mode(a.get("agent_type", "")) == "service"])
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            error=str(e),
            total_agents=0,
            agent_types=[]
        )

@router.post("/direct", response_model=AnalysisResponse)
async def direct_agent_analysis(
    project_id: str = Path(..., description="Project ID"),
    application_name: str = Path(..., description="Application name"),
    request: AnalysisRequest = ...
):
    """Direct agent analysis using hybrid orchestrator - simplified interface"""
    try:
        logger.info(f"Starting direct hybrid agent analysis: {request.agent_type} for {project_id}/{application_name}")
        
        # Use orchestrator for direct analysis (integrated or service)
        result = await orchestrator.analyze_logs(
            project_id=project_id,
            application_name=application_name,
            agent_type=request.agent_type,
            log_data={},  # Will be populated by orchestrator
            analysis_config=request.analysis_config
        )
        
        return AnalysisResponse(
            status=result.get("status", "completed"),
            analysis_id=result.get("analysis_id"),
            agent_type=request.agent_type,
            execution_mode=result.get("metadata", {}).get("execution_mode", "unknown"),
            project_id=project_id,
            application_name=application_name,
            message=f"Direct agent analysis completed",
            analysis_data=result.get("analysis_data"),
            metadata=result.get("metadata"),
            error=result.get("error"),
            result=result
        )
        
    except Exception as e:
        logger.error(f"Direct agent analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for result conversion

def _convert_result_to_html(result: dict) -> str:
    """Convert integrated agent result to HTML format"""
    try:
        import json
        
        # Extract key components
        analysis_data = result.get("analysis_data", {})
        metadata = result.get("metadata", {})
        agent_metadata = result.get("agent_metadata", {})
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Agent Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .key-value {{ margin: 5px 0; }}
                .json-block {{ background-color: #f8f8f8; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                pre {{ margin: 0; white-space: pre-wrap; }}
                .insights {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; }}
                .metrics {{ background-color: #f0f8e8; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Agent Analysis Report</h1>
                <div class="key-value"><strong>Agent Type:</strong> {agent_metadata.get('agent_type', 'Unknown')}</div>
                <div class="key-value"><strong>Agent Version:</strong> {agent_metadata.get('version', 'Unknown')}</div>
                <div class="key-value"><strong>Execution Mode:</strong> {metadata.get('execution_mode', 'Unknown')}</div>
                <div class="key-value"><strong>Processing Time:</strong> {metadata.get('processing_time', 'Unknown')}</div>
            </div>
        """
        
        # Add summary section if available
        if isinstance(analysis_data, dict) and "summary" in analysis_data:
            summary = analysis_data["summary"]
            html_content += f"""
            <div class="section">
                <h2>Summary</h2>
                <div class="key-value"><strong>Status:</strong> {summary.get('status', 'N/A')}</div>
                <div class="key-value"><strong>Total Events:</strong> {summary.get('total_events', 'N/A')}</div>
                <div class="key-value"><strong>Time Range:</strong> {summary.get('time_range', 'N/A')}</div>
            </div>
            """
        
        # Add insights section if available
        if isinstance(analysis_data, dict) and "insights" in analysis_data:
            insights = analysis_data["insights"]
            if insights:
                html_content += f"""
                <div class="section insights">
                    <h2>Key Insights</h2>
                    <ul>
                """
                for insight in insights:
                    html_content += f"<li>{insight}</li>"
                html_content += "</ul></div>"
        
        # Add metrics section if available
        if isinstance(analysis_data, dict) and "metrics" in analysis_data:
            metrics = analysis_data["metrics"]
            if isinstance(metrics, dict):
                html_content += f"""
                <div class="section metrics">
                    <h2>Metrics</h2>
                """
                for key, value in metrics.items():
                    html_content += f'<div class="key-value"><strong>{key}:</strong> {value}</div>'
                html_content += "</div>"
        
        # Add raw data section
        html_content += f"""
            <div class="section">
                <h2>Complete Analysis Data</h2>
                <div class="json-block">
                    <pre>{json.dumps(result, indent=2, default=str)}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        # Fallback to simple HTML
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Agent Analysis Report</title></head>
        <body>
            <h1>Agent Analysis Report</h1>
            <p><strong>Status:</strong> {result.get('status', 'Unknown')}</p>
            <h2>Raw Data</h2>
            <pre>{json.dumps(result, indent=2, default=str)}</pre>
        </body>
        </html>
        """

def _convert_result_to_csv(result: dict) -> str:
    """Convert integrated agent result to CSV format"""
    try:
        import csv
        import io
        
        output = io.StringIO()
        
        # Extract key data
        analysis_data = result.get("analysis_data", {})
        metadata = result.get("metadata", {})
        
        # Create CSV with key metrics
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Metric", "Value"])
        
        # Basic info
        writer.writerow(["Status", result.get("status", "Unknown")])
        writer.writerow(["Analysis ID", result.get("analysis_id", "Unknown")])
        writer.writerow(["Execution Mode", metadata.get("execution_mode", "Unknown")])
        
        # Analysis-specific data
        if isinstance(analysis_data, dict):
            if "summary" in analysis_data and isinstance(analysis_data["summary"], dict):
                for key, value in analysis_data["summary"].items():
                    writer.writerow([f"Summary.{key}", value])
            
            if "metrics" in analysis_data and isinstance(analysis_data["metrics"], dict):
                for key, value in analysis_data["metrics"].items():
                    writer.writerow([f"Metrics.{key}", value])
        
        return output.getvalue()
        
    except Exception as e:
        # Fallback to simple CSV
        return f"Error,Failed to convert to CSV: {str(e)}\n"
