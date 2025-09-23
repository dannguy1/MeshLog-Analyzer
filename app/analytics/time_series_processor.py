# prplOS LCM Log Analysis System - Time Series Processor

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import logging
from dataclasses import dataclass

from app.models.core import LogEntry, LogLevel

logger = logging.getLogger(__name__)

@dataclass
class TimeSeriesData:
    """Time series data structure"""
    timestamps: List[datetime]
    values: List[Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamps": [ts.isoformat() for ts in self.timestamps],
            "values": self.values,
            "metadata": self.metadata
        }

@dataclass
class EventPattern:
    """Event pattern structure"""
    pattern_id: str
    name: str
    description: str
    events: List[str]
    time_window: timedelta
    confidence: float
    occurrences: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "description": self.description,
            "events": self.events,
            "time_window_seconds": self.time_window.total_seconds(),
            "confidence": self.confidence,
            "occurrences": self.occurrences,
            "metadata": self.metadata
        }

@dataclass
class CorrelationResult:
    """Event correlation result"""
    correlation_id: str
    source_events: List[str]
    target_events: List[str]
    correlation_type: str
    strength: float
    confidence: float
    time_lag: Optional[timedelta]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "correlation_id": self.correlation_id,
            "source_events": self.source_events,
            "target_events": self.target_events,
            "correlation_type": self.correlation_type,
            "strength": self.strength,
            "confidence": self.confidence,
            "time_lag_seconds": self.time_lag.total_seconds() if self.time_lag else None,
            "metadata": self.metadata
        }

class TimeSeriesProcessor:
    """Process log entries into time series data"""
    
    def __init__(self):
        self.time_resolution = timedelta(minutes=1)  # Default 1-minute resolution
        
    def create_time_series(self, log_entries: List[LogEntry], 
                          metric: str = "count", 
                          time_resolution: Optional[timedelta] = None) -> TimeSeriesData:
        """Create time series from log entries"""
        logger.info(f"Creating time series for metric: {metric}")
        
        if time_resolution:
            self.time_resolution = time_resolution
        
        # Sort entries by timestamp
        sorted_entries = sorted(log_entries, key=lambda x: x.timestamp)
        
        if not sorted_entries:
            return TimeSeriesData([], [], {"metric": metric, "empty": True})
        
        # Create time bins
        start_time = sorted_entries[0].timestamp
        end_time = sorted_entries[-1].timestamp
        
        time_bins = self._create_time_bins(start_time, end_time)
        
        # Aggregate data by time bin
        aggregated_data = self._aggregate_by_time_bin(sorted_entries, time_bins, metric)
        
        # Create time series data
        timestamps = list(aggregated_data.keys())
        values = list(aggregated_data.values())
        
        metadata = {
            "metric": metric,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "time_resolution_seconds": self.time_resolution.total_seconds(),
            "total_entries": len(log_entries),
            "time_bins": len(timestamps)
        }
        
        return TimeSeriesData(timestamps, values, metadata)
    
    def _create_time_bins(self, start_time: datetime, end_time: datetime) -> List[datetime]:
        """Create time bins for aggregation"""
        bins = []
        current_time = start_time
        
        while current_time <= end_time:
            bins.append(current_time)
            current_time += self.time_resolution
        
        return bins
    
    def _aggregate_by_time_bin(self, entries: List[LogEntry], 
                              time_bins: List[datetime], 
                              metric: str) -> Dict[datetime, Any]:
        """Aggregate log entries by time bin"""
        aggregated = defaultdict(lambda: 0)
        
        for entry in entries:
            # Find the appropriate time bin
            bin_time = self._find_time_bin(entry.timestamp, time_bins)
            if bin_time:
                if metric == "count":
                    aggregated[bin_time] += 1
                elif metric == "error_count":
                    if entry.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                        aggregated[bin_time] += 1
                elif metric == "warning_count":
                    if entry.log_level == LogLevel.WARNING:
                        aggregated[bin_time] += 1
                elif metric == "unique_applications":
                    # Count unique applications per bin
                    if bin_time not in aggregated:
                        aggregated[bin_time] = set()
                    aggregated[bin_time].add(entry.application)
        
        # Convert sets to counts for unique_applications
        if metric == "unique_applications":
            return {k: len(v) if isinstance(v, set) else v for k, v in aggregated.items()}
        
        return dict(aggregated)
    
    def _find_time_bin(self, timestamp: datetime, time_bins: List[datetime]) -> Optional[datetime]:
        """Find the appropriate time bin for a timestamp"""
        for bin_time in time_bins:
            if timestamp >= bin_time and timestamp < bin_time + self.time_resolution:
                return bin_time
        return None
    
    def get_statistics(self, time_series: TimeSeriesData) -> Dict[str, Any]:
        """Calculate statistics for time series data"""
        if not time_series.values:
            return {"empty": True}
        
        values = [v for v in time_series.values if v is not None]
        
        if not values:
            return {"empty": True}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": np.mean(values),
            "median": np.median(values),
            "std": np.std(values),
            "sum": sum(values),
            "non_zero_count": sum(1 for v in values if v > 0),
            "zero_count": sum(1 for v in values if v == 0)
        }

class EventCorrelator:
    """Correlate events across different applications and time periods"""
    
    def __init__(self):
        self.correlation_patterns = {
            "error_cascade": {
                "description": "Error events that trigger subsequent errors",
                "patterns": [
                    ["error", "error", "error"],
                    ["critical", "error", "error"],
                    ["error", "critical", "error"]
                ]
            },
            "startup_sequence": {
                "description": "Application startup sequence patterns",
                "patterns": [
                    ["starting", "started", "ready"],
                    ["initializing", "initialized", "running"],
                    ["loading", "loaded", "active"]
                ]
            },
            "shutdown_sequence": {
                "description": "Application shutdown sequence patterns",
                "patterns": [
                    ["stopping", "stopped", "terminated"],
                    ["shutting", "shutdown", "closed"],
                    ["exiting", "exited", "terminated"]
                ]
            }
        }
    
    def find_event_patterns(self, log_entries: List[LogEntry], 
                           time_window: timedelta = timedelta(minutes=5)) -> List[EventPattern]:
        """Find event patterns in log entries"""
        logger.info(f"Finding event patterns with time window: {time_window}")
        
        patterns = []
        
        # Group entries by application
        app_entries = defaultdict(list)
        for entry in log_entries:
            app_entries[entry.application].append(entry)
        
        # Find patterns for each application
        for app_name, entries in app_entries.items():
            app_patterns = self._find_application_patterns(entries, time_window, app_name)
            patterns.extend(app_patterns)
        
        # Find cross-application patterns
        cross_app_patterns = self._find_cross_application_patterns(log_entries, time_window)
        patterns.extend(cross_app_patterns)
        
        logger.info(f"Found {len(patterns)} event patterns")
        return patterns
    
    def _find_application_patterns(self, entries: List[LogEntry], 
                                  time_window: timedelta, 
                                  app_name: str) -> List[EventPattern]:
        """Find patterns within a single application"""
        patterns = []
        
        # Sort entries by timestamp
        sorted_entries = sorted(entries, key=lambda x: x.timestamp)
        
        # Look for predefined patterns
        for pattern_name, pattern_info in self.correlation_patterns.items():
            pattern_occurrences = self._find_pattern_occurrences(
                sorted_entries, pattern_info["patterns"], time_window
            )
            
            for occurrence in pattern_occurrences:
                pattern = EventPattern(
                    pattern_id=f"{app_name}_{pattern_name}_{len(patterns)}",
                    name=f"{pattern_name} ({app_name})",
                    description=pattern_info["description"],
                    events=occurrence["events"],
                    time_window=time_window,
                    confidence=occurrence["confidence"],
                    occurrences=occurrence["count"],
                    metadata={
                        "application": app_name,
                        "pattern_type": pattern_name,
                        "start_time": occurrence["start_time"].isoformat(),
                        "end_time": occurrence["end_time"].isoformat()
                    }
                )
                patterns.append(pattern)
        
        return patterns
    
    def _find_pattern_occurrences(self, entries: List[LogEntry], 
                                 pattern_sequences: List[List[str]], 
                                 time_window: timedelta) -> List[Dict[str, Any]]:
        """Find occurrences of specific pattern sequences"""
        occurrences = []
        
        for i, entry in enumerate(entries):
            for pattern_sequence in pattern_sequences:
                if self._matches_pattern_sequence(entries, i, pattern_sequence, time_window):
                    occurrence = self._extract_pattern_occurrence(
                        entries, i, pattern_sequence, time_window
                    )
                    occurrences.append(occurrence)
        
        return occurrences
    
    def _matches_pattern_sequence(self, entries: List[LogEntry], 
                                 start_index: int, 
                                 pattern_sequence: List[str], 
                                 time_window: timedelta) -> bool:
        """Check if entries match a pattern sequence within time window"""
        if start_index + len(pattern_sequence) > len(entries):
            return False
        
        start_time = entries[start_index].timestamp
        
        for i, pattern in enumerate(pattern_sequence):
            entry_index = start_index + i
            if entry_index >= len(entries):
                return False
            
            entry = entries[entry_index]
            
            # Check time window
            if entry.timestamp - start_time > time_window:
                return False
            
            # Check if entry matches pattern
            if not self._entry_matches_pattern(entry, pattern):
                return False
        
        return True
    
    def _entry_matches_pattern(self, entry: LogEntry, pattern: str) -> bool:
        """Check if a log entry matches a pattern"""
        message_lower = entry.message.lower()
        pattern_lower = pattern.lower()
        
        # Check log level patterns
        if pattern_lower in ["error", "critical", "warning", "info", "debug"]:
            return entry.log_level.value == pattern_lower
        
        # Check message content patterns
        return pattern_lower in message_lower
    
    def _extract_pattern_occurrence(self, entries: List[LogEntry], 
                                   start_index: int, 
                                   pattern_sequence: List[str], 
                                   time_window: timedelta) -> Dict[str, Any]:
        """Extract pattern occurrence details"""
        start_time = entries[start_index].timestamp
        end_time = entries[start_index + len(pattern_sequence) - 1].timestamp
        
        events = []
        for i in range(len(pattern_sequence)):
            entry = entries[start_index + i]
            events.append(f"{entry.application}:{entry.message[:50]}")
        
        return {
            "events": events,
            "start_time": start_time,
            "end_time": end_time,
            "confidence": 0.8,  # Base confidence
            "count": 1
        }
    
    def _find_cross_application_patterns(self, log_entries: List[LogEntry], 
                                        time_window: timedelta) -> List[EventPattern]:
        """Find patterns across different applications"""
        patterns = []
        
        # Group entries by time windows
        time_windows = self._create_time_windows(log_entries, time_window)
        
        for window_start, window_entries in time_windows.items():
            if len(window_entries) > 1:
                # Look for error cascades across applications
                error_entries = [e for e in window_entries 
                               if e.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]]
                
                if len(error_entries) > 1:
                    apps_involved = list(set(e.application for e in error_entries))
                    
                    pattern = EventPattern(
                        pattern_id=f"cross_app_error_{len(patterns)}",
                        name="Cross-Application Error Cascade",
                        description="Multiple applications experiencing errors simultaneously",
                        events=[f"{e.application}:{e.message[:50]}" for e in error_entries],
                        time_window=time_window,
                        confidence=0.7,
                        occurrences=1,
                        metadata={
                            "applications": apps_involved,
                            "error_count": len(error_entries),
                            "window_start": window_start.isoformat()
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _create_time_windows(self, log_entries: List[LogEntry], 
                            window_size: timedelta) -> Dict[datetime, List[LogEntry]]:
        """Create time windows for cross-application analysis"""
        windows = defaultdict(list)
        
        for entry in log_entries:
            window_start = entry.timestamp.replace(
                second=0, microsecond=0
            )
            windows[window_start].append(entry)
        
        return dict(windows)
    
    def correlate_events(self, log_entries: List[LogEntry]) -> List[CorrelationResult]:
        """Find correlations between different types of events"""
        logger.info("Finding event correlations")
        
        correlations = []
        
        # Group entries by type
        error_entries = [e for e in log_entries if e.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        warning_entries = [e for e in log_entries if e.log_level == LogLevel.WARNING]
        info_entries = [e for e in log_entries if e.log_level == LogLevel.INFO]
        
        # Find error-warning correlations
        error_warning_corr = self._find_correlation(error_entries, warning_entries, "error_warning")
        if error_warning_corr:
            correlations.append(error_warning_corr)
        
        # Find application-specific correlations
        app_correlations = self._find_application_correlations(log_entries)
        correlations.extend(app_correlations)
        
        logger.info(f"Found {len(correlations)} correlations")
        return correlations
    
    def _find_correlation(self, source_events: List[LogEntry], 
                         target_events: List[LogEntry], 
                         correlation_type: str) -> Optional[CorrelationResult]:
        """Find correlation between two sets of events"""
        if not source_events or not target_events:
            return None
        
        # Calculate correlation strength based on temporal proximity
        correlations = []
        
        for source in source_events:
            for target in target_events:
                time_diff = abs((target.timestamp - source.timestamp).total_seconds())
                
                # Strong correlation if events are within 5 minutes
                if time_diff <= 300:  # 5 minutes
                    strength = 1.0 - (time_diff / 300)
                    correlations.append({
                        "strength": strength,
                        "time_lag": target.timestamp - source.timestamp,
                        "source": source,
                        "target": target
                    })
        
        if not correlations:
            return None
        
        # Calculate average correlation strength
        avg_strength = np.mean([c["strength"] for c in correlations])
        avg_time_lag = np.mean([c["time_lag"].total_seconds() for c in correlations])
        
        return CorrelationResult(
            correlation_id=f"{correlation_type}_{len(correlations)}",
            source_events=[f"{c['source'].application}:{c['source'].message[:30]}" for c in correlations[:3]],
            target_events=[f"{c['target'].application}:{c['target'].message[:30]}" for c in correlations[:3]],
            correlation_type=correlation_type,
            strength=avg_strength,
            confidence=min(avg_strength, 0.9),
            time_lag=timedelta(seconds=avg_time_lag),
            metadata={
                "total_correlations": len(correlations),
                "time_window_seconds": 300
            }
        )
    
    def _find_application_correlations(self, log_entries: List[LogEntry]) -> List[CorrelationResult]:
        """Find correlations specific to applications"""
        correlations = []
        
        # Group by application
        app_entries = defaultdict(list)
        for entry in log_entries:
            app_entries[entry.application].append(entry)
        
        # Find correlations between different applications
        app_names = list(app_entries.keys())
        
        for i, app1 in enumerate(app_names):
            for app2 in app_names[i+1:]:
                corr = self._find_correlation(
                    app_entries[app1], 
                    app_entries[app2], 
                    f"{app1}_{app2}"
                )
                if corr:
                    correlations.append(corr)
        
        return correlations
