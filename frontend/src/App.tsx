import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import MainLayout from '@/components/layout/MainLayout'

// Auth Pages
import LoginPage from '@/pages/LoginPage'
import CallbackPage from '@/pages/auth/CallbackPage'
import SilentRenewPage from '@/pages/auth/SilentRenewPage'

// Protected Pages
import HomePage from '@/pages/HomePage'
import ProfilePage from '@/pages/ProfilePage'

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
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<CallbackPage />} />
          <Route path="/auth/silent-renew" element={<SilentRenewPage />} />

          {/* Protected Routes */}
          <Route element={<MainLayout />}>
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <HomePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/mapa"
              element={
                <ProtectedRoute>
                  <MapaPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/etl"
              element={
                <ProtectedRoute requiredRoles={['ADMIN', 'GESTOR']}>
                  <ETLPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/relatorios"
              element={
                <ProtectedRoute>
                  <RelatoriosPage />
                </ProtectedRoute>
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
