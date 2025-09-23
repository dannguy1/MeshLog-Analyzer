# prplOS LCM Log Analysis System - WebSocket Manager

import logging
from typing import Dict
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, analysis_id: str):
        await websocket.accept()
        self.active_connections[analysis_id] = websocket
        logger.info(f"WebSocket connected for analysis: {analysis_id}")

    async def disconnect(self, analysis_id: str):
        if analysis_id in self.active_connections:
            del self.active_connections[analysis_id]
            logger.info(f"WebSocket disconnected for analysis: {analysis_id}")

    async def send_event(self, analysis_id: str, event: dict):
        if analysis_id in self.active_connections:
            try:
                await self.active_connections[analysis_id].send_json(event)
            except Exception as e:
                logger.error(f"Failed to send event to {analysis_id}: {e}")
                await self.disconnect(analysis_id)

# Global instance
manager = ConnectionManager()
