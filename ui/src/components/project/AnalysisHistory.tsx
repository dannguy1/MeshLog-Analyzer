import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  LinearProgress
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  ContentCopy as CloneIcon,
  Download as DownloadIcon
} from '@mui/icons-material'
import { formatDistanceToNow } from 'date-fns'

interface Analysis {
  id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  progress_percentage: number
  created_timestamp: string
  started_timestamp?: string
  completed_timestamp?: string
  error_message?: string
}

interface AnalysisHistoryProps {
  analyses: Analysis[]
  currentAnalysis?: Analysis
  onSelectAnalysis: (analysis: Analysis) => void
  onDeleteAnalysis?: (analysisId: string) => void
  onCloneAnalysis?: (analysisId: string) => void
  onExportAnalysis?: (analysisId: string) => void
  loading?: boolean
}

export const AnalysisHistory: React.FC<AnalysisHistoryProps> = ({
  analyses,
  currentAnalysis,
  onSelectAnalysis,
  onDeleteAnalysis,
  onCloneAnalysis,
  onExportAnalysis,
  loading = false
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'running': return 'info'
      case 'failed': return 'error'
      case 'queued': return 'warning'
      default: return 'default'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅'
      case 'running': return '🔄'
      case 'failed': return '❌'
      case 'queued': return '⏳'
      default: return '❓'
    }
  }

  const sortedAnalyses = [...analyses].sort((a, b) => 
    new Date(b.created_timestamp).getTime() - new Date(a.created_timestamp).getTime()
  )

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">
          Analysis History ({analyses.length})
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => window.location.reload()}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Analysis Cards */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <LinearProgress sx={{ width: '100%', maxWidth: 400 }} />
        </Box>
      ) : (
        <Grid container spacing={2}>
          {sortedAnalyses.length > 0 ? (
            sortedAnalyses.map((analysis) => (
              <Grid item xs={12} md={6} lg={4} key={analysis.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    border: currentAnalysis?.id === analysis.id ? 2 : 1,
                    borderColor: currentAnalysis?.id === analysis.id ? 'primary.main' : 'divider',
                    '&:hover': { boxShadow: 3 }
                  }}
                  onClick={() => onSelectAnalysis(analysis)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" noWrap>
                        Analysis {analysis.id.slice(-8)}
                      </Typography>
                      <Chip 
                        label={analysis.status} 
                        color={getStatusColor(analysis.status)}
                        size="small"
                        icon={<span>{getStatusIcon(analysis.status)}</span>}
                      />
                    </Box>

                    {analysis.status === 'running' && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Progress: {analysis.progress_percentage}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={analysis.progress_percentage}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    )}

                    {analysis.error_message && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="error" sx={{ fontStyle: 'italic' }}>
                          Error: {analysis.error_message}
                        </Typography>
                      </Box>
                    )}

                    {/* Timestamps */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Created: {formatDistanceToNow(new Date(analysis.created_timestamp))} ago
                      </Typography>
                      {analysis.started_timestamp && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Started: {formatDistanceToNow(new Date(analysis.started_timestamp))} ago
                        </Typography>
                      )}
                      {analysis.completed_timestamp && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Completed: {formatDistanceToNow(new Date(analysis.completed_timestamp))} ago
                        </Typography>
                      )}
                    </Box>

                    {/* Action Buttons */}
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={(e) => {
                          e.stopPropagation()
                          onSelectAnalysis(analysis)
                        }}
                      >
                        View
                      </Button>
                      {analysis.status === 'completed' && (
                        <>
                          {onCloneAnalysis && (
                            <Button
                              size="small"
                              variant="outlined"
                              startIcon={<CloneIcon />}
                              onClick={(e) => {
                                e.stopPropagation()
                                onCloneAnalysis(analysis.id)
                              }}
                            >
                              Clone
                            </Button>
                          )}
                          {onExportAnalysis && (
                            <Button
                              size="small"
                              variant="outlined"
                              startIcon={<DownloadIcon />}
                              onClick={(e) => {
                                e.stopPropagation()
                                onExportAnalysis(analysis.id)
                              }}
                            >
                              Export
                            </Button>
                          )}
                          {onDeleteAnalysis && (
                            <Button
                              size="small"
                              variant="outlined"
                              color="error"
                              startIcon={<DeleteIcon />}
                              onClick={(e) => {
                                e.stopPropagation()
                                onDeleteAnalysis(analysis.id)
                              }}
                            >
                              Delete
                            </Button>
                          )}
                        </>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))
          ) : (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      No Analyses Available
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      No analyses have been run yet. Go to the project page to start application-specific analyses.
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}

      {/* Analysis Statistics */}
      {analyses.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Analysis Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Typography variant="h4" color="primary">
                  {analyses.filter(a => a.status === 'completed').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completed
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="h4" color="info.main">
                  {analyses.filter(a => a.status === 'running').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Running
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="h4" color="warning.main">
                  {analyses.filter(a => a.status === 'queued').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Queued
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="h4" color="error.main">
                  {analyses.filter(a => a.status === 'failed').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Failed
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}
