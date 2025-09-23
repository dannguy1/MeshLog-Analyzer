import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  LinearProgress
} from '@mui/material'
import {
  Search as SearchIcon,
  ViewList as ViewListIcon,
  GridView as GridViewIcon
} from '@mui/icons-material'
import { ApplicationCard } from '../dashboard/ApplicationCard'
import { Application } from '../../utils/types'

interface ApplicationDiscoveryProps {
  applications: Application[]
  onApplicationSelect: (appName: string) => void
  onViewTimeSequence?: (appName: string) => void
  loading?: boolean
}

export const ApplicationDiscovery: React.FC<ApplicationDiscoveryProps> = ({
  applications,
  onApplicationSelect,
  onViewTimeSequence,
  loading = false
}) => {
  const [viewMode, setViewMode] = React.useState<'grid' | 'list'>('grid')
  const [searchTerm, setSearchTerm] = React.useState('')
  const [selectedDomain, setSelectedDomain] = React.useState<string>('all')

  const domains = ['all', ...Array.from(new Set(applications.map(app => app.functionalDomain)))]

  const filteredApplications = applications.filter(app => {
    const matchesSearch = app.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.functionalDomain.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesDomain = selectedDomain === 'all' || app.functionalDomain === selectedDomain
    return matchesSearch && matchesDomain
  })

  const getDomainStats = (domain: string) => {
    if (domain === 'all') return applications.length
    return applications.filter(app => app.functionalDomain === domain).length
  }

  const getAverageHealthScore = (domain: string) => {
    const domainApps = domain === 'all' 
      ? applications 
      : applications.filter(app => app.functionalDomain === domain)
    
    if (domainApps.length === 0) return 0
    return domainApps.reduce((sum, app) => sum + app.healthScore, 0) / domainApps.length
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">
          Discovered Applications ({applications.length})
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant={viewMode === 'grid' ? 'contained' : 'outlined'}
            size="small"
            onClick={() => setViewMode('grid')}
            startIcon={<GridViewIcon />}
          >
            Grid
          </Button>
          <Button
            variant={viewMode === 'list' ? 'contained' : 'outlined'}
            size="small"
            onClick={() => setViewMode('list')}
            startIcon={<ViewListIcon />}
          >
            List
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <SearchIcon color="action" />
                <input
                  type="text"
                  placeholder="Search applications..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    border: 'none',
                    outline: 'none',
                    fontSize: '1rem',
                    width: '100%',
                    padding: '8px'
                  }}
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {domains.map((domain) => (
                  <Chip
                    key={domain}
                    label={`${domain} (${getDomainStats(domain)})`}
                    variant={selectedDomain === domain ? 'filled' : 'outlined'}
                    color={selectedDomain === domain ? 'primary' : 'default'}
                    onClick={() => setSelectedDomain(domain)}
                    size="small"
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Domain Overview */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {domains.map((domain) => (
          <Grid item xs={12} sm={6} md={3} key={domain}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                border: selectedDomain === domain ? 2 : 1,
                borderColor: selectedDomain === domain ? 'primary.main' : 'divider'
              }}
              onClick={() => setSelectedDomain(domain)}
            >
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {domain === 'all' ? 'All Domains' : domain}
                </Typography>
                <Typography variant="h4" color="primary" gutterBottom>
                  {getDomainStats(domain)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Applications
                </Typography>
                {domain !== 'all' && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Avg Health: {getAverageHealthScore(domain).toFixed(1)}/100
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Applications Grid/List */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <LinearProgress sx={{ width: '100%', maxWidth: 400 }} />
        </Box>
      ) : (
        <Box>
          {filteredApplications.length > 0 ? (
            viewMode === 'grid' ? (
              <Grid container spacing={3}>
                {filteredApplications.map((app) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={app.name}>
                    <ApplicationCard
                      application={app}
                      onSelect={onApplicationSelect}
                      onViewTimeSequence={onViewTimeSequence}
                    />
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Card>
                <CardContent>
                  {filteredApplications.map((app, index) => (
                    <Box
                      key={app.name}
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        py: 2,
                        borderBottom: index < filteredApplications.length - 1 ? 1 : 0,
                        borderColor: 'divider',
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                      onClick={() => onApplicationSelect(app.name)}
                    >
                      <Box>
                        <Typography variant="h6">
                          {app.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {app.functionalDomain}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          {app.logVolume.toLocaleString()} logs
                        </Typography>
                        <Chip
                          label={`${app.healthScore.toFixed(0)}/100`}
                          color={app.healthScore >= 80 ? 'success' : app.healthScore >= 60 ? 'warning' : 'error'}
                          size="small"
                        />
                        {onViewTimeSequence && (
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={(e) => {
                              e.stopPropagation()
                              onViewTimeSequence(app.name)
                            }}
                          >
                            Time Sequence
                          </Button>
                        )}
                      </Box>
                    </Box>
                  ))}
                </CardContent>
              </Card>
            )
          ) : (
            <Card>
              <CardContent>
                <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  No applications found matching your criteria
                </Typography>
              </CardContent>
            </Card>
          )}
        </Box>
      )}
    </Box>
  )
}
