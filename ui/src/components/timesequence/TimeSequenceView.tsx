import React, { useState } from 'react';
import { Box, Typography, Chip, IconButton, FormControlLabel, Checkbox, Button, Pagination } from '@mui/material';
import { ChevronLeft, ChevronRight, FilterList } from '@mui/icons-material';
import { LogEvent, ApplicationFilter } from '../../utils/types';
import { SEVERITY_COLORS } from '../../utils/constants';

interface TimeSequenceViewProps {
  applicationName: string;
  events: LogEvent[];
  totalEvents: number;
  filters: ApplicationFilter[];
  activeFilters: string[];
  onFilterChange: (filters: string[]) => void;
  onEventSelect: (event: LogEvent) => void;
  onApplyFilters: (filters: string[], page?: number) => void;
  isFiltering?: boolean;
  currentPage?: number;
  totalPages?: number;
}

export const TimeSequenceView: React.FC<TimeSequenceViewProps> = ({
  applicationName,
  events,
  totalEvents,
  filters,
  activeFilters,
  onFilterChange,
  onEventSelect,
  onApplyFilters,
  isFiltering = false,
  currentPage = 1,
  totalPages = 1
}) => {
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<LogEvent | undefined>();

  const handleEventClick = (event: LogEvent) => {
    setSelectedEvent(event);
    onEventSelect(event);
  };

  const getSeverityColor = (severity: string) => {
    return SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS] || SEVERITY_COLORS.info;
  };

  const handleFilterToggle = (filterId: string) => {
    const newFilters = activeFilters.includes(filterId)
      ? activeFilters.filter(id => id !== filterId)
      : [...activeFilters, filterId];
    onFilterChange(newFilters);
  };

  const handlePageChange = (_event: React.ChangeEvent<unknown>, page: number) => {
    onApplyFilters(activeFilters, page);
  };

  return (
    <Box sx={{ display: 'flex', height: '600px', border: 1, borderColor: 'divider' }}>
      {/* Filter Panel */}
      <Box sx={{ width: isFilterPanelOpen ? 300 : 50, borderRight: 1, borderColor: 'divider' }}>
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ flex: 1 }}>
              Filters
            </Typography>
            <IconButton onClick={() => setIsFilterPanelOpen(!isFilterPanelOpen)}>
              {isFilterPanelOpen ? <ChevronLeft /> : <ChevronRight />}
            </IconButton>
          </Box>

          {isFilterPanelOpen && (
            <Box>
              {filters.map((filter) => (
                <Box key={filter.id} sx={{ mb: 1 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={activeFilters.includes(filter.id)}
                        onChange={() => handleFilterToggle(filter.id)}
                        sx={{
                          color: filter.color,
                          '&.Mui-checked': {
                            color: filter.color,
                          },
                        }}
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2">
                          {filter.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {filter.count} events
                        </Typography>
                      </Box>
                    }
                  />
                </Box>
              ))}
              
              {/* Apply Filters Button */}
              <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<FilterList />}
                  onClick={() => onApplyFilters(activeFilters)}
                  disabled={isFiltering}
                  sx={{ mb: 1 }}
                >
                  {isFiltering ? 'Applying...' : (activeFilters.length === 0 ? 'Clear All Events' : 'Apply Filters')}
                </Button>
                <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', display: 'block' }}>
                  {activeFilters.length === 0 
                    ? 'Select filters to apply (or click to clear all)' 
                    : `${activeFilters.length} filter${activeFilters.length === 1 ? '' : 's'} selected`
                  }
                </Typography>
              </Box>
            </Box>
          )}
        </Box>
      </Box>

      {/* Timeline */}
      <Box sx={{ flex: 1 }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" gutterBottom>
            Event Timeline - {applicationName}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {events.length} events on page {currentPage} of {totalPages} ({totalEvents} total)
          </Typography>
        </Box>

        <Box sx={{ p: 2, height: 'calc(100% - 160px)', overflow: 'auto' }}>
          {events.map((event) => (
            <Box
              key={event.id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                p: 1,
                mb: 1,
                border: selectedEvent?.id === event.id ? 2 : 1,
                borderColor: selectedEvent?.id === event.id ? 'primary.main' : 'divider',
                borderRadius: 1,
                cursor: 'pointer',
                '&:hover': { bgcolor: 'action.hover' },
                transition: 'all 0.2s ease-in-out'
              }}
              onClick={() => handleEventClick(event)}
            >
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  bgcolor: getSeverityColor(event.severity),
                  mr: 2,
                  flexShrink: 0
                }}
              />
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" fontWeight="medium">
                  {event.eventType}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(event.timestamp).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {event.message}
                </Typography>
              </Box>
              <Chip
                label={event.category}
                size="small"
                variant="outlined"
                sx={{ ml: 1 }}
              />
            </Box>
          ))}
        </Box>

        {/* Pagination */}
        {totalPages >= 1 && (
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', display: 'flex', justifyContent: 'center' }}>
            <Pagination
              count={totalPages}
              page={currentPage}
              onChange={handlePageChange}
              color="primary"
              disabled={isFiltering}
              showFirstButton
              showLastButton
            />
          </Box>
        )}
      </Box>
    </Box>
  );
};
