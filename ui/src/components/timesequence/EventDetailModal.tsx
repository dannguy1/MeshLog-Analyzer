import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Paper,
  Grid
} from '@mui/material';
import { LogEvent } from '../../utils/types';
import { SEVERITY_COLORS } from '../../utils/constants';

interface EventDetailModalProps {
  event: LogEvent | null;
  open: boolean;
  onClose: () => void;
}

export const EventDetailModal: React.FC<EventDetailModalProps> = ({
  event,
  open,
  onClose
}) => {
  if (!event) return null;

  const getSeverityColor = (severity: string) => {
    return SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS] || SEVERITY_COLORS.info;
  };

  const formatValue = (value: any): string => {
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { maxHeight: '80vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              width: 16,
              height: 16,
              borderRadius: '50%',
              bgcolor: getSeverityColor(event.severity),
              flexShrink: 0
            }}
          />
          <Typography variant="h6" component="span">
            Event Details
          </Typography>
          <Chip
            label={event.severity}
            size="small"
            sx={{
              bgcolor: getSeverityColor(event.severity),
              color: 'white',
              fontWeight: 'bold'
            }}
          />
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Grid container spacing={3}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom color="primary">
                Basic Information
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" fontWeight="medium">ID:</Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{event.id}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" fontWeight="medium">Timestamp:</Typography>
                  <Typography variant="body2">{new Date(event.timestamp).toLocaleString()}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" fontWeight="medium">Event Type:</Typography>
                  <Typography variant="body2">{event.eventType}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" fontWeight="medium">Category:</Typography>
                  <Chip label={event.category} size="small" variant="outlined" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" fontWeight="medium">Severity:</Typography>
                  <Chip
                    label={event.severity}
                    size="small"
                    sx={{
                      bgcolor: getSeverityColor(event.severity),
                      color: 'white'
                    }}
                  />
                </Box>
              </Box>
            </Paper>
          </Grid>

          {/* Message */}
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom color="primary">
                Message
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  bgcolor: 'grey.50',
                  p: 1,
                  borderRadius: 1
                }}
              >
                {event.message}
              </Typography>
            </Paper>
          </Grid>

          {/* Source Information */}
          {event.source && (
            <Grid item xs={12}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom color="primary">
                  Source Information
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" fontWeight="medium">Source:</Typography>
                  <Typography variant="body2">{event.source}</Typography>
                </Box>
              </Paper>
            </Grid>
          )}

          {/* Metadata */}
          {event.metadata && Object.keys(event.metadata).length > 0 && (
            <Grid item xs={12}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom color="primary">
                  Metadata
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {Object.entries(event.metadata).map(([key, value]) => (
                    <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Typography variant="body2" fontWeight="medium" sx={{ minWidth: '120px' }}>
                        {key}:
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          fontFamily: 'monospace',
                          textAlign: 'right',
                          maxWidth: '300px',
                          overflow: 'auto'
                        }}
                      >
                        {formatValue(value)}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Paper>
            </Grid>
          )}

          {/* Raw Event Data */}
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom color="primary">
                Raw Event Data
              </Typography>
              <Box
                sx={{
                  bgcolor: 'grey.50',
                  p: 2,
                  borderRadius: 1,
                  maxHeight: '200px',
                  overflow: 'auto'
                }}
              >
                <Typography
                  variant="body2"
                  component="pre"
                  sx={{
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    margin: 0,
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  {JSON.stringify(event, null, 2)}
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};