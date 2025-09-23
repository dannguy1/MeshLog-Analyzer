import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button
} from '@mui/material'
import {
  Delete as DeleteIcon,
  Visibility as ViewIcon
} from '@mui/icons-material'
import { Project } from '../../utils/types'

interface ProjectCardProps {
  project: Project
  isSelected: boolean
  onSelect: (projectId: string) => void
  onDelete?: (projectId: string) => void
  onView?: (projectId: string) => void
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  isSelected,
  onSelect,
  onDelete,
  onView
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return 'success'
      case 'processing': return 'warning'
      case 'error': return 'error'
      default: return 'default'
    }
  }

  return (
    <Card
      sx={{
        cursor: 'pointer',
        border: isSelected ? 2 : 1,
        borderColor: isSelected ? 'primary.main' : 'divider',
        '&:hover': { boxShadow: 3 },
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}
      onClick={() => onSelect(project.id)}
    >
      <CardContent sx={{ flex: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ flex: 1 }}>
            {project.name}
          </Typography>
          <Chip
            label={project.status}
            color={getStatusColor(project.status)}
            size="small"
          />
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          {project.description || 'No description'}
        </Typography>

        <Box sx={{ mt: 2, mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Applications: {project.applicationCount || 0}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Size: {((project.fileSize || project.file_size_bytes || 0) / 1024 / 1024).toFixed(1)} MB
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Uploaded: {project.created_at ? new Date(project.created_at).toLocaleDateString() : 'Unknown'}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', mt: 'auto' }}>
          {onView && (
            <Button
              size="small"
              variant="outlined"
              startIcon={<ViewIcon />}
              onClick={(e) => {
                e.stopPropagation()
                onView(project.id)
              }}
            >
              View
            </Button>
          )}
          {onDelete && (
            <Button
              size="small"
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={(e) => {
                e.stopPropagation()
                onDelete(project.id)
              }}
            >
              Delete
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  )
}
