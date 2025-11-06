import { useAuth } from '@/contexts/AuthContext'
import { UserRole } from '@/config/auth'
import Icon from '@/components/ui/Icon'

interface RoleBadgeProps {
  variant?: 'compact' | 'full'
  showTooltip?: boolean
}

const roleConfig: Record<UserRole, { label: string; color: string; icon: string }> = {
  ADMIN: {
    label: 'Administrador',
    color: 'bg-purple-100 text-purple-800 border-purple-200',
    icon: 'Shield'
  },
  GESTOR: {
    label: 'Gestor',
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: 'Briefcase'
  },
  VIGILANCIA: {
    label: 'Vigilância',
    color: 'bg-green-100 text-green-800 border-green-200',
    icon: 'Activity'
  },
  CAMPO: {
    label: 'Campo',
    color: 'bg-amber-100 text-amber-800 border-amber-200',
    icon: 'MapPin'
  }
}

export function RoleBadge({ variant = 'compact', showTooltip = true }: RoleBadgeProps) {
  const { user } = useAuth()

  if (!user) return null

  // Extract roles from user
  const profile = user.profile as { realm_access?: { roles?: string[] } }
  const userRoles = profile?.realm_access?.roles || []
  const validRoles = userRoles.filter((r): r is UserRole => 
    ['ADMIN', 'GESTOR', 'VIGILANCIA', 'CAMPO'].includes(r)
  )

  if (validRoles.length === 0) return null

  // If compact, show only highest role (ADMIN > GESTOR > VIGILANCIA > CAMPO)
  const roleOrder: UserRole[] = ['ADMIN', 'GESTOR', 'VIGILANCIA', 'CAMPO']
  const displayRoles = variant === 'compact' 
    ? [validRoles.sort((a, b) => roleOrder.indexOf(a) - roleOrder.indexOf(b))[0]]
    : validRoles

  return (
    <div className="flex items-center gap-1.5">
      {displayRoles.map((role) => {
        const config = roleConfig[role]
        return (
          <div
            key={role}
            className={`
              flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border
              ${config.color}
              transition-all duration-200 hover:shadow-sm
            `}
            title={showTooltip ? config.label : undefined}
          >
            <Icon name={config.icon} size={14} />
            {variant === 'full' && <span>{config.label}</span>}
          </div>
        )
      })}
      
      {variant === 'compact' && validRoles.length > 1 && (
        <div 
          className="text-xs text-gray-500 font-medium px-1.5"
          title={`Roles: ${validRoles.map(r => roleConfig[r].label).join(', ')}`}
        >
          +{validRoles.length - 1}
        </div>
      )}
    </div>
  )
}
