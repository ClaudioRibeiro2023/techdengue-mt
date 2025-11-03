import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import MainLayout from '@/components/layout/MainLayout'
import { UserRole } from '@/config/auth'

// Auth Pages
import LoginPage from '@/pages/LoginPage'
import CallbackPage from '@/pages/auth/CallbackPage'
import SilentRenewPage from '@/pages/auth/SilentRenewPage'
import ConsultarDenunciaPage from '@/pages/eDenuncia/ConsultarDenunciaPage'

// Protected Pages
import HomePage from '@/pages/HomePage'
import ProfilePage from '@/pages/ProfilePage'
import DashboardEPI from '@/pages/DashboardEPI'
import NovaDenunciaPage from '@/pages/eDenuncia/NovaDenunciaPage'

// Check if demo mode is enabled
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

// Placeholder pages for other modules (to be implemented)
function MapaPage() {
  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Mapa Vivo</h1>
        <p className="page-subtitle">WebMapa Unificado - Navegação e análises espaciais</p>
        <div className="development-notice">
          <span>⚠️</span>
          <span>Em Desenvolvimento</span>
        </div>
      </div>
      <div className="content-section">
        <p>Selecione uma função no painel lateral para começar.</p>
      </div>
    </>
  )
}
function ETLPage() {
  return (
    <>
      <div className="page-header">
        <h1 className="page-title">ETL & Integração</h1>
        <p className="page-subtitle">Importadores e tratamento de dados</p>
        <div className="development-notice">
          <span>⚠️</span>
          <span>Em Desenvolvimento</span>
        </div>
      </div>
      <div className="content-section">
        <p>Selecione uma função no painel lateral para começar.</p>
      </div>
    </>
  )
}
function RelatoriosPage() {
  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Relatórios & Indicadores</h1>
        <p className="page-subtitle">Relatórios EPI e exportações</p>
        <div className="development-notice">
          <span>⚠️</span>
          <span>Em Desenvolvimento</span>
        </div>
      </div>
      <div className="content-section">
        <p>Selecione uma função no painel lateral para começar.</p>
      </div>
    </>
  )
}

export default function App() {
  // Wrapper component for demo mode
  const RouteWrapper = ({ children }: { children: React.ReactNode }) => {
    return DEMO_MODE ? <>{children}</> : <ProtectedRoute>{children}</ProtectedRoute>
  }

  const RoleRouteWrapper = ({ children, roles }: { children: React.ReactNode; roles?: UserRole[] }) => {
    return DEMO_MODE ? <>{children}</> : <ProtectedRoute requiredRoles={roles}>{children}</ProtectedRoute>
  }

  const router = createBrowserRouter(
    [
      // Public routes (auth)
      ...(!DEMO_MODE
        ? [
            { path: '/login', element: <LoginPage /> },
            { path: '/auth/callback', element: <CallbackPage /> },
            { path: '/auth/silent-renew', element: <SilentRenewPage /> },
          ]
        : []),

      // Protected routes within MainLayout
      {
        element: <MainLayout />,
        children: [
          { path: '/', element: <RouteWrapper><HomePage /></RouteWrapper> },
          { path: '/profile', element: <RouteWrapper><ProfilePage /></RouteWrapper> },
          { path: '/mapa', element: <RouteWrapper><MapaPage /></RouteWrapper> },
          { path: '/dashboard', element: <RouteWrapper><DashboardEPI /></RouteWrapper> },
          { path: '/etl', element: <RoleRouteWrapper roles={['ADMIN', 'GESTOR']}><ETLPage /></RoleRouteWrapper> },
          { path: '/relatorios', element: <RouteWrapper><RelatoriosPage /></RouteWrapper> },
          // e-Denúncia pública (sem wrapper de proteção)
          { path: '/denuncia', element: <NovaDenunciaPage /> },
          { path: '/denuncia/consultar/:protocolo', element: <ConsultarDenunciaPage /> },
        ],
      },

      // Catch all - redirect to home
      { path: '*', element: <Navigate to="/" replace /> },
    ],
    {
      future: {
        v7_relativeSplatPath: true,
      },
    }
  )

  return (
    <AuthProvider>
      <RouterProvider
        router={router}
        future={{ v7_startTransition: true }}
      />
    </AuthProvider>
  )
}
