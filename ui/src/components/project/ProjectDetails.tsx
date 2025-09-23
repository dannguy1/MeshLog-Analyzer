import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Divider
} from '@mui/material'
import {
  Storage as StorageIcon,
  Schedule as ScheduleIcon,
  Apps as AppsIcon
} from '@mui/icons-material'
import { Project } from '../../utils/types'

interface ProjectDetailsProps {
  project: Project
  applications: Array<{
    name: string
    functionalDomain: string
    healthScore: number
    logVolume: number
    errorRate: number
  }>
  onViewApplications?: () => void
}

export const ProjectDetails: React.FC<ProjectDetailsProps> = ({
  project,
  applications,
  onViewApplications
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return 'success'
      case 'processing': return 'warning'
      case 'error': return 'error'
      default: return 'default'
    }
  }

  const totalLogEntries = applications.reduce((sum, app) => sum + app.logVolume, 0)
  const averageHealthScore = applications.length > 0 
    ? applications.reduce((sum, app) => sum + app.healthScore, 0) / applications.length 
    : 0
  const totalErrorRate = applications.length > 0
    ? applications.reduce((sum, app) => sum + app.errorRate, 0) / applications.length
    : 0

  return (
    <Box>
      {/* Project Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography variant="h5" gutterBottom>
                {project.name}
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                {project.description || 'No description provided'}
              </Typography>
            </Box>
            <Chip
              label={project.status}
              color={getStatusColor(project.status)}
              size="medium"
            />
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <StorageIcon color="primary" />
                <Typography variant="body2" color="text.secondary">
                  File Size: {((project.fileSize || project.file_size_bytes || 0) / 1024 / 1024).toFixed(1)} MB
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <ScheduleIcon color="primary" />
                <Typography variant="body2" color="text.secondary">
                  Uploaded: {project.created_at ? new Date(project.created_at).toLocaleString() : 'Unknown'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AppsIcon color="primary" />
                <Typography variant="body2" color="text.secondary">
                  Applications Detected: {applications.length}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                {onViewApplications && (
                  <Button
                    variant="outlined"
                    onClick={onViewApplications}
                  >
                    View Applications
                  </Button>
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Project Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="primary" gutterBottom>
                {applications.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Applications
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="primary" gutterBottom>
                {totalLogEntries.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Log Entries
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="primary" gutterBottom>
                {averageHealthScore.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Health Score
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="primary" gutterBottom>
                {(totalErrorRate * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Error Rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Application Summary */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Application Summary
          </Typography>
          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {applications.length > 0 ? (
              applications.map((app, index) => (
                <Box key={app.name}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 1 }}>
                    <Box>
                      <Typography variant="body1" fontWeight="medium">
                        {app.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {app.functionalDomain}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        {app.logVolume.toLocaleString()} logs
                      </Typography>
                      <Chip
                        label={`${app.healthScore.toFixed(0)}/100`}
                        color={app.healthScore >= 80 ? 'success' : app.healthScore >= 60 ? 'warning' : 'error'}
                        size="small"
                      />
                    </Box>
                  </Box>
                  {index < applications.length - 1 && <Divider />}
                </Box>
              ))
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                No applications detected
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}
