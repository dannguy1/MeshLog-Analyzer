import axios from 'axios'

// Get API base URL from environment variable or default based on environment
// In containerized deployment, use empty string so API calls go through nginx proxy
// In development, detect hostname dynamically for cross-machine access
const isDevelopment = import.meta.env.DEV
const getApiBaseUrl = () => {
  // If explicitly set, use that
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  
  // In production, use empty string for relative URLs (nginx proxy)
  if (!isDevelopment) {
    return ''
  }
  
  // In development, use the same hostname as the frontend (allows cross-machine access)
  // This ensures when accessing frontend via IP (e.g., 192.168.10.5:3000),
  // API calls go to the same IP (192.168.10.5:8000) instead of localhost
  const hostname = window.location.hostname
  const port = '8000'
  
  // Use localhost only if frontend is also on localhost
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `http://localhost:${port}`
  }
  
  // Otherwise use the same hostname as the frontend
  return `http://${hostname}:${port}`
}

const API_BASE_URL = getApiBaseUrl()

// Create axios instance with default configuration
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10 minutes for large uploads
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens, etc.
api.interceptors.request.use(
  (config) => {
    // Add any request modifications here
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling common errors
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access')
    } else if (error.response?.status === 500) {
      // Handle server errors
      console.error('Server error:', error.response.data)
    } else if (error.code === 'ECONNABORTED') {
      // Handle timeout
      console.error('Request timeout - the server took too long to respond')
    } else if (error.message === 'Network Error') {
      // Handle network errors
      console.error('Network error - unable to connect to the server')
    }
    
    console.error('API Error Details:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data
    })
    
    return Promise.reject(error)
  }
)

// API endpoints
export const endpoints = {
  // Projects
  projects: '/api/v1/projects',
  project: (id: string) => `/api/v1/projects/${id}`,
  projectResults: (id: string) => `/api/v1/projects/${id}/results`,
  
  // Project Analyses (new project-centric structure)
  projectAnalyses: (projectId: string) => `/api/v1/projects/${projectId}/analyses`,
  projectAnalysis: (projectId: string, analysisId: string) => `/api/v1/projects/${projectId}/analyses/${analysisId}`,
  startAnalysis: (projectId: string) => `/api/v1/projects/${projectId}/analyze`,
  
  // New application-specific endpoints
  analysisResults: (projectId: string, analysisId: string) => 
    `/api/v1/projects/${projectId}/analyses/${analysisId}/results`,
  applicationAnalysis: (projectId: string, analysisId: string, appName: string) => 
    `/api/v1/projects/${projectId}/analyses/${analysisId}/applications/${appName}`,
  timeSequenceData: (projectId: string, analysisId: string, appName: string) => 
    `/api/v1/projects/${projectId}/analyses/${analysisId}/timesequence/${appName}`,
  realtimeEvents: (projectId: string, analysisId: string) => 
    `ws://${API_BASE_URL.replace('http://', '')}/api/v1/projects/${projectId}/analyses/${analysisId}/events`,
  
  // Application-specific analysis management endpoints
  applicationAnalysisStatus: (projectId: string, appName: string) => 
    `/api/v1/projects/${projectId}/applications/${appName}/analysis-status`,
  applicationAnalysisResult: (projectId: string, appName: string, analysisId: string) => 
    `/api/v1/projects/${projectId}/applications/${appName}/analysis/${analysisId}`,
  
  // Application Data Manager endpoints (SQLite-based)
  applicationLogs: (projectId: string, appName: string) => 
    `/api/v1/projects/${projectId}/applications/${appName}/data/logs`,
  applicationStatistics: (projectId: string, appName: string) => 
    `/api/v1/projects/${projectId}/applications/${appName}/data/statistics`,
  applicationDataSummary: (projectId: string, appName: string) => 
    `/api/v1/projects/${projectId}/applications/${appName}/data/summary`,
  applicationDataExport: (projectId: string, appName: string) => 
    `/api/v1/projects/${projectId}/applications/${appName}/data/export/csv`,
  applicationDataCleanup: (projectId: string, appName: string) => 
    `/api/v1/projects/${projectId}/applications/${appName}/data/cleanup`,
  applicationDatabaseInfo: (projectId: string, appName: string) => 
    `/api/v1/projects/${projectId}/applications/${appName}/data/database/info`,
  
  // Agent Analysis endpoints
  agentAnalysis: {
    agents: (projectId: string, appName: string) => 
      `/api/v1/projects/${projectId}/applications/${appName}/agent-analysis/agents`,
    availableApplications: (projectId: string, appName: string) => 
      `/api/v1/projects/${projectId}/applications/${appName}/agent-analysis/available-applications`,
    start: (projectId: string, appName: string) => 
      `/api/v1/projects/${projectId}/applications/${appName}/agent-analysis/start`,
    status: (projectId: string, appName: string, analysisId: string) => 
      `/api/v1/projects/${projectId}/applications/${appName}/agent-analysis/status/${analysisId}`,
    results: (projectId: string, appName: string) => 
      `/api/v1/projects/${projectId}/applications/${appName}/agent-analysis/results`,
  },
  
  // Legacy Analyses (deprecated - for backward compatibility)
  analyses: '/api/v1/analyses',
  analysisStatus: (id: string) => `/api/v1/analyses/${id}`,
  
  // Visualization
  visualizationHealth: '/api/v1/visualization/health',
  generateChart: '/api/v1/visualization/charts/generate',
  generateDashboard: '/api/v1/visualization/dashboard/generate',
  startMonitoring: '/api/v1/visualization/monitoring/start',
  stopMonitoring: '/api/v1/visualization/monitoring/stop',
  alerts: '/api/v1/visualization/monitoring/alerts',
  alertSummary: '/api/v1/visualization/monitoring/alerts/summary',
  acknowledgeAlert: (alertId: string) => `/api/v1/visualization/monitoring/alerts/${alertId}/acknowledge`,
  websocket: (analysisId: string) => `ws://${API_BASE_URL.replace('http://', '')}/api/v1/visualization/ws/${analysisId}`,
}

// API service methods
export const apiService = {
  // Project methods
  async getProjects(): Promise<any[]> {
    const response = await api.get(endpoints.projects)
    return response.data
  },

  async getProject(id: string): Promise<any> {
    const response = await api.get(endpoints.project(id))
    return response.data
  },

  async getProjectResults(id: string): Promise<any> {
    const response = await api.get(endpoints.projectResults(id))
    return response.data
  },

  // Project restoration methods
  async getAvailablePackages(): Promise<any> {
    const response = await api.get('/api/v1/projects/restore/available')
    return response.data
  },

  async restoreProject(filename: string, name: string, description?: string): Promise<any> {
    const formData = new FormData()
    formData.append('filename', filename)
    formData.append('name', name)
    if (description) {
      formData.append('description', description)
    }
    
    const response = await api.post('/api/v1/projects/restore', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Analysis methods
  async getProjectAnalyses(projectId: string): Promise<any> {
    const response = await api.get(endpoints.projectAnalyses(projectId))
    return response.data
  },

  async getProjectAnalysis(projectId: string, analysisId: string): Promise<any> {
    const response = await api.get(endpoints.projectAnalysis(projectId, analysisId))
    return response.data
  },

  async startAnalysis(projectId: string, config?: any): Promise<any> {
    const response = await api.post(endpoints.startAnalysis(projectId), config)
    return response.data
  },

  // New application-specific methods
  async getAnalysisResults(projectId: string, analysisId: string): Promise<any> {
    const response = await api.get(endpoints.analysisResults(projectId, analysisId))
    return response.data
  },

  async getApplicationAnalysis(projectId: string, analysisId: string, appName: string): Promise<any> {
    const response = await api.get(endpoints.applicationAnalysis(projectId, analysisId, appName))
    return response.data
  },

  async getTimeSequenceData(projectId: string, analysisId: string, appName: string): Promise<any> {
    const response = await api.get(endpoints.timeSequenceData(projectId, analysisId, appName))
    return response.data
  },

  // Application-specific analysis management methods
  async getApplicationAnalysisStatus(projectId: string, appName: string): Promise<any> {
    const response = await api.get(endpoints.applicationAnalysisStatus(projectId, appName))
    return response.data
  },

  async getApplicationAnalysisResult(projectId: string, appName: string, analysisId: string): Promise<any> {
    const response = await api.get(endpoints.applicationAnalysisResult(projectId, appName, analysisId))
    return response.data
  },

  // Application Data Manager methods (SQLite-based)
  async getApplicationLogs(
    projectId: string, 
    appName: string, 
    params?: {
      query?: string;
      log_level?: string;
      start_time?: string;
      end_time?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<any> {
    const response = await api.get(endpoints.applicationLogs(projectId, appName), { params })
    return response.data
  },

  async getApplicationStatistics(projectId: string, appName: string): Promise<any> {
    const response = await api.get(endpoints.applicationStatistics(projectId, appName))
    return response.data
  },

  async getApplicationDataSummary(projectId: string, appName: string): Promise<any> {
    const response = await api.get(endpoints.applicationDataSummary(projectId, appName))
    return response.data
  },

  async exportApplicationData(
    projectId: string, 
    appName: string, 
    params?: {
      query?: string;
      log_level?: string;
      start_time?: string;
      end_time?: string;
    }
  ): Promise<Blob> {
    const response = await api.get(endpoints.applicationDataExport(projectId, appName), { 
      params,
      responseType: 'blob'
    })
    return response.data
  },

  async cleanupApplicationData(projectId: string, appName: string, retentionDays: number = 30): Promise<any> {
    const response = await api.post(endpoints.applicationDataCleanup(projectId, appName), null, {
      params: { retention_days: retentionDays }
    })
    return response.data
  },

  async getApplicationDatabaseInfo(projectId: string, appName: string): Promise<any> {
    const response = await api.get(endpoints.applicationDatabaseInfo(projectId, appName))
    return response.data
  },

  // Legacy methods (for backward compatibility)
  async getAnalyses(projectId?: string): Promise<any> {
    const params = projectId ? { project_id: projectId } : {}
    const response = await api.get(endpoints.analyses, { params })
    return response.data
  },

  async getAnalysisStatus(id: string): Promise<any> {
    const response = await api.get(endpoints.analysisStatus(id))
    return response.data
  },

  // Visualization methods
  async getVisualizationHealth(): Promise<any> {
    const response = await api.get(endpoints.visualizationHealth)
    return response.data
  },

  async generateChart(request: any): Promise<any> {
    const response = await api.post(endpoints.generateChart, request)
    return response.data
  },

  async generateDashboard(request: any): Promise<any> {
    const response = await api.post(endpoints.generateDashboard, request)
    return response.data
  },

  async startMonitoring(analysisId: string, config?: any): Promise<any> {
    const response = await api.post(endpoints.startMonitoring, { analysisId, config })
    return response.data
  },

  async stopMonitoring(analysisId: string): Promise<any> {
    const response = await api.post(endpoints.stopMonitoring, { analysisId })
    return response.data
  },

  async getAlerts(): Promise<any> {
    const response = await api.get(endpoints.alerts)
    return response.data
  },

  async getAlertSummary(): Promise<any> {
    const response = await api.get(endpoints.alertSummary)
    return response.data
  },

  async acknowledgeAlert(alertId: string): Promise<any> {
    const response = await api.post(endpoints.acknowledgeAlert(alertId))
    return response.data
  },

  // Agent Analysis methods
  async getAgentAnalysisAgents(projectId: string, appName: string): Promise<any> {
    const response = await api.get(endpoints.agentAnalysis.agents(projectId, appName))
    return response.data
  },

  async getAgentAnalysisAvailableApplications(projectId: string, appName: string): Promise<any> {
    const response = await api.get(endpoints.agentAnalysis.availableApplications(projectId, appName))
    return response.data
  },

  async startAgentAnalysis(projectId: string, appName: string, agentType: string, config?: any): Promise<any> {
    const response = await api.post(endpoints.agentAnalysis.start(projectId, appName), config, {
      params: { agent_type: agentType }
    })
    return response.data
  },

  async getAgentAnalysisStatus(projectId: string, appName: string, analysisId: string): Promise<any> {
    const response = await api.get(endpoints.agentAnalysis.status(projectId, appName, analysisId))
    return response.data
  },

  async getAgentAnalysisResults(projectId: string, appName: string, format: 'html' | 'json' | 'csv' = 'html', analysisId?: string): Promise<any> {
    const params: any = { format }
    if (analysisId) {
      params.analysis_id = analysisId
    }
    
    const response = await api.get(endpoints.agentAnalysis.results(projectId, appName), {
      params
    })
    return response.data
  }
}

export default api
