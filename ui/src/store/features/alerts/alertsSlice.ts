import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { api } from '../../../services/api'

export interface Alert {
  id: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  message: string
  timestamp: string
  source: string
  metric_name?: string
  value?: number
  threshold?: number
  acknowledged: boolean
  acknowledged_by?: string
  acknowledged_at?: string
}

interface AlertsState {
  alerts: Alert[]
  unacknowledgedCount: number
  loading: boolean
  error: string | null
}

const initialState: AlertsState = {
  alerts: [],
  unacknowledgedCount: 0,
  loading: false,
  error: null,
}

// Async thunks
export const fetchAlerts = createAsyncThunk(
  'alerts/fetchAlerts',
  async ({ analysisId: _analysisId, severity, acknowledged }: { analysisId: string; severity?: string; acknowledged?: boolean }) => {
    const params: any = {}
    if (severity) params.severity = severity
    if (acknowledged !== undefined) params.acknowledged = acknowledged
    
    const response = await api.get(`/api/v1/visualization/monitoring/alerts`, { params })
    return response.data
  }
)

export const acknowledgeAlert = createAsyncThunk(
  'alerts/acknowledgeAlert',
  async ({ alertId, user }: { alertId: string; user: string }) => {
    const response = await api.post(`/api/v1/visualization/monitoring/alerts/${alertId}/acknowledge`, { user })
    return response.data
  }
)

export const getAlertSummary = createAsyncThunk(
  'alerts/getAlertSummary',
  async (analysisId: string) => {
    const response = await api.get(`/api/v1/visualization/monitoring/alerts/summary`, { params: { analysis_id: analysisId } })
    return response.data
  }
)

const alertsSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    addAlert: (state, action: PayloadAction<Alert>) => {
      state.alerts.unshift(action.payload)
      if (!action.payload.acknowledged) {
        state.unacknowledgedCount += 1
      }
    },
    updateAlert: (state, action: PayloadAction<Alert>) => {
      const index = state.alerts.findIndex(a => a.id === action.payload.id)
      if (index !== -1) {
        const wasAcknowledged = state.alerts[index].acknowledged
        const isNowAcknowledged = action.payload.acknowledged
        
        state.alerts[index] = action.payload
        
        if (!wasAcknowledged && isNowAcknowledged) {
          state.unacknowledgedCount -= 1
        } else if (wasAcknowledged && !isNowAcknowledged) {
          state.unacknowledgedCount += 1
        }
      }
    },
    clearAlerts: (state) => {
      state.alerts = []
      state.unacknowledgedCount = 0
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch alerts
      .addCase(fetchAlerts.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.loading = false
        state.alerts = action.payload
        state.unacknowledgedCount = action.payload.filter((alert: Alert) => !alert.acknowledged).length
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch alerts'
      })
      // Acknowledge alert
      .addCase(acknowledgeAlert.fulfilled, (state, action) => {
        const alert = state.alerts.find(a => a.id === action.payload.alert_id)
        if (alert && !alert.acknowledged) {
          alert.acknowledged = true
          alert.acknowledged_by = action.payload.acknowledged_by
          alert.acknowledged_at = action.payload.acknowledged_at
          state.unacknowledgedCount -= 1
        }
      })
      // Get alert summary
      .addCase(getAlertSummary.fulfilled, (_state, _action) => {
        // Handle alert summary if needed
      })
  },
})

export const { addAlert, updateAlert, clearAlerts, clearError } = alertsSlice.actions
export default alertsSlice.reducer
