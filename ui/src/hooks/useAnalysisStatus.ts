import { useEffect, useState, useRef } from 'react'
import { useDispatch } from 'react-redux'
import { getApplicationAnalysisStatus } from '../store/features/analysis/analysisSlice'

interface AnalysisStatusUpdate {
  analysis_id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  timestamp: string
  data: {
    progress_percentage?: number
    current_stage?: string
    error_message?: string
    log_volume?: number
    error_rate?: number
    health_score?: number
  }
}

export const useAnalysisStatus = (projectId: string, applicationName: string, shouldConnect: boolean = false) => {
  const dispatch = useDispatch()
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<AnalysisStatusUpdate | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const connectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connectWebSocket = () => {
    // Use the same host as the current page, but port 8000 for WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const wsUrl = `${protocol}//${host}:8000/ws/analysis-status/${projectId}/${applicationName}`
    
    try {
      console.log(`Attempting to connect WebSocket: ${wsUrl}`)
      const websocket = new WebSocket(wsUrl)
      
      websocket.onopen = () => {
        console.log(`WebSocket connected for ${projectId}:${applicationName}`)
        setIsConnected(true)
        reconnectAttempts.current = 0
      }
      
      websocket.onmessage = (event) => {
        try {
          console.log(`WebSocket received message for ${applicationName}:`, event.data)
          const data = JSON.parse(event.data)
          console.log(`WebSocket parsed data for ${applicationName}:`, data)
          
          // Check if this is a complete analysis status (from initial connection)
          if (data.analysis_summary && data.available_analyses) {
            console.log(`Received complete analysis status for ${applicationName}:`, data)
            
            // Update Redux state with complete analysis status
            dispatch({
              type: 'analysis/updateCompleteStatusFromWebSocket',
              payload: data
            })
            console.log(`Dispatched complete analysis status to Redux for ${applicationName}`)
          } else {
            // This is a real-time status update
            const statusUpdate: AnalysisStatusUpdate = data
            setLastUpdate(statusUpdate)
            
            // Update Redux state with new status
            dispatch({
              type: 'analysis/updateStatusFromWebSocket',
              payload: {
                projectId,
                applicationName,
                statusUpdate
              }
            })
            
            console.log(`Received status update: ${statusUpdate.status} for ${applicationName}`)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      websocket.onclose = () => {
        console.log(`WebSocket disconnected for ${projectId}:${applicationName}`)
        setIsConnected(false)
        
        // Attempt to reconnect with exponential backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Attempting to reconnect WebSocket (attempt ${reconnectAttempts.current})`)
            connectWebSocket()
          }, delay)
        } else {
          console.error('Max reconnection attempts reached. WebSocket connection failed.')
          // NO POLLING FALLBACK - WebSocket is the only real-time mechanism
          // Manual refresh is still available via the refresh button
        }
      }
      
      websocket.onerror = (error) => {
        console.error(`WebSocket error for ${projectId}:${applicationName}:`, error)
        console.error('WebSocket error details:', {
          url: wsUrl,
          readyState: websocket.readyState,
          protocol: websocket.protocol
        })
        setIsConnected(false)
      }
      
      setWs(websocket)
      
    } catch (error) {
      console.error('Error creating WebSocket:', error)
      setIsConnected(false)
    }
  }

  useEffect(() => {
    console.log(`useAnalysisStatus hook called for ${projectId}:${applicationName}, shouldConnect: ${shouldConnect}`)
    
    // Only connect WebSocket when explicitly requested
    if (projectId && applicationName && shouldConnect) {
      console.log(`Connecting WebSocket for ${projectId}:${applicationName}`)
      connectWebSocket()
    }

    return () => {
      console.log(`useAnalysisStatus cleanup for ${projectId}:${applicationName}`)
      if (connectTimeoutRef.current) {
        clearTimeout(connectTimeoutRef.current)
      }
      if (ws) {
        ws.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [projectId, applicationName, shouldConnect])

  const manualRefresh = () => {
    dispatch(getApplicationAnalysisStatus({ projectId, appName: applicationName }) as any)
  }

  return {
    isConnected,
    lastUpdate,
    manualRefresh
  }
}
