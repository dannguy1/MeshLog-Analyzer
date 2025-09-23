# prplOS LCM Log Analysis System - Application Classifier

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.models.core import LogEntry, ApplicationInfo
from app.core.config import app_config

logger = logging.getLogger(__name__)

class ApplicationClassifier:
    """Classify applications based on log patterns"""
    
    def __init__(self):
        self.config = app_config
        
        # Application classification patterns
        self.application_patterns = {
            "wnc-steer": {
                "name": "WiFi Network Controller - Client Steering",
                "description": "Manages client steering and load balancing across WiFi access points",
                "patterns": [
                    r"steer_info",
                    r"sta_info\.mac",
                    r"weak signal clients",
                    r"RSSI",
                    r"client steering",
                    r"load balancing",
                    r"steering decision"
                ],
                "keywords": [
                    "steer", "client", "RSSI", "signal", "load", "balance", "decision"
                ],
                "config_files": [
                    "steer_config.json",
                    "client_config.json"
                ]
            },
            "wnc-acs": {
                "name": "WiFi Network Controller - Auto Channel Selection",
                "description": "Automatically selects optimal WiFi channels based on interference analysis",
                "patterns": [
                    r"channelList",
                    r"opClass",
                    r"X_PRPL-ORG_WiFiController",
                    r"channel selection",
                    r"interference",
                    r"auto channel"
                ],
                "keywords": [
                    "channel", "interference", "auto", "selection", "opClass", "WiFiController"
                ],
                "config_files": [
                    "acs_config.json",
                    "channel_config.json"
                ]
            },
            "wnc-tpyopt": {
                "name": "WiFi Network Controller - Topology Optimizer",
                "description": "Optimizes WiFi network topology for optimal performance and coverage",
                "patterns": [
                    r"topology optimization",
                    r"State: WaitTrigger --> SendScan",
                    r"Build topology fail!",
                    r"topology analysis",
                    r"network optimization"
                ],
                "keywords": [
                    "topology", "optimization", "network", "scan", "build", "analysis"
                ],
                "config_files": [
                    "topology_config.json",
                    "optimization_config.json"
                ]
            },
            "otbr-agent": {
                "name": "OpenThread Border Router Agent",
                "description": "Manages Thread network border routing and Matter IoT device connectivity",
                "patterns": [
                    r"Mle-----------: Send Advertisement",
                    r"MeshForwarder-: Sent IPv6 UDP msg",
                    r"Beacon Request",
                    r"Thread network",
                    r"border router",
                    r"Matter device"
                ],
                "keywords": [
                    "Thread", "Matter", "border", "router", "IPv6", "UDP", "Beacon"
                ],
                "config_files": [
                    "otbr_config.json",
                    "thread_config.json"
                ]
            }
        }
    
    def classify_application(self, log_entries: List[LogEntry], container_id: str = "") -> List[ApplicationInfo]:
        """Classify applications based on log patterns"""
        logger.info(f"Classifying applications for container: {container_id}")
        
        if not log_entries:
            logger.warning("No log entries provided for classification")
            return []
        
        # Group entries by application name
        app_groups = {}
        for entry in log_entries:
            app_name = entry.application
            if app_name not in app_groups:
                app_groups[app_name] = []
            app_groups[app_name].append(entry)
        
        # Classify each application group
        application_infos = []
        for app_name, entries in app_groups.items():
            app_info = self._classify_single_application(app_name, entries, container_id)
            if app_info:
                application_infos.append(app_info)
        
        logger.info(f"Classification completed: {len(application_infos)} applications identified")
        return application_infos
    
    def _classify_single_application(self, app_name: str, log_entries: List[LogEntry], container_id: str) -> Optional[ApplicationInfo]:
        """Classify a single application"""
        logger.debug(f"Classifying application: {app_name}")
        
        # Get application statistics
        stats = self._get_application_statistics(log_entries)
        
        # Determine functional domain and confidence
        functional_domain, confidence_score = self._determine_functional_domain(app_name, log_entries)
        
        # Extract log patterns
        log_patterns = self._extract_log_patterns(log_entries)
        
        # Find configuration files
        config_files = self._find_configuration_files(log_entries)
        
        # Determine dependencies
        dependencies = self._determine_dependencies(log_entries)
        
        # Create application info
        app_info = ApplicationInfo(
            application_name=app_name,
            container_id=container_id,
            functional_domain=functional_domain,
            description=self._get_application_description(app_name),
            version=self._extract_version(log_entries),
            configuration_files=config_files,
            log_patterns=log_patterns,
            dependencies=dependencies,
            metrics=stats
        )
        
        logger.debug(f"Application classified: {app_name} -> {functional_domain} (confidence: {confidence_score:.2f})")
        return app_info
    
    def _determine_functional_domain(self, app_name: str, log_entries: List[LogEntry]) -> tuple[str, float]:
        """Determine functional domain and confidence score"""
        # First, check if app_name matches known patterns
        for known_app, app_data in self.application_patterns.items():
            if known_app.lower() in app_name.lower():
                return app_data["name"], 0.95
        
        # Analyze log content for patterns
        content = " ".join([entry.message for entry in log_entries])
        content_lower = content.lower()
        
        best_match = None
        best_score = 0.0
        
        for app_key, app_data in self.application_patterns.items():
            score = self._calculate_pattern_score(content_lower, app_data)
            if score > best_score:
                best_score = score
                best_match = app_data["name"]
        
        # If no good match found, use app_name as domain
        if best_score < 0.3:
            return f"Unknown Application: {app_name}", 0.1
        
        return best_match, best_score
    
    def _calculate_pattern_score(self, content: str, app_data: Dict[str, Any]) -> float:
        """Calculate pattern matching score"""
        score = 0.0
        total_patterns = len(app_data["patterns"]) + len(app_data["keywords"])
        
        # Check regex patterns
        for pattern in app_data["patterns"]:
            if re.search(pattern, content, re.IGNORECASE):
                score += 0.4  # Higher weight for regex patterns
        
        # Check keywords
        for keyword in app_data["keywords"]:
            if keyword.lower() in content:
                score += 0.1  # Lower weight for keywords
        
        # Normalize score
        if total_patterns > 0:
            score = min(score / total_patterns, 1.0)
        
        return score
    
    def _get_application_description(self, app_name: str) -> str:
        """Get application description"""
        for app_key, app_data in self.application_patterns.items():
            if app_key.lower() in app_name.lower():
                return app_data["description"]
        
        return f"Application: {app_name}"
    
    def _extract_version(self, log_entries: List[LogEntry]) -> Optional[str]:
        """Extract version information from log entries"""
        version_patterns = [
            r"version[:\s]+([0-9]+\.[0-9]+(?:\.[0-9]+)?)",
            r"v([0-9]+\.[0-9]+(?:\.[0-9]+)?)",
            r"([0-9]+\.[0-9]+(?:\.[0-9]+)?)"
        ]
        
        for entry in log_entries:
            for pattern in version_patterns:
                match = re.search(pattern, entry.message, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None
    
    def _extract_log_patterns(self, log_entries: List[LogEntry]) -> List[str]:
        """Extract common log patterns"""
        patterns = []
        
        # Look for common patterns in messages
        message_samples = [entry.message for entry in log_entries[:100]]  # Sample first 100
        
        # Find common prefixes
        prefixes = {}
        for message in message_samples:
            parts = message.split()
            if len(parts) > 0:
                prefix = parts[0]
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
        
        # Add common prefixes as patterns
        for prefix, count in prefixes.items():
            if count > len(message_samples) * 0.1:  # At least 10% of messages
                patterns.append(f"{prefix}*")
        
        # Look for structured data patterns
        structured_entries = [entry for entry in log_entries if entry.structured_data]
        if structured_entries:
            patterns.append("structured_data")
        
        return patterns[:10]  # Limit to 10 patterns
    
    def _find_configuration_files(self, log_entries: List[LogEntry]) -> List[str]:
        """Find configuration files mentioned in logs"""
        config_files = []
        
        config_patterns = [
            r"config[:\s]+([^\s]+\.(?:json|yaml|yml|conf))",
            r"loading[:\s]+([^\s]+\.(?:json|yaml|yml|conf))",
            r"([^\s]+\.(?:json|yaml|yml|conf))"
        ]
        
        for entry in log_entries:
            for pattern in config_patterns:
                matches = re.findall(pattern, entry.message, re.IGNORECASE)
                config_files.extend(matches)
        
        return list(set(config_files))  # Remove duplicates
    
    def _determine_dependencies(self, log_entries: List[LogEntry]) -> List[str]:
        """Determine application dependencies from logs"""
        dependencies = []
        
        # Common dependency indicators
        dep_patterns = [
            r"connecting to ([^\s]+)",
            r"dependency ([^\s]+)",
            r"requires ([^\s]+)",
            r"using ([^\s]+)",
            r"initializing ([^\s]+)"
        ]
        
        for entry in log_entries:
            for pattern in dep_patterns:
                matches = re.findall(pattern, entry.message, re.IGNORECASE)
                dependencies.extend(matches)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _get_application_statistics(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """Get application statistics"""
        if not log_entries:
            return {}
        
        # Time range
        timestamps = [entry.timestamp for entry in log_entries]
        time_range = {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat(),
            "duration_seconds": (max(timestamps) - min(timestamps)).total_seconds()
        }
        
        # Log level distribution
        level_counts = {}
        for entry in log_entries:
            level = entry.log_level.value
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Structured data usage
        structured_count = sum(1 for entry in log_entries if entry.structured_data)
        
        return {
            "total_entries": len(log_entries),
            "time_range": time_range,
            "level_distribution": level_counts,
            "structured_data_usage": {
                "count": structured_count,
                "percentage": (structured_count / len(log_entries)) * 100 if log_entries else 0
            },
            "average_message_length": sum(len(entry.message) for entry in log_entries) / len(log_entries) if log_entries else 0
        }
    
    def get_classification_summary(self, application_infos: List[ApplicationInfo]) -> Dict[str, Any]:
        """Get summary of application classification results"""
        if not application_infos:
            return {}
        
        # Count by functional domain
        domain_counts = {}
        for app_info in application_infos:
            domain = app_info.functional_domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Application types
        app_types = list(set(app_info.application_name for app_info in application_infos))
        
        # Total log entries
        total_entries = sum(app_info.metrics.get("total_entries", 0) for app_info in application_infos)
        
        return {
            "total_applications": len(application_infos),
            "total_log_entries": total_entries,
            "application_types": app_types,
            "domain_distribution": domain_counts,
            "classification_confidence": "high" if len(application_infos) > 0 else "low"
        }
    
    def validate_classification(self, application_infos: List[ApplicationInfo]) -> List[str]:
        """Validate classification results"""
        validation_errors = []
        
        # Check for unknown applications
        unknown_apps = [app for app in application_infos if "Unknown" in app.functional_domain]
        if unknown_apps:
            validation_errors.append(f"Unknown applications detected: {len(unknown_apps)}")
        
        # Check for duplicate container IDs
        container_ids = [app.container_id for app in application_infos]
        if len(container_ids) != len(set(container_ids)):
            validation_errors.append("Duplicate container IDs found")
        
        # Check for empty applications
        empty_apps = [app for app in application_infos if app.metrics.get("total_entries", 0) == 0]
        if empty_apps:
            validation_errors.append(f"Empty applications found: {len(empty_apps)}")
        
        return validation_errors
