import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PatientsPage from './pages/PatientsPage'
import PatientDetailPage from './pages/PatientDetailPage'
import VisitsPage from './pages/VisitsPage'
import VisitDetailPage from './pages/VisitDetailPage'
import AppointmentsPage from './pages/AppointmentsPage'
import PrescriptionsPage from './pages/PrescriptionsPage'
import EmrPage from './pages/EmrPage'
import AnalyticsPage from './pages/AnalyticsPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token, isLoading } = useAuth()
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-700" />
      </div>
    )
  }
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

function RootRedirect() {
  const { token, isLoading } = useAuth()
  if (isLoading) return null
  return <Navigate to={token ? '/dashboard' : '/login'} replace />
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<RootRedirect />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/patients"
          element={
            <ProtectedRoute>
              <Layout>
                <PatientsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/patients/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <PatientDetailPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/visits"
          element={
            <ProtectedRoute>
              <Layout>
                <VisitsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/visits/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <VisitDetailPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/appointments"
          element={
            <ProtectedRoute>
              <Layout>
                <AppointmentsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/prescriptions"
          element={
            <ProtectedRoute>
              <Layout>
                <PrescriptionsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/emr/:patientId"
          element={
            <ProtectedRoute>
              <Layout>
                <EmrPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <Layout>
                <AnalyticsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
