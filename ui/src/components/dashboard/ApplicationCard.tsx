import React from 'react';
import { Card, CardContent, Typography, Box, Grid, Chip, Button } from '@mui/material';
import { Application } from '../../utils/types';
import { HealthScore } from '../common/HealthScore';

interface TimeSequencePreview {
  recentEvents: Array<{
    timestamp: string;
    eventType: string;
    severity: 'info' | 'warning' | 'error' | 'critical';
    message: string;
  }>;
  eventCount: number;
  timeRange: { start: string; end: string };
}

interface ApplicationCardProps {
  application: Application;
  onSelect: (appName: string) => void;
  onViewTimeSequence?: (appName: string) => void;
  timeSequenceData?: TimeSequencePreview;
  variant?: 'compact' | 'detailed';
}

export const ApplicationCard: React.FC<ApplicationCardProps> = ({
  application,
  onSelect,
  onViewTimeSequence,
  timeSequenceData,
  variant = 'detailed'
}) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#d32f2f'
      case 'error': return '#f44336'
      case 'warning': return '#ff9800'
      default: return '#2196f3'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }
  return (
    <Card
      sx={{
        cursor: 'pointer',
        '&:hover': { boxShadow: 3 },
        height: variant === 'compact' ? 180 : 240,
        transition: 'box-shadow 0.2s ease-in-out',
        // Responsive design according to spec
        width: {
          xs: '100%',      // Mobile: < 768px - Single column
          sm: '100%',      // Tablet: 768px - 1024px - Single column
          md: '100%',      // Desktop: > 1024px - Grid layout
          lg: '100%'       // Large Desktop: > 1440px - Grid layout
        }
      }}
      onClick={() => onSelect(application.name)}
      role="button"
      tabIndex={0}
      aria-label={`Application ${application.name} with health score ${application.healthScore} out of 100`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onSelect(application.name)
        }
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" component="div">
            {application.name}
          </Typography>
          <Chip
            label={application.functionalDomain}
            color="primary"
            size="small"
          />
        </Box>

        <HealthScore score={application.healthScore} size="large" />

        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={6}>
            <Typography variant="h4" color="primary">
              {application.logVolume.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Log Entries
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="h4" color="error">
              {(application.errorRate * 100).toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Error Rate
            </Typography>
          </Grid>
        </Grid>

        {timeSequenceData && variant === 'detailed' && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Recent Events ({timeSequenceData.eventCount})
            </Typography>
            <Box sx={{ maxHeight: 80, overflow: 'hidden' }}>
              {timeSequenceData.recentEvents.slice(0, 3).map((event, index) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: getSeverityColor(event.severity),
                      mr: 1
                    }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {formatTimestamp(event.timestamp)}: {event.message}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>
        )}

        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
          <Button
            size="small"
            variant="outlined"
            onClick={(e) => {
              e.stopPropagation();
              onSelect(application.name);
            }}
          >
            View Details
          </Button>
          {onViewTimeSequence && (
            <Button
              size="small"
              variant="outlined"
              onClick={(e) => {
                e.stopPropagation();
                onViewTimeSequence(application.name);
              }}
            >
              Time Sequence
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
