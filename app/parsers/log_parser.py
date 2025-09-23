# prplOS LCM Log Analysis System - Log Parser

import re
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Iterator
import logging

from app.models.core import LogEntry, LogLevel

logger = logging.getLogger(__name__)

class LogParser:
    """Parse syslog format entries"""
    
    def __init__(self):
        # Syslog regex pattern
        self.syslog_pattern = re.compile(
            r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+([^:]+):\s*(.*)$'
        )
        
        # Log level patterns
        self.level_patterns = {
            'debug': re.compile(r'\b(debug|DEBUG)\b'),
            'info': re.compile(r'\b(info|INFO|notice|NOTICE)\b'),
            'warning': re.compile(r'\b(warning|WARNING|warn|WARN)\b'),
            'error': re.compile(r'\b(error|ERROR|err|ERR)\b'),
            'critical': re.compile(r'\b(critical|CRITICAL|fatal|FATAL|emerg|EMERG)\b')
        }
        
        # JSON pattern for structured data
        self.json_pattern = re.compile(r'\{[^}]*\}')
    
    def parse_syslog_entry(self, line: str, container_id: str = "", file_path: str = "", line_number: int = 0) -> Optional[LogEntry]:
        """Parse syslog format entry"""
        try:
            # Skip empty lines
            if not line.strip():
                return None
            
            # Match syslog pattern
            match = self.syslog_pattern.match(line.strip())
            if not match:
                logger.debug(f"Line does not match syslog pattern: {line[:100]}...")
                return None
            
            timestamp_str, hostname, process, message = match.groups()
            
            # Parse timestamp
            timestamp = self._parse_timestamp(timestamp_str)
            if not timestamp:
                logger.warning(f"Failed to parse timestamp: {timestamp_str}")
                return None
            
            # Determine log level
            log_level = self._detect_log_level(message)
            
            # Extract structured data
            structured_data = self._extract_structured_data(message)
            
            # Categorize message for fast filtering
            message_type = self._categorize_message(message, self._extract_application_name(process))
            
            # Create log entry
            log_entry = LogEntry(
                timestamp=timestamp,
                container_id=container_id,
                application=self._extract_application_name(process),
                log_level=log_level,
                message=message,
                structured_data=structured_data,
                raw_line=line,
                line_number=line_number,
                file_path=file_path,
                message_type=message_type
            )
            
            return log_entry
            
        except Exception as e:
            logger.error(f"Failed to parse log entry: {e}")
            return None
    
    def parse_log_file(self, file_path: str, container_id: str = "") -> Iterator[LogEntry]:
        """Parse entire log file"""
        logger.info(f"Parsing log file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_number, line in enumerate(f, 1):
                    log_entry = self.parse_syslog_entry(
                        line, 
                        container_id=container_id,
                        file_path=file_path,
                        line_number=line_number
                    )
                    if log_entry:
                        yield log_entry
                        
        except Exception as e:
            logger.error(f"Failed to parse log file {file_path}: {e}")
    
    def parse_log_files(self, log_files: List[str], container_id: str = "") -> List[LogEntry]:
        """Parse multiple log files"""
        logger.info(f"Parsing {len(log_files)} log files for container: {container_id}")
        
        all_entries = []
        
        for file_path in log_files:
            try:
                entries = list(self.parse_log_file(file_path, container_id))
                all_entries.extend(entries)
                logger.debug(f"Parsed {len(entries)} entries from {file_path}")
            except Exception as e:
                logger.error(f"Failed to parse log file {file_path}: {e}")
        
        logger.info(f"Total entries parsed: {len(all_entries)}")
        return all_entries
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse syslog timestamp"""
        try:
            # Add current year since syslog doesn't include it
            current_year = datetime.now().year
            timestamp_with_year = f"{current_year} {timestamp_str}"
            
            # Try different formats
            formats = [
                "%Y %b %d %H:%M:%S",
                "%Y %b  %d %H:%M:%S",  # Handle single digit day
                "%Y %b %d %H:%M:%S",
                "%Y %b  %d %H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_with_year, fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse timestamp: {timestamp_str}")
            return None
            
        except Exception as e:
            logger.error(f"Timestamp parsing error: {e}")
            return None
    
    def _detect_log_level(self, message: str) -> LogLevel:
        """Detect log level from message content"""
        message_lower = message.lower()
        
        # Check for explicit level indicators
        for level_name, pattern in self.level_patterns.items():
            if pattern.search(message_lower):
                return LogLevel(level_name)
        
        # Default to INFO if no level detected
        return LogLevel.INFO
    
    def _extract_structured_data(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract structured data from log message"""
        try:
            # Look for JSON objects
            json_matches = self.json_pattern.findall(message)
            if json_matches:
                # Try to parse the first JSON object
                json_str = json_matches[0]
                structured_data = json.loads(json_str)
                return structured_data
            
            # Look for key-value pairs
            kv_pairs = self._extract_key_value_pairs(message)
            if kv_pairs:
                return kv_pairs
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to extract structured data: {e}")
            return None
    
    def _extract_key_value_pairs(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract key-value pairs from log message"""
        try:
            # Pattern for key=value pairs
            kv_pattern = re.compile(r'(\w+)=([^\s,]+)')
            matches = kv_pattern.findall(message)
            
            if matches:
                return dict(matches)
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to extract key-value pairs: {e}")
            return None
    
    def _extract_application_name(self, process: str) -> str:
        """Extract application name from process string"""
        try:
            # Remove common prefixes/suffixes
            process_clean = process.strip()
            
            # Remove common system prefixes
            prefixes_to_remove = ['systemd', 'kernel', 'daemon']
            for prefix in prefixes_to_remove:
                if process_clean.startswith(prefix):
                    process_clean = process_clean[len(prefix):].strip()
            
            # Extract application name (before any brackets or special chars)
            app_name = re.split(r'[\[\(]', process_clean)[0].strip()
            
            return app_name if app_name else "unknown"
            
        except Exception as e:
            logger.debug(f"Failed to extract application name: {e}")
            return "unknown"
    
    def get_log_statistics(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """Generate statistics from log entries"""
        if not log_entries:
            return {}
        
        # Count by log level
        level_counts = {}
        for level in LogLevel:
            level_counts[level.value] = 0
        
        for entry in log_entries:
            level_counts[entry.log_level.value] += 1
        
        # Time range
        timestamps = [entry.timestamp for entry in log_entries]
        time_range = {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat(),
            "duration_seconds": (max(timestamps) - min(timestamps)).total_seconds()
        }
        
        # Application distribution
        app_counts = {}
        for entry in log_entries:
            app_counts[entry.application] = app_counts.get(entry.application, 0) + 1
        
        # Container distribution
        container_counts = {}
        for entry in log_entries:
            container_counts[entry.container_id] = container_counts.get(entry.container_id, 0) + 1
        
        return {
            "total_entries": len(log_entries),
            "level_distribution": level_counts,
            "time_range": time_range,
            "application_distribution": app_counts,
            "container_distribution": container_counts,
            "has_structured_data": any(entry.structured_data for entry in log_entries)
        }
    
    def filter_entries(self, log_entries: List[LogEntry], 
                      level: Optional[LogLevel] = None,
                      application: Optional[str] = None,
                      container_id: Optional[str] = None,
                      time_start: Optional[datetime] = None,
                      time_end: Optional[datetime] = None) -> List[LogEntry]:
        """Filter log entries based on criteria
        
        NOTE: Time filtering (time_start, time_end) is disabled to keep analysis simple.
        All log entries should be included in analysis regardless of timestamp.
        """
        filtered_entries = log_entries
        
        if level:
            filtered_entries = [e for e in filtered_entries if e.log_level == level]
        
        if application:
            filtered_entries = [e for e in filtered_entries if e.application == application]
        
        if container_id:
            filtered_entries = [e for e in filtered_entries if e.container_id == container_id]
        
        # Time filtering disabled to keep analysis simple
        # if time_start:
        #     filtered_entries = [e for e in filtered_entries if e.timestamp >= time_start]
        # 
        # if time_end:
        #     filtered_entries = [e for e in filtered_entries if e.timestamp <= time_end]
        
        return filtered_entries
    
    def search_entries(self, log_entries: List[LogEntry], search_term: str) -> List[LogEntry]:
        """Search log entries for specific term"""
        search_term_lower = search_term.lower()
        
        matching_entries = []
        for entry in log_entries:
            # Search in message
            if search_term_lower in entry.message.lower():
                matching_entries.append(entry)
                continue
            
            # Search in structured data
            if entry.structured_data:
                if self._search_in_dict(entry.structured_data, search_term_lower):
                    matching_entries.append(entry)
                    continue
            
            # Search in application name
            if search_term_lower in entry.application.lower():
                matching_entries.append(entry)
                continue
        
        return matching_entries
    
    def _search_in_dict(self, data: Dict[str, Any], search_term: str) -> bool:
        """Recursively search in dictionary"""
        for key, value in data.items():
            if search_term in str(key).lower() or search_term in str(value).lower():
                return True
            if isinstance(value, dict) and self._search_in_dict(value, search_term):
                return True
        return False
    
    def _categorize_message(self, message: str, application: str) -> str:
        """Categorize message based on content - matches frontend filter categories"""
        message_lower = message.lower()
        
        # Application-specific categorization
        if application == "wnc-steer":
            if "steer" in message_lower:
                if "request" in message_lower or "enable" in message_lower:
                    return "steer-requests"
                elif "action" in message_lower or "triggered" in message_lower or "moved" in message_lower:
                    return "steer-actions"
                else:
                    return "steer-requests"
            elif "rssi" in message_lower or "rcpi" in message_lower or "signal" in message_lower or "weak" in message_lower:
                return "monitoring"
            elif "load" in message_lower or "balance" in message_lower or "capacity" in message_lower or "distribution" in message_lower:
                return "optimization"
            else:
                return "general"
        
        elif application == "wnc-acs":
            if "channel" in message_lower or "scan" in message_lower:
                return "channel-management"
            elif "interference" in message_lower or "noise" in message_lower:
                return "interference-detection"
            else:
                return "general"
        
        elif application == "wnc-tpyopt":
            if "topology" in message_lower or "optimization" in message_lower:
                return "topology-optimization"
            elif "scan" in message_lower or "trigger" in message_lower:
                return "scan-management"
            else:
                return "general"
        
        # Default categorization for other applications
        return "general"
