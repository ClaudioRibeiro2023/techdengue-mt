/**
 * Hook para verificação de permissões granulares
 */

import { useMemo } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import type { UserRole } from '@/config/auth'
import {
  type Permission,
  type PermissionAction,
  type PermissionResource,
  hasPermission,
  hasAllPermissions,
  hasAnyPermission,
  getPermissions,
  can,
  getMissingPermissions,
  getAccessLevel,
} from '@/config/permissions'

interface UsePermissionsReturn {
  /**
   * Verifica se tem uma permissão específica
   * @example hasPermission('DASHBOARD.VIEW')
   */
  hasPermission: (permission: Permission) => boolean

  /**
   * Verifica se tem todas as permissões
   * @example hasAllPermissions(['DASHBOARD.VIEW', 'DASHBOARD.EXPORT'])
   */
  hasAllPermissions: (permissions: Permission[]) => boolean

  /**
   * Verifica se tem pelo menos uma permissão
   * @example hasAnyPermission(['ADMIN.VIEW', 'ADMIN.EDIT'])
   */
  hasAnyPermission: (permissions: Permission[]) => boolean

  /**
   * Verifica se pode realizar ação em recurso
   * @example can('VIEW', 'DASHBOARD')
   */
  can: (action: PermissionAction, resource: PermissionResource) => boolean

  /**
   * Obtém permissões faltantes
   * @example getMissingPermissions(['ADMIN.VIEW', 'ADMIN.EDIT'])
   */
  getMissingPermissions: (required: Permission[]) => Permission[]

  /**
   * Obtém nível de acesso a um recurso
   * @example getAccessLevel('DASHBOARD') // retorna 'VIEW' ou 'ADMIN'
   */
  getAccessLevel: (resource: PermissionResource) => PermissionAction | null

  /**
   * Lista todas as permissões do usuário
   */
  permissions: Permission[]

  /**
   * Roles do usuário
   */
  roles: UserRole[]

  /**
   * Se está autenticado
   */
  isAuthenticated: boolean
}

/**
 * Hook principal para verificação de permissões
 */
export function usePermissions(): UsePermissionsReturn {
  const { user, isAuthenticated } = useAuth()

  // Extrair roles do usuário
  const roles = useMemo<UserRole[]>(() => {
    if (!user) return []

    const profile = user.profile as { realm_access?: { roles?: string[] } }
    const userRoles = profile?.realm_access?.roles || []

    return userRoles.filter((r): r is UserRole =>
      ['ADMIN', 'GESTOR', 'VIGILANCIA', 'CAMPO'].includes(r)
    )
  }, [user])

  // Obter todas as permissões do usuário
  const permissions = useMemo(() => getPermissions(roles), [roles])

  return {
    hasPermission: (permission: Permission) => hasPermission(roles, permission),
    hasAllPermissions: (permissions: Permission[]) => hasAllPermissions(roles, permissions),
    hasAnyPermission: (permissions: Permission[]) => hasAnyPermission(roles, permissions),
    can: (action: PermissionAction, resource: PermissionResource) => can(roles, action, resource),
    getMissingPermissions: (required: Permission[]) => getMissingPermissions(roles, required),
    getAccessLevel: (resource: PermissionResource) => getAccessLevel(roles, resource),
    permissions,
    roles,
    isAuthenticated,
  }
}

/**
 * Hook simplificado para verificar se pode realizar ação
 * @example const canEdit = useCan('EDIT', 'DASHBOARD')
 */
export function useCan(action: PermissionAction, resource: PermissionResource): boolean {
  const { can } = usePermissions()
  return can(action, resource)
}

/**
 * Hook para obter nível de acesso
 * @example const access = useAccessLevel('DASHBOARD') // 'VIEW' | 'ADMIN' | null
 */
export function useAccessLevel(resource: PermissionResource): PermissionAction | null {
  const { getAccessLevel } = usePermissions()
  return getAccessLevel(resource)
}
