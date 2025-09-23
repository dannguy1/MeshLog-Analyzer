import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress
} from '@mui/material'
import { MetricsGrid, MetricItem } from '../common/MetricsGrid'
import { Application } from '../../utils/types'

interface ApplicationMetricsProps {
  application: Application
  timeSeriesData?: Array<{
    timestamp: string
    value: number
    metric: string
  }>
}

export const ApplicationMetrics: React.FC<ApplicationMetricsProps> = ({
  application
}) => {
  const healthMetrics: MetricItem[] = [
    {
      id: 'health-score',
      label: 'Health Score',
      value: application.healthScore.toFixed(1),
      unit: '/100',
      color: application.healthScore >= 80 ? 'success' : application.healthScore >= 60 ? 'warning' : 'error',
      progress: application.healthScore
    },
    {
      id: 'log-volume',
      label: 'Log Volume',
      value: application.logVolume.toLocaleString(),
      color: 'primary'
    },
    {
      id: 'error-rate',
      label: 'Error Rate',
      value: (application.errorRate * 100).toFixed(1),
      unit: '%',
      color: application.errorRate < 0.05 ? 'success' : application.errorRate < 0.1 ? 'warning' : 'error'
    },
    {
      id: 'anomaly-count',
      label: 'Anomalies',
      value: application.anomalyCount,
      color: application.anomalyCount === 0 ? 'success' : 'warning'
    }
  ]

  const performanceMetrics: MetricItem[] = [
    {
      id: 'response-time',
      label: 'Avg Response Time',
      value: '45.2',
      unit: 'ms',
      color: 'primary',
      trend: 'down',
      trendValue: -12
    },
    {
      id: 'throughput',
      label: 'Throughput',
      value: '1,234',
      unit: 'req/s',
      color: 'success',
      trend: 'up',
      trendValue: 8
    },
    {
      id: 'cpu-usage',
      label: 'CPU Usage',
      value: '23.4',
      unit: '%',
      color: 'warning',
      progress: 23.4
    },
    {
      id: 'memory-usage',
      label: 'Memory Usage',
      value: '67.8',
      unit: '%',
      color: 'warning',
      progress: 67.8
    }
  ]

  return (
    <Box>
      {/* Health Metrics */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Health Metrics
        </Typography>
        <MetricsGrid metrics={healthMetrics} columns={4} showProgress />
      </Box>

      {/* Performance Metrics */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Performance Metrics
        </Typography>
        <MetricsGrid metrics={performanceMetrics} columns={4} showTrends showProgress />
      </Box>

      {/* Detailed Metrics */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Log Volume Trend
              </Typography>
              <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Chart placeholder - Log volume over time
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Error Rate Trend
              </Typography>
              <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Chart placeholder - Error rate over time
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Metric Details */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Metric Details
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Log Volume Distribution
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="caption">Info</Typography>
                  <Typography variant="caption">75%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={75} sx={{ height: 8, borderRadius: 4 }} />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="caption">Warning</Typography>
                  <Typography variant="caption">15%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={15} 
                  sx={{ height: 8, borderRadius: 4, backgroundColor: 'rgba(255, 152, 0, 0.2)' }}
                />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="caption">Error</Typography>
                  <Typography variant="caption">10%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={10} 
                  sx={{ height: 8, borderRadius: 4, backgroundColor: 'rgba(244, 67, 54, 0.2)' }}
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Performance Summary
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Response Time</Typography>
                  <Typography variant="body2" color="primary">45.2ms</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Throughput</Typography>
                  <Typography variant="body2" color="primary">1,234 req/s</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">CPU Usage</Typography>
                  <Typography variant="body2" color="warning.main">23.4%</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Memory Usage</Typography>
                  <Typography variant="body2" color="warning.main">67.8%</Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}
