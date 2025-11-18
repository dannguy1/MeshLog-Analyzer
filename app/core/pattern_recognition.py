#!/usr/bin/env python3
"""
Advanced Pattern Recognition Framework Implementation
Part of the MeshLog Agent System

This module provides a unified, high-performance pattern recognition framework
for all MeshLog agents, eliminating code duplication and improving maintainability.
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import re
import json
import time
import threading
from pathlib import Path
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatternCategory(Enum):
    """Pattern categories for organization and optimization"""
    TIMESTAMP = "timestamp"
    MAC_ADDRESS = "mac_address"
    COMPONENT_ID = "component_id"
    MESSAGE_FORMAT = "message_format"
    EVENT_SPECIFIC = "event_specific"
    CONFIGURATION = "configuration"
    PERFORMANCE = "performance"

class PatternPriority(Enum):
    """Pattern execution priority for optimization"""
    CRITICAL = 1      # Timestamp, component ID
    HIGH = 2          # Event patterns
    MEDIUM = 3        # Configuration patterns
    LOW = 4           # Optional patterns

@dataclass
class PatternDefinition:
    """Enhanced pattern definition with metadata"""
    name: str
    pattern: str
    category: PatternCategory
    priority: PatternPriority
    description: str
    agent_types: List[str] = field(default_factory=list)
    compiled_pattern: Optional[re.Pattern] = None
    match_count: int = 0
    last_used: Optional[float] = None
    performance_score: float = 0.0
    validation_samples: List[str] = field(default_factory=list)
    is_active: bool = True
    
    def __post_init__(self):
        if self.compiled_pattern is None:
            try:
                self.compiled_pattern = re.compile(self.pattern, re.IGNORECASE)
            except re.error as e:
                logger.error(f"Failed to compile pattern '{self.name}': {e}")
                self.is_active = False
    
    def get_compiled(self) -> re.Pattern:
        """Get compiled pattern with lazy loading"""
        if self.compiled_pattern is None and self.is_active:
            try:
                self.compiled_pattern = re.compile(self.pattern, re.IGNORECASE)
            except re.error as e:
                logger.error(f"Failed to compile pattern '{self.name}': {e}")
                self.is_active = False
        return self.compiled_pattern

@dataclass
class PatternMatch:
    """Result of pattern matching with enhanced metadata"""
    pattern_name: str
    match_data: Dict[str, Any]
    confidence: float
    processing_time: float
    line_number: int
    context: str

class PatternRegistry:
    """Centralized pattern registry with advanced management"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.patterns: Dict[str, PatternDefinition] = {}
        self.category_index: Dict[PatternCategory, List[str]] = defaultdict(list)
        self.agent_index: Dict[str, List[str]] = defaultdict(list)
        self.performance_stats = defaultdict(lambda: {'matches': 0, 'time': 0.0})
        self.config_path = config_path or Path("patterns.json")
        self._lock = threading.RLock()
        self._load_default_patterns()
        self._load_patterns()
    
    def _load_default_patterns(self) -> None:
        """Load default patterns that are common across all agents"""
        default_patterns = [
            {
                'name': 'wnc_timestamp',
                'pattern': r'(?P<year>\d{4}) (?P<month>\w{3}) (?P<day>\d{1,2}) (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})\.(?P<microsecond>\d+)',
                'category': 'timestamp',
                'priority': 'CRITICAL',
                'description': 'Standard WNC log timestamp format',
                'agent_types': ['wnc-acs', 'wnc-steering', 'wnc-tpyopt'],
                'validation_samples': [
                    '2024 Jan 10 14:30:15.123456',
                    '2024 Dec 25 09:15:30.789012'
                ]
            },
            {
                'name': 'mac_address_standard',
                'pattern': r'(?P<mac>[0-9a-f]{2}(:[0-9a-f]{2}){5})',
                'category': 'mac_address',
                'priority': 'HIGH',
                'description': 'Standard MAC address format',
                'agent_types': ['wnc-acs', 'wnc-steering', 'wnc-tpyopt'],
                'validation_samples': [
                    'aa:bb:cc:dd:ee:ff',
                    '11:22:33:44:55:66'
                ]
            },
            {
                'name': 'wnc_component_acs',
                'pattern': r'wnc-acs:',
                'category': 'component_id',
                'priority': 'CRITICAL',
                'description': 'WNC ACS component identifier',
                'agent_types': ['wnc-acs'],
                'validation_samples': [
                    '2024 Jan 10 14:30:15.123456 router wnc-acs: RADIO aa:bb:cc:dd:ee:ff',
                    '2024 Jan 10 14:30:16.123456 router wnc-acs: trigger ACS'
                ]
            },
            {
                'name': 'wnc_component_steering',
                'pattern': r'wnc-steer:',
                'category': 'component_id',
                'priority': 'CRITICAL',
                'description': 'WNC Steering component identifier',
                'agent_types': ['wnc-steering'],
                'validation_samples': [
                    '2024 Jan 10 14:30:15.123456 router wnc-steer: Processing weak signal client',
                    '2024 Jan 10 14:30:16.123456 router wnc-steer: beacon_measurement_map'
                ]
            },
            {
                'name': 'wnc_component_tpyopt',
                'pattern': r'wnc-tpyopt:',
                'category': 'component_id',
                'priority': 'CRITICAL',
                'description': 'WNC TPYOPT component identifier',
                'agent_types': ['wnc-tpyopt'],
                'validation_samples': [
                    '2024 Jan 10 14:30:15.123456 router wnc-tpyopt: State: WaitTrigger --> SendScan',
                    '2024 Jan 10 14:30:16.123456 router wnc-tpyopt: Build topology success!'
                ]
            }
        ]
        
        for pattern_data in default_patterns:
            try:
                pattern_def = PatternDefinition(
                    name=pattern_data['name'],
                    pattern=pattern_data['pattern'],
                    category=PatternCategory(pattern_data['category']),
                    priority=PatternPriority[pattern_data['priority']],
                    description=pattern_data['description'],
                    agent_types=pattern_data.get('agent_types', []),
                    validation_samples=pattern_data.get('validation_samples', [])
                )
                self.register_pattern(pattern_def)
            except Exception as e:
                logger.error(f"Failed to load default pattern '{pattern_data['name']}': {e}")
    
    def register_pattern(self, pattern_def: PatternDefinition) -> None:
        """Register a new pattern with validation"""
        with self._lock:
            # Validate pattern syntax
            try:
                test_compile = re.compile(pattern_def.pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern_def.name}': {e}")
            
            # Register pattern
            self.patterns[pattern_def.name] = pattern_def
            self.category_index[pattern_def.category].append(pattern_def.name)
            
            for agent_type in pattern_def.agent_types:
                self.agent_index[agent_type].append(pattern_def.name)
            
            logger.info(f"Registered pattern '{pattern_def.name}' for agents: {pattern_def.agent_types}")
    
    def get_patterns_for_agent(self, agent_type: str, 
                              priority_filter: Optional[PatternPriority] = None) -> List[PatternDefinition]:
        """Get patterns for specific agent with optional priority filtering"""
        with self._lock:
            pattern_names = self.agent_index.get(agent_type, [])
            patterns = [self.patterns[name] for name in pattern_names if self.patterns[name].is_active]
            
            if priority_filter:
                patterns = [p for p in patterns if p.priority.value <= priority_filter.value]
            
            # Sort by priority and performance score
            return sorted(patterns, key=lambda p: (p.priority.value, -p.performance_score))
    
    def update_performance(self, pattern_name: str, processing_time: float) -> None:
        """Update pattern performance metrics"""
        with self._lock:
            if pattern_name in self.patterns:
                pattern = self.patterns[pattern_name]
                pattern.match_count += 1
                pattern.last_used = time.time()
                
                # Calculate rolling performance score
                stats = self.performance_stats[pattern_name]
                stats['matches'] += 1
                stats['time'] += processing_time
                pattern.performance_score = stats['matches'] / stats['time'] if stats['time'] > 0 else 0
    
    def _load_patterns(self) -> None:
        """Load patterns from configuration file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                for pattern_data in data.get('patterns', []):
                    try:
                        pattern_def = PatternDefinition(
                            name=pattern_data['name'],
                            pattern=pattern_data['pattern'],
                            category=PatternCategory(pattern_data['category']),
                            priority=PatternPriority[pattern_data['priority']],
                            description=pattern_data['description'],
                            agent_types=pattern_data.get('agent_types', []),
                            validation_samples=pattern_data.get('validation_samples', [])
                        )
                        self.register_pattern(pattern_def)
                    except Exception as e:
                        logger.error(f"Failed to load pattern '{pattern_data.get('name', 'unknown')}': {e}")
                        
            except Exception as e:
                logger.warning(f"Failed to load patterns from {self.config_path}: {e}")
    
    def save_patterns(self) -> None:
        """Save current patterns to configuration file"""
        with self._lock:
            try:
                data = {
                    'version': '1.0.0',
                    'description': 'MeshLog Agent Pattern Recognition Configuration',
                    'patterns': []
                }
                
                for pattern_def in self.patterns.values():
                    pattern_data = {
                        'name': pattern_def.name,
                        'pattern': pattern_def.pattern,
                        'category': pattern_def.category.value,
                        'priority': pattern_def.priority.value,
                        'description': pattern_def.description,
                        'agent_types': pattern_def.agent_types,
                        'validation_samples': pattern_def.validation_samples
                    }
                    data['patterns'].append(pattern_data)
                
                with open(self.config_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Saved {len(self.patterns)} patterns to {self.config_path}")
                
            except Exception as e:
                logger.error(f"Failed to save patterns to {self.config_path}: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all patterns"""
        with self._lock:
            summary = {
                'total_patterns': len(self.patterns),
                'active_patterns': sum(1 for p in self.patterns.values() if p.is_active),
                'patterns_by_agent': {},
                'top_performers': [],
                'performance_stats': {}
            }
            
            # Patterns by agent
            for agent_type in self.agent_index.keys():
                agent_patterns = self.get_patterns_for_agent(agent_type)
                summary['patterns_by_agent'][agent_type] = {
                    'total': len(agent_patterns),
                    'active': sum(1 for p in agent_patterns if p.is_active),
                    'total_matches': sum(p.match_count for p in agent_patterns)
                }
            
            # Top performers
            top_patterns = sorted(
                self.patterns.values(), 
                key=lambda p: p.performance_score, 
                reverse=True
            )[:10]
            
            summary['top_performers'] = [
                {
                    'name': p.name,
                    'performance_score': p.performance_score,
                    'match_count': p.match_count,
                    'category': p.category.value
                }
                for p in top_patterns
            ]
            
            return summary

class PatternEngine:
    """High-performance pattern matching engine with optimization"""
    
    def __init__(self, registry: PatternRegistry):
        self.registry = registry
        self.match_cache: Dict[str, List[PatternMatch]] = {}
        self.cache_max_size = 1000
        self.performance_monitor = defaultdict(list)
    
    def match_line(self, line: str, agent_type: str, 
                   context: Optional[Dict] = None) -> List[PatternMatch]:
        """
        Match line against all relevant patterns with optimization
        
        Args:
            line: Log line to match
            agent_type: Type of agent requesting match
            context: Additional context for matching
            
        Returns:
            List of pattern matches ordered by priority and confidence
        """
        start_time = time.perf_counter()
        matches = []
        
        # Get patterns for this agent, ordered by priority
        patterns = self.registry.get_patterns_for_agent(agent_type)
        
        for pattern_def in patterns:
            if not pattern_def.is_active:
                continue
            
            pattern_start = time.perf_counter()
            
            try:
                compiled = pattern_def.get_compiled()
                if compiled is None:
                    continue
                    
                match = compiled.search(line)
                
                if match:
                    # Extract match data
                    match_data = match.groupdict() if match.groupdict() else {'full_match': match.group()}
                    
                    # Calculate confidence based on pattern characteristics
                    confidence = self._calculate_confidence(pattern_def, match_data, line)
                    
                    pattern_match = PatternMatch(
                        pattern_name=pattern_def.name,
                        match_data=match_data,
                        confidence=confidence,
                        processing_time=time.perf_counter() - pattern_start,
                        line_number=context.get('line_number', 0) if context else 0,
                        context=line[:100] + "..." if len(line) > 100 else line
                    )
                    
                    matches.append(pattern_match)
                    
                    # Update performance metrics
                    self.registry.update_performance(
                        pattern_def.name, 
                        time.perf_counter() - pattern_start
                    )
                    
                    # Early exit for high-confidence matches
                    if confidence > 0.9 and pattern_def.priority == PatternPriority.CRITICAL:
                        break
            
            except Exception as e:
                logger.error(f"Pattern matching error for '{pattern_def.name}': {e}")
        
        # Sort matches by confidence and priority
        # Handle case where pattern might not be in registry (shouldn't happen but be safe)
        matches.sort(key=lambda m: (
            -m.confidence,
            self.registry.patterns.get(m.pattern_name, 
                PatternDefinition(name=m.pattern_name, pattern='', 
                category=PatternCategory.EVENT_SPECIFIC, 
                priority=PatternPriority.LOW, 
                description='', agent_types=[])).priority.value
        ))
        
        # Record overall performance
        total_time = time.perf_counter() - start_time
        self.performance_monitor['total_matching_time'].append({
            'time': total_time,
            'matches_found': len(matches),
            'agent_type': agent_type,
            'timestamp': time.time()
        })
        
        return matches
    
    def _calculate_confidence(self, pattern_def: PatternDefinition, 
                            match_data: Dict[str, Any], line: str) -> float:
        """Calculate confidence score for pattern match"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for named groups
        if match_data and any(k != 'full_match' for k in match_data.keys()):
            confidence += 0.2
        
        # Boost confidence for specific patterns
        if pattern_def.category == PatternCategory.TIMESTAMP:
            confidence += 0.3
        elif pattern_def.category == PatternCategory.COMPONENT_ID:
            confidence += 0.2
        
        # Boost confidence based on historical performance
        confidence += min(0.2, pattern_def.performance_score / 100)
        
        return min(1.0, confidence)
    
    def batch_match(self, lines: List[str], agent_type: str) -> Dict[int, List[PatternMatch]]:
        """Optimized batch matching for multiple lines"""
        results = {}
        
        # Pre-compile patterns for this agent
        patterns = self.registry.get_patterns_for_agent(agent_type)
        compiled_patterns = [(p.name, p.get_compiled()) for p in patterns if p.is_active and p.get_compiled() is not None]
        
        for i, line in enumerate(lines):
            matches = []
            for pattern_name, compiled in compiled_patterns:
                try:
                    match = compiled.search(line)
                    if match:
                        match_data = match.groupdict() if match.groupdict() else {'full_match': match.group()}
                        confidence = self._calculate_confidence(
                            self.registry.patterns[pattern_name], match_data, line
                        )
                        
                        pattern_match = PatternMatch(
                            pattern_name=pattern_name,
                            match_data=match_data,
                            confidence=confidence,
                            processing_time=0.0,  # Batch processing time not measured per pattern
                            line_number=i,
                            context=line[:100] + "..." if len(line) > 100 else line
                        )
                        matches.append(pattern_match)
                except Exception as e:
                    logger.error(f"Batch matching error for pattern '{pattern_name}': {e}")
            
            results[i] = matches
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}
        
        for metric_name, values in self.performance_monitor.items():
            if values:
                recent_values = values[-100:]  # Last 100 measurements
                stats[metric_name] = {
                    'avg': sum(v['time'] for v in recent_values) / len(recent_values),
                    'min': min(v['time'] for v in recent_values),
                    'max': max(v['time'] for v in recent_values),
                    'count': len(values)
                }
        
        return stats

class AgentPatternInterface:
    """Simplified interface for agents to use the pattern recognition framework"""
    
    def __init__(self, agent_type: str, registry: PatternRegistry):
        self.agent_type = agent_type
        self.registry = registry
        self.engine = PatternEngine(registry)
        logger.info(f"Initialized pattern interface for agent: {agent_type}")
    
    def parse_log_line(self, line: str, line_number: int = 0) -> Dict[str, Any]:
        """Parse single log line and return structured data"""
        context = {'line_number': line_number}
        matches = self.engine.match_line(line, self.agent_type, context)
        
        if not matches:
            return {'status': 'no_match', 'line': line}
        
        # Return the highest confidence match
        best_match = matches[0]
        
        return {
            'status': 'matched',
            'pattern_name': best_match.pattern_name,
            'match_data': best_match.match_data,
            'confidence': best_match.confidence,
            'line': line,
            'all_matches': [{'name': m.pattern_name, 'confidence': m.confidence} for m in matches]
        }
    
    def parse_log_batch(self, lines: List[str]) -> Dict[int, Dict[str, Any]]:
        """Parse multiple log lines efficiently"""
        batch_results = self.engine.batch_match(lines, self.agent_type)
        
        results = {}
        for line_idx, matches in batch_results.items():
            if matches:
                best_match = matches[0]
                results[line_idx] = {
                    'status': 'matched',
                    'pattern_name': best_match.pattern_name,
                    'match_data': best_match.match_data,
                    'confidence': best_match.confidence,
                    'line': lines[line_idx]
                }
            else:
                results[line_idx] = {
                    'status': 'no_match',
                    'line': lines[line_idx]
                }
        
        return results
    
    def add_custom_pattern(self, name: str, pattern: str, 
                          description: str, samples: List[str] = None) -> bool:
        """Add custom pattern for this agent"""
        try:
            pattern_def = PatternDefinition(
                name=name,
                pattern=pattern,
                category=PatternCategory.EVENT_SPECIFIC,
                priority=PatternPriority.MEDIUM,
                description=description,
                agent_types=[self.agent_type],
                validation_samples=samples or []
            )
            
            self.registry.register_pattern(pattern_def)
            logger.info(f"Added custom pattern '{name}' for agent '{self.agent_type}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom pattern '{name}': {e}")
            return False
    
    def get_pattern_performance(self) -> Dict[str, Any]:
        """Get performance statistics for patterns used by this agent"""
        agent_patterns = self.registry.get_patterns_for_agent(self.agent_type)
        performance_data = {}
        
        for pattern in agent_patterns:
            performance_data[pattern.name] = {
                'match_count': pattern.match_count,
                'performance_score': pattern.performance_score,
                'last_used': pattern.last_used,
                'is_active': pattern.is_active,
                'category': pattern.category.value,
                'priority': pattern.priority.value
            }
        
        return performance_data
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        return {
            'agent_type': self.agent_type,
            'pattern_performance': self.get_pattern_performance(),
            'engine_stats': self.engine.get_performance_stats(),
            'registry_summary': self.registry.get_performance_summary()
        }

# Global registry instance
_global_registry = None

def get_pattern_registry(config_path: Optional[Path] = None) -> PatternRegistry:
    """Get global pattern registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = PatternRegistry(config_path)
    return _global_registry

def get_agent_interface(agent_type: str, config_path: Optional[Path] = None) -> AgentPatternInterface:
    """Get pattern interface for specific agent type"""
    registry = get_pattern_registry(config_path)
    return AgentPatternInterface(agent_type, registry)

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    print("Advanced Pattern Recognition Framework")
    print("=" * 50)
    
    # Get agent interface
    acs_interface = get_agent_interface("wnc-acs")
    
    # Test with sample log lines
    test_lines = [
        "2024 Jan 10 14:30:15.123456 router wnc-acs: RADIO aa:bb:cc:dd:ee:ff FSM: SERVING --> CHECKING",
        "2024 Jan 10 14:30:16.123456 router wnc-acs: trigger ACS, reason: PERIOD",
        "2024 Jan 10 14:30:17.123456 router wnc-acs: Radio INFO: mac aa:bb:cc:dd:ee:ff, channel 6, freq 2437 MHz, bandwidth 20MHz"
    ]
    
    print("\nTesting pattern matching:")
    for i, line in enumerate(test_lines):
        result = acs_interface.parse_log_line(line, i)
        print(f"Line {i}: {result['status']}")
        if result['status'] == 'matched':
            print(f"  Pattern: {result['pattern_name']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Data: {result['match_data']}")
    
    # Test performance
    print("\nPerformance Summary:")
    perf = acs_interface.get_performance_summary()
    print(f"Total patterns: {perf['registry_summary']['total_patterns']}")
    print(f"Active patterns: {perf['registry_summary']['active_patterns']}")
    
    print("\nFramework initialized successfully!")

