import React, { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Breadcrumbs,
  Link,
  Alert,
  LinearProgress,
  Grid,
  Button,
  Chip
} from '@mui/material'
import {
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material'
import { useParams, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store'
import { fetchProject } from '../store/features/projects/projectsSlice'
import { fetchProjectAnalyses, startApplicationAnalysis, getAnalysisResult } from '../store/features/analysis/analysisSlice'
import ApplicationAnalysis from '../components/ApplicationAnalysis'
import ApplicationAnalysisManager from '../components/analysis/ApplicationAnalysisManager'
import AgentInvocationControls from '../components/agent/AgentInvocationControls'

const ApplicationAnalysisPage: React.FC = () => {
  console.log('ApplicationAnalysisPage: Component mounted')
  
  const { projectId, applicationName, analysisId } = useParams<{ 
    projectId: string; 
    applicationName: string; 
    analysisId?: string;
  }>()
  
  // Debug logging
  console.log('ApplicationAnalysisPage params:', { projectId, applicationName, analysisId })
  console.log('ApplicationAnalysisPage safety check:', { 
    hasProjectId: !!projectId, 
    hasApplicationName: !!applicationName, 
    applicationNameValue: applicationName,
    isUndefined: applicationName === 'undefined'
  })
  
  // Safety check for required parameters
  if (!projectId || !applicationName || applicationName === 'undefined') {
    console.log('ApplicationAnalysisPage: Rendering error due to missing parameters')
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Missing required parameters: projectId={projectId}, applicationName={applicationName}
        </Alert>
      </Box>
    )
  }
  
  console.log('ApplicationAnalysisPage: Rendering main content')
  
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()
  
  const { currentProject, loading: projectLoading } = useSelector((state: RootState) => state.projects)
  const { analyses, analysisResult, loading: analysisLoading } = useSelector((state: RootState) => state.analysis)
  
  // Debug logging for project state
  console.log('ApplicationAnalysisPage project state:', {
    currentProject,
    projectLoading,
    projectId,
    applicationName
  })
  
  const [isStartingAnalysis, setIsStartingAnalysis] = useState(false)
  
  // If analysisId is provided, we're viewing a specific analysis result
  const isViewingResult = Boolean(analysisId)
  const currentAnalysis = isViewingResult ? analyses.find(a => a.id === analysisId) : null

  useEffect(() => {
    if (projectId) {
      dispatch(fetchProject(projectId))
      dispatch(fetchProjectAnalyses(projectId))
    }
  }, [dispatch, projectId])


  // Fetch analysis result when viewing a specific analysis
  useEffect(() => {
    if (isViewingResult && analysisId && currentAnalysis?.status === 'completed') {
      dispatch(getAnalysisResult(analysisId))
    }
  }, [dispatch, analysisId, isViewingResult, currentAnalysis?.status])

  const handleStartAnalysis = async () => {
    if (!projectId || !applicationName) return
    
    setIsStartingAnalysis(true)
    try {
      console.log('Starting local analysis for:', applicationName)
      const result = await dispatch(startApplicationAnalysis({ 
        projectId, 
        applicationName 
      })).unwrap()
      console.log('Local analysis started:', result)
      
      // Refresh analyses to get the latest status
      await dispatch(fetchProjectAnalyses(projectId))
      
      // Navigate to the analysis results
      navigate(`/analysis/${projectId}/${applicationName}/${result.analysis_id}`)
    } catch (error) {
      console.error('Failed to start local analysis:', error)
      alert(`Failed to start local analysis for ${applicationName}. Please try again.`)
    } finally {
      setIsStartingAnalysis(false)
    }
  }

  const handleRefresh = async () => {
    if (!projectId) return
    
    try {
      await dispatch(fetchProjectAnalyses(projectId))
      if (isViewingResult && analysisId && currentAnalysis?.status === 'completed') {
        await dispatch(getAnalysisResult(analysisId))
      }
    } catch (error) {
      console.error('Failed to refresh:', error)
    }
  }

  const handleBackToProject = () => {
    navigate(`/analysis/${projectId}`)
  }

  // Removed unused getStatusColor function

  // Auto-redirect to latest completed analysis if no specific analysis is being viewed
  // Only redirect if we have completed analyses and we're not already viewing a specific analysis
  useEffect(() => {
    if (!isViewingResult && analyses.length > 0) {
      // Find the latest completed analysis for this application
      const applicationAnalyses = analyses.filter(analysis => 
        analysis.application_focus === applicationName
      )
      const latestCompletedAnalysis = applicationAnalyses
        .filter(analysis => analysis.status === 'completed')
        .sort((a, b) => new Date(b.completed_timestamp || b.started_timestamp || 0).getTime() - 
                         new Date(a.completed_timestamp || a.started_timestamp || 0).getTime())[0]
      
      if (latestCompletedAnalysis) {
        console.log('Auto-redirecting to latest completed analysis:', latestCompletedAnalysis.id)
        navigate(`/analysis/${projectId}/${applicationName}/${latestCompletedAnalysis.id}`, { replace: true })
      }
    }
  }, [isViewingResult, analyses, navigate, projectId, applicationName])

  if (projectLoading || analysisLoading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    )
  }

  if (!projectId || !applicationName) {
    console.log('ApplicationAnalysisPage: Early return - missing projectId or applicationName')
    return (
      <Box sx={{ width: '100%' }}>
        <Alert severity="error">
          Missing project ID or application name. <Link onClick={() => navigate('/')}>Return to Dashboard</Link>
        </Alert>
      </Box>
    )
  }

  if (!currentProject) {
    console.log('ApplicationAnalysisPage: Early return - currentProject not found')
    return (
      <Box sx={{ width: '100%' }}>
        <Alert severity="error">
          Project not found. <Link onClick={() => navigate('/')}>Return to Dashboard</Link>
        </Alert>
      </Box>
    )
  }

  // Check if application exists in project
  const applicationsDetected = (currentProject as any).applications_detected || []
  console.log('ApplicationAnalysisPage: Checking applications:', { applicationName, applicationsDetected })
  if (!applicationsDetected.includes(applicationName)) {
    console.log('ApplicationAnalysisPage: Early return - application not found in project')
    return (
      <Box sx={{ width: '100%' }}>
        <Alert severity="error">
          Application "{applicationName}" not found in project. Available applications: {applicationsDetected.join(', ')}
        </Alert>
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
          <Link
            color="inherit"
            href="#"
            onClick={(e) => {
              e.preventDefault()
              navigate(`/analysis/${projectId}`)
            }}
          >
            {currentProject.name}
          </Link>
          <Typography color="text.primary">{applicationName}</Typography>
        </Breadcrumbs>
      </Box>

      {/* Application Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              {applicationName} Analysis
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Detailed analysis and monitoring for {applicationName} application
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={handleRefresh}
            >
              Refresh
            </Button>
            <Button
              variant="outlined"
              onClick={handleBackToProject}
            >
              Back to Project
            </Button>
            {isViewingResult ? (
              <Button
                variant="contained"
                startIcon={<PlayIcon />}
                onClick={handleStartAnalysis}
                disabled={isStartingAnalysis}
              >
                Start Local Analysis
              </Button>
            ) : (
              <Button
                variant="contained"
                startIcon={isStartingAnalysis ? <RefreshIcon /> : <PlayIcon />}
                onClick={handleStartAnalysis}
                disabled={isStartingAnalysis}
              >
                {isStartingAnalysis ? 'Starting Analysis...' : 'Start Local Analysis'}
              </Button>
            )}
          </Box>
        </Box>
        
        {/* Application Info */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Application Information
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Chip label={applicationName} color="primary" />
                  <Chip label="LCM Application" variant="outlined" />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  This application is part of the prplOS LCM (Lifecycle Management) system.
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Analysis Management
                </Typography>
                {projectId && applicationName && applicationName !== 'undefined' ? (
                  <ApplicationAnalysisManager
                    projectId={projectId}
                    applicationName={applicationName}
                    onStartAnalysis={handleStartAnalysis}
                  />
                ) : (
                  <Alert severity="error">
                    Missing required parameters: projectId={projectId}, applicationName={applicationName}
                  </Alert>
                )}
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Agent Analysis Controls */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Remote Agent Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Invoke specialized agents for advanced analysis of {applicationName} logs
            </Typography>
            {projectId && applicationName && applicationName !== 'undefined' ? (
              <AgentInvocationControls
                projectId={projectId}
                applicationName={applicationName}
                onAnalysisStarted={(analysisId) => {
                  console.log('Agent analysis started:', analysisId)
                  // Optionally refresh the page or show notification
                }}
                onResultsReady={(results) => {
                  console.log('Agent analysis results ready:', results)
                  // Optionally show notification or update UI
                }}
              />
            ) : (
              <Alert severity="error">
                Missing required parameters: projectId={projectId}, applicationName={applicationName}
              </Alert>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Local Analysis Section */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <TimelineIcon />
            <Typography variant="h6">
              Local Analysis - Time Sequence
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            MeshLog's built-in analysis showing the time sequence of events for {applicationName}
          </Typography>
          
          {isViewingResult && currentAnalysis?.status === 'completed' && analysisResult && (analysisResult as any).application_analyses && (analysisResult as any).application_analyses[applicationName] ? (
            <Box sx={{ mt: 3 }}>
              <ApplicationAnalysis
                applicationName={applicationName}
                analysis={{
                  ...(analysisResult as any).application_analyses[applicationName],
                  project_id: projectId,
                  id: analysisId || currentAnalysis?.id
                }}
              />
            </Box>
          ) : (
            <Box sx={{ 
              height: 400, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              border: '2px dashed #ccc',
              borderRadius: 1,
              mt: 2
            }}>
              <Box sx={{ textAlign: 'center' }}>
                <TimelineIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Time Sequence Analysis
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Start a local analysis to view the time sequence of events for {applicationName}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={handleStartAnalysis}
                  disabled={isStartingAnalysis}
                >
                  {isStartingAnalysis ? 'Starting Analysis...' : 'Start Local Analysis'}
                </Button>
              </Box>
            </Box>
          )}
          
          {currentAnalysis?.status === 'failed' && (
            <Box sx={{ mt: 3 }}>
              <Alert severity="error">
                <Typography variant="h6" gutterBottom>
                  Local Analysis Failed
                </Typography>
                <Typography variant="body2">
                  {currentAnalysis.error_message || 'Unknown error occurred'}
                </Typography>
              </Alert>
            </Box>
          )}
        </CardContent>
      </Card>

    </Box>
  )
}

export default ApplicationAnalysisPage
