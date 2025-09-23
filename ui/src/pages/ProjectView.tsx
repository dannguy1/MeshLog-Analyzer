import React, { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Breadcrumbs,
  Link,
  Chip,
  Alert,
  LinearProgress,
} from '@mui/material'
import { useParams, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store'
import { fetchProject } from '../store/features/projects/projectsSlice'
import { fetchProjectAnalyses, startApplicationAnalysis } from '../store/features/analysis/analysisSlice'
import AnalysisView from './AnalysisView'
import RealTimeMonitor from './RealTimeMonitor'
import { ProjectSummary } from '../components/project/ProjectSummary'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`project-tabpanel-${index}`}
      aria-labelledby={`project-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

const ProjectView: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()
  const [tabValue, setTabValue] = useState(0)
  const [analysisLoading, setAnalysisLoading] = useState<{ [key: string]: boolean }>({})
  const [refreshLoading, setRefreshLoading] = useState(false)

  const { currentProject, loading: projectLoading } = useSelector((state: RootState) => state.projects)
  const { applicationAnalysisStatus } = useSelector((state: RootState) => state.analysis)

  useEffect(() => {
    if (projectId) {
      dispatch(fetchProject(projectId))
      dispatch(fetchProjectAnalyses(projectId))
    }
  }, [dispatch, projectId])

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handleStartApplicationAnalysis = async (applicationName: string) => {
    if (!projectId) return
    
    try {
      setAnalysisLoading(prev => ({ ...prev, [applicationName]: true }))
      
      const result = await dispatch(startApplicationAnalysis({ 
        projectId, 
        applicationName 
      })).unwrap()
      
      console.log(`Analysis started for ${applicationName}:`, result)
      
      // Navigate to analysis view for this application
      navigate(`/analysis/${projectId}/${applicationName}`)
      
    } catch (error) {
      console.error(`Failed to start analysis for ${applicationName}:`, error)
      alert(`Failed to start analysis for ${applicationName}. Please try again.`)
    } finally {
      setAnalysisLoading(prev => ({ ...prev, [applicationName]: false }))
    }
  }

  const handleRefresh = async () => {
    if (!projectId) return
    
    try {
      setRefreshLoading(true)
      
      // Refresh project data and analyses
      await Promise.all([
        dispatch(fetchProject(projectId)),
        dispatch(fetchProjectAnalyses(projectId))
      ])
      
      console.log('Project data refreshed successfully')
      
    } catch (error) {
      console.error('Failed to refresh project data:', error)
      alert('Failed to refresh project data. Please try again.')
    } finally {
      setRefreshLoading(false)
    }
  }

  if (projectLoading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    )
  }

  if (!currentProject) {
    return (
      <Alert severity="error">
        Project not found. <Link onClick={() => navigate('/')}>Return to Dashboard</Link>
      </Alert>
    )
  }

  return (
    <Box>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          component="button"
          variant="body1"
          onClick={() => navigate('/')}
          sx={{ cursor: 'pointer' }}
        >
          Dashboard
        </Link>
        <Typography color="text.primary">{currentProject.name}</Typography>
      </Breadcrumbs>

      {/* Project Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h4" gutterBottom>
            {currentProject.name}
          </Typography>
          <Chip
            label={currentProject.status}
            color={currentProject.status === 'completed' ? 'success' : currentProject.status === 'failed' ? 'error' : 'default'}
          />
        </Box>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          {currentProject.description || 'No description'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Created {currentProject.created_at ? new Date(currentProject.created_at).toLocaleDateString() : 'Unknown'}
        </Typography>
      </Box>

      {/* Project Summary - Log Package and Applications */}
      <ProjectSummary 
        project={currentProject} 
        onStartApplicationAnalysis={handleStartApplicationAnalysis}
        analysisLoading={analysisLoading}
        onRefresh={handleRefresh}
        refreshLoading={refreshLoading}
        applicationAnalysisStatus={applicationAnalysisStatus}
      />

      {/* Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="project tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Analysis" id="project-tab-0" aria-controls="project-tabpanel-0" />
          <Tab label="Real-time Monitor" id="project-tab-1" aria-controls="project-tabpanel-1" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <AnalysisView projectId={projectId!} />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <RealTimeMonitor projectId={projectId!} />
        </TabPanel>
      </Paper>
    </Box>
  )
}

export default ProjectView
