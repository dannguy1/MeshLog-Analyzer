# 802.11k/v Client Capability Detection in WNC Steering Logs

## Executive Summary

This document outlines the research findings and implementation strategy for detecting client 802.11k/v capabilities from WNC steering logs. This capability detection is crucial for optimal WiFi steering strategy selection.

## Research Findings: 802.11k/v Standards Overview

### 802.11k (Radio Resource Measurement)
- **Purpose**: Provides information to discover the best available access point
- **Key Features**:
  - Neighbor Report Requests/Responses
  - Beacon Report Requests/Responses
  - Radio Resource Measurement
  - Load balancing optimization
- **Protocol Operation**:
  1. AP determines client is moving away
  2. Informs client to prepare to switch
  3. Client requests list of nearby APs
  4. AP provides site report
  5. Client moves to best AP based on report

### 802.11v (Wireless Network Management)
- **Purpose**: Enables client devices to exchange network topology information
- **Key Features**:
  - BSS Transition Management
  - Network-assisted Power Savings
  - Network-assisted Roaming
  - Topology awareness

## Current Implementation Analysis

Based on the existing WNC Steering Agent implementation, the system already has foundational capability detection:

### Existing Detection Patterns
```json
{
  "neighbor_report_request": "Neighbor report request.*client=([0-9a-f:]+)",
  "neighbor_report_response": "Neighbor report response.*client=([0-9a-f:]+)", 
  "bss_transition_request": "BSS transition request.*client=([0-9a-f:]+)",
  "bss_transition_response": "BSS transition response.*client=([0-9a-f:]+)",
  "beacon_measurement": "beacon_measurement_map.*client=([0-9a-f:]+).*RSSI=(-?\\d+)",
  "client_capability": "parsed clientCapability.*mac=([0-9a-f:]+)"
}
```

### Current Capability Detection Logic
```python
# From wnc_steering.py
elif 'neighbor_report' in pattern_name:
    client_stat['supports_11k'] = True
elif 'bss_transition' in pattern_name:
    client_stat['supports_11v'] = True
```

## Enhanced Detection Strategy

### 1. Explicit Capability Announcement Detection

**Pattern**: Direct capability advertisement in logs
```regex
clientCapability.*mac=(?P<mac>[0-9a-f:]+).*rrm_enabled=(?P<rrm_enabled>[01]).*btm_enabled=(?P<btm_enabled>[01])
```

**Example Log Entries**:
```
2024-01-15 10:30:15.123 wnc-steer: parsed clientCapability mac=aa:bb:cc:dd:ee:ff rrm_enabled=1 btm_enabled=1
2024-01-15 10:30:16.456 wnc-steer: client capability mac=11:22:33:44:55:66 supports_rrm=true supports_btm=false
```

### 2. Behavioral Capability Detection

**802.11k Indicators**:
- Successful neighbor report exchanges
- Beacon report responses
- Radio measurement requests/responses

**802.11v Indicators**:
- BSS transition management responses
- Network-assisted roaming participation
- Topology awareness messages

### 3. Enhanced Log Patterns

```json
{
  "client_capability_explicit": {
    "pattern": "(?:parsed\\s+)?clientCapability.*mac=(?P<mac>[0-9a-f:]+)(?:.*rrm[_=](?P<rrm_enabled>\\w+))?(?:.*btm[_=](?P<btm_enabled>\\w+))?",
    "description": "Explicit client capability announcement with RRM/BTM flags"
  },
  "neighbor_report_capability": {
    "pattern": "neighbor.*report.*(request|response).*(?:client|mac)[=\\s](?P<mac>[0-9a-f:]+)",
    "description": "802.11k neighbor report capability indicator"
  },
  "beacon_report_capability": {
    "pattern": "beacon.*(?:request|report).*(?:client|mac)[=\\s](?P<mac>[0-9a-f:]+)",
    "description": "802.11k beacon report capability indicator"
  },
  "bss_transition_capability": {
    "pattern": "(?:bss|BSS).*transition.*(request|response|query).*(?:client|mac)[=\\s](?P<mac>[0-9a-f:]+)",
    "description": "802.11v BSS transition capability indicator"
  },
  "rrm_capability_direct": {
    "pattern": "RRM.*(?:capability|enabled|support).*(?:client|mac)[=\\s](?P<mac>[0-9a-f:]+)",
    "description": "Direct RRM capability indication"
  },
  "btm_capability_direct": {
    "pattern": "BTM.*(?:capability|enabled|support).*(?:client|mac)[=\\s](?P<mac>[0-9a-f:]+)",
    "description": "Direct BTM capability indication"
  }
}
```

### 4. Negative Capability Detection

**Failed Capability Indicators**:
```json
{
  "neighbor_report_failed": {
    "pattern": "neighbor.*report.*(?:failed|timeout|unsupported).*(?:client|mac)[=\\s](?P<mac>[0-9a-f:]+)",
    "description": "Neighbor report failure indicates lack of 802.11k support"
  },
  "bss_transition_failed": {
    "pattern": "(?:bss|BSS).*transition.*(?:failed|rejected|unsupported).*(?:client|mac)[=\\s](?P<mac>[0-9a-f:]+)",
    "description": "BSS transition failure indicates lack of 802.11v support"
  }
}
```

## Implementation Plan

### Phase 1: Enhanced Pattern Recognition

1. **Extend Pattern Framework**: Add new 802.11k/v capability patterns to `patterns.json`
2. **Update Detection Logic**: Enhance `_update_client_stats_for_pattern()` method
3. **Add Negative Detection**: Implement failure-based capability detection

### Phase 2: Client Capability Database

```python
class ClientCapabilityManager:
    def __init__(self):
        self.capabilities = {}
    
    def update_capability(self, client_mac: str, capability_type: str, 
                         supported: bool, detection_method: str):
        """
        capability_type: '802.11k', '802.11v', 'neighbor_report', 'bss_transition', etc.
        detection_method: 'explicit', 'behavioral_success', 'behavioral_failure'
        """
        if client_mac not in self.capabilities:
            self.capabilities[client_mac] = {
                '802.11k': {'supported': None, 'confidence': 0, 'methods': []},
                '802.11v': {'supported': None, 'confidence': 0, 'methods': []},
                'neighbor_report': {'supported': None, 'confidence': 0, 'methods': []},
                'bss_transition': {'supported': None, 'confidence': 0, 'methods': []},
                'beacon_report': {'supported': None, 'confidence': 0, 'methods': []},
            }
        
        # Update capability with confidence scoring
        self._update_with_confidence(client_mac, capability_type, supported, detection_method)
```

### Phase 3: Confidence Scoring

```python
def calculate_capability_confidence(detection_methods: List[str]) -> float:
    """
    Calculate confidence score based on detection methods:
    - explicit: 0.95 confidence
    - behavioral_success: 0.85 confidence  
    - behavioral_failure: 0.75 confidence (for negative detection)
    - multiple_confirmations: +0.05 per additional confirmation
    """
    base_scores = {
        'explicit': 0.95,
        'behavioral_success': 0.85,
        'behavioral_failure': 0.75
    }
    
    if not detection_methods:
        return 0.0
    
    max_score = max(base_scores.get(method, 0.5) for method in detection_methods)
    bonus = min(0.05 * (len(detection_methods) - 1), 0.05 * 3)  # Max 3 bonuses
    
    return min(max_score + bonus, 1.0)
```

### Phase 4: Steering Strategy Selection

```python
def select_steering_strategy(client_mac: str, capabilities: dict) -> str:
    """
    Select optimal steering strategy based on client capabilities:
    
    High 802.11k/v Support:
    - Use neighbor reports for AP discovery
    - Use BSS transition management for seamless handoffs
    - Enable fast BSS transition if 802.11r also supported
    
    Limited/No 802.11k/v Support:
    - Fall back to legacy steering methods
    - Use RSSI-based steering decisions
    - Implement forced disconnection if necessary
    """
    
    k_support = capabilities.get('802.11k', {}).get('supported', False)
    v_support = capabilities.get('802.11v', {}).get('supported', False)
    k_confidence = capabilities.get('802.11k', {}).get('confidence', 0)
    v_confidence = capabilities.get('802.11v', {}).get('confidence', 0)
    
    if k_support and v_support and k_confidence > 0.8 and v_confidence > 0.8:
        return "advanced_kv_steering"
    elif k_support and k_confidence > 0.7:
        return "neighbor_report_steering" 
    elif v_support and v_confidence > 0.7:
        return "bss_transition_steering"
    else:
        return "legacy_steering"
```

## Recommended Log Enhancements

### Suggested Log Format Improvements

**Current**: `wnc-steer: client aa:bb:cc:dd:ee:ff steering failed`

**Enhanced**: `wnc-steer: client aa:bb:cc:dd:ee:ff steering failed reason=no_btm_support capabilities=[rrm=false,btm=false]`

### Additional Logging Recommendations

1. **Capability Discovery Logs**:
   ```
   wnc-steer: discovered client capabilities mac=aa:bb:cc:dd:ee:ff rrm_enabled=1 btm_enabled=1 fast_bss_transition=0
   ```

2. **Strategy Selection Logs**:
   ```
   wnc-steer: selected steering strategy=advanced_kv_steering client=aa:bb:cc:dd:ee:ff confidence=0.95
   ```

3. **Capability Test Logs**:
   ```
   wnc-steer: testing 802.11k capability client=aa:bb:cc:dd:ee:ff sending neighbor_report_request
   wnc-steer: 802.11k test result client=aa:bb:cc:dd:ee:ff neighbor_report_response=success
   ```

## Integration with Existing System

### Pattern Integration

Add new patterns to the existing `patterns.json`:

```json
{
  "name": "steering_capability_explicit",
  "pattern": "(?:parsed\\s+)?clientCapability.*mac=(?P<mac>[0-9a-f:]+)(?:.*rrm[_=](?P<rrm_enabled>\\w+))?(?:.*btm[_=](?P<btm_enabled>\\w+))?",
  "category": "event_specific", 
  "priority": "HIGH",
  "description": "Explicit client 802.11k/v capability detection",
  "agent_types": ["wnc-steering"]
}
```

### Enhanced Client Statistics

Extend the existing client statistics structure:

```python
client_stats = {
    'weak_signals': 0,
    'steering_attempts': 0,
    'steering_successes': 0,
    'steering_failures': 0,
    'supports_11k': False,
    'supports_11v': False,
    # New enhanced capability tracking
    'capability_confidence': {
        '802.11k': 0.0,
        '802.11v': 0.0
    },
    'capability_detection_methods': {
        '802.11k': [],
        '802.11v': []
    },
    'recommended_steering_strategy': 'legacy_steering',
    'last_capability_test': None,
    'neighbor_report_successes': 0,
    'neighbor_report_failures': 0,
    'bss_transition_successes': 0,
    'bss_transition_failures': 0
}
```

## Testing and Validation

### Test Scenarios

1. **Client with Full 802.11k/v Support**:
   - Verify detection of both capabilities
   - Confirm advanced steering strategy selection
   - Test successful neighbor reports and BSS transitions

2. **Client with Partial Support**:
   - 802.11k only: Should detect neighbor report capability
   - 802.11v only: Should detect BSS transition capability
   - Verify appropriate strategy selection

3. **Legacy Client (No 802.11k/v)**:
   - Verify fallback to legacy steering methods
   - Confirm negative detection through failed attempts
   - Test RSSI-based steering approach

### Validation Metrics

- **Detection Accuracy**: % of correctly identified client capabilities
- **Strategy Effectiveness**: Success rate by steering strategy type
- **Performance Impact**: Time to detect capabilities vs. steering decision speed

## Conclusion

By implementing enhanced 802.11k/v capability detection, the WNC steering system can:

1. **Optimize Steering Performance**: Use advanced features when available
2. **Improve Client Experience**: Seamless transitions for capable clients
3. **Maintain Compatibility**: Graceful fallback for legacy clients
4. **Provide Better Analytics**: Detailed capability reporting and insights

The proposed solution builds on the existing pattern recognition framework while adding sophisticated capability detection and strategic steering selection based on client capabilities.
