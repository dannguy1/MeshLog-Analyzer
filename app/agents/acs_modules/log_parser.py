"""
ACS Log Parser Module

Handles pattern-based log parsing and event extraction for ACS analysis.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class ACSLogParser:
    """ACS-specific log parser using pattern recognition framework"""
    
    def __init__(self, pattern_interface, logger: logging.Logger):
        self.pattern_interface = pattern_interface
        self.logger = logger
        
        # Reset for each analysis
        self.events = []
        
        # Processing statistics
        self.lines_processed = 0
        self.lines_matched = 0
        
    def reset(self):
        """Reset parser state for new analysis"""
        self.events.clear()
        self.lines_processed = 0
        self.lines_matched = 0
    
    def process_log_file(self, log_file: str) -> tuple:
        """Process a single log file and extract ACS events"""
        lines_processed = 0
        lines_matched = 0
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    lines_processed += 1
                    
                    # Use pattern framework to parse the log line
                    result = self.pattern_interface.parse_log_line(line, line_num)
                    if result['status'] == 'matched':
                        lines_matched += 1
                        self._process_pattern_match(result, line, line_num)
        except Exception as e:
            self.logger.warning(f"Error processing file {log_file}: {e}")
        
        self.lines_processed += lines_processed
        self.lines_matched += lines_matched
        return lines_processed, lines_matched
    
    def _process_pattern_match(self, result: dict, line: str, line_num: int) -> None:
        """Process a pattern match result"""
        try:
            event = {
                'timestamp': self._extract_timestamp(line),
                'pattern_name': result['pattern_name'],
                'confidence': result['confidence'],
                'raw_line': line,
                'line_number': line_num,
                'match_data': result['match_data'],
                'event_type': self._determine_event_type(result['pattern_name'])
            }
            
            # Extract common ACS fields
            match_data = result['match_data']
            if 'radio' in match_data:
                event['radio'] = match_data['radio']
            if 'channel' in match_data:
                event['channel'] = match_data['channel']
            if 'fsm_state' in match_data:
                event['fsm_state'] = match_data['fsm_state']
            if 'reason' in match_data:
                event['reason'] = match_data['reason']
            if 'from_state' in match_data and 'to_state' in match_data:
                event['from_state'] = match_data['from_state']
                event['to_state'] = match_data['to_state']
            
            self.events.append(event)
            
        except Exception as e:
            self.logger.warning(f"Error processing pattern match: {e}")
    
    def _determine_event_type(self, pattern_name: str) -> str:
        """Determine event type from pattern name"""
        if 'fsm' in pattern_name.lower():
            return 'fsm_transition'
        elif 'channel' in pattern_name.lower():
            return 'channel_event'
        elif 'scan' in pattern_name.lower():
            return 'scan_event'
        elif 'acs' in pattern_name.lower():
            return 'acs_event'
        else:
            return 'general'
    
    def _extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line"""
        # Use pattern framework for timestamp extraction
        timestamp_result = self.pattern_interface.parse_log_line(line)
        
        if timestamp_result['status'] == 'matched' and 'timestamp' in timestamp_result['pattern_name']:
            match_data = timestamp_result['match_data']
            if all(key in match_data for key in ['year', 'month', 'day', 'hour', 'minute', 'second']):
                return f"{match_data['year']} {match_data['month']} {match_data['day']} {match_data['hour']}:{match_data['minute']}:{match_data['second']}"
        
        # Fallback: try to extract timestamp with regex
        timestamp_patterns = [
            r'(\d{4})\s+(\w{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})',  # 2023 Dec 15 14:30:25
            r'(\d{2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2}):(\d{2})',        # 12/15/2023 14:30:25
            r'(\d{4}-\d{2}-\d{2})\s+(\d{2}):(\d{2}):(\d{2})'            # 2023-12-15 14:30:25
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                return ' '.join(match.groups())
        
        return ""
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all parsed events"""
        return self.events
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        return {
            'lines_processed': self.lines_processed,
            'lines_matched': self.lines_matched,
            'match_rate': self.lines_matched / max(1, self.lines_processed),
            'total_events': len(self.events),
            'event_types': self._get_event_type_distribution()
        }
    
    def _get_event_type_distribution(self) -> Dict[str, int]:
        """Get distribution of event types"""
        distribution = defaultdict(int)
        for event in self.events:
            event_type = event.get('event_type', 'unknown')
            distribution[event_type] += 1
        return dict(distribution)
