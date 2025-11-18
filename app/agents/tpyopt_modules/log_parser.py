"""
TPYOPT Log Parser Module

Handles pattern-based log parsing and event extraction for TPYOPT analysis.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class TPYOPTLogParser:
    """TPYOPT-specific log parser using pattern recognition framework"""
    
    def __init__(self, pattern_interface, logger: logging.Logger):
        self.pattern_interface = pattern_interface
        self.logger = logger
        
        # Reset for each analysis
        self.events = []
        self.device_data = defaultdict(lambda: {
            'events': [],
            'fsm_transitions': [],
            'roaming_commands': [],
            'packet_loss_events': [],
            'first_seen': None,
            'last_seen': None
        })
        
        # Processing statistics
        self.lines_processed = 0
        self.lines_matched = 0
        
    def reset(self):
        """Reset parser state for new analysis"""
        self.events.clear()
        self.device_data.clear()
        self.lines_processed = 0
        self.lines_matched = 0
    
    def process_log_file(self, file_path: str) -> tuple:
        """Process a single log file and extract TPYOPT events"""
        file_lines_processed = 0
        file_lines_matched = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    file_lines_processed += 1
                    
                    # Use pattern recognition framework
                    result = self.pattern_interface.parse_log_line(line, line_num)
                    
                    if result['status'] == 'matched':
                        file_lines_matched += 1
                        event = self._process_pattern_match(result, line)
                        if event:
                            self.events.append(event)
                            self._update_device_data(event)
                            
        except Exception as e:
            self.logger.warning(f"Could not process file {file_path}: {e}")
        
        self.lines_processed += file_lines_processed
        self.lines_matched += file_lines_matched
        
        return file_lines_processed, file_lines_matched
    
    def _process_pattern_match(self, result: dict, line: str) -> Optional[Dict[str, Any]]:
        """Process a pattern match result into a structured event"""
        pattern_name = result['pattern_name']
        match_data = result['match_data']
        
        timestamp = self._extract_timestamp(line)
        
        event = {
            'timestamp': timestamp,
            'pattern_name': pattern_name,
            'confidence': result['confidence'],
            'raw_line': line,
            'match_data': match_data,
            'event_type': self._determine_event_type(pattern_name)
        }
        
        # Extract common fields
        if 'mac' in match_data:
            event['device_mac'] = match_data['mac']
        if 'from_state' in match_data and 'to_state' in match_data:
            event['from_state'] = match_data['from_state']
            event['to_state'] = match_data['to_state']
        if 'from_mac' in match_data and 'to_mac' in match_data:
            event['from_mac'] = match_data['from_mac']
            event['to_mac'] = match_data['to_mac']
        if 'reason' in match_data:
            event['reason'] = match_data['reason']
        if 'rssi' in match_data:
            event['rssi'] = match_data['rssi']
        if 'channel' in match_data:
            event['channel'] = match_data['channel']
        if 'packet_loss' in match_data:
            event['packet_loss'] = match_data['packet_loss']
        
        return event
    
    def _determine_event_type(self, pattern_name: str) -> str:
        """Determine event type from pattern name with improved matching"""
        pattern_lower = pattern_name.lower()
        
        # Check for specific event types first (more specific patterns)
        if 'fsm_transition' in pattern_lower or ('fsm' in pattern_lower and 'transition' in pattern_lower):
            return 'fsm_transition'
        elif 'roaming_command' in pattern_lower or ('roaming' in pattern_lower and 'command' in pattern_lower):
            return 'roaming_command'
        elif 'build_topology' in pattern_lower:
            return 'topology_build'
        elif 'topology' in pattern_lower:
            return 'topology_change'
        elif 'optimization_trigger' in pattern_lower or 'optimization' in pattern_lower:
            return 'optimization'
        elif 'packet_loss' in pattern_lower:
            return 'packet_loss'
        elif 'scan_trigger' in pattern_lower:
            return 'scan_event'
        elif 'failure' in pattern_lower or 'error' in pattern_lower or 'fail' in pattern_lower:
            return 'failure'
        else:
            return 'general'
    
    def _extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line with consistent ISO format"""
        # Use pattern framework for timestamp extraction
        try:
            timestamp_result = self.pattern_interface.parse_log_line(line)
            
            if timestamp_result['status'] == 'matched' and 'timestamp' in timestamp_result['pattern_name']:
                match_data = timestamp_result['match_data']
                if all(key in match_data for key in ['year', 'month', 'day', 'hour', 'minute', 'second']):
                    # Format timestamp with microseconds if present (preserve month name format)
                    microsecond = match_data.get('microsecond', '0')
                    if microsecond:
                        # Pad to 6 digits if needed
                        microsecond = microsecond.ljust(6, '0')[:6]
                        return f"{match_data['year']} {match_data['month']} {match_data['day']} {match_data['hour']}:{match_data['minute']}:{match_data['second']}.{microsecond}"
                    else:
                        return f"{match_data['year']} {match_data['month']} {match_data['day']} {match_data['hour']}:{match_data['minute']}:{match_data['second']}"
        except Exception as e:
            self.logger.debug(f"Pattern framework timestamp extraction failed: {e}")
        
        # Fallback: try to extract timestamp with regex (handle microseconds)
        timestamp_patterns = [
            (r'(\d{4})\s+(\w{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})\.(\d+)', True),   # 2023 Dec 15 14:30:25.123456
            (r'(\d{4})\s+(\w{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})', False),         # 2023 Dec 15 14:30:25
            (r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})', False),              # 2023-12-15 14:30:25
        ]
        
        for pattern, has_microseconds in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                if has_microseconds and len(groups) >= 7:
                    year, month, day, hour, minute, second, microsecond = groups[:7]
                    microsecond = microsecond.ljust(6, '0')[:6]
                    return f"{year} {month} {day} {hour}:{minute}:{second}.{microsecond}"
                elif len(groups) >= 6:
                    year, month, day, hour, minute, second = groups[:6]
                    return f"{year} {month} {day} {hour}:{minute}:{second}"
        
        return ""
    
    def _update_device_data(self, event: Dict[str, Any]) -> None:
        """Update device tracking data with new event"""
        if 'device_mac' not in event:
            return
        
        device_mac = event['device_mac']
        device_info = self.device_data[device_mac]
        
        # Add event to device history
        device_info['events'].append(event)
        
        # Update time tracking
        timestamp = event.get('timestamp', '')
        if timestamp:
            if not device_info['first_seen'] or timestamp < device_info['first_seen']:
                device_info['first_seen'] = timestamp
            if not device_info['last_seen'] or timestamp > device_info['last_seen']:
                device_info['last_seen'] = timestamp
        
        # Categorize event by type
        event_type = event.get('event_type', '')
        pattern_name = event.get('pattern_name', '')
        
        if event_type == 'fsm_transition' or 'fsm_transition' in pattern_name:
            device_info['fsm_transitions'].append(event)
        elif event_type == 'roaming_command' or 'roaming_command' in pattern_name:
            device_info['roaming_commands'].append(event)
        elif event_type == 'packet_loss' or 'packet_loss' in pattern_name:
            device_info['packet_loss_events'].append(event)
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all parsed events"""
        return self.events
    
    def get_device_data(self) -> Dict[str, Dict[str, Any]]:
        """Get device tracking data"""
        return dict(self.device_data)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        return {
            'lines_processed': self.lines_processed,
            'lines_matched': self.lines_matched,
            'match_rate': self.lines_matched / max(1, self.lines_processed),
            'total_events': len(self.events),
            'devices_tracked': len(self.device_data),
            'event_types': self._get_event_type_distribution()
        }
    
    def _get_event_type_distribution(self) -> Dict[str, int]:
        """Get distribution of event types"""
        distribution = defaultdict(int)
        for event in self.events:
            event_type = event.get('event_type', 'unknown')
            distribution[event_type] += 1
        return dict(distribution)
    
    def get_devices_by_activity(self) -> List[Dict[str, Any]]:
        """Get devices sorted by activity level"""
        devices = []
        for mac, data in self.device_data.items():
            devices.append({
                'mac': mac,
                'total_events': len(data['events']),
                'fsm_transitions': len(data['fsm_transitions']),
                'roaming_commands': len(data['roaming_commands']),
                'packet_loss_events': len(data['packet_loss_events']),
                'first_seen': data['first_seen'],
                'last_seen': data['last_seen']
            })
        
        # Sort by total events (most active first)
        devices.sort(key=lambda x: x['total_events'], reverse=True)
        return devices
