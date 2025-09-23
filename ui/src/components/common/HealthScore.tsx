import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';
import { HEALTH_COLORS } from '../../utils/constants';

interface HealthScoreProps {
  score: number;
  size?: 'small' | 'medium' | 'large';
  showProgress?: boolean;
  showLabel?: boolean;
}

export const HealthScore: React.FC<HealthScoreProps> = ({
  score,
  size = 'medium',
  showProgress = true,
  showLabel = true
}) => {
  const getColor = (score: number) => {
    if (score >= 80) return HEALTH_COLORS.healthy;
    if (score >= 60) return HEALTH_COLORS.degraded;
    return HEALTH_COLORS.critical;
  };

  const getVariant = () => {
    switch (size) {
      case 'large':
        return 'h4';
      case 'small':
        return 'body1';
      default:
        return 'h6';
    }
  };

  return (
    <Box>
      <Typography variant={getVariant()} color={getColor(score)}>
        {score.toFixed(0)}
      </Typography>
      {showProgress && (
        <LinearProgress
          variant="determinate"
          value={score}
          sx={{ 
            height: size === 'large' ? 12 : 8, 
            borderRadius: 4,
            backgroundColor: 'rgba(0,0,0,0.1)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: getColor(score)
            }
          }}
        />
      )}
      {showLabel && (
        <Typography variant="caption" color="text.secondary">
          Health Score
        </Typography>
      )}
    </Box>
  );
};
