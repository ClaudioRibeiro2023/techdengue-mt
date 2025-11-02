import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import MainLayout from '@/components/layout/MainLayout'
import { UserRole } from '@/config/auth'

// Auth Pages
import LoginPage from '@/pages/LoginPage'
import CallbackPage from '@/pages/auth/CallbackPage'
import SilentRenewPage from '@/pages/auth/SilentRenewPage'

// Protected Pages
import HomePage from '@/pages/HomePage'
import ProfilePage from '@/pages/ProfilePage'

// Check if demo mode is enabled
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

// Placeholder pages for other modules (to be implemented)
function MapaPage() {
  return <div className="p-8"><h1 className="text-2xl font-bold">Mapa - Em Desenvolvimento</h1></div>
}
function DashboardPage() {
  return <div className="p-8"><h1 className="text-2xl font-bold">Dashboard - Em Desenvolvimento</h1></div>
}
function ETLPage() {
  return <div className="p-8"><h1 className="text-2xl font-bold">ETL - Em Desenvolvimento</h1></div>
}
function RelatoriosPage() {
  return <div className="p-8"><h1 className="text-2xl font-bold">Relatórios - Em Desenvolvimento</h1></div>
}

export default function App() {
  // Wrapper component for demo mode
  const RouteWrapper = ({ children }: { children: React.ReactNode }) => {
    return DEMO_MODE ? <>{children}</> : <ProtectedRoute>{children}</ProtectedRoute>
  }

  const RoleRouteWrapper = ({ children, roles }: { children: React.ReactNode; roles?: UserRole[] }) => {
    return DEMO_MODE ? <>{children}</> : <ProtectedRoute requiredRoles={roles}>{children}</ProtectedRoute>
  }

  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          {!DEMO_MODE && (
            <>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/auth/callback" element={<CallbackPage />} />
              <Route path="/auth/silent-renew" element={<SilentRenewPage />} />
            </>
          )}

          {/* Protected Routes */}
          <Route element={<MainLayout />}>
            <Route
              path="/"
              element={
                <RouteWrapper>
                  <HomePage />
                </RouteWrapper>
              }
            />
            <Route
              path="/profile"
              element={
                <RouteWrapper>
                  <ProfilePage />
                </RouteWrapper>
              }
            />
            <Route
              path="/mapa"
              element={
                <RouteWrapper>
                  <MapaPage />
                </RouteWrapper>
              }
            />
            <Route
              path="/dashboard"
              element={
                <RouteWrapper>
                  <DashboardPage />
                </RouteWrapper>
              }
            />
            <Route
              path="/etl"
              element={
                <RoleRouteWrapper roles={['ADMIN', 'GESTOR']}>
                  <ETLPage />
                </RoleRouteWrapper>
              }
            />
            <Route
              path="/relatorios"
              element={
                <RouteWrapper>
                  <RelatoriosPage />
                </RouteWrapper>
              }
            />
          </Route>

          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
