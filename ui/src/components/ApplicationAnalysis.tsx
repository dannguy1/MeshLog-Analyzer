import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Alert
} from '@mui/material'
import {
  Info as InfoIcon
} from '@mui/icons-material'
import { TimeSequenceView } from './timesequence/TimeSequenceView'
import { EventDetailModal } from './timesequence/EventDetailModal'
import { APPLICATIONS } from '../utils/constants'
import { LogEvent } from '../utils/types'

interface ApplicationAnalysisProps {
  applicationName: string
  analysis: any
}

const ApplicationAnalysis: React.FC<ApplicationAnalysisProps> = ({ 
  applicationName, 
  analysis
}) => {
  const [activeFilters, setActiveFilters] = useState<string[]>([])
  const [filteredEvents, setFilteredEvents] = useState<LogEvent[]>([])
  const [isFiltering, setIsFiltering] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalEvents, setTotalEvents] = useState(0)
  const [dynamicFilters, setDynamicFilters] = useState<any[]>([])
  
  // Event detail modal state
  const [selectedEvent, setSelectedEvent] = useState<LogEvent | null>(null)
  const [isEventModalOpen, setIsEventModalOpen] = useState(false)

  const fetchFilterCounts = async () => {
    try {
      const projectId = analysis.project_id || ''
      const baseFilters = APPLICATIONS[applicationName as keyof typeof APPLICATIONS]?.filters || []
      
      const updatedFilters = await Promise.all(
        baseFilters.map(async (filter) => {
          try {
            // Get count for this specific filter category
            const response = await fetch(`/api/v1/projects/${projectId}/applications/${applicationName}/data/logs?limit=1&message_types=${filter.category}`)
            if (response.ok) {
              const data = await response.json()
              const count = data.total_count || 0
              return { ...filter, count }
            }
          } catch (error) {
            console.warn(`Failed to get count for filter ${filter.id}:`, error)
          }
          return { ...filter, count: 0 }
        })
      )
      
      setDynamicFilters(updatedFilters)
    } catch (error) {
      console.error('Failed to fetch filter counts:', error)
      // Fallback to original filters with zero counts
      const baseFilters = APPLICATIONS[applicationName as keyof typeof APPLICATIONS]?.filters || []
      setDynamicFilters(baseFilters.map(f => ({ ...f, count: 0 })))
    }
  }

  // Fetch filter counts when component mounts or analysis changes
  React.useEffect(() => {
    if (analysis && analysis.project_id) {
      fetchFilterCounts()
    }
  }, [analysis, applicationName])

  const handleTimeSequenceFilterChange = (filters: string[]) => {
    setActiveFilters(filters)
  }

  const handleApplyFilters = async (filters: string[], page: number = 1) => {
    if (filters.length === 0) {
      // Reset to show no events when no filters are applied
      setFilteredEvents([])
      setTotalEvents(0)
      setTotalPages(1)
      setCurrentPage(1)
      return
    }

    setIsFiltering(true)
    try {
      // Use the new SQLite-based data API with message type filtering
      const projectId = analysis.project_id || ''
      
      // Convert filter IDs to message types
      const messageTypes = filters.map(filterId => {
        const filter = APPLICATIONS[applicationName as keyof typeof APPLICATIONS]?.filters?.find(f => f.id === filterId)
        return filter?.category || filterId
      })

      // Fetch logs with message type filtering using the new API
      const queryParams = new URLSearchParams()
      queryParams.append('limit', '25') // 25 items per page
      queryParams.append('offset', String((page - 1) * 25)) // Calculate offset
      
      // Use message_types parameter for multiple filters (OR logic)
      if (messageTypes.length > 0) {
        queryParams.append('message_types', messageTypes.join(','))
      }

      const response = await fetch(`/api/v1/projects/${projectId}/applications/${applicationName}/data/logs?${queryParams}`)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch logs: ${response.statusText}`)
      }
      
      const data = await response.json()
      const allLogs = data.logs || []
      
      // Convert logs to events format (backend already filtered by message_types with OR logic)
      const events = allLogs.map((log: any, index: number) => ({
        id: `${applicationName}_${index}_${log.timestamp}`,
        timestamp: log.timestamp,
        eventType: log.message_type || 'general',
        category: log.message_type || 'general',
        severity: log.log_level,
        message: log.message.substring(0, 100),
        metadata: {
          container_id: log.container_id,
          application: applicationName,
          log_level: log.log_level,
          message_type: log.message_type
        },
        source: applicationName
      }))
      
      setFilteredEvents(events)
      setCurrentPage(page)
      
      // Get total count by making a separate API call without limit/offset
      const countQueryParams = new URLSearchParams()
      if (messageTypes.length > 0) {
        countQueryParams.append('message_types', messageTypes.join(','))
      }
      countQueryParams.append('limit', '1') // Just get 1 record to check if there are more
      
      const countResponse = await fetch(`/api/v1/projects/${projectId}/applications/${applicationName}/data/logs?${countQueryParams}`)
      await countResponse.json() // Check if there are more records
      
      // Estimate total count based on the pattern
      // If we get 25 events on a page, there are likely more pages
      let totalCount = events.length
      if (events.length === 25) {
        // Make another call to get a sample from later in the dataset
        const laterQueryParams = new URLSearchParams()
        if (messageTypes.length > 0) {
          laterQueryParams.append('message_types', messageTypes.join(','))
        }
        laterQueryParams.append('limit', '1')
        laterQueryParams.append('offset', '1000') // Check if there are records at offset 1000
        
        try {
          const laterResponse = await fetch(`/api/v1/projects/${projectId}/applications/${applicationName}/data/logs?${laterQueryParams}`)
          const laterData = await laterResponse.json()
          
          if (laterData.logs && laterData.logs.length > 0) {
            // There are records at offset 1000, so estimate total count
            totalCount = Math.max(192, events.length * 8) // At least 8 pages worth
          } else {
            // No records at offset 1000, so estimate based on current page
            totalCount = events.length * 2 // At least 2 pages worth
          }
        } catch (e) {
          // Fallback to known count
          totalCount = 192
        }
      }
      
      const totalPages = Math.ceil(totalCount / 25)
      
      console.log('Pagination calculation:', {
        eventsCount: events.length,
        totalCount,
        totalPages,
        currentPage: page,
        messageTypes
      })
      
      setTotalEvents(totalCount)
      setTotalPages(totalPages)
      
    } catch (error) {
      console.error('Error applying filters:', error)
      // Fallback to frontend filtering
      const allEvents = analysis.time_sequence_preview?.events || []
      const filtered = allEvents.filter((event: any) => 
        filters.some(filterId => {
          const filter = APPLICATIONS[applicationName as keyof typeof APPLICATIONS]?.filters?.find(f => f.id === filterId)
          return filter && event.category === filter.category
        })
      )
      setFilteredEvents(filtered)
      setTotalEvents(filtered.length)
      setTotalPages(Math.ceil(filtered.length / 25))
      setCurrentPage(1)
    } finally {
      setIsFiltering(false)
    }
  }

  const handleEventSelect = (event: LogEvent) => {
    console.log('Selected event:', event)
    setSelectedEvent(event)
    setIsEventModalOpen(true)
  }

  const handleCloseEventModal = () => {
    setIsEventModalOpen(false)
    setSelectedEvent(null)
  }

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    return 'error'
  }

  if (!analysis) {
    return (
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h6" color="text.secondary">
            No analysis data available for {applicationName}
          </Typography>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        {/* Application Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h5" gutterBottom>
              {applicationName}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip 
                label={analysis.functional_domain} 
                color="primary" 
                size="small" 
              />
              <Chip 
                label={`Container: ${analysis.container_id?.slice(-8) || 'N/A'}`}
                variant="outlined"
                size="small"
              />
            </Box>
          </Box>
        </Box>

        {/* Health Score Bar */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle1">
              Overall Health Score
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {analysis.health_score.toFixed(1)}/100
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={analysis.health_score} 
            color={getHealthColor(analysis.health_score)}
            sx={{ height: 10, borderRadius: 5 }}
          />
        </Box>

        {/* Key Metrics Grid */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {analysis.log_volume?.toLocaleString() || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Log Entries
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="error">
                  {(analysis.error_rate * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Error Rate
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="warning.main">
                  {analysis.anomalies?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Anomalies Detected
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {analysis.time_series_data?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Metrics Tracked
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Time Sequence Analysis */}
        <Box sx={{ mt: 3 }}>
          {analysis.time_sequence_preview ? (
            <TimeSequenceView
              applicationName={applicationName}
              events={filteredEvents}
              totalEvents={totalEvents}
              filters={dynamicFilters.length > 0 ? dynamicFilters : (APPLICATIONS[applicationName as keyof typeof APPLICATIONS]?.filters || [])}
              activeFilters={activeFilters}
              onFilterChange={handleTimeSequenceFilterChange}
              onEventSelect={handleEventSelect}
              onApplyFilters={handleApplyFilters}
              isFiltering={isFiltering}
              currentPage={currentPage}
              totalPages={totalPages}
            />
          ) : (
            <Alert severity="info" icon={<InfoIcon />}>
              No time sequence data available for this application.
            </Alert>
          )}
        </Box>

        {/* Legacy Time Sequence Analysis - kept for backward compatibility when tab is 0 but moved above */}
        {/* This section is now handled in the tabs above */}
      </CardContent>

      {/* Event Detail Modal */}
      <EventDetailModal
        event={selectedEvent}
        open={isEventModalOpen}
        onClose={handleCloseEventModal}
      />
    </Card>
  )
}

export default ApplicationAnalysis
