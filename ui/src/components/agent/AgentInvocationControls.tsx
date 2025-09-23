import React, { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  Chip,
  Grid,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  LinearProgress
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material'

// Agent Results Display Component - Simple HTML Rendering
const AgentResultsDisplay = ({ agentResults, applicationName }: { agentResults: any; applicationName: string }) => {
  if (!agentResults) return null

  // Extract capability analysis data if available
  const capabilityData = agentResults?.analysis_data?.client_capabilities || 
                        agentResults?.client_capabilities ||
                        agentResults?.capability_analysis

  return (
    <Box>
      {/* Agent Analysis Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          🤖 Agent Analysis Results
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Analysis performed by specialized agent for {applicationName}
        </Typography>
      </Box>

      {/* HTML Content - Direct Rendering */}
      {agentResults.html_content ? (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box
            sx={{
              '& .header': { 
                backgroundColor: '#f4f4f4', 
                padding: '20px', 
                borderRadius: '5px', 
                marginBottom: '20px' 
              },
              '& .summary': { 
                backgroundColor: '#e8f4f8', 
                padding: '15px', 
                borderRadius: '5px', 
                margin: '20px 0' 
              },
              '& .metrics': { 
                backgroundColor: '#f0f8e8', 
                padding: '15px', 
                borderRadius: '5px', 
                margin: '20px 0' 
              },
              '& .insights': { 
                backgroundColor: '#fff8e8', 
                padding: '15px', 
                borderRadius: '5px', 
                margin: '20px 0' 
              },
              '& .metric': { margin: '5px 0' },
              '& .success': { color: '#28a745' },
              '& .warning': { color: '#ffc107' },
              '& .error': { color: '#dc3545' },
              '& h1': { 
                fontSize: '1.5rem', 
                fontWeight: 'bold', 
                margin: '20px 0 10px 0',
                color: '#1976d2'
              },
              '& h2': { 
                fontSize: '1.25rem', 
                fontWeight: 'bold', 
                margin: '15px 0 8px 0',
                color: '#424242'
              },
              '& h3': { 
                fontSize: '1.1rem', 
                fontWeight: 'bold', 
                margin: '10px 0 5px 0' 
              },
              '& p': { margin: '5px 0' },
              '& div': { margin: '5px 0' }
            }}
            dangerouslySetInnerHTML={{ __html: agentResults.html_content }}
          />
        </Paper>
      ) : (
        // Fallback for non-HTML results
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Raw Analysis Data
          </Typography>
          <pre style={{ 
            whiteSpace: 'pre-wrap', 
            fontSize: '0.875rem', 
            maxHeight: '400px', 
            overflow: 'auto',
            backgroundColor: '#f5f5f5',
            padding: '16px',
            borderRadius: '4px'
          }}>
            {JSON.stringify(agentResults, null, 2)}
          </pre>
        </Paper>
      )}

      {/* 802.11k/v Capability Details - Accordion Style */}
      {capabilityData && (
        <Paper sx={{ p: 0 }}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">
                📡 802.11k/v Capability Analysis
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              {/* Overview Stats */}
              {capabilityData.overview && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                    Overview
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#e3f2fd', borderRadius: 1 }}>
                        <Typography variant="h4" color="primary">
                          {capabilityData.overview.total_clients_analyzed}
                        </Typography>
                        <Typography variant="caption">Total Clients</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#e8f5e8', borderRadius: 1 }}>
                        <Typography variant="h4" color="success.main">
                          {capabilityData.overview.k_support_percentage?.toFixed(1)}%
                        </Typography>
                        <Typography variant="caption">802.11k Support</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#fff3e0', borderRadius: 1 }}>
                        <Typography variant="h4" color="warning.main">
                          {capabilityData.overview.v_support_percentage?.toFixed(1)}%
                        </Typography>
                        <Typography variant="caption">802.11v Support</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#f3e5f5', borderRadius: 1 }}>
                        <Typography variant="h4" color="secondary.main">
                          {capabilityData.overview.fully_capable_percentage?.toFixed(1)}%
                        </Typography>
                        <Typography variant="caption">Fully Capable</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {/* Client Breakdown */}
              {capabilityData.client_breakdown && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                    Client Details
                  </Typography>
                  
                  {/* Fully Capable Clients */}
                  {capabilityData.client_breakdown.fully_capable_clients?.count > 0 && (
                    <Accordion sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>
                          ✅ Fully Capable Clients ({capabilityData.client_breakdown.fully_capable_clients.count})
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {capabilityData.client_breakdown.fully_capable_clients.clients.map((client: any, index: number) => (
                            <ListItem key={index}>
                              <ListItemText
                                primary={client.mac_address || `Client ${index + 1}`}
                                secondary={`802.11k: ${client.supports_802_11k ? 'Yes' : 'No'}, 802.11v: ${client.supports_802_11v ? 'Yes' : 'No'}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}

                  {/* 802.11k Only Clients */}
                  {capabilityData.client_breakdown.k_only_clients?.count > 0 && (
                    <Accordion sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>
                          📶 802.11k Only Clients ({capabilityData.client_breakdown.k_only_clients.count})
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {capabilityData.client_breakdown.k_only_clients.clients.map((client: any, index: number) => (
                            <ListItem key={index}>
                              <ListItemText
                                primary={client.mac_address || `Client ${index + 1}`}
                                secondary="Supports 802.11k neighbor reports but not 802.11v BSS transition"
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}

                  {/* 802.11v Only Clients */}
                  {capabilityData.client_breakdown.v_only_clients?.count > 0 && (
                    <Accordion sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>
                          🔄 802.11v Only Clients ({capabilityData.client_breakdown.v_only_clients.count})
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {capabilityData.client_breakdown.v_only_clients.clients.map((client: any, index: number) => (
                            <ListItem key={index}>
                              <ListItemText
                                primary={client.mac_address || `Client ${index + 1}`}
                                secondary="Supports 802.11v BSS transition but not 802.11k neighbor reports"
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}

                  {/* Legacy Clients */}
                  {capabilityData.client_breakdown.legacy_clients?.count > 0 && (
                    <Accordion sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>
                          ⚠️ Legacy Clients ({capabilityData.client_breakdown.legacy_clients.count})
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {capabilityData.client_breakdown.legacy_clients.clients.map((client: any, index: number) => (
                            <ListItem key={index}>
                              <ListItemText
                                primary={client.mac_address || `Client ${index + 1}`}
                                secondary="No 802.11k/v capabilities detected - requires manual steering"
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        </Paper>
      )}
    </Box>
  )
}

interface AgentInvocationControlsProps {
  projectId: string
  applicationName: string
  onAnalysisStarted?: (analysisId: string) => void
  onResultsReady?: (results: any) => void
}

interface Agent {
  name: string
  version: string
  description: string
  supported_log_types: string[]
  capabilities: string[]
}

interface AvailableApplication {
  application_name: string
  agent_type: string
  has_discovery_data: boolean
  ready_for_analysis: boolean
  container_count: number
  total_log_size_bytes: number
}

const AgentInvocationControls: React.FC<AgentInvocationControlsProps> = ({
  projectId,
  applicationName,
  onAnalysisStarted,
  onResultsReady
}) => {
  const [, setAvailableApplications] = useState<AvailableApplication[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [isStartingAnalysis, setIsStartingAnalysis] = useState(false)
  const [, setCurrentAnalysisId] = useState<string | null>(null)
  const [analysisStatus, setAnalysisStatus] = useState<any>(null)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  // Load agents and available applications on component mount
  useEffect(() => {
    loadAgents()
    loadAvailableApplications()
    checkForExistingResultsSilent()
  }, [projectId, applicationName])

  const loadAgents = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`/api/v1/projects/${projectId}/applications/${applicationName}/agent-analysis/agents`)
      const data = await response.json()
      
      if (data.agents && data.agents.length > 0) {
        // Auto-select appropriate agent based on application name
        const appropriateAgent = findAppropriateAgent(data.agents, applicationName)
        if (appropriateAgent) {
          setSelectedAgent(appropriateAgent)
        }
      }
    } catch (error) {
      console.error('Failed to load agents:', error)
      setError('Failed to load available agents')
    } finally {
      setIsLoading(false)
    }
  }

  const loadAvailableApplications = async () => {
    try {
      const response = await fetch(`/api/v1/agents/available-applications`)
      const data = await response.json()
      setAvailableApplications(data.applications || [])
    } catch (error) {
      console.error('Failed to load available applications:', error)
    }
  }

  const findAppropriateAgent = (agents: Agent[], appName: string): string => {
    // Auto-select agent based on application name
    const lowerAppName = appName.toLowerCase()
    console.log('🔍 Agent Selection Debug:', { appName, lowerAppName, availableAgents: agents.map(a => ({ name: a.name, agent_type: (a as any).agent_type })) })
    
    // Application to agent type mapping
    if (lowerAppName.includes('wnc-steer') || lowerAppName.includes('steer') || lowerAppName.includes('steering')) {
      // Look for WNC steering agent
      const steeringAgent = agents.find(agent => 
        agent.name.includes('steering') || 
        agent.name.includes('wnc-steering') ||
        (agent as any).agent_type === 'wnc-steering'
      )
      console.log('🎯 Steering Agent Search:', { found: !!steeringAgent, agent: steeringAgent })
      if (steeringAgent) return steeringAgent.name
    }
    
    if (lowerAppName.includes('wnc-acs') || lowerAppName.includes('acs')) {
      // Look for ACS agent when available
      const acsAgent = agents.find(agent => 
        agent.name.includes('acs') || 
        agent.name.includes('wnc-acs') ||
        (agent as any).agent_type === 'wnc-acs'
      )
      if (acsAgent) return acsAgent.name
    }
    
    if (lowerAppName.includes('otbr') || lowerAppName.includes('thread')) {
      // Look for Thread/OTBR agent when available
      const threadAgent = agents.find(agent => 
        agent.name.includes('otbr') || 
        agent.name.includes('thread') ||
        (agent as any).agent_type === 'otbr-agent'
      )
      if (threadAgent) return threadAgent.name
    }
    
    // Default to first available agent (excluding template)
    const nonTemplateAgents = agents.filter(agent => 
      !agent.name.includes('template') && 
      !(agent as any).agent_type?.includes('template')
    )
    const defaultAgent = nonTemplateAgents.length > 0 ? nonTemplateAgents[0].name : 
           (agents.length > 0 ? agents[0].name : '')
    
    console.log('⚠️ Using default agent selection:', { defaultAgent, nonTemplateAgents: nonTemplateAgents.map(a => a.name) })
    return defaultAgent
  }

  const checkForExistingResultsSilent = async () => {
    try {
      const response = await fetch(`/api/v1/projects/${projectId}/applications/${applicationName}/agent-analysis/results`)
      if (response.ok) {
        const data = await response.json()
        if (data.html_content || data) {  // Check for html_content or any data
          setResults(data)  // Use data directly
          if (onResultsReady) {
            onResultsReady(data)
          }
        }
      }
    } catch (error) {
      // Silent check - don't show errors
      console.debug('No existing results found:', error)
    }
  }

  const startAnalysis = async () => {
    if (!selectedAgent) {
      setError('No agent selected for analysis')
      return
    }

    try {
      setIsStartingAnalysis(true)
      setError(null)
      setResults(null)

      console.log(`Starting agent analysis: ${selectedAgent} for ${applicationName}`)

      const response = await fetch(
        `/api/v1/projects/${projectId}/applications/${applicationName}/agent-analysis/start?agent_type=${encodeURIComponent(selectedAgent)}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            raw_data_mode: true,
            meshlog_raw_data: true
          })
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Agent analysis response:', data)

      if (data.status === 'initiated' || data.status === 'processing') {
        setCurrentAnalysisId(data.analysis_id)
        if (onAnalysisStarted) {
          onAnalysisStarted(data.analysis_id)
        }
        
        // Start polling for results
        pollForResults(data.analysis_id)
      } else if (data.status === 'completed' && data.result) {
        // Analysis completed immediately
        setResults(data.result)  // Keep as is since this is the full result object
        if (onResultsReady) {
          onResultsReady(data.result)
        }
      } else {
        throw new Error(data.error || 'Analysis failed to start')
      }

    } catch (error) {
      console.error('Failed to start agent analysis:', error)
      setError(`Failed to start analysis: ${error instanceof Error ? error.message : String(error)}`)
    } finally {
      setIsStartingAnalysis(false)
    }
  }

  const pollForResults = async (analysisId: string) => {
    const maxAttempts = 30
    const pollInterval = 2000
    let attempts = 0

    const poll = async () => {
      try {
        attempts++
        const response = await fetch(`/api/v1/projects/${projectId}/applications/${applicationName}/agent-analysis/status/${analysisId}`)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        setAnalysisStatus(data)

        if (data.status === 'completed') {
          // Get the results
          const resultsResponse = await fetch(`/api/v1/projects/${projectId}/applications/${applicationName}/agent-analysis/results`)
          if (resultsResponse.ok) {
            const resultsData = await resultsResponse.json()
            setResults(resultsData)  // Use resultsData directly, not resultsData.results
            if (onResultsReady) {
              onResultsReady(resultsData)
            }
          }
          return
        } else if (data.status === 'failed') {
          setError(data.error || 'Analysis failed')
          return
        } else if (attempts >= maxAttempts) {
          setError('Analysis timed out')
          return
        }

        // Continue polling
        setTimeout(poll, pollInterval)
      } catch (error) {
        console.error('Polling error:', error)
        if (attempts >= maxAttempts) {
          setError('Failed to get analysis status')
        } else {
          setTimeout(poll, pollInterval)
        }
      }
    }

    poll()
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon color="success" />
      case 'failed':
        return <ErrorIcon color="error" />
      case 'processing':
        return <PendingIcon color="warning" />
      default:
        return <PendingIcon />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'failed':
        return 'error'
      case 'processing':
        return 'warning'
      default:
        return 'default'
    }
  }

  if (isLoading) {
    return <LinearProgress />
  }

  return (
    <Box>
      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Agent Controls */}
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={6}>
          <Button
            variant="contained"
            startIcon={isStartingAnalysis ? <RefreshIcon /> : <PlayIcon />}
            onClick={startAnalysis}
            disabled={isStartingAnalysis || !selectedAgent}
            fullWidth
          >
            {isStartingAnalysis ? 'Starting Analysis...' : 'Start Agent Analysis'}
          </Button>
        </Grid>
      </Grid>      {/* Analysis Status */}
      {analysisStatus && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              {getStatusIcon(analysisStatus.status)}
              <Typography variant="h6">
                Analysis Status
              </Typography>
              <Chip 
                label={analysisStatus.status} 
                color={getStatusColor(analysisStatus.status) as any}
                size="small"
              />
            </Box>
            {analysisStatus.message && (
              <Typography variant="body2" color="text.secondary">
                {analysisStatus.message}
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      {/* Inline Results Display */}
      {results && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <AgentResultsDisplay agentResults={results} applicationName={applicationName} />
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default AgentInvocationControls
