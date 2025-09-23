// prplOS LCM Log Analysis System - Type Definitions

export interface PackageMetadata {
  total_containers: number;
  total_log_files: number;
  total_log_size_bytes: number;
  time_range_start?: string;
  time_range_end?: string;
  applications_detected: string[];
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at?: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed' | 'ready' | 'error';
  uploadTimestamp?: string; // For backward compatibility
  upload_timestamp?: string; // Backend field
  fileSize?: number; // For backward compatibility
  file_size?: number; // Redux store field
  file_size_bytes?: number; // Backend field
  applicationCount?: number; // For backward compatibility
  lastAnalysisTimestamp?: string; // For backward compatibility
  original_filename?: string;
  extraction_path?: string;
  analysis_count?: number;
  last_analysis_timestamp?: string;
  package_metadata?: PackageMetadata;
  applications_detected?: string[];
  total_log_entries?: number;
}

export interface Application {
  name: string;                    // matches application_name
  functionalDomain: string;        // matches functional_domain
  containerId: string;             // matches container_id
  healthScore: number;             // matches health_score
  logVolume: number;               // matches log_volume
  errorRate: number;               // matches error_rate
  anomalyCount: number;            // derived from anomalies.length
  lastUpdated: string;             // matches analysis_timestamp
  timeSequenceData?: TimeSequencePreview; // new field from backend
}

export interface TimeSequencePreview {
  recentEvents: Array<{
    timestamp: string;
    eventType: string;
    severity: 'info' | 'warning' | 'error' | 'critical';
    message: string;
  }>;
  eventCount: number;
  timeRange: { start: string; end: string };
}

export interface LogEvent {
  id: string;
  timestamp: string;
  eventType: string;
  category: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  metadata: Record<string, any>;
  source: string;
}

export interface ApplicationFilter {
  id: string;
  name: string;
  category: string;
  description: string;
  count: number;
  color: string;
  patterns: string[];
}

export interface ApplicationAnalysisResult {
  application_name: string;
  container_id: string;
  functional_domain: string;
  log_volume: number;
  error_rate: number;
  health_score: number;
  time_series_data: TimeSeriesData[];
  anomalies: AnomalyResult[];
  time_sequence_preview?: TimeSequencePreview;
  // ... other fields from backend
}

export interface TimeSeriesData {
  metric_name: string;
  application: string;
  data_points: TimeSeriesDataPoint[];
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
}

export interface AnomalyResult {
  timestamp: string;
  metric_name: string;
  application: string;
  anomaly_type: string;
  score: number;
  severity: string;
  description: string;
  confidence: number;
}

export interface AnalysisResult {
  analysis_id: string;
  project_id: string;
  completed_at: string;
  summary: {
    total_applications: number;
    total_log_entries: number;
    time_range: string;
    applications: string[];
  };
  time_series_data: any[];
  anomalies: any[];
  predictions: any[];
  statistical_results: any[];
  recommendations: string[];
  // Add the missing properties that are being used in the code
  application_analyses: Record<string, ApplicationAnalysisResult>;
  cross_application_correlations: CorrelationResult[];
  timestamp?: string; // For backward compatibility
}

export interface CorrelationResult {
  metric1: string;
  metric2: string;
  correlation_type: string;
  strength: number;
  confidence: number;
  description: string;
}
