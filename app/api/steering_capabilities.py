"""
API endpoints for WiFi client 802.11k/v capability detection and steering strategy recommendations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from app.agents.wnc_steering import WNCSteeringAgent
from app.core.pattern_recognition import PatternRegistry

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/steering", tags=["steering"])

@router.get("/capabilities/summary")
async def get_capability_summary() -> Dict[str, Any]:
    """Get summary of all client 802.11k/v capabilities detected."""
    try:
        # Initialize steering agent for analysis
        steering_agent = WNCSteeringAgent()
        
        # Process recent logs to get current capabilities
        # Note: The analyze method expects log_paths and output_path
        # For now, return a simulated summary
        summary = {
            "total_clients": 0,
            "k_capable": 0,
            "v_capable": 0,
            "both_capable": 0,
            "legacy_only": 0,
            "unknown": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "capability_distribution": {},
            "message": "No log files processed yet - upload and analyze a project with steering logs"
        }
        
        return summary
    
    except Exception as e:
        logger.error(f"Error getting capability summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/capabilities/detailed")
async def get_detailed_capabilities() -> Dict[str, Dict[str, Any]]:
    """Get detailed capability information for all clients."""
    try:
        steering_agent = WNCSteeringAgent()
        
        # For now, return empty detailed capabilities
        return {
            "message": "No log files processed yet - upload and analyze a project with steering logs"
        }
    
    except Exception as e:
        logger.error(f"Error getting detailed capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategy/{mac_address}")
async def get_steering_strategy(mac_address: str) -> Dict[str, Any]:
    """Get recommended steering strategy for a specific client MAC address."""
    try:
        # Normalize MAC address format
        mac_address = mac_address.lower().strip()
        
        steering_agent = WNCSteeringAgent()
        
        # For demo purposes, return a sample strategy
        return {
            "strategy": "adaptive_discovery",
            "methods": ["capability_probing", "behavioral_analysis"],
            "reason": "Client capabilities unknown - discovery needed",
            "confidence": 0.0,
            "recommendation": "Test client capabilities with neighbor reports and BSS transitions",
            "mac_address": mac_address,
            "message": "Upload and analyze a project with steering logs to get real capability data"
        }
    
    except Exception as e:
        logger.error(f"Error getting steering strategy for {mac_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/capability-trends")
async def get_capability_trends(
    hours: Optional[int] = Query(24, description="Number of hours to analyze"),
    include_unknown: Optional[bool] = Query(True, description="Include clients with unknown capabilities")
) -> Dict[str, Any]:
    """Get trends in client capability detection over time."""
    try:
        steering_agent = WNCSteeringAgent()
        steering_agent.process_logs()
        
        # Get capability summary
        summary = steering_agent.get_client_capability_summary()
        detailed = steering_agent.get_detailed_client_capabilities()
        
        # Calculate trends
        trends = {
            'time_period_hours': hours,
            'total_clients_analyzed': summary['total_clients'],
            'capability_breakdown': {
                '802.11k_and_v_capable': summary['both_capable'],
                '802.11k_only': summary['k_capable'],
                '802.11v_only': summary['v_capable'],
                'legacy_only': summary['legacy_only'],
                'unknown_capability': summary['unknown']
            },
            'confidence_distribution': {
                'high_confidence': summary['high_confidence'],
                'medium_confidence': summary['medium_confidence'],
                'low_confidence': summary['low_confidence']
            },
            'steering_strategy_recommendations': {},
            'recent_discoveries': []
        }
        
        # Count strategy recommendations
        strategy_counts = {}
        recent_discoveries = []
        
        for mac, client_data in detailed.items():
            strategy = client_data['recommended_strategy']['strategy']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
            # Collect recent capability discoveries (high confidence, recent)
            if (client_data['capability_confidence'] > 0.8 and 
                client_data['evidence_summary']['total_evidence'] > 0):
                recent_discoveries.append({
                    'mac': mac,
                    'capabilities': {
                        '802.11k': client_data['supports_11k'],
                        '802.11v': client_data['supports_11v']
                    },
                    'confidence': client_data['capability_confidence'],
                    'strategy': strategy,
                    'last_seen': client_data['last_seen']
                })
        
        trends['steering_strategy_recommendations'] = strategy_counts
        trends['recent_discoveries'] = sorted(recent_discoveries, 
                                            key=lambda x: x['last_seen'], 
                                            reverse=True)[:10]
        
        return trends
    
    except Exception as e:
        logger.error(f"Error getting capability trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patterns/802.11kv")
async def get_80211kv_patterns() -> Dict[str, Any]:
    """Get information about 802.11k/v detection patterns used by the system."""
    try:
        pattern_registry = PatternRegistry()
        
        # Get all steering-related patterns
        all_patterns = pattern_registry.get_patterns_by_agent("wnc-steering")
        kv_patterns = {}
        
        for pattern_name, pattern_def in all_patterns.items():
            if any(keyword in pattern_name.lower() for keyword in 
                   ['neighbor', 'bss', 'transition', 'beacon', 'capability', 'rrm', 'btm']):
                kv_patterns[pattern_name] = {
                    'pattern': pattern_def.pattern,
                    'description': pattern_def.description,
                    'priority': pattern_def.priority,
                    'category': pattern_def.category,
                    'validation_samples': pattern_def.validation_samples
                }
        
        return {
            'total_patterns': len(kv_patterns),
            '802.11k_patterns': {k: v for k, v in kv_patterns.items() 
                               if 'neighbor' in k or 'beacon' in k or 'rrm' in k},
            '802.11v_patterns': {k: v for k, v in kv_patterns.items() 
                               if 'bss' in k or 'transition' in k or 'btm' in k},
            'capability_patterns': {k: v for k, v in kv_patterns.items() 
                                  if 'capability' in k},
            'all_patterns': kv_patterns
        }
    
    except Exception as e:
        logger.error(f"Error getting 802.11k/v patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis/refresh")
async def refresh_capability_analysis() -> Dict[str, Any]:
    """Trigger a fresh analysis of client capabilities from logs."""
    try:
        steering_agent = WNCSteeringAgent()
        
        # Clear existing stats and reprocess
        steering_agent.client_stats.clear()
        result = steering_agent.process_logs()
        
        capability_summary = steering_agent.get_client_capability_summary()
        
        return {
            'status': 'success',
            'message': 'Capability analysis refreshed',
            'processing_result': result,
            'capability_summary': capability_summary,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error refreshing capability analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
