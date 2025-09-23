import React, { useEffect, useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  LinearProgress,
  CircularProgress,
  Breadcrumbs,
  Link,
  Alert,
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  Analytics as AnalyticsIcon,
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
  Download as DownloadIcon,
  Monitor as MonitorIcon,
  Delete as DeleteIcon,
  ContentCopy as CloneIcon,
  Visibility as ViewIcon
} from '@mui/icons-material'
import { useNavigate, useSearchParams, useParams } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store'
import { 
  getAnalysisResult, 
  getProjectAnalysis, 
  fetchProjectAnalyses, 
  setCurrentAnalysis,
  deleteAnalysis,
  cloneAnalysis,
  exportAnalysisResults
} from '../store/features/analysis/analysisSlice'
import { fetchProject } from '../store/features/projects/projectsSlice'
import { generateChart, generateDashboard } from '../store/features/visualization/visualizationSlice'
import { formatDistanceToNow } from 'date-fns'
import { ProjectSummary } from '../components/project/ProjectSummary'

interface AnalysisViewProps {
  projectId?: string
}

const AnalysisView: React.FC<AnalysisViewProps> = ({ projectId: propProjectId }) => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const dispatch = useDispatch<AppDispatch>()
  const { projectId: urlProjectId } = useParams<{ projectId: string }>()
  const projectId = propProjectId || urlProjectId
  
  if (!projectId) {
    return (
      <Box sx={{ width: '100%' }}>
        <Alert severity="error">
          Project ID not found. <Link onClick={() => navigate('/')}>Return to Dashboard</Link>
        </Alert>
      </Box>
    )
  }
  
  const { analyses, currentAnalysis, analysisResult, loading } = useSelector((state: RootState) => state.analysis)
  const { dashboard, loading: vizLoading } = useSelector((state: RootState) => state.visualization)
  const { currentProject, loading: projectLoading } = useSelector((state: RootState) => state.projects)
  
  const [statusInterval, setStatusInterval] = useState<NodeJS.Timeout | null>(null)
  
  // Get URL parameters for application focus
  const focusedApp = searchParams.get('app')
  const focusedTab = searchParams.get('tab')
  const focusedAnalysis = searchParams.get('analysis')

  useEffect(() => {
    if (projectId) {
      dispatch(fetchProject(projectId))
      dispatch(fetchProjectAnalyses(projectId))
    }
  }, [dispatch, projectId])

  useEffect(() => {
    if (focusedAnalysis) {
      // Set the focused analysis as current
      const analysis = analyses.find(a => a.id === focusedAnalysis)
      if (analysis) {
        dispatch(setCurrentAnalysis(analysis))
      }
    }
  }, [focusedAnalysis, analyses, dispatch])

  useEffect(() => {
    if (currentAnalysis?.status === 'running' || currentAnalysis?.status === 'queued') {
      const interval = setInterval(() => {
        if (currentAnalysis?.id) {
          dispatch(getProjectAnalysis({ projectId, analysisId: currentAnalysis.id }))
        }
      }, 2000)
      setStatusInterval(interval)
      
      return () => clearInterval(interval)
    } else if (currentAnalysis?.status === 'completed') {
      if (currentAnalysis?.id) {
        dispatch(getAnalysisResult(currentAnalysis.id))
      }
    }
  }, [currentAnalysis?.status, currentAnalysis?.id, projectId, dispatch])

  useEffect(() => {
    return () => {
      if (statusInterval) {
        clearInterval(statusInterval)
      }
    }
  }, [statusInterval])

  // Set initial tab based on URL parameter
  useEffect(() => {
    if (focusedTab) {
      // Note: tabValue state was removed, so this effect is now unused
    }
  }, [focusedTab])

  const handleGenerateCharts = async (applicationName?: string) => {
    if (currentAnalysis?.id) {
      if (applicationName) {
        console.log(`Generating charts for application: ${applicationName}`)
        await dispatch(generateChart({ analysisId: currentAnalysis.id, chartType: 'time_series', config: { application: applicationName } }))
        await dispatch(generateChart({ analysisId: currentAnalysis.id, chartType: 'anomalies', config: { application: applicationName } }))
        await dispatch(generateChart({ analysisId: currentAnalysis.id, chartType: 'predictions', config: { application: applicationName } }))
        await dispatch(generateChart({ analysisId: currentAnalysis.id, chartType: 'statistics', config: { application: applicationName } }))
      } else {
        console.log('Generating charts for all applications')
        await dispatch(generateChart({ analysisId: currentAnalysis.id, chartType: 'time_series' }))
        await dispatch(generateChart({ analysisId: currentAnalysis.id, chartType: 'anomalies' }))
        await dispatch(generateChart({ analysisId: currentAnalysis.id, chartType: 'predictions' }))
        await dispatch(generateChart({ analysisId: currentAnalysis.id, chartType: 'statistics' }))
      }
    }
  }

  const handleGenerateDashboard = async () => {
    if (currentAnalysis?.id) {
      console.log('Generating dashboard for analysis:', currentAnalysis.id)
      try {
        const result = await dispatch(generateDashboard({ analysisId: currentAnalysis.id }))
        console.log('Dashboard generation result:', result)
      } catch (error) {
        console.error('Error generating dashboard:', error)
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'running': return 'info'
      case 'failed': return 'error'
      case 'queued': return 'warning'
      default: return 'default'
    }
  }

  // Removed unused handleApplicationFocus function

  const handleClearFocus = () => {
    navigate(`/analysis/${projectId}`)
  }


  const handleExportResults = async () => {
    try {
      if (!currentAnalysis?.id) {
        alert('No analysis selected for export')
        return
      }
      
      console.log('Exporting analysis results for project:', projectId)
      const result = await dispatch(exportAnalysisResults({ 
        projectId, 
        analysisId: currentAnalysis.id,
        format: 'json'
      })).unwrap()
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([result.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', result.filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
    } catch (error) {
      console.error('Failed to export results:', error)
      alert('Failed to export results. Please try again.')
    }
  }

  const handleStartMonitoring = () => {
    navigate(`/monitor/${projectId}`)
  }

  const handleDeleteAnalysis = async (analysisId: string) => {
    if (window.confirm('Are you sure you want to delete this analysis? This action cannot be undone.')) {
      try {
        console.log('Deleting analysis:', analysisId)
        await dispatch(deleteAnalysis({ projectId, analysisId })).unwrap()
        console.log('Analysis deleted successfully')
      } catch (error) {
        console.error('Failed to delete analysis:', error)
        alert('Failed to delete analysis. Please try again.')
      }
    }
  }

  const handleCloneAnalysis = async (analysisId: string) => {
    try {
      console.log('Cloning analysis:', analysisId)
      const result = await dispatch(cloneAnalysis({ projectId, analysisId })).unwrap()
      console.log('Analysis cloned:', result)
      alert('Analysis cloned successfully!')
    } catch (error) {
      console.error('Failed to clone analysis:', error)
      alert('Failed to clone analysis. Please try again.')
    }
  }

  // Removed unused functions: handleViewAnomalies and handleViewTimeSequence

  if (loading || projectLoading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    )
  }

  return (
    <Box>
      {/* Breadcrumb Navigation */}
      <Box sx={{ mb: 3 }}>
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />}>
          <Link
            color="inherit"
            href="#"
            onClick={(e) => {
              e.preventDefault()
              navigate('/')
            }}
            sx={{ display: 'flex', alignItems: 'center' }}
          >
            <HomeIcon sx={{ mr: 0.5 }} fontSize="small" />
            Dashboard
          </Link>
          <Link
            color="inherit"
            href="#"
            onClick={(e) => {
              e.preventDefault()
              navigate('/')
            }}
          >
            Projects
          </Link>
          <Typography color="text.primary">Project {projectId?.slice(-8)}</Typography>
          {focusedApp && (
            <>
              <Typography color="text.primary">{focusedApp}</Typography>
              {focusedTab && (
                <Typography color="text.primary" sx={{ textTransform: 'capitalize' }}>
                  {focusedTab.replace('-', ' ')}
                </Typography>
              )}
            </>
          )}
        </Breadcrumbs>
      </Box>

      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              {focusedApp ? `${focusedApp} Analysis` : 'Application Analysis'}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {focusedApp 
                ? `Detailed analysis for ${focusedApp} application`
                : 'Comprehensive analysis of all LCM applications'
              }
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {!focusedApp && (
              <>
                <Button
                  variant="outlined"
                  startIcon={<MonitorIcon />}
                  onClick={handleStartMonitoring}
                >
                  Real-time Monitor
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportResults}
                  disabled={!analysisResult}
                >
                  Export Results
                </Button>
              </>
            )}
            {focusedApp && (
              <Button
                variant="outlined"
                onClick={handleClearFocus}
                startIcon={<RefreshIcon />}
              >
                View All Applications
              </Button>
            )}
          </Box>
        </Box>
      </Box>

      {/* Project Summary with Application Analysis Buttons */}
      {currentProject && (
        <ProjectSummary 
          project={currentProject} 
          analysisLoading={{}}
        />
      )}

      {/* Analysis History - MOVED TO APPLICATION-SPECIFIC PAGES */}
      {/* Dashboard Results */}
      {false && analyses.length > 0 ? (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Analysis History
          </Typography>
          <Grid container spacing={2}>
            {analyses.map((analysis) => (
              <Grid item xs={12} md={6} lg={4} key={analysis.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    border: currentAnalysis?.id === analysis.id ? 2 : 1,
                    borderColor: currentAnalysis?.id === analysis.id ? 'primary.main' : 'divider'
                  }}
                  onClick={() => {
                    if (analysis.application_focus) {
                      // Navigate to application-specific analysis page
                      navigate(`/analysis/${projectId}/${analysis.application_focus}/${analysis.id}`)
                    } else {
                      // For comprehensive analysis, just select it
                      dispatch(setCurrentAnalysis(analysis))
                    }
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Box>
                        <Typography variant="h6" noWrap>
                          {analysis.application_focus ? `${analysis.application_focus} Analysis` : 'Comprehensive Analysis'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ID: {analysis.id.slice(-8)}
                        </Typography>
                      </Box>
                      <Chip 
                        label={analysis.status} 
                        color={getStatusColor(analysis.status)}
                        size="small"
                      />
                    </Box>

                    {analysis.status === 'running' && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Progress: {analysis.progress_percentage}%
                        </Typography>
                        <LinearProgress variant="determinate" value={analysis.progress_percentage} />
                      </Box>
                    )}

                    {/* Timestamps */}
                    <Box sx={{ mt: 3 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={4}>
                          <Typography variant="caption" color="text.secondary">
                            Created: {formatDistanceToNow(new Date(analysis.created_timestamp))} ago
                          </Typography>
                        </Grid>
                        {analysis.started_timestamp && (
                          <Grid item xs={12} md={4}>
                            <Typography variant="caption" color="text.secondary">
                              Started: {formatDistanceToNow(new Date(analysis.started_timestamp))} ago
                            </Typography>
                          </Grid>
                        )}
                        {analysis.completed_timestamp && (
                          <Grid item xs={12} md={4}>
                            <Typography variant="caption" color="text.secondary">
                              Completed: {formatDistanceToNow(new Date(analysis.completed_timestamp))} ago
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    </Box>

                    {/* Action Buttons */}
                    <Box sx={{ display: 'flex', gap: 1, mt: 2, justifyContent: 'flex-end' }}>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<ViewIcon />}
                        onClick={(e) => {
                          e.stopPropagation()
                          dispatch(setCurrentAnalysis(analysis))
                        }}
                      >
                        View
                      </Button>
                      {analysis.status === 'completed' && (
                        <>
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<CloneIcon />}
                            onClick={(e) => {
                              e.stopPropagation()
                              handleCloneAnalysis(analysis.id)
                            }}
                          >
                            Clone
                          </Button>
                          <Button
                            size="small"
                            variant="outlined"
                            color="error"
                            startIcon={<DeleteIcon />}
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteAnalysis(analysis.id)
                            }}
                          >
                            Delete
                          </Button>
                        </>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      ) : (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <AnalyticsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No Analyses Available
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                No analyses have been run yet. Use the application-specific analysis buttons above to start analyzing individual applications, or use the real-time monitor to observe live data.
              </Typography>
              <Box sx={{ mt: 3 }}>
                <Button
                  variant="outlined"
                  startIcon={<MonitorIcon />}
                  onClick={handleStartMonitoring}
                >
                  Real-time Monitor
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Current Analysis Details */}
      {currentAnalysis && (
        <Card sx={{ mt: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Analysis Details
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" color="text.secondary">
                  ID: {currentAnalysis.id}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Status: {currentAnalysis.status}
                </Typography>
                {currentAnalysis.error_message && (
                  <Typography variant="body2" color="error">
                    Error: {currentAnalysis.error_message}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  {currentAnalysis.status === 'completed' && (
                    <>
                      <Button
                        variant="outlined"
                        onClick={() => handleGenerateCharts()}
                      >
                        Generate Charts
                      </Button>
                      <Button
                        variant="outlined"
                        onClick={handleGenerateDashboard}
                      >
                        Generate Dashboard
                      </Button>
                    </>
                  )}
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Dashboard Results */}
      {dashboard && (
        <Card sx={{ mt: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Dashboard Results
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Generated at: {dashboard.generated_at}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Total charts: {dashboard.total_charts}
            </Typography>
            
            {/* Display individual charts */}
            {Object.entries((dashboard as any).charts || {}).map(([chartType, chart]: [string, any]) => (
              <Box key={chartType} sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {chartType.charAt(0).toUpperCase() + chartType.slice(1).replace('_', ' ')} Chart
                </Typography>
                {(chart as any).type === 'html' ? (
                  <div 
                    dangerouslySetInnerHTML={{ __html: (chart as any).data }}
                    style={{ width: '100%', height: '400px' }}
                  />
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Chart data available in {(chart as any).type} format
                  </Typography>
                )}
              </Box>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Loading indicator for dashboard generation */}
      {vizLoading && (
        <Card sx={{ mt: 4 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CircularProgress size={20} />
              <Typography>Generating dashboard...</Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default AnalysisView
