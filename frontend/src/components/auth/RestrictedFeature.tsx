import { ReactNode } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { UserRole } from '@/config/auth'
import Icon from '@/components/ui/Icon'

interface RestrictedFeatureProps {
  children: ReactNode
  requiredRoles: UserRole[]
  requireAllRoles?: boolean
  fallback?: ReactNode
  showLock?: boolean
  tooltipPosition?: 'top' | 'bottom' | 'left' | 'right'
}

export function RestrictedFeature({
  children,
  requiredRoles,
  requireAllRoles = false,
  fallback,
  showLock = true,
  tooltipPosition = 'top'
}: RestrictedFeatureProps) {
  const { hasRole, hasAnyRole } = useAuth()

  const hasAccess = requireAllRoles
    ? requiredRoles.every((role) => hasRole(role))
    : hasAnyRole(requiredRoles)

  if (hasAccess) {
    return <>{children}</>
  }

  // Se tem fallback customizado, usa ele
  if (fallback) {
    return <>{fallback}</>
  }

  // Fallback padrão: versão desabilitada com lock
  if (showLock) {
    return (
      <div className="relative group">
        <div className="opacity-50 pointer-events-none select-none">
          {children}
        </div>
        
        {/* Lock overlay */}
        <div 
          className="absolute inset-0 flex items-center justify-center bg-gray-900/5 backdrop-blur-[1px] rounded-md cursor-not-allowed"
          title={`Requer role(s): ${requiredRoles.join(', ')}`}
        >
          <div className="bg-white rounded-full p-1.5 shadow-md border border-gray-200">
            <Icon name="Lock" size={16} className="text-gray-500" />
          </div>
        </div>

        {/* Tooltip */}
        <div 
          className={`
            absolute hidden group-hover:block z-50
            px-3 py-2 text-xs font-medium text-white bg-gray-900 rounded-md shadow-lg
            whitespace-nowrap pointer-events-none
            ${tooltipPosition === 'top' ? 'bottom-full left-1/2 -translate-x-1/2 mb-2' : ''}
            ${tooltipPosition === 'bottom' ? 'top-full left-1/2 -translate-x-1/2 mt-2' : ''}
            ${tooltipPosition === 'left' ? 'right-full top-1/2 -translate-y-1/2 mr-2' : ''}
            ${tooltipPosition === 'right' ? 'left-full top-1/2 -translate-y-1/2 ml-2' : ''}
          `}
        >
          🔒 Requer: {requiredRoles.join(', ')}
          
          {/* Tooltip arrow */}
          <div 
            className={`
              absolute w-2 h-2 bg-gray-900 rotate-45
              ${tooltipPosition === 'top' ? 'top-full left-1/2 -translate-x-1/2 -translate-y-1/2' : ''}
              ${tooltipPosition === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 translate-y-1/2' : ''}
              ${tooltipPosition === 'left' ? 'left-full top-1/2 -translate-y-1/2 -translate-x-1/2' : ''}
              ${tooltipPosition === 'right' ? 'right-full top-1/2 -translate-y-1/2 translate-x-1/2' : ''}
            `}
          />
        </div>
      </div>
    )
  }

  // Sem lock, apenas não renderiza
  return null
}

/**
 * Componente mais simples para uso inline
 */
export function Restricted({ 
  roles, 
  children 
}: { 
  roles: UserRole[]; 
  children: ReactNode 
}) {
  const { hasAnyRole } = useAuth()
  return hasAnyRole(roles) ? <>{children}</> : null
}

/**
 * Hook para verificar acesso programaticamente
 */
export function useRestricted(roles: UserRole[], requireAll = false) {
  const { hasRole, hasAnyRole } = useAuth()
  
  return {
    hasAccess: requireAll 
      ? roles.every((role) => hasRole(role))
      : hasAnyRole(roles),
    missingRoles: roles.filter((role) => !hasRole(role))
  }
}
