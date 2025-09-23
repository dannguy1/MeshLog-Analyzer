"""
Redis Manager for Real-Time Status Updates

This service manages Redis pub/sub functionality for real-time analysis status updates,
enabling instant communication between backend analysis processes and frontend clients.
"""

import redis
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.config import get_settings


class RedisManager:
    """Manages Redis pub/sub for real-time status updates"""
    
    def __init__(self):
        settings = get_settings()
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self._pubsub = None
    
    def get_pubsub(self):
        """Get or create pubsub instance"""
        if not self._pubsub:
            self._pubsub = self.redis_client.pubsub()
        return self._pubsub
    
    async def publish_analysis_status(self, project_id: str, application_name: str, 
                                    analysis_id: str, status: str, data: Dict[str, Any] = None):
        """Publish analysis status update to Redis"""
        try:
            channel = f"analysis_status:{project_id}:{application_name}"
            message = {
                "analysis_id": analysis_id,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "data": data or {}
            }
            
            # Publish to Redis channel
            self.redis_client.publish(channel, json.dumps(message))
            
            # Also store latest status for new subscribers
            self.redis_client.setex(
                f"latest_status:{project_id}:{application_name}", 
                3600,  # 1 hour TTL
                json.dumps(message)
            )
            
            print(f"Published status update: {project_id}:{application_name} -> {status}")
            
        except Exception as e:
            print(f"Error publishing status update: {e}")
    
    async def publish_analysis_progress(self, project_id: str, application_name: str, 
                                      analysis_id: str, progress: float, stage: str = None):
        """Publish analysis progress update"""
        await self.publish_analysis_status(
            project_id, application_name, analysis_id, "running", {
                "progress_percentage": progress,
                "current_stage": stage
            }
        )
    
    async def publish_analysis_started(self, project_id: str, application_name: str, analysis_id: str):
        """Publish analysis started event"""
        await self.publish_analysis_status(
            project_id, application_name, analysis_id, "running", {
                "started_timestamp": datetime.now().isoformat(),
                "progress_percentage": 0.0
            }
        )
    
    async def publish_analysis_completed(self, project_id: str, application_name: str, 
                                      analysis_id: str, result_data: Dict[str, Any] = None):
        """Publish analysis completed event"""
        await self.publish_analysis_status(
            project_id, application_name, analysis_id, "completed", {
                "completed_timestamp": datetime.now().isoformat(),
                "progress_percentage": 100.0,
                "result_data": result_data or {}
            }
        )
    
    async def publish_analysis_failed(self, project_id: str, application_name: str, 
                                    analysis_id: str, error_message: str):
        """Publish analysis failed event"""
        await self.publish_analysis_status(
            project_id, application_name, analysis_id, "failed", {
                "error_message": error_message,
                "failed_timestamp": datetime.now().isoformat()
            }
        )
    
    def get_latest_status(self, project_id: str, application_name: str) -> Optional[Dict[str, Any]]:
        """Get latest status for an application"""
        try:
            latest_data = self.redis_client.get(f"latest_status:{project_id}:{application_name}")
            if latest_data:
                return json.loads(latest_data)
            return None
        except Exception as e:
            print(f"Error getting latest status: {e}")
            return None
    
    def subscribe_to_analysis_status(self, project_id: str, application_name: str):
        """Subscribe to analysis status updates for a specific application"""
        channel = f"analysis_status:{project_id}:{application_name}"
        pubsub = self.get_pubsub()
        pubsub.subscribe(channel)
        return pubsub
    
    def unsubscribe_from_analysis_status(self, project_id: str, application_name: str):
        """Unsubscribe from analysis status updates"""
        channel = f"analysis_status:{project_id}:{application_name}"
        pubsub = self.get_pubsub()
        pubsub.unsubscribe(channel)
    
    def close(self):
        """Close Redis connections"""
        if self._pubsub:
            self._pubsub.close()
        self.redis_client.close()


# Global Redis manager instance
redis_manager = RedisManager()
