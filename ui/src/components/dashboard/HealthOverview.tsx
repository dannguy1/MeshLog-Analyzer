import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip
} from '@mui/material'
import {
  TrendingDown as TrendingDownIcon,
  Speed as SpeedIcon,
  Warning as WarningIcon
} from '@mui/icons-material'
import { HealthScore } from '../common/HealthScore'
import { MetricsGrid, MetricItem } from '../common/MetricsGrid'

interface HealthOverviewProps {
  totalApplications: number
  healthyApplications: number
  degradedApplications: number
  criticalApplications: number
  averageHealthScore: number
  totalLogEntries: number
  errorRate: number
  anomalyCount: number
  recentActivity: Array<{
    id: string
    application: string
    event: string
    timestamp: string
    severity: 'info' | 'warning' | 'error' | 'critical'
  }>
}

export const HealthOverview: React.FC<HealthOverviewProps> = ({
  totalApplications,
  healthyApplications,
  degradedApplications,
  criticalApplications,
  averageHealthScore,
  totalLogEntries,
  errorRate,
  anomalyCount,
  recentActivity
}) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#d32f2f'
      case 'error': return '#f44336'
      case 'warning': return '#ff9800'
      default: return '#2196f3'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'error':
        return <WarningIcon sx={{ color: getSeverityColor(severity) }} />
      case 'warning':
        return <TrendingDownIcon sx={{ color: getSeverityColor(severity) }} />
      default:
        return <SpeedIcon sx={{ color: getSeverityColor(severity) }} />
    }
  }

  const metrics: MetricItem[] = [
    {
      id: 'total-apps',
      label: 'Total Applications',
      value: totalApplications,
      color: 'primary'
    },
    {
      id: 'healthy-apps',
      label: 'Healthy',
      value: healthyApplications,
      color: 'success',
      trend: 'up',
      trendValue: Math.round((healthyApplications / totalApplications) * 100)
    },
    {
      id: 'degraded-apps',
      label: 'Degraded',
      value: degradedApplications,
      color: 'warning'
    },
    {
      id: 'critical-apps',
      label: 'Critical',
      value: criticalApplications,
      color: 'error'
    }
  ]

  const performanceMetrics: MetricItem[] = [
    {
      id: 'avg-health',
      label: 'Average Health Score',
      value: averageHealthScore.toFixed(1),
      unit: '/100',
      color: averageHealthScore >= 80 ? 'success' : averageHealthScore >= 60 ? 'warning' : 'error'
    },
    {
      id: 'log-entries',
      label: 'Total Log Entries',
      value: totalLogEntries.toLocaleString(),
      color: 'primary'
    },
    {
      id: 'error-rate',
      label: 'Error Rate',
      value: (errorRate * 100).toFixed(1),
      unit: '%',
      color: errorRate < 0.05 ? 'success' : errorRate < 0.1 ? 'warning' : 'error'
    },
    {
      id: 'anomalies',
      label: 'Anomalies Detected',
      value: anomalyCount,
      color: anomalyCount === 0 ? 'success' : 'warning'
    }
  ]

  return (
    <Box>
      {/* Overall Health Score */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Overall System Health
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <HealthScore score={averageHealthScore} size="large" />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Average health score across all applications
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Based on {totalApplications} applications
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Application Health Metrics */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Application Health Distribution
        </Typography>
        <MetricsGrid metrics={metrics} columns={4} />
      </Box>

      {/* Performance Metrics */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Performance Metrics
        </Typography>
        <MetricsGrid metrics={performanceMetrics} columns={4} />
      </Box>

      {/* Recent Activity */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
            {recentActivity.length > 0 ? (
              recentActivity.map((activity) => (
                <Box
                  key={activity.id}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    p: 1,
                    borderBottom: 1,
                    borderColor: 'divider',
                    '&:last-child': { borderBottom: 0 }
                  }}
                >
                  {getSeverityIcon(activity.severity)}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2">
                      <strong>{activity.application}</strong>: {activity.event}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(activity.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                  <Chip
                    label={activity.severity}
                    size="small"
                    sx={{ 
                      backgroundColor: getSeverityColor(activity.severity),
                      color: 'white'
                    }}
                  />
                </Box>
              ))
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                No recent activity
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}
