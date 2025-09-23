import React from 'react'
import {
  Box,
  Typography,
  Chip,
  Button,
  Avatar
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon
} from '@mui/icons-material'
import { HealthScore } from '../common/HealthScore'
import { Application } from '../../utils/types'

interface ApplicationHeaderProps {
  application: Application
  onBackToAll?: () => void
  showBackButton?: boolean
  onRefresh?: () => void
  onSettings?: () => void
}

export const ApplicationHeader: React.FC<ApplicationHeaderProps> = ({
  application,
  onBackToAll,
  showBackButton = true,
  onRefresh,
  onSettings
}) => {
  const getDomainColor = (domain: string) => {
    switch (domain.toLowerCase()) {
      case 'client_steering': return 'primary'
      case 'channel_selection': return 'secondary'
      case 'topology_optimization': return 'success'
      case 'iot_networking': return 'warning'
      default: return 'default'
    }
  }

  return (
    <Box sx={{ mb: 4 }}>
      {/* Back Button */}
      {showBackButton && onBackToAll && (
        <Box sx={{ mb: 2 }}>
          <Button
            variant="text"
            startIcon={<ArrowBackIcon />}
            onClick={onBackToAll}
            sx={{ color: 'text.secondary' }}
          >
            Back to All Applications
          </Button>
        </Box>
      )}

      {/* Main Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Avatar
              sx={{ 
                bgcolor: 'primary.main',
                width: 56,
                height: 56,
                fontSize: '1.5rem'
              }}
            >
              {application.name.charAt(0).toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="h4" gutterBottom>
                {application.name}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={application.functionalDomain}
                  color={getDomainColor(application.functionalDomain)}
                  size="small"
                />
                <Chip
                  label={`Container: ${application.containerId.slice(-8)}`}
                  variant="outlined"
                  size="small"
                />
              </Box>
            </Box>
          </Box>

          <Typography variant="body1" color="text.secondary">
            Last updated: {new Date(application.lastUpdated).toLocaleString()}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <HealthScore score={application.healthScore} size="large" />
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            {onRefresh && (
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={onRefresh}
              >
                Refresh
              </Button>
            )}
            {onSettings && (
              <Button
                variant="outlined"
                startIcon={<SettingsIcon />}
                onClick={onSettings}
              >
                Settings
              </Button>
            )}
          </Box>
        </Box>
      </Box>

      {/* Quick Stats */}
      <Box sx={{ display: 'flex', gap: 3, mt: 3 }}>
        <Box>
          <Typography variant="h6" color="primary">
            {application.logVolume.toLocaleString()}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Log Entries
          </Typography>
        </Box>
        <Box>
          <Typography variant="h6" color="error">
            {(application.errorRate * 100).toFixed(1)}%
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Error Rate
          </Typography>
        </Box>
        <Box>
          <Typography variant="h6" color="warning.main">
            {application.anomalyCount}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Anomalies
          </Typography>
        </Box>
      </Box>
    </Box>
  )
}
