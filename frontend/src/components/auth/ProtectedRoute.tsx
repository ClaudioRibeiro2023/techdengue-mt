import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { UserRole } from '@/config/auth'
import { logger } from '@/utils/logger'
import { AccessDeniedBanner } from './AccessDeniedBanner'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRoles?: UserRole[]
  requireAllRoles?: boolean
}

export default function ProtectedRoute({
  children,
  requiredRoles = [],
  requireAllRoles = false,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, hasRole, hasAnyRole } = useAuth()
  const location = useLocation()
  const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'
  const MODE = import.meta.env.MODE

  // E2E/DEMO bypass: do not require auth in e2e mode or demo mode
  if (DEMO_MODE || MODE === 'e2e') {
    return <>{children}</>
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    // Redirect to login page with return URL
    logger.navigation('access-denied', location.pathname, {
      reason: 'not authenticated',
      redirectTo: '/login'
    })
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Check role requirements
  if (requiredRoles.length > 0) {
    const hasRequiredAccess = requireAllRoles
      ? requiredRoles.every((role) => hasRole(role))
      : hasAnyRole(requiredRoles)

    if (!hasRequiredAccess) {
      logger.navigation('access-denied', location.pathname, {
        reason: 'insufficient roles',
        requiredRoles,
        requireAllRoles
      })
      
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="max-w-2xl w-full">
            <AccessDeniedBanner
              requiredRoles={requiredRoles}
              currentPath={location.pathname}
              variant="error"
            />
          </div>
        </div>
      )
    }
  }

  return <>{children}</>
}
