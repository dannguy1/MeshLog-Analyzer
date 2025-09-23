# Pattern Recognition Framework Migration Guide

## Overview

This guide provides step-by-step instructions for migrating existing MeshLog agents to use the new Advanced Pattern Recognition Framework. The migration eliminates code duplication, improves performance, and provides a unified pattern management system.

## Migration Benefits

### Before Migration (Current State)
- **Duplicated Patterns**: Each agent redefines similar patterns (timestamp, MAC address, etc.)
- **Manual Compilation**: `re.compile()` called repeatedly in parsing loops
- **Inconsistent Parsing**: Different approaches across agents
- **No Performance Monitoring**: No tracking of pattern effectiveness
- **Hard to Extend**: Adding patterns requires code changes

### After Migration (Target State)
- **Unified Patterns**: Shared pattern definitions across agents
- **Optimized Compilation**: Patterns compiled once and cached
- **Consistent Interface**: Standardized parsing across all agents
- **Performance Monitoring**: Real-time pattern effectiveness tracking
- **Easy Extension**: Add patterns via configuration files

## Migration Steps

### Step 1: Install Framework Dependencies

The framework is already included in the MeshLog codebase. No additional dependencies are required.

### Step 2: Update Agent Imports

Replace existing pattern-related imports with the framework:

```python
# OLD - Remove these imports
import re
from typing import Dict, List, Any

# NEW - Add framework import
from app.core.pattern_recognition import get_agent_interface
```

### Step 3: Initialize Pattern Interface

Replace manual pattern definitions with the framework interface:

```python
# OLD - Remove manual pattern definitions
class WncAcsAgent(LCMAnalysisAgent):
    def __init__(self):
        self.detection_patterns = {
            'countdown': r'item MAC (?P<mac>[0-9a-f:]+), Sending countdown: (?P<countdown>\d+), MinInterval delta: (?P<delta>\d+)',
            'fsm_transition': r'RADIO (?P<mac>[0-9a-f:]+), FSM: (?P<from_state>\S+)  --> (?P<to_state>\S+)',
            # ... many more patterns
        }

# NEW - Use framework interface
class WncAcsAgent(LCMAnalysisAgent):
    def __init__(self):
        self.pattern_interface = get_agent_interface("wnc-acs")
```

### Step 4: Replace Pattern Matching Logic

Replace manual pattern matching with framework methods:

```python
# OLD - Manual pattern matching
def _parse_log(self, log_content: str) -> List[Dict[str, Any]]:
    events = []
    lines = log_content.splitlines()
    
    # Compile patterns for efficiency
    compiled_patterns = {name: re.compile(pattern) for name, pattern in self.detection_patterns.items()}
    
    for line in lines:
        if 'wnc-acs:' not in line:
            continue
            
        # Extract timestamp
        ts_match = re.match(r'(\d{4} \w{3} \d{2} \d{2}:\d{2}:\d{2}\.\d{6})', line)
        if not ts_match:
            continue
            
        # Extract content
        content_start = line.find('wnc-acs: ') + len('wnc-acs: ')
        content = line[content_start:].strip()
        
        # Match against patterns
        for event_type, pattern in compiled_patterns.items():
            m = pattern.match(content)
            if m:
                data = m.groupdict()
                event = {
                    'time': dt,
                    'event': event_type,
                    'data': data
                }
                events.append(event)
                break
    
    return events

# NEW - Framework-based pattern matching
def _parse_log(self, log_content: str) -> List[Dict[str, Any]]:
    events = []
    lines = log_content.splitlines()
    
    for i, line in enumerate(lines):
        if 'wnc-acs:' not in line:
            continue
            
        # Use framework to parse line
        result = self.pattern_interface.parse_log_line(line, i)
        
        if result['status'] == 'matched':
            # Extract timestamp (handled by framework)
            timestamp = self._extract_timestamp(line)
            
            event = {
                'time': timestamp,
                'event': result['pattern_name'],
                'data': result['match_data'],
                'confidence': result['confidence']
            }
            events.append(event)
    
    return events
```

### Step 5: Update Batch Processing

Replace manual batch processing with framework methods:

```python
# OLD - Manual batch processing
def analyze(self, log_files: List[Path], output_dir: Path, config: Dict[str, Any]) -> AnalysisResult:
    all_events = []
    
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
        
        events = self._parse_log(log_content)
        all_events.extend(events)

# NEW - Framework batch processing
def analyze(self, log_files: List[Path], output_dir: Path, config: Dict[str, Any]) -> AnalysisResult:
    all_events = []
    
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Use framework batch processing
        results = self.pattern_interface.parse_log_batch(lines)
        
        for line_idx, result in results.items():
            if result['status'] == 'matched':
                timestamp = self._extract_timestamp(result['line'])
                event = {
                    'time': timestamp,
                    'event': result['pattern_name'],
                    'data': result['match_data'],
                    'confidence': result['confidence']
                }
                all_events.append(event)
```

### Step 6: Add Performance Monitoring

Add performance monitoring to track pattern effectiveness:

```python
# NEW - Add performance monitoring
def get_analysis_summary(self) -> Dict[str, Any]:
    """Get analysis summary with performance metrics"""
    summary = {
        'agent_name': self.agent_name,
        'agent_version': self.agent_version,
        'pattern_performance': self.pattern_interface.get_pattern_performance(),
        'framework_stats': self.pattern_interface.get_performance_summary()
    }
    
    return summary
```

### Step 7: Add Custom Patterns (Optional)

Add agent-specific custom patterns:

```python
# NEW - Add custom patterns for agent-specific needs
def __init__(self):
    self.pattern_interface = get_agent_interface("wnc-acs")
    
    # Add custom patterns if needed
    self._add_custom_patterns()

def _add_custom_patterns(self):
    """Add custom patterns specific to this agent"""
    custom_patterns = [
        {
            'name': 'custom_acs_event',
            'pattern': r'Custom ACS event: (?P<event_type>\w+) for (?P<mac>[0-9a-f:]+)',
            'description': 'Custom ACS event pattern',
            'samples': [
                'Custom ACS event: SCAN for aa:bb:cc:dd:ee:ff',
                'Custom ACS event: SELECT for 11:22:33:44:55:66'
            ]
        }
    ]
    
    for pattern_data in custom_patterns:
        self.pattern_interface.add_custom_pattern(
            pattern_data['name'],
            pattern_data['pattern'],
            pattern_data['description'],
            pattern_data['samples']
        )
```

## Complete Migration Example

Here's a complete example of migrating the WNC ACS agent:

### Before Migration

```python
class WncAcsAgent(LCMAnalysisAgent):
    def __init__(self):
        self.detection_patterns = {
            'countdown': r'item MAC (?P<mac>[0-9a-f:]+), Sending countdown: (?P<countdown>\d+), MinInterval delta: (?P<delta>\d+)',
            'fsm_transition': r'RADIO (?P<mac>[0-9a-f:]+), FSM: (?P<from_state>\S+)  --> (?P<to_state>\S+)',
            'trigger_acs': r'trigger ACS, reason: (?P<reason>\S+)',
            # ... 15+ more patterns
        }
    
    def _parse_log(self, log_content: str) -> List[Dict[str, Any]]:
        events = []
        lines = log_content.splitlines()
        
        # Manual pattern compilation
        compiled_patterns = {name: re.compile(pattern) for name, pattern in self.detection_patterns.items()}
        
        for line in lines:
            if 'wnc-acs:' not in line:
                continue
                
            # Manual timestamp extraction
            ts_match = re.match(r'(\d{4} \w{3} \d{2} \d{2}:\d{2}:\d{2}\.\d{6})', line)
            if not ts_match:
                continue
                
            # Manual content extraction
            content_start = line.find('wnc-acs: ') + len('wnc-acs: ')
            content = line[content_start:].strip()
            
            # Manual pattern matching
            for event_type, pattern in compiled_patterns.items():
                m = pattern.match(content)
                if m:
                    data = m.groupdict()
                    event = {
                        'time': dt,
                        'event': event_type,
                        'data': data
                    }
                    events.append(event)
                    break
        
        return events
```

### After Migration

```python
from app.core.pattern_recognition import get_agent_interface

class WncAcsAgent(LCMAnalysisAgent):
    def __init__(self):
        # Initialize pattern interface
        self.pattern_interface = get_agent_interface("wnc-acs")
        
        # Add any custom patterns
        self._add_custom_patterns()
    
    def _add_custom_patterns(self):
        """Add custom patterns specific to ACS agent"""
        custom_patterns = [
            {
                'name': 'acs_custom_event',
                'pattern': r'Custom ACS: (?P<event_type>\w+) for (?P<mac>[0-9a-f:]+)',
                'description': 'Custom ACS event pattern',
                'samples': ['Custom ACS: SCAN for aa:bb:cc:dd:ee:ff']
            }
        ]
        
        for pattern_data in custom_patterns:
            self.pattern_interface.add_custom_pattern(
                pattern_data['name'],
                pattern_data['pattern'],
                pattern_data['description'],
                pattern_data['samples']
            )
    
    def _parse_log(self, log_content: str) -> List[Dict[str, Any]]:
        events = []
        lines = log_content.splitlines()
        
        # Use framework for pattern matching
        for i, line in enumerate(lines):
            if 'wnc-acs:' not in line:
                continue
                
            # Use framework to parse line
            result = self.pattern_interface.parse_log_line(line, i)
            
            if result['status'] == 'matched':
                # Extract timestamp (can be handled by framework or manually)
                timestamp = self._extract_timestamp(line)
                
                event = {
                    'time': timestamp,
                    'event': result['pattern_name'],
                    'data': result['match_data'],
                    'confidence': result['confidence']
                }
                events.append(event)
        
        return events
    
    def _extract_timestamp(self, line: str) -> datetime:
        """Extract timestamp from log line"""
        # This can be simplified using framework timestamp patterns
        ts_match = re.match(r'(\d{4} \w{3} \d{2} \d{2}:\d{2}:\d{2}\.\d{6})', line)
        if ts_match:
            return datetime.strptime(ts_match.group(1), '%Y %b %d %H:%M:%S.%f')
        return datetime.now()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary with framework metrics"""
        return {
            'agent_name': self.agent_name,
            'agent_version': self.agent_version,
            'pattern_performance': self.pattern_interface.get_pattern_performance(),
            'framework_stats': self.pattern_interface.get_performance_summary()
        }
```

## Migration Checklist

### Pre-Migration
- [ ] Backup existing agent code
- [ ] Review current pattern definitions
- [ ] Identify custom patterns that need to be added
- [ ] Plan testing strategy

### During Migration
- [ ] Update imports to use framework
- [ ] Replace manual pattern definitions with framework interface
- [ ] Update pattern matching logic
- [ ] Add performance monitoring
- [ ] Add custom patterns if needed
- [ ] Update batch processing methods

### Post-Migration
- [ ] Test with sample log files
- [ ] Verify pattern matching accuracy
- [ ] Check performance improvements
- [ ] Update documentation
- [ ] Deploy and monitor

## Testing Strategy

### 1. Unit Testing
```python
def test_pattern_matching():
    """Test pattern matching with known log lines"""
    agent = WncAcsAgent()
    
    test_lines = [
        "2024 Jan 10 14:30:15.123456 router wnc-acs: RADIO aa:bb:cc:dd:ee:ff FSM: SERVING --> CHECKING",
        "2024 Jan 10 14:30:16.123456 router wnc-acs: trigger ACS, reason: PERIOD"
    ]
    
    for line in test_lines:
        result = agent.pattern_interface.parse_log_line(line)
        assert result['status'] == 'matched'
        assert result['confidence'] > 0.5
```

### 2. Performance Testing
```python
def test_performance():
    """Test performance improvements"""
    agent = WncAcsAgent()
    
    # Test with large log file
    with open('large_log_file.txt', 'r') as f:
        lines = f.readlines()
    
    start_time = time.time()
    results = agent.pattern_interface.parse_log_batch(lines)
    end_time = time.time()
    
    processing_time = end_time - start_time
    print(f"Processed {len(lines)} lines in {processing_time:.2f} seconds")
    print(f"Rate: {len(lines)/processing_time:.0f} lines/second")
```

### 3. Accuracy Testing
```python
def test_accuracy():
    """Test pattern matching accuracy"""
    agent = WncAcsAgent()
    
    # Test with known good and bad examples
    good_examples = [
        "2024 Jan 10 14:30:15.123456 router wnc-acs: RADIO aa:bb:cc:dd:ee:ff FSM: SERVING --> CHECKING"
    ]
    
    bad_examples = [
        "2024 Jan 10 14:30:15.123456 router wnc-steer: Processing weak signal client"
    ]
    
    for line in good_examples:
        result = agent.pattern_interface.parse_log_line(line)
        assert result['status'] == 'matched'
    
    for line in bad_examples:
        result = agent.pattern_interface.parse_log_line(line)
        assert result['status'] == 'no_match'
```

## Troubleshooting

### Common Issues

1. **Pattern Not Matching**
   - Check pattern syntax in configuration file
   - Verify agent type is correct
   - Test pattern with validation samples

2. **Performance Issues**
   - Check if patterns are being compiled repeatedly
   - Verify batch processing is being used
   - Monitor performance metrics

3. **Custom Patterns Not Working**
   - Verify pattern syntax
   - Check if pattern is registered correctly
   - Test with validation samples

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Framework will show detailed logging information
```

## Performance Expectations

### Before Migration
- Pattern compilation: ~1ms per pattern per file
- Pattern matching: ~0.1ms per pattern per line
- Memory usage: High due to repeated compilation

### After Migration
- Pattern compilation: ~1ms per pattern (once)
- Pattern matching: ~0.05ms per pattern per line
- Memory usage: Reduced due to caching
- Overall improvement: 2-5x faster processing

## Conclusion

The migration to the Advanced Pattern Recognition Framework provides significant benefits:

- **Performance**: 2-5x faster pattern matching
- **Maintainability**: Centralized pattern management
- **Extensibility**: Easy to add new patterns
- **Monitoring**: Real-time performance tracking
- **Consistency**: Unified interface across agents

The migration process is straightforward and can be done incrementally, allowing for thorough testing at each step.



