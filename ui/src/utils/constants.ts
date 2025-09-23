// prplOS LCM Log Analysis System - Constants

// WiFi EasyMesh Application-Specific Filters

export const wncSteerFilters = [
  {
    id: 'client_management',
    name: 'Client Management',
    category: 'client_management',
    description: 'Client connection and management events',
    patterns: ['client', 'connection', 'management'],
    count: 0, // Will be calculated dynamically
    color: '#2196f3'
  },
  {
    id: 'general_info',
    name: 'General Information',
    category: 'general_info',
    description: 'General system information and status',
    patterns: ['info', 'status', 'general'],
    count: 0, // Will be calculated dynamically
    color: '#4caf50'
  },
  {
    id: 'network_operation',
    name: 'Network Operations',
    category: 'network_operation',
    description: 'Network connectivity and operation events',
    patterns: ['network', 'operation', 'connectivity'],
    count: 0, // Will be calculated dynamically
    color: '#ff9800'
  },
  {
    id: 'configuration',
    name: 'Configuration',
    category: 'configuration',
    description: 'System configuration and settings',
    patterns: ['config', 'setting', 'parameter'],
    count: 0, // Will be calculated dynamically
    color: '#9c27b0'
  },
  {
    id: 'steering_decision',
    name: 'Steering Decisions',
    category: 'steering_decision',
    description: 'Client steering decision events',
    patterns: ['steering', 'decision', 'choice'],
    count: 0, // Will be calculated dynamically
    color: '#f44336'
  },
  {
    id: 'steering_action',
    name: 'Steering Actions',
    category: 'steering_action',
    description: 'Executed steering actions',
    patterns: ['action', 'execute', 'trigger'],
    count: 0, // Will be calculated dynamically
    color: '#e91e63'
  },
  {
    id: 'steering_evaluation',
    name: 'Steering Evaluation',
    category: 'steering_evaluation',
    description: 'Steering effectiveness evaluation',
    patterns: ['evaluation', 'assessment', 'analysis'],
    count: 0, // Will be calculated dynamically
    color: '#795548'
  }
];

export const wncAcsFilters = [
  {
    id: 'channel-scans',
    name: 'Channel Scans',
    category: 'scanning',
    description: 'Channel scanning operations',
    patterns: ['scan.*channel', 'channel.*scan', 'interference.*scan'],
    count: 0,
    color: '#2196f3'
  },
  {
    id: 'interference-detection',
    name: 'Interference Detection',
    category: 'detection',
    description: 'Interference detection events',
    patterns: ['interference.*detected', 'noise.*level', 'channel.*busy'],
    count: 0,
    color: '#ff9800'
  },
  {
    id: 'channel-switches',
    name: 'Channel Switches',
    category: 'optimization',
    description: 'Channel switching decisions',
    patterns: ['channel.*switch', 'switch.*channel', 'new.*channel'],
    count: 0,
    color: '#4caf50'
  },
  {
    id: 'spectrum-analysis',
    name: 'Spectrum Analysis',
    category: 'analysis',
    description: 'Spectrum analysis results',
    patterns: ['spectrum.*analysis', 'frequency.*analysis', 'bandwidth.*check'],
    count: 0,
    color: '#9c27b0'
  },
  {
    id: 'regulatory-compliance',
    name: 'Regulatory Compliance',
    category: 'compliance',
    description: 'Regulatory compliance checks',
    patterns: ['regulatory.*check', 'compliance.*verify', 'legal.*channel'],
    count: 0,
    color: '#f44336'
  }
];

export const wncTpyoptFilters = [
  {
    id: 'topology-discovery',
    name: 'Topology Discovery',
    category: 'discovery',
    description: 'Network topology discovery',
    patterns: ['topology.*discovery', 'neighbor.*discovery', 'mesh.*scan'],
    count: 0,
    color: '#2196f3'
  },
  {
    id: 'path-optimization',
    name: 'Path Optimization',
    category: 'optimization',
    description: 'Path optimization decisions',
    patterns: ['path.*optimize', 'route.*optimize', 'best.*path'],
    count: 0,
    color: '#4caf50'
  },
  {
    id: 'link-quality-assessment',
    name: 'Link Quality Assessment',
    category: 'assessment',
    description: 'Link quality evaluation',
    patterns: ['link.*quality', 'quality.*assessment', 'link.*score'],
    count: 0,
    color: '#ff9800'
  },
  {
    id: 'redundancy-management',
    name: 'Redundancy Management',
    category: 'management',
    description: 'Redundancy path management',
    patterns: ['redundancy.*path', 'backup.*path', 'failover.*path'],
    count: 0,
    color: '#9c27b0'
  },
  {
    id: 'congestion-detection',
    name: 'Congestion Detection',
    category: 'detection',
    description: 'Network congestion detection',
    patterns: ['congestion.*detected', 'traffic.*congestion', 'bottleneck'],
    count: 0,
    color: '#f44336'
  }
];

export const otbrAgentFilters = [
  {
    id: 'thread-network-join',
    name: 'Thread Network Join',
    category: 'networking',
    description: 'Thread network join events',
    patterns: ['thread.*join', 'network.*join', 'commissioning'],
    count: 0,
    color: '#2196f3'
  },
  {
    id: 'border-routing',
    name: 'Border Routing',
    category: 'routing',
    description: 'Border routing operations',
    patterns: ['border.*route', 'route.*border', 'gateway.*route'],
    count: 0,
    color: '#4caf50'
  },
  {
    id: 'commissioning-events',
    name: 'Commissioning Events',
    category: 'commissioning',
    description: 'Device commissioning events',
    patterns: ['commissioning.*event', 'device.*commission', 'join.*network'],
    count: 0,
    color: '#ff9800'
  },
  {
    id: 'security-events',
    name: 'Security Events',
    category: 'security',
    description: 'Security-related events',
    patterns: ['security.*event', 'authentication', 'authorization'],
    count: 0,
    color: '#f44336'
  },
  {
    id: 'mesh-formation',
    name: 'Mesh Formation',
    category: 'mesh',
    description: 'Mesh network formation',
    patterns: ['mesh.*formation', 'network.*formation', 'topology.*build'],
    count: 0,
    color: '#9c27b0'
  }
];

export const APPLICATIONS = {
  'wnc-steer': {
    name: 'WiFi Network Controller - Client Steering',
    domain: 'client_steering',
    filters: wncSteerFilters
  },
  'wnc-acs': {
    name: 'WiFi Network Controller - Auto Channel Selection',
    domain: 'channel_selection',
    filters: wncAcsFilters
  },
  'wnc-tpyopt': {
    name: 'WiFi Network Controller - Topology Optimizer',
    domain: 'topology_optimization',
    filters: wncTpyoptFilters
  },
  'otbr-agent': {
    name: 'OpenThread Border Router Agent',
    domain: 'iot_networking',
    filters: otbrAgentFilters
  }
};

export const HEALTH_COLORS = {
  healthy: '#4caf50',
  degraded: '#ff9800',
  critical: '#f44336'
};

export const SEVERITY_COLORS = {
  info: '#2196f3',
  warning: '#ff9800',
  error: '#f44336',
  critical: '#d32f2f'
};
