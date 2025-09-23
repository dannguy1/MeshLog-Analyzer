import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { api } from '../../../services/api'

export interface Project {
  id: string
  name: string
  description?: string
  created_at?: string
  status: 'uploading' | 'processing' | 'completed' | 'failed' | 'ready' | 'error'
  file_size?: number
  file_size_bytes?: number
  original_filename?: string
  upload_timestamp?: string
  extraction_path?: string
  analysis_count?: number
  last_analysis_timestamp?: string
  applications_detected?: string[]
  total_log_entries?: number
  package_metadata?: {
    total_containers: number
    total_log_files: number
    total_log_size_bytes: number
    time_range_start?: string
    time_range_end?: string
    applications_detected: string[]
  }
}

interface ProjectsState {
  projects: Project[]
  loading: boolean
  error: string | null
  currentProject: Project | null
}

const initialState: ProjectsState = {
  projects: [],
  loading: false,
  error: null,
  currentProject: null,
}

// Async thunks
export const fetchProjects = createAsyncThunk(
  'projects/fetchProjects',
  async () => {
    const response = await api.get('/api/v1/projects')
    return response.data.projects
  }
)

export const fetchProject = createAsyncThunk(
  'projects/fetchProject',
  async (projectId: string) => {
    const response = await api.get(`/api/v1/projects/${projectId}`)
    return response.data
  }
)

export const createProject = createAsyncThunk(
  'projects/createProject',
  async (projectData: { name: string; description?: string; file: File }) => {
    const formData = new FormData()
    formData.append('name', projectData.name)
    if (projectData.description) {
      formData.append('description', projectData.description)
    }
    formData.append('file', projectData.file)
    
    const response = await api.post('/api/v1/projects', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    // Extract only the project fields we need, ignoring extra fields like 'message', 'project_id'
    const { id, name, description, status, created_at, file_size, original_filename } = response.data
    return {
      id,
      name,
      description,
      status,
      created_at,
      file_size,
      original_filename
    }
  }
)

export const getProjectResults = createAsyncThunk(
  'projects/getProjectResults',
  async (projectId: string) => {
    const response = await api.get(`/api/v1/projects/${projectId}/results`)
    return response.data
  }
)

export const deleteProject = createAsyncThunk(
  'projects/deleteProject',
  async (projectId: string) => {
    const response = await api.delete(`/api/v1/projects/${projectId}`)
    return { projectId, ...response.data }
  }
)

const projectsSlice = createSlice({
  name: 'projects',
  initialState,
  reducers: {
    setCurrentProject: (state, action: PayloadAction<Project | null>) => {
      state.currentProject = action.payload
    },
    updateProjectStatus: (state, action: PayloadAction<{ id: string; status: Project['status'] }>) => {
      const project = state.projects.find(p => p.id === action.payload.id)
      if (project) {
        project.status = action.payload.status
      }
      if (state.currentProject?.id === action.payload.id) {
        state.currentProject.status = action.payload.status
      }
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch projects
      .addCase(fetchProjects.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        state.loading = false
        state.projects = action.payload || []
      })
      .addCase(fetchProjects.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch projects'
      })
      // Fetch single project
      .addCase(fetchProject.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchProject.fulfilled, (state, action) => {
        state.loading = false
        state.currentProject = action.payload
      })
      .addCase(fetchProject.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch project'
      })
      // Create project
      .addCase(createProject.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(createProject.fulfilled, (state, action) => {
        state.loading = false
        state.projects.unshift(action.payload)
        state.currentProject = action.payload
      })
      .addCase(createProject.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to create project'
      })
      // Get project results
      .addCase(getProjectResults.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(getProjectResults.fulfilled, (state, _action) => {
        state.loading = false
        // Handle project results
      })
      .addCase(getProjectResults.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to get project results'
      })
      // Delete project
      .addCase(deleteProject.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(deleteProject.fulfilled, (state, action) => {
        state.loading = false
        state.projects = state.projects.filter(p => p.id !== action.payload.projectId)
        if (state.currentProject?.id === action.payload.projectId) {
          state.currentProject = null
        }
      })
      .addCase(deleteProject.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to delete project'
      })
  },
})

export const { setCurrentProject, updateProjectStatus, clearError } = projectsSlice.actions
export default projectsSlice.reducer
