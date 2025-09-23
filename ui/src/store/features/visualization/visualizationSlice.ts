import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { api } from '../../../services/api'

export interface Chart {
  type: string
  data: any
  config: any
}

export interface Dashboard {
  charts: Record<string, Chart>
  layout: string
  total_charts: number
  generated_at: string
}

export interface MonitoringConfig {
  alert_thresholds: Record<string, number>
  update_interval: number
  enable_notifications: boolean
}

interface VisualizationState {
  charts: Record<string, Chart>
  dashboard: Dashboard | null
  monitoringConfig: MonitoringConfig | null
  loading: boolean
  error: string | null
}

const initialState: VisualizationState = {
  charts: {},
  dashboard: null,
  monitoringConfig: null,
  loading: false,
  error: null,
}

// Async thunks
export const generateChart = createAsyncThunk(
  'visualization/generateChart',
  async ({ analysisId, chartType, config }: { analysisId: string; chartType: string; config?: any }) => {
    const response = await api.post('/api/v1/visualization/charts/generate', {
      analysis_id: analysisId,
      chart_type: chartType,
      config,
    })
    return response.data
  }
)

export const generateDashboard = createAsyncThunk(
  'visualization/generateDashboard',
  async ({ analysisId, includeCharts, layout }: { analysisId: string; includeCharts?: string[]; layout?: any }) => {
    const response = await api.post('/api/v1/visualization/dashboard/generate', {
      analysis_id: analysisId,
      include_charts: includeCharts || ['time_series', 'anomalies', 'predictions', 'statistics'],
      layout,
    })
    return response.data
  }
)

export const startMonitoring = createAsyncThunk(
  'visualization/startMonitoring',
  async ({ analysisId, config }: { analysisId: string; config?: Partial<MonitoringConfig> }) => {
    const response = await api.post('/api/v1/visualization/monitoring/start', {
      analysis_id: analysisId,
      alert_thresholds: config?.alert_thresholds || {},
      update_interval: config?.update_interval || 5,
      enable_notifications: config?.enable_notifications !== false,
    })
    return response.data
  }
)

export const stopMonitoring = createAsyncThunk(
  'visualization/stopMonitoring',
  async (analysisId: string) => {
    const response = await api.post('/api/v1/visualization/monitoring/stop', { analysis_id: analysisId })
    return response.data
  }
)

const visualizationSlice = createSlice({
  name: 'visualization',
  initialState,
  reducers: {
    setChart: (state, action: PayloadAction<{ chartType: string; chart: Chart }>) => {
      state.charts[action.payload.chartType] = action.payload.chart
    },
    setDashboard: (state, action: PayloadAction<Dashboard>) => {
      state.dashboard = action.payload
    },
    setMonitoringConfig: (state, action: PayloadAction<MonitoringConfig>) => {
      state.monitoringConfig = action.payload
    },
    clearCharts: (state) => {
      state.charts = {}
    },
    clearDashboard: (state) => {
      state.dashboard = null
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Generate chart
      .addCase(generateChart.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(generateChart.fulfilled, (state, action) => {
        state.loading = false
        state.charts[action.payload.chart_type] = action.payload.chart
      })
      .addCase(generateChart.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to generate chart'
      })
      // Generate dashboard
      .addCase(generateDashboard.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(generateDashboard.fulfilled, (state, action) => {
        state.loading = false
        state.dashboard = action.payload.dashboard
      })
      .addCase(generateDashboard.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to generate dashboard'
      })
      // Start monitoring
      .addCase(startMonitoring.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(startMonitoring.fulfilled, (state, action) => {
        state.loading = false
        state.monitoringConfig = action.payload.monitoring
      })
      .addCase(startMonitoring.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to start monitoring'
      })
      // Stop monitoring
      .addCase(stopMonitoring.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(stopMonitoring.fulfilled, (state) => {
        state.loading = false
        state.monitoringConfig = null
      })
      .addCase(stopMonitoring.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to stop monitoring'
      })
  },
})

export const {
  setChart,
  setDashboard,
  setMonitoringConfig,
  clearCharts,
  clearDashboard,
  clearError,
} = visualizationSlice.actions
export default visualizationSlice.reducer
