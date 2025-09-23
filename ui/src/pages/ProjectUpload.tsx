import React, { useState, useCallback, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  LinearProgress,
  Paper,
  Grid,
  Chip,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
} from '@mui/material'
import { useDropzone } from 'react-dropzone'
import { 
  CloudUpload as CloudUploadIcon, 
  Description as DescriptionIcon,
  Restore as RestoreIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { AppDispatch, RootState } from '../store'
import { createProject } from '../store/features/projects/projectsSlice'
import { apiService } from '../services/api'

const ProjectUpload: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { loading, error } = useSelector((state: RootState) => state.projects)
  
  const [activeTab, setActiveTab] = useState(0)
  const [projectName, setProjectName] = useState('')
  const [projectDescription, setProjectDescription] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  
  // Restoration state
  const [availablePackages, setAvailablePackages] = useState<any[]>([])
  const [restoreLoading, setRestoreLoading] = useState(false)
  const [restoreError, setRestoreError] = useState<string | null>(null)
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0])
    }
  }, [])

  // Load available packages when restoration tab is active
  useEffect(() => {
    if (activeTab === 1) {
      loadAvailablePackages()
    }
  }, [activeTab])

  const loadAvailablePackages = async () => {
    try {
      const response = await apiService.getAvailablePackages()
      setAvailablePackages(response.packages || [])
      setRestoreError(null)
    } catch (error) {
      console.error('Failed to load available packages:', error)
      setRestoreError('Failed to load available packages')
    }
  }

  const handleRestoreProject = async () => {
    if (!selectedPackage || !projectName.trim()) {
      return
    }

    try {
      setRestoreLoading(true)
      setRestoreError(null)
      
      const result = await apiService.restoreProject(
        selectedPackage,
        projectName.trim(),
        projectDescription.trim() || undefined
      )
      
      // Navigate to the restored project
      navigate(`/analysis/${result.id}`)
    } catch (error: any) {
      console.error('Restoration failed:', error)
      setRestoreError(error.response?.data?.detail || 'Failed to restore project')
    } finally {
      setRestoreLoading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/x-tar': ['.tar'],
      'application/gzip': ['.tar.gz', '.tgz'],
    },
    multiple: false,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!projectName.trim() || !selectedFile) {
      return
    }

    try {
      setUploadProgress(10)
      
      setUploadProgress(30)
      
      const result = await dispatch(createProject({
        name: projectName.trim(),
        description: projectDescription.trim() || undefined,
        file: selectedFile,
      })).unwrap()

      setUploadProgress(100)
      
      // Navigate directly to the analysis page
      navigate(`/analysis/${result.id}`)
    } catch (error) {
      console.error('Upload failed:', error)
      setUploadProgress(0)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Project Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload a new log package or restore a project from previously uploaded packages
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab 
            icon={<CloudUploadIcon />} 
            label="Upload New Project" 
            iconPosition="start"
          />
          <Tab 
            icon={<RestoreIcon />} 
            label="Restore Project" 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              {/* Upload Tab Content */}
              {activeTab === 0 && (
                <form onSubmit={handleSubmit}>
                {/* Project Details */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    Project Details
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Project Name"
                        value={projectName}
                        onChange={(e) => setProjectName(e.target.value)}
                        required
                        placeholder="Enter a descriptive name for your project"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Description (Optional)"
                        value={projectDescription}
                        onChange={(e) => setProjectDescription(e.target.value)}
                        multiline
                        rows={3}
                        placeholder="Describe the project, environment, or any relevant details"
                      />
                    </Grid>
                  </Grid>
                </Box>

                {/* File Upload */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    Log Package Upload
                  </Typography>
                  <Paper
                    {...getRootProps()}
                    sx={{
                      border: '2px dashed',
                      borderColor: isDragActive ? 'primary.main' : 'grey.300',
                      borderRadius: 2,
                      p: 4,
                      textAlign: 'center',
                      cursor: 'pointer',
                      backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                      '&:hover': {
                        borderColor: 'primary.main',
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <input {...getInputProps()} />
                    <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      {isDragActive ? 'Drop the file here' : 'Drag & drop a log package here'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      or click to select a file
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Supported formats: .tar, .tar.gz, .tgz
                    </Typography>
                  </Paper>
                </Box>

                {/* Selected File Info */}
                {selectedFile && (
                  <Box sx={{ mb: 4 }}>
                    <Paper sx={{ p: 2, backgroundColor: 'success.light' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <DescriptionIcon color="success" />
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle2" fontWeight="medium">
                            {selectedFile.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Size: {formatFileSize(selectedFile.size)} ({selectedFile.size} bytes)
                          </Typography>
                        </Box>
                        <Chip label="Ready to upload" color="success" size="small" />
                      </Box>
                    </Paper>
                  </Box>
                )}

                {/* Upload Progress */}
                {loading && (
                  <Box sx={{ mb: 4 }}>
                    <Typography variant="body2" gutterBottom>
                      Uploading project...
                    </Typography>
                    <LinearProgress variant="determinate" value={uploadProgress} />
                  </Box>
                )}

                {/* Error Display */}
                {error && (
                  <Alert severity="error" sx={{ mb: 4 }}>
                    <Typography variant="body2" gutterBottom>
                      Upload failed: {error}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Please check your file size (max 100MB) and try again. If the problem persists, try a smaller file or check your network connection.
                    </Typography>
                  </Alert>
                )}

                {/* Submit Button */}
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/')}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={!projectName.trim() || !selectedFile || loading}
                    startIcon={<CloudUploadIcon />}
                    onClick={() => console.log('Upload button clicked', { 
                      projectName: projectName.trim(), 
                      selectedFile: !!selectedFile, 
                      loading,
                      projectNameLength: projectName.length,
                      selectedFileName: selectedFile?.name
                    })}
                  >
                    {loading ? 'Uploading...' : 'Upload Project'}
                  </Button>
                </Box>
                
                {/* Debug Info */}
                <Box sx={{ mt: 2, p: 2, backgroundColor: 'grey.100', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Debug Info: projectName="{projectName}" (length: {projectName.length}), 
                    selectedFile: {selectedFile ? selectedFile.name : 'none'}, 
                    loading: {loading.toString()}, 
                    buttonDisabled: {(!projectName.trim() || !selectedFile || loading).toString()}
                  </Typography>
                </Box>
              </form>
              )}

              {/* Restoration Tab Content */}
              {activeTab === 1 && (
                <Box>
                  {/* Project Details */}
                  <Box sx={{ mb: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      Project Details
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Project Name"
                          value={projectName}
                          onChange={(e) => setProjectName(e.target.value)}
                          required
                          placeholder="Enter a descriptive name for your restored project"
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Description (Optional)"
                          value={projectDescription}
                          onChange={(e) => setProjectDescription(e.target.value)}
                          multiline
                          rows={3}
                          placeholder="Describe the project, environment, or any relevant details"
                        />
                      </Grid>
                    </Grid>
                  </Box>

                  {/* Available Packages */}
                  <Box sx={{ mb: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        Available Packages
                      </Typography>
                      <Tooltip title="Refresh packages">
                        <IconButton onClick={loadAvailablePackages} size="small">
                          <RefreshIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>

                    {restoreError && (
                      <Alert severity="error" sx={{ mb: 2 }}>
                        {restoreError}
                      </Alert>
                    )}

                    {availablePackages.length === 0 ? (
                      <Paper sx={{ p: 3, textAlign: 'center' }}>
                        <Typography variant="body1" color="text.secondary">
                          No packages available for restoration
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          Upload packages first to enable restoration
                        </Typography>
                      </Paper>
                    ) : (
                      <TableContainer component={Paper}>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Select</TableCell>
                              <TableCell>Filename</TableCell>
                              <TableCell>Size</TableCell>
                              <TableCell>Uploaded</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {availablePackages.map((pkg) => (
                              <TableRow 
                                key={pkg.filename}
                                hover
                                selected={selectedPackage === pkg.filename}
                                onClick={() => setSelectedPackage(pkg.filename)}
                                sx={{ cursor: 'pointer' }}
                              >
                                <TableCell>
                                  <input
                                    type="radio"
                                    checked={selectedPackage === pkg.filename}
                                    onChange={() => setSelectedPackage(pkg.filename)}
                                  />
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                    {pkg.filename}
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2">
                                    {pkg.size_mb} MB
                                  </Typography>
                                </TableCell>
                                <TableCell>
                                  <Typography variant="body2">
                                    {new Date(pkg.uploaded_at).toLocaleString()}
                                  </Typography>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </Box>

                  {/* Restore Button */}
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      variant="contained"
                      size="large"
                      onClick={handleRestoreProject}
                      disabled={!selectedPackage || !projectName.trim() || restoreLoading}
                      startIcon={<RestoreIcon />}
                    >
                      {restoreLoading ? 'Restoring...' : 'Restore Project'}
                    </Button>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Instructions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              {activeTab === 0 ? (
                <>
                  <Typography variant="h6" gutterBottom>
                    Upload Instructions
                  </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Supported Formats:
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Chip label=".tar" size="small" variant="outlined" />
                  <Chip label=".tar.gz" size="small" variant="outlined" />
                  <Chip label=".tgz" size="small" variant="outlined" />
                </Box>
              </Box>

              <Typography variant="subtitle2" gutterBottom>
                Package Structure:
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Your log package should contain syslog files from prplOS LCM applications. 
                The system will automatically detect and analyze applications within subdirectories.
              </Typography>

              <Typography variant="subtitle2" gutterBottom>
                File Size Limits:
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Maximum file size: 100MB
              </Typography>

              <Typography variant="subtitle2" gutterBottom>
                Processing Time:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Analysis time depends on the size and complexity of your log package. 
                You'll be notified when processing is complete.
              </Typography>
                </>
              ) : (
                <>
                  <Typography variant="h6" gutterBottom>
                    Restoration Instructions
                  </Typography>
                  
                  <Typography variant="subtitle2" gutterBottom>
                    What is Restoration?
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Restoration allows you to recreate projects from previously uploaded log packages. 
                    This is useful when projects get corrupted or deleted during development.
                  </Typography>

                  <Typography variant="subtitle2" gutterBottom>
                    How it Works:
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    1. Select a package from the available list<br/>
                    2. Enter a new project name<br/>
                    3. The system will extract and process the package again
                  </Typography>

                  <Typography variant="subtitle2" gutterBottom>
                    Benefits:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    • Quick project recovery<br/>
                    • No need to re-upload large files<br/>
                    • Preserves original package for future use
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default ProjectUpload
