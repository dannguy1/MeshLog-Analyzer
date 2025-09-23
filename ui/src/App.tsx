import { Routes, Route } from 'react-router-dom'
import { Box, Container } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ProjectUpload from './pages/ProjectUpload'
import ProjectView from './pages/ProjectView'
import AnalysisView from './pages/AnalysisView'
import ApplicationAnalysisPage from './pages/ApplicationAnalysisPage'
import NotFound from './pages/NotFound'

function App() {
  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <Layout>
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<ProjectUpload />} />
            <Route path="/project/:projectId" element={<ProjectView />} />
            <Route path="/analysis/:projectId/:applicationName/:analysisId" element={<ApplicationAnalysisPage />} />
            <Route path="/analysis/:projectId/:applicationName" element={<ApplicationAnalysisPage />} />
            <Route path="/analysis/:projectId" element={<AnalysisView />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Container>
      </Layout>
    </Box>
  )
}

export default App
