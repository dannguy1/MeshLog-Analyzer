import React, { useEffect } from 'react'
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
  Add as AddIcon,
  Delete as DeleteIcon
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store'
import { fetchProjects, deleteProject } from '../store/features/projects/projectsSlice'


const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()
  
  const { projects, loading: projectsLoading } = useSelector((state: RootState) => state.projects)

  useEffect(() => {
    dispatch(fetchProjects())
  }, [dispatch])




  const handleAddProject = () => {
    navigate('/upload')
  }

  const handleDeleteProject = async (projectId: string) => {
    if (window.confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      try {
        await dispatch(deleteProject(projectId)).unwrap()
      } catch (error) {
        console.error('Failed to delete project:', error)
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

  if (projectsLoading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    )
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Application-Centric Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor and analyze individual LCM applications
        </Typography>
        {projects.length > 0 && (
          <Box sx={{ mt: 2, display: 'flex', gap: 3 }}>
            <Chip 
              label={`${projects.length} Projects`} 
              color="primary" 
              variant="outlined"
            />
            <Chip 
              label={`${projects.filter(p => p.status === 'completed').length} Completed`} 
              color="success" 
              variant="outlined"
            />
            <Chip 
              label={`${(projects.reduce((sum, p) => sum + (p.file_size || 0), 0) / (1024 * 1024)).toFixed(1)} MB Total`} 
              color="info" 
              variant="outlined"
            />
          </Box>
        )}
      </Box>

      {/* Project Selection */}
      <Card sx={{ mb: 4 }}>
            <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Projects ({projects.length})
            </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
              onClick={handleAddProject}
            >
              Add Project
                  </Button>
                </Box>
                <Grid container spacing={2}>
            {projects.map((project) => (
              <Grid item xs={12} md={4} key={project.id}>
                        <Card
                          sx={{
                            cursor: 'pointer',
                            '&:hover': { boxShadow: 3 }
                          }}
                          onClick={() => navigate(`/analysis/${project.id}`)}
                        >
                          <CardContent>
                      <Typography variant="h6" gutterBottom>
                                {project.name}
                              </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {project.description || 'No description provided'}
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="caption" color="text.secondary">
                          File Size: {project.file_size ? (project.file_size / (1024 * 1024)).toFixed(2) + ' MB' : 'Unknown'}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                              <Chip
                                label={project.status}
                          color={getStatusColor(project.status)}
                                size="small"
                              />
                        <Typography variant="caption" color="text.secondary">
                          {project.created_at ? new Date(project.created_at).toLocaleDateString() : 'Unknown'}
                        </Typography>
                            </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="caption" color="text.secondary">
                          {(project as any).applications_detected?.length || 0} applications
                            </Typography>
                        <Button
                          size="small"
                          color="error"
                          startIcon={<DeleteIcon />}
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteProject(project.id)
                          }}
                        >
                          Delete
                        </Button>
                      </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                ))}
                </Grid>
        </CardContent>
      </Card>


      {/* No Projects */}
      {!projectsLoading && projects.length === 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              No Projects Available
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Upload a log package to get started with application analysis.
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/upload')}
              sx={{ mt: 2 }}
            >
              Upload Package
              </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default Dashboard
