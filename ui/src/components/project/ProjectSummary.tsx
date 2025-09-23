import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Button,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  Storage as StorageIcon,
  Folder as FolderIcon,
  Schedule as ScheduleIcon,
  Apps as AppsIcon,
  Description as DescriptionIcon,
  Timeline as TimelineIcon,
  Analytics as AnalyticsIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Schedule as PendingIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { Project } from '../../utils/types';
import { APPLICATIONS } from '../../utils/constants';

interface ProjectSummaryProps {
  project: Project;
  onStartApplicationAnalysis?: (applicationName: string) => void;
  analysisLoading?: { [key: string]: boolean };
  onRefresh?: () => void;
  refreshLoading?: boolean;
  applicationAnalysisStatus?: { [key: string]: any };
}

export const ProjectSummary: React.FC<ProjectSummaryProps> = ({ 
  project, 
  onStartApplicationAnalysis,
  analysisLoading = {},
  onRefresh,
  refreshLoading = false,
  applicationAnalysisStatus = {}
}) => {
  const navigate = useNavigate();
  
  // Debug logging
  console.log('ProjectSummary props:', { 
    hasOnRefresh: !!onRefresh, 
    refreshLoading, 
    applicationsDetected: project.applications_detected?.length || 0 
  });
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getApplicationInfo = (appName: string) => {
    return APPLICATIONS[appName as keyof typeof APPLICATIONS] || {
      name: appName,
      domain: 'unknown',
      filters: []
    };
  };

  const getAnalysisStatusInfo = (appName: string) => {
    const status = applicationAnalysisStatus[appName];
    if (!status || !status.analysis_summary) {
      return { status: 'not_analyzed', icon: <PendingIcon />, color: 'default' };
    }
    
    const summary = status.analysis_summary;
    switch (summary.status) {
      case 'completed':
        return { 
          status: 'completed', 
          icon: <CheckIcon />, 
          color: 'success',
          logVolume: summary.log_volume,
          errorRate: summary.error_rate,
          healthScore: summary.health_score
        };
      case 'running':
        return { 
          status: 'running', 
          icon: <ScheduleIcon />, 
          color: 'warning' 
        };
      case 'failed':
        return { 
          status: 'failed', 
          icon: <ErrorIcon />, 
          color: 'error' 
        };
      default:
        return { 
          status: 'not_analyzed', 
          icon: <PendingIcon />, 
          color: 'default' 
        };
    }
  };

  const packageMetadata = project.package_metadata;
  const applicationsDetected = project.applications_detected || [];

  return (
    <Box sx={{ mb: 4 }}>
      {/* Log Package Summary */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h2">
              Log Package Summary
            </Typography>
          </Box>
          
          <Grid container spacing={3}>
            {/* File Information */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                  File Information
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <DescriptionIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Original Filename"
                      secondary={project.original_filename || 'N/A'}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <StorageIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary="File Size"
                      secondary={formatFileSize(project.file_size_bytes || project.fileSize || 0)}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <ScheduleIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Upload Date"
                      secondary={formatDate(project.created_at)}
                    />
                  </ListItem>
                </List>
              </Paper>
            </Grid>

            {/* Package Statistics */}
            {packageMetadata && (
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Package Statistics
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <FolderIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Total Containers"
                        secondary={packageMetadata.total_containers.toLocaleString()}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <DescriptionIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Log Files"
                        secondary={packageMetadata.total_log_files.toLocaleString()}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <StorageIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Log Data Size"
                        secondary={formatFileSize(packageMetadata.total_log_size_bytes)}
                      />
                    </ListItem>
                  </List>
                </Paper>
              </Grid>
            )}
          </Grid>

          {/* Time Range */}
          {packageMetadata && (packageMetadata.time_range_start || packageMetadata.time_range_end) && (
            <Box sx={{ mt: 2 }}>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TimelineIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                  Log Time Range
                </Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Start:</strong> {formatDate(packageMetadata.time_range_start)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>End:</strong> {formatDate(packageMetadata.time_range_end)}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Applications Discovery */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AppsIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h2">
              Applications Discovered
            </Typography>
            <Chip 
              label={`${applicationsDetected.length} applications`}
              color="primary"
              size="small"
              sx={{ ml: 2 }}
            />
            <Button
              variant="outlined"
              size="small"
              startIcon={refreshLoading ? <CircularProgress size={16} /> : <RefreshIcon />}
              onClick={onRefresh || (() => window.location.reload())}
              disabled={refreshLoading}
              sx={{ ml: 'auto' }}
            >
              {refreshLoading ? 'Refreshing...' : 'Refresh'}
            </Button>
          </Box>

          {applicationsDetected.length > 0 ? (
            <Grid container spacing={2}>
              {applicationsDetected.map((appName) => {
                const appInfo = getApplicationInfo(appName);
                const isLoading = analysisLoading[appName] || false;
                const analysisStatus = getAnalysisStatusInfo(appName);
                return (
                  <Grid item xs={12} sm={6} md={4} key={appName}>
                    <Paper sx={{ p: 2, border: 1, borderColor: 'divider' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                          {appName}
                        </Typography>
                        <Tooltip title={`Analysis Status: ${analysisStatus.status}`}>
                          <Chip
                            icon={analysisStatus.icon}
                            label={analysisStatus.status}
                            size="small"
                            color={analysisStatus.color as any}
                            variant="outlined"
                          />
                        </Tooltip>
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {appInfo.name}
                      </Typography>
                      <Chip 
                        label={appInfo.domain}
                        size="small"
                        color="secondary"
                        variant="outlined"
                        sx={{ mb: 2 }}
                      />
                      
                      {/* Analysis Metrics */}
                      {analysisStatus.status === 'completed' && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Log Volume: {analysisStatus.logVolume?.toLocaleString() || 'N/A'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Error Rate: {(analysisStatus.errorRate * 100)?.toFixed(2) || '0'}%
                          </Typography>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Health Score: {analysisStatus.healthScore?.toFixed(2) || 'N/A'}
                          </Typography>
                        </Box>
                      )}
                      
                      {/* Application Analysis Button */}
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={isLoading ? <CircularProgress size={16} /> : <AnalyticsIcon />}
                        onClick={() => {
                          if (onStartApplicationAnalysis) {
                            onStartApplicationAnalysis(appName);
                          } else {
                            navigate(`/analysis/${project.id}/${appName}`);
                          }
                        }}
                        disabled={isLoading}
                        fullWidth
                        sx={{ mt: 1 }}
                      >
                        {isLoading ? 'Analyzing...' : `Open ${appName} Analysis`}
                      </Button>
                    </Paper>
                  </Grid>
                );
              })}
            </Grid>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No applications detected in this log package.
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                This may indicate the package is still processing or contains no recognizable application logs.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};
