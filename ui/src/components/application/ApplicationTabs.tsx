import React from 'react'
import {
  Box,
  Paper,
  Tabs,
  Tab
} from '@mui/material'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`application-tabpanel-${index}`}
      aria-labelledby={`application-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

interface ApplicationTabsProps {
  activeTab: number
  onTabChange: (tab: number) => void
  applicationName: string
  showTimeSequence?: boolean
}

export const ApplicationTabs: React.FC<ApplicationTabsProps> = ({
  activeTab,
  onTabChange,
  applicationName,
  showTimeSequence = true
}) => {
  const tabs = [
    { label: 'Overview', value: 0 },
    { label: 'Anomalies', value: 1 },
    { label: 'Metrics', value: 2 },
    { label: 'Performance', value: 3 },
    { label: 'Recommendations', value: 4 }
  ]

  if (showTimeSequence) {
    tabs.push({ label: 'Time Sequence', value: 5 })
  }

  return (
    <Paper sx={{ width: '100%' }}>
      <Tabs
        value={activeTab}
        onChange={(_e, newValue) => onTabChange(newValue)}
        aria-label={`${applicationName} analysis tabs`}
        variant="scrollable"
        scrollButtons="auto"
      >
        {tabs.map((tab) => (
          <Tab key={tab.value} label={tab.label} />
        ))}
      </Tabs>
    </Paper>
  )
}

export { TabPanel }
