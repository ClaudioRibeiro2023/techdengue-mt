import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { UserRole } from '@/config/auth'

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
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Check role requirements
  if (requiredRoles.length > 0) {
    const hasRequiredAccess = requireAllRoles
      ? requiredRoles.every((role) => hasRole(role))
      : hasAnyRole(requiredRoles)

    if (!hasRequiredAccess) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="text-center">
              <div className="text-red-600 text-5xl mb-4">🚫</div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Acesso Negado
              </h1>
              <p className="text-gray-600 mb-4">
                Você não possui permissão para acessar esta página.
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Roles necessárias: {requiredRoles.join(', ')}
              </p>
              <button
                onClick={() => window.history.back()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Voltar
              </button>
            </div>
          </div>
        </div>
      )
    }
  }

  return <>{children}</>
}
