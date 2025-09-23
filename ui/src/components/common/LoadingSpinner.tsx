import React from 'react'
import {
  Box,
  CircularProgress,
  Typography,
  LinearProgress
} from '@mui/material'

interface LoadingSpinnerProps {
  message?: string
  size?: 'small' | 'medium' | 'large'
  variant?: 'circular' | 'linear'
  fullScreen?: boolean
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  size = 'medium',
  variant = 'circular',
  fullScreen = false
}) => {
  const getSize = () => {
    switch (size) {
      case 'small': return 24
      case 'large': return 64
      default: return 40
    }
  }

  const content = (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2
      }}
    >
      {variant === 'circular' ? (
        <CircularProgress size={getSize()} />
      ) : (
        <Box sx={{ width: '100%', maxWidth: 300 }}>
          <LinearProgress />
        </Box>
      )}
      {message && (
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      )}
    </Box>
  )

  if (fullScreen) {
    return (
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}
      >
        {content}
      </Box>
    )
  }

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 200
      }}
    >
      {content}
    </Box>
  )
}
