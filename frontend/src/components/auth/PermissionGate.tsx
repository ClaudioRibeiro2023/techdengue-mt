/**
 * Componentes para controle de acesso baseado em permissões granulares
 */

import { ReactNode, isValidElement } from 'react'
import { usePermissions } from '@/hooks/usePermissions'
import type { Permission, PermissionAction, PermissionResource } from '@/config/permissions'

interface PermissionGateProps {
  children: ReactNode
  /**
   * Permissão específica necessária
   * @example permission="DASHBOARD.VIEW"
   */
  permission?: Permission
  /**
   * Lista de permissões (pelo menos uma necessária)
   * @example permissions={['ADMIN.VIEW', 'ADMIN.EDIT']}
   */
  permissions?: Permission[]
  /**
   * Se true, exige TODAS as permissões (default: false)
   */
  requireAll?: boolean
  /**
   * Componente alternativo quando sem permissão
   */
  fallback?: ReactNode
  /**
   * Ação e recurso (alternativa a permission)
   * @example action="VIEW" resource="DASHBOARD"
   */
  action?: PermissionAction
  resource?: PermissionResource
}

/**
 * Componente principal para gate de permissões
 * 
 * @example
 * // Permissão única
 * <PermissionGate permission="DASHBOARD.VIEW">
 *   <Dashboard />
 * </PermissionGate>
 * 
 * @example
 * // Múltiplas permissões (pelo menos uma)
 * <PermissionGate permissions={['ADMIN.VIEW', 'ADMIN.EDIT']}>
 *   <AdminPanel />
 * </PermissionGate>
 * 
 * @example
 * // Ação + Recurso
 * <PermissionGate action="EDIT" resource="DASHBOARD">
 *   <EditButton />
 * </PermissionGate>
 */
export function PermissionGate({
  children,
  permission,
  permissions,
  requireAll = false,
  fallback = null,
  action,
  resource,
}: PermissionGateProps) {
  const perms = usePermissions()

  // Verificar permissão via action/resource
  if (action && resource) {
    if (!perms.can(action, resource)) {
      return <>{fallback}</>
    }
    return <>{children}</>
  }

  // Verificar permissão única
  if (permission) {
    if (!perms.hasPermission(permission)) {
      return <>{fallback}</>
    }
    return <>{children}</>
  }

  // Verificar múltiplas permissões
  if (permissions) {
    const hasAccess = requireAll
      ? perms.hasAllPermissions(permissions)
      : perms.hasAnyPermission(permissions)

    if (!hasAccess) {
      return <>{fallback}</>
    }
    return <>{children}</>
  }

  // Se nenhuma regra especificada, bloquear por segurança
  console.warn('PermissionGate: Nenhuma permissão especificada')
  return <>{fallback}</>
}

/**
 * Componente simplificado para verificar se pode realizar ação
 * 
 * @example
 * <Can action="EDIT" resource="DASHBOARD">
 *   <EditButton />
 * </Can>
 */
export function Can({
  action,
  resource,
  children,
  fallback = null,
}: {
  action: PermissionAction
  resource: PermissionResource
  children: ReactNode
  fallback?: ReactNode
}) {
  return (
    <PermissionGate action={action} resource={resource} fallback={fallback}>
      {children}
    </PermissionGate>
  )
}

/**
 * Componente para mostrar conteúdo baseado em nível de acesso
 * 
 * @example
 * <AccessLevel resource="DASHBOARD">
 *   {(level) => (
 *     level === 'ADMIN' ? <AdminView /> : <ReadonlyView />
 *   )}
 * </AccessLevel>
 */
export function AccessLevel({
  resource,
  children,
}: {
  resource: PermissionResource
  children: (level: PermissionAction | null) => ReactNode
}) {
  const { getAccessLevel } = usePermissions()
  const level = getAccessLevel(resource)
  return <>{children(level)}</>
}

/**
 * Componente para mostrar diferentes UIs por nível de acesso
 * 
 * @example
 * <AccessSwitch resource="DASHBOARD">
 *   <AccessSwitch.Admin><AdminDashboard /></AccessSwitch.Admin>
 *   <AccessSwitch.Edit><EditorDashboard /></AccessSwitch.Edit>
 *   <AccessSwitch.View><ViewerDashboard /></AccessSwitch.View>
 *   <AccessSwitch.None><NoAccess /></AccessSwitch.None>
 * </AccessSwitch>
 */
export function AccessSwitch({
  resource,
  children,
}: {
  resource: PermissionResource
  children: ReactNode
}) {
  const { getAccessLevel } = usePermissions()
  const level = getAccessLevel(resource)

  // Encontrar componente filho apropriado
  const childArray = Array.isArray(children) ? children : [children]

  // Procurar por level exato ou próximo
  const levelOrder: (PermissionAction | 'None')[] = ['ADMIN', 'DELETE', 'EDIT', 'CREATE', 'EXECUTE', 'EXPORT', 'VIEW', 'None']
  const currentLevelIndex = level ? levelOrder.indexOf(level) : levelOrder.length - 1

  for (let i = currentLevelIndex; i < levelOrder.length; i++) {
    const targetLevel = levelOrder[i]
    const child = childArray.find((c) => {
      if (!isValidElement(c)) return false
      const typeObj = c.type as unknown as { displayName?: string; name?: string }
      const childLevel = typeObj.displayName || typeObj.name || ''
      return childLevel === `AccessSwitch.${targetLevel}`
    })

    if (child) return <>{child}</>
  }

  return null
}

// Sub-componentes do AccessSwitch
AccessSwitch.Admin = ({ children }: { children: ReactNode }) => <>{children}</>
AccessSwitch.Delete = ({ children }: { children: ReactNode }) => <>{children}</>
AccessSwitch.Edit = ({ children }: { children: ReactNode }) => <>{children}</>
AccessSwitch.Create = ({ children }: { children: ReactNode }) => <>{children}</>
AccessSwitch.Execute = ({ children }: { children: ReactNode }) => <>{children}</>
AccessSwitch.Export = ({ children }: { children: ReactNode }) => <>{children}</>
AccessSwitch.View = ({ children }: { children: ReactNode }) => <>{children}</>
AccessSwitch.None = ({ children }: { children: ReactNode }) => <>{children}</>
