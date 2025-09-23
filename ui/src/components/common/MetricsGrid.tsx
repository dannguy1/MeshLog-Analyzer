import React from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Speed as SpeedIcon
} from '@mui/icons-material'

export interface MetricItem {
  id: string
  label: string
  value: number | string
  unit?: string
  trend?: 'up' | 'down' | 'stable'
  trendValue?: number
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning'
  progress?: number
  maxValue?: number
}

interface MetricsGridProps {
  metrics: MetricItem[]
  columns?: 2 | 3 | 4
  showTrends?: boolean
  showProgress?: boolean
  size?: 'small' | 'medium' | 'large'
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({
  metrics,
  columns = 3,
  showTrends = true,
  showProgress = false,
  size = 'medium'
}) => {
  const getTrendIcon = (trend?: 'up' | 'down' | 'stable') => {
    if (!trend) return null
    
    switch (trend) {
      case 'up':
        return <TrendingUpIcon color="success" fontSize="small" />
      case 'down':
        return <TrendingDownIcon color="error" fontSize="small" />
      case 'stable':
        return <SpeedIcon color="primary" fontSize="small" />
      default:
        return null
    }
  }

  const getColor = (color?: string) => {
    switch (color) {
      case 'success': return '#4caf50'
      case 'error': return '#f44336'
      case 'warning': return '#ff9800'
      case 'secondary': return '#9c27b0'
      default: return '#2196f3'
    }
  }

  const getTypographyVariant = () => {
    switch (size) {
      case 'small': return 'h6'
      case 'large': return 'h3'
      default: return 'h4'
    }
  }

  return (
    <Grid container spacing={2}>
      {metrics.map((metric) => (
        <Grid item xs={12} md={12 / columns} key={metric.id}>
          <Card 
            sx={{ 
              height: '100%',
              borderLeft: 3,
              borderColor: getColor(metric.color)
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {metric.label}
                </Typography>
                {showTrends && metric.trend && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    {getTrendIcon(metric.trend)}
                    {metric.trendValue && (
                      <Typography variant="caption" color="text.secondary">
                        {metric.trendValue > 0 ? '+' : ''}{metric.trendValue}%
                      </Typography>
                    )}
                  </Box>
                )}
              </Box>

              <Typography 
                variant={getTypographyVariant()} 
                color={getColor(metric.color)}
                sx={{ mb: 1 }}
              >
                {metric.value}
                {metric.unit && (
                  <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
                    {metric.unit}
                  </Typography>
                )}
              </Typography>

              {showProgress && metric.progress !== undefined && (
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">
                      Progress
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {metric.progress}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={metric.progress} 
                    sx={{ 
                      height: 6, 
                      borderRadius: 3,
                      backgroundColor: 'rgba(0,0,0,0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getColor(metric.color)
                      }
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  )
}
