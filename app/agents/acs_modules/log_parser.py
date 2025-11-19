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
            self.logger.info(f"Processing log file: {log_file}")
            
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    lines_processed += 1
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Pre-filter: Only process lines that might contain ACS events
                    # This is an optimization similar to steering agent
                    if 'wnc-acs' not in line.lower():
                        continue
                    
                    # Use pattern framework to parse the log line
                    result = self.pattern_interface.parse_log_line(line, line_num)
                    if result['status'] == 'matched':
                        lines_matched += 1
                        pattern_name = result.get('pattern_name', 'unknown')
                        all_matches = result.get('all_matches', [])
                        
                        # Log diagnostic info for component identifier matches
                        if pattern_name == 'wnc_component_acs':
                            # Check if there are other matches that should have been preferred
                            event_matches = [m for m in all_matches if m.get('name') != 'wnc_component_acs']
                            if event_matches:
                                self.logger.warning(f"Line {line_num}: Component identifier selected but event-specific patterns available: {[m.get('name') for m in event_matches]}. Line: {line[:150]}")
                            else:
                                # Only component identifier matched - log sample for debugging
                                if lines_processed % 100 == 0:
                                    self.logger.debug(f"Line {line_num}: Only component identifier matched, no event-specific patterns. Line: {line[:150]}")
                        
                        self._process_pattern_match(result, line, line_num)
                    else:
                        # Log debug info for lines that contain 'wnc-acs' but don't match patterns
                        # Only log a sample to avoid log spam (log every 100th line)
                        if lines_processed % 100 == 0:
                            self.logger.debug(f"Line {line_num} contains 'wnc-acs' but didn't match any patterns: {line[:150]}")
        except Exception as e:
            self.logger.warning(f"Error processing file {log_file}: {e}")
        
        self.lines_processed += lines_processed
        self.lines_matched += lines_matched
        
        # Log summary statistics
        if lines_processed > 0:
            match_rate = (lines_matched / lines_processed) * 100
            events_created = len(self.events)
            component_id_matches = sum(1 for e in self.events if e.get('pattern_name') == 'wnc_component_acs')
            
            self.logger.info(f"File {log_file}: Processed {lines_processed} lines, matched {lines_matched} ({match_rate:.1f}% match rate), created {events_created} events")
            
            if lines_matched > 0 and events_created == 0:
                self.logger.error(f"File {log_file}: {lines_matched} pattern matches but 0 events created - all matches may be component identifiers being skipped")
            
            if lines_matched == 0 and lines_processed > 100:
                self.logger.warning(f"File {log_file}: No pattern matches found despite {lines_processed} lines containing 'wnc-acs' - check pattern definitions")
            
            # Log pattern distribution for debugging
            if events_created > 0:
                pattern_counts = {}
                for event in self.events:
                    pattern_name = event.get('pattern_name', 'unknown')
                    pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1
                self.logger.info(f"Event pattern distribution: {pattern_counts}")
        
        return lines_processed, lines_matched
    
    def _process_pattern_match(self, result: dict, line: str, line_num: int) -> None:
        """Process a pattern match result"""
        try:
            # Skip component identifier patterns - they're used for filtering, not event creation
            if result.get('pattern_name') == 'wnc_component_acs':
                # Component identifier matched but no event-specific pattern - skip this line
                # This should be rare with the fix, but handle it gracefully
                return
            
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
            # Handle radio MAC - patterns use 'mac' but ACS events use 'radio'
            if 'radio' in match_data:
                event['radio'] = match_data['radio']
            elif 'mac' in match_data:  # FSM transition pattern uses 'mac' for radio MAC
                event['radio'] = match_data['mac']
            elif 'radio_mac' in match_data:
                event['radio'] = match_data['radio_mac']
            
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
        """Determine event type from pattern name with improved matching"""
        pattern_lower = pattern_name.lower()
        
        # Check for specific event types first (more specific patterns)
        if 'fsm_transition' in pattern_lower or 'fsm' in pattern_lower:
            return 'fsm_transition'
        elif 'channel_change_failure' in pattern_lower or 'channel_change' in pattern_lower:
            return 'channel_failure'
        elif 'channel_scan' in pattern_lower or 'scan_result' in pattern_lower:
            return 'scan_event'
        elif 'channel' in pattern_lower:
            return 'channel_event'
        elif 'interference' in pattern_lower:
            return 'interference_event'
        elif 'dfs' in pattern_lower or 'radar' in pattern_lower:
            return 'dfs_event'
        elif 'trigger' in pattern_lower and 'acs' in pattern_lower:
            return 'acs_trigger'
        elif 'acs' in pattern_lower:
            return 'acs_event'
        elif 'failure' in pattern_lower or 'error' in pattern_lower:
            return 'failure_event'
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
