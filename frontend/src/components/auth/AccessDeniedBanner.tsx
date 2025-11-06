import { useState } from 'react'
import { UserRole } from '@/config/auth'
import Icon from '@/components/ui/Icon'

interface AccessDeniedBannerProps {
  requiredRoles: UserRole[]
  currentPath?: string
  onDismiss?: () => void
  variant?: 'error' | 'warning' | 'info'
}

export function AccessDeniedBanner({
  requiredRoles,
  currentPath,
  onDismiss,
  variant = 'warning'
}: AccessDeniedBannerProps) {
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) return null

  const variantConfig = {
    error: {
      bgColor: 'bg-red-50 border-red-200',
      iconColor: 'text-red-600',
      textColor: 'text-red-800',
      icon: 'ShieldAlert'
    },
    warning: {
      bgColor: 'bg-amber-50 border-amber-200',
      iconColor: 'text-amber-600',
      textColor: 'text-amber-800',
      icon: 'ShieldOff'
    },
    info: {
      bgColor: 'bg-blue-50 border-blue-200',
      iconColor: 'text-blue-600',
      textColor: 'text-blue-800',
      icon: 'Info'
    }
  }

  const config = variantConfig[variant]

  const handleDismiss = () => {
    setDismissed(true)
    onDismiss?.()
  }

  return (
    <div 
      className={`
        ${config.bgColor} 
        border-l-4 p-4 mb-6 rounded-r-md shadow-sm
        animate-slideDown
      `}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`${config.iconColor} mt-0.5`}>
          <Icon name={config.icon} size={20} />
        </div>

        {/* Content */}
        <div className="flex-1">
          <h3 className={`text-sm font-semibold ${config.textColor} mb-1`}>
            Acesso Limitado
          </h3>
          <p className="text-sm text-gray-700 mb-2">
            Você não possui as permissões necessárias para acessar esta funcionalidade.
          </p>
          
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-gray-600 font-medium">Requer:</span>
            {requiredRoles.map((role) => (
              <span 
                key={role}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-white border border-gray-300 rounded text-gray-700 font-medium"
              >
                <Icon name="Shield" size={12} />
                {role}
              </span>
            ))}
          </div>

          {currentPath && (
            <p className="text-xs text-gray-500 mt-2">
              Rota: <code className="bg-white px-1.5 py-0.5 rounded border border-gray-200 font-mono">{currentPath}</code>
            </p>
          )}

          <div className="mt-3 flex items-center gap-2">
            <button
              onClick={() => window.history.back()}
              className="text-xs font-medium text-gray-700 hover:text-gray-900 underline"
            >
              ← Voltar
            </button>
            <span className="text-gray-300">|</span>
            <button
              onClick={() => window.location.href = '/'}
              className="text-xs font-medium text-gray-700 hover:text-gray-900 underline"
            >
              Ir para Home
            </button>
          </div>
        </div>

        {/* Dismiss button */}
        {onDismiss && (
          <button
            onClick={handleDismiss}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Fechar"
          >
            <Icon name="X" size={16} />
          </button>
        )}
      </div>
    </div>
  )
}

/**
 * Banner compacto para uso em pequenos espaços
 */
export function AccessDeniedInline({ roles }: { roles: UserRole[] }) {
  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-md text-sm">
      <Icon name="Lock" size={14} className="text-amber-600" />
      <span className="text-amber-800 text-xs">
        Requer: <strong>{roles.join(', ')}</strong>
      </span>
    </div>
  )
}
