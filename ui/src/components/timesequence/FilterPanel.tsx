import React from 'react'
import {
  Box,
  Typography,
  FormControlLabel,
  Checkbox,
  Chip,
  Button,
  Divider,
  IconButton,
  Collapse
} from '@mui/material'
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  FilterList as FilterListIcon,
  Clear as ClearIcon
} from '@mui/icons-material'
import { ApplicationFilter } from '../../utils/types'

interface FilterPanelProps {
  filters: ApplicationFilter[]
  activeFilters: string[]
  onFilterChange: (filters: string[]) => void
  isOpen: boolean
  onToggle: () => void
  onClearAll?: () => void
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  activeFilters,
  onFilterChange,
  isOpen,
  onToggle,
  onClearAll
}) => {
  const handleFilterToggle = (filterId: string) => {
    const newFilters = activeFilters.includes(filterId)
      ? activeFilters.filter(id => id !== filterId)
      : [...activeFilters, filterId]
    onFilterChange(newFilters)
  }

  const handleSelectAll = () => {
    onFilterChange(filters.map(f => f.id))
  }

  const handleClearAll = () => {
    onFilterChange([])
    onClearAll?.()
  }

  const getFilterCount = (filterId: string) => {
    const filter = filters.find(f => f.id === filterId)
    return filter?.count || 0
  }

  const totalEvents = filters.reduce((sum, filter) => sum + filter.count, 0)
  const activeEvents = activeFilters.reduce((sum, filterId) => sum + getFilterCount(filterId), 0)

  return (
    <Box sx={{ borderRight: 1, borderColor: 'divider', height: '100%' }}>
      {/* Header */}
      <Box sx={{ 
        p: 2, 
        borderBottom: 1, 
        borderColor: 'divider',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterListIcon color="action" />
          <Typography variant="h6">
            Filters
          </Typography>
        </Box>
        <IconButton onClick={onToggle} size="small">
          {isOpen ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Box>

      <Collapse in={isOpen}>
        {/* Summary */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Showing {activeEvents} of {totalEvents} events
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
            <Button
              size="small"
              variant="outlined"
              onClick={handleSelectAll}
              disabled={activeFilters.length === filters.length}
            >
              Select All
            </Button>
            <Button
              size="small"
              variant="outlined"
              onClick={handleClearAll}
              disabled={activeFilters.length === 0}
              startIcon={<ClearIcon />}
            >
              Clear All
            </Button>
          </Box>
        </Box>

        {/* Filter List */}
        <Box sx={{ p: 2, maxHeight: 400, overflow: 'auto' }}>
          {filters.map((filter) => (
            <Box key={filter.id} sx={{ mb: 2 }}>
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
                  <Box sx={{ width: '100%' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" fontWeight="medium">
                        {filter.name}
                      </Typography>
                      <Chip
                        label={filter.count}
                        size="small"
                        sx={{ 
                          backgroundColor: filter.color,
                          color: 'white',
                          fontSize: '0.7rem'
                        }}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {filter.description}
                    </Typography>
                    {filter.patterns && filter.patterns.length > 0 && (
                      <Box sx={{ mt: 0.5 }}>
                        {filter.patterns.slice(0, 2).map((pattern, index) => (
                          <Chip
                            key={index}
                            label={pattern}
                            size="small"
                            variant="outlined"
                            sx={{ 
                              fontSize: '0.6rem',
                              mr: 0.5,
                              mb: 0.5
                            }}
                          />
                        ))}
                        {filter.patterns.length > 2 && (
                          <Typography variant="caption" color="text.secondary">
                            +{filter.patterns.length - 2} more patterns
                          </Typography>
                        )}
                      </Box>
                    )}
                  </Box>
                }
                sx={{ 
                  width: '100%',
                  alignItems: 'flex-start',
                  '& .MuiFormControlLabel-label': {
                    width: '100%'
                  }
                }}
              />
              <Divider sx={{ mt: 1 }} />
            </Box>
          ))}
        </Box>

        {/* Active Filters Summary */}
        {activeFilters.length > 0 && (
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle2" gutterBottom>
              Active Filters ({activeFilters.length})
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {activeFilters.map((filterId) => {
                const filter = filters.find(f => f.id === filterId)
                return filter ? (
                  <Chip
                    key={filterId}
                    label={filter.name}
                    size="small"
                    onDelete={() => handleFilterToggle(filterId)}
                    sx={{ 
                      backgroundColor: filter.color,
                      color: 'white',
                      fontSize: '0.7rem'
                    }}
                  />
                ) : null
              })}
            </Box>
          </Box>
        )}
      </Collapse>
    </Box>
  )
}
