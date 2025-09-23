import React from 'react'
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Divider,
  Pagination
} from '@mui/material'
import { LogEvent } from '../../utils/types'

interface EventTimelineProps {
  events: LogEvent[]
  onEventClick?: (event: LogEvent) => void
  selectedEvent?: LogEvent
  maxHeight?: number
  currentPage?: number
  totalPages?: number
  totalEvents?: number
  onPageChange?: (page: number) => void
  isFiltering?: boolean
}

export const EventTimeline: React.FC<EventTimelineProps> = ({
  events,
  onEventClick,
  selectedEvent,
  maxHeight = 600,
  currentPage = 1,
  totalPages = 1,
  totalEvents = 0,
  onPageChange,
  isFiltering = false
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

  const handlePageChange = (_event: React.ChangeEvent<unknown>, page: number) => {
    if (onPageChange) {
      onPageChange(page)
    }
  }

  return (
    <Box sx={{ height: maxHeight, display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          Event Timeline
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {events.length} events on page {currentPage} of {totalPages} ({totalEvents} total)
        </Typography>
      </Box>
      
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
      
      <List sx={{ p: 0 }}>
        {events.map((event, index) => (
          <React.Fragment key={event.id}>
            <ListItem
              sx={{
                cursor: onEventClick ? 'pointer' : 'default',
                backgroundColor: selectedEvent?.id === event.id ? 'action.selected' : 'transparent',
                border: selectedEvent?.id === event.id ? 1 : 0,
                borderColor: 'primary.main',
                borderRadius: 1,
                mb: 1,
                '&:hover': {
                  backgroundColor: onEventClick ? 'action.hover' : 'transparent'
                }
              }}
              onClick={() => onEventClick?.(event)}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    backgroundColor: getSeverityColor(event.severity),
                    mr: 1
                  }}
                />
              </ListItemIcon>
              
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" fontWeight="medium">
                      {event.eventType}
                    </Typography>
                    <Chip
                      label={event.category}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '0.7rem' }}
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {formatTimestamp(event.timestamp)}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {event.message}
                    </Typography>
                    {event.metadata && Object.keys(event.metadata).length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Source: {event.source}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                }
              />
              
              <Chip
                label={event.severity}
                size="small"
                sx={{
                  backgroundColor: getSeverityColor(event.severity),
                  color: 'white',
                  fontSize: '0.7rem'
                }}
              />
            </ListItem>
            
            {index < events.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
      
        {events.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No events found in the selected time range
            </Typography>
          </Box>
        )}
      </Box>

      {/* Pagination */}
      {totalPages > 1 && onPageChange && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', display: 'flex', justifyContent: 'center' }}>
          <Pagination
            count={totalPages}
            page={currentPage}
            onChange={handlePageChange}
            color="primary"
            disabled={isFiltering}
          />
        </Box>
      )}
    </Box>
  )
}
