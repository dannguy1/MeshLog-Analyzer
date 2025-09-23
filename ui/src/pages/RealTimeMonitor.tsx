import React, { useEffect, useState, useRef } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  Slider,
  Divider,
  LinearProgress,
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store'
import { startMonitoring, stopMonitoring } from '../store/features/visualization/visualizationSlice'
import { fetchAlerts, acknowledgeAlert } from '../store/features/alerts/alertsSlice'
import { formatDistanceToNow } from 'date-fns'

interface RealTimeMonitorProps {
  projectId: string
}

const RealTimeMonitor: React.FC<RealTimeMonitorProps> = ({ projectId: _projectId }) => {
  const dispatch = useDispatch<AppDispatch>()
  
  const { analyses } = useSelector((state: RootState) => state.analysis)
  const { loading: vizLoading } = useSelector((state: RootState) => state.visualization)
  const { alerts, unacknowledgedCount, loading: alertsLoading } = useSelector((state: RootState) => state.alerts)
  
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [updateInterval, setUpdateInterval] = useState(5)
  const [enableNotifications, setEnableNotifications] = useState(true)
  const [alertThresholds, setAlertThresholds] = useState({
    error_rate: 0.1,
    response_time: 1000,
    memory_usage: 80,
  })
  
  const websocketRef = useRef<WebSocket | null>(null)
  
  // Get the latest analysis for this project
  const latestAnalysis = analyses.length > 0 ? analyses[0] : null

  useEffect(() => {
    if (latestAnalysis?.id) {
      // Fetch initial alerts
      dispatch(fetchAlerts({ analysisId: latestAnalysis.id }))
    }
  }, [latestAnalysis?.id, dispatch])

  useEffect(() => {
    return () => {
      // Cleanup WebSocket connection
      if (websocketRef.current) {
        websocketRef.current.close()
      }
    }
  }, [])

  const handleStartMonitoring = async () => {
    if (!latestAnalysis?.id) return

    try {
      await dispatch(startMonitoring({
        analysisId: latestAnalysis.id,
        config: {
          alert_thresholds: alertThresholds,
          update_interval: updateInterval,
          enable_notifications: enableNotifications,
        },
      })).unwrap()

      setIsMonitoring(true)
      
      // Connect to WebSocket for real-time updates
      const wsUrl = `ws://0.0.0.0:8000/api/v1/visualization/ws/${latestAnalysis.id}`
      websocketRef.current = new WebSocket(wsUrl)
      
      websocketRef.current.onopen = () => {
        console.log('WebSocket connected')
      }
      
      websocketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data)
        console.log('WebSocket message:', data)
        
        // Handle different message types
        if (data.type === 'alert') {
          // Handle new alert
          console.log('New alert received:', data.alert)
        } else if (data.type === 'chart_update') {
          // Handle chart update
          console.log('Chart update received:', data.chart)
        }
      }
      
      websocketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
      websocketRef.current.onclose = () => {
        console.log('WebSocket disconnected')
      }
    } catch (error) {
      console.error('Failed to start monitoring:', error)
    }
  }

  const handleStopMonitoring = async () => {
    if (!latestAnalysis?.id) return

    try {
      await dispatch(stopMonitoring(latestAnalysis.id)).unwrap()
      setIsMonitoring(false)
      
      // Close WebSocket connection
      if (websocketRef.current) {
        websocketRef.current.close()
        websocketRef.current = null
      }
    } catch (error) {
      console.error('Failed to stop monitoring:', error)
    }
  }

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await dispatch(acknowledgeAlert({ alertId, user: 'current_user' })).unwrap()
    } catch (error) {
      console.error('Failed to acknowledge alert:', error)
    }
  }

  const getAlertSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error'
      case 'error': return 'error'
      case 'warning': return 'warning'
      case 'info': return 'info'
      default: return 'default'
    }
  }

  const getAlertSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <ErrorIcon />
      case 'error': return <ErrorIcon />
      case 'warning': return <WarningIcon />
      case 'info': return <InfoIcon />
      default: return <InfoIcon />
    }
  }

  if (!latestAnalysis) {
    return (
      <Alert severity="error">
        No analysis found for this project. Please start an analysis first.
      </Alert>
    )
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Real-time Monitor
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor analysis for this project
        </Typography>
      </Box>

      {/* Monitoring Controls */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingUpIcon color={isMonitoring ? 'success' : 'disabled'} />
                <Box>
                  <Typography variant="h6">
                    Monitoring Status
                  </Typography>
                  <Chip
                    label={isMonitoring ? 'Active' : 'Inactive'}
                    color={isMonitoring ? 'success' : 'default'}
                    icon={isMonitoring ? <PlayIcon /> : <StopIcon />}
                  />
                </Box>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={() => dispatch(fetchAlerts({ analysisId: latestAnalysis.id }))}
                  disabled={alertsLoading}
                >
                  Refresh Alerts
                </Button>
                {!isMonitoring ? (
                  <Button
                    variant="contained"
                    startIcon={<PlayIcon />}
                    onClick={handleStartMonitoring}
                    disabled={vizLoading}
                  >
                    Start Monitoring
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    color="error"
                    startIcon={<StopIcon />}
                    onClick={handleStopMonitoring}
                    disabled={vizLoading}
                  >
                    Stop Monitoring
                  </Button>
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Monitoring Configuration */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Configuration
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Update Interval: {updateInterval} seconds
                </Typography>
                <Slider
                  value={updateInterval}
                  onChange={(_, value) => setUpdateInterval(value as number)}
                  min={1}
                  max={30}
                  marks
                  valueLabelDisplay="auto"
                  disabled={isMonitoring}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={enableNotifications}
                      onChange={(e) => setEnableNotifications(e.target.checked)}
                      disabled={isMonitoring}
                    />
                  }
                  label="Enable Notifications"
                />
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>
                Alert Thresholds
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Error Rate: {alertThresholds.error_rate * 100}%
                </Typography>
                <Slider
                  value={alertThresholds.error_rate}
                  onChange={(_, value) => setAlertThresholds(prev => ({ ...prev, error_rate: value as number }))}
                  min={0}
                  max={1}
                  step={0.01}
                  disabled={isMonitoring}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Response Time: {alertThresholds.response_time}ms
                </Typography>
                <Slider
                  value={alertThresholds.response_time}
                  onChange={(_, value) => setAlertThresholds(prev => ({ ...prev, response_time: value as number }))}
                  min={100}
                  max={5000}
                  step={100}
                  disabled={isMonitoring}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Memory Usage: {alertThresholds.memory_usage}%
                </Typography>
                <Slider
                  value={alertThresholds.memory_usage}
                  onChange={(_, value) => setAlertThresholds(prev => ({ ...prev, memory_usage: value as number }))}
                  min={50}
                  max={100}
                  step={5}
                  disabled={isMonitoring}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Live Charts */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Live Charts
              </Typography>
              
              {isMonitoring ? (
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, height: 200 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Error Rate
                      </Typography>
                      <Box sx={{ height: 150, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Typography color="text.secondary">
                          Real-time chart would be rendered here
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, height: 200 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Response Time
                      </Typography>
                      <Box sx={{ height: 150, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Typography color="text.secondary">
                          Real-time chart would be rendered here
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, height: 200 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Memory Usage
                      </Typography>
                      <Box sx={{ height: 150, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Typography color="text.secondary">
                          Real-time chart would be rendered here
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, height: 200 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        System Health
                      </Typography>
                      <Box sx={{ height: 150, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Typography color="text.secondary">
                          Real-time chart would be rendered here
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                </Grid>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <NotificationsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography color="text.secondary">
                    Start monitoring to see live charts and metrics
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              <NotificationsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Alerts ({unacknowledgedCount} unacknowledged)
            </Typography>
            <Chip
              label={alerts.length}
              color="primary"
              size="small"
            />
          </Box>

          {alertsLoading ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary">Loading alerts...</Typography>
            </Box>
          ) : alerts.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary">No alerts found</Typography>
            </Box>
          ) : (
            <List>
              {alerts.map((alert) => (
                <ListItem
                  key={alert.id}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    backgroundColor: alert.acknowledged ? 'action.hover' : 'background.paper',
                  }}
                >
                  <ListItemIcon>
                    {getAlertSeverityIcon(alert.severity)}
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.message}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          {formatDistanceToNow(new Date(alert.timestamp))} ago • {alert.source}
                        </Typography>
                        {alert.metric_name && (
                          <Typography variant="caption" display="block">
                            {alert.metric_name}: {alert.value} (threshold: {alert.threshold})
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={alert.severity}
                      color={getAlertSeverityColor(alert.severity) as any}
                      size="small"
                    />
                    {!alert.acknowledged && (
                      <Button
                        size="small"
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                      >
                        Acknowledge
                      </Button>
                    )}
                  </Box>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Loading State */}
      {vizLoading && (
        <Box sx={{ width: '100%', mt: 2 }}>
          <LinearProgress />
        </Box>
      )}
    </Box>
  )
}

export default RealTimeMonitor
