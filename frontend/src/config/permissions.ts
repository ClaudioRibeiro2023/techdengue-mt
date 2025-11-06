/**
 * Sistema de Permissões Granulares
 * 
 * Evolução do sistema de roles para permissões mais específicas.
 * Permite controle fino de acesso a funcionalidades.
 */

import { UserRole } from './auth'

// Tipos de ações
export type PermissionAction = 'VIEW' | 'CREATE' | 'EDIT' | 'DELETE' | 'EXECUTE' | 'EXPORT' | 'ADMIN'

// Recursos do sistema
export type PermissionResource = 
  | 'DASHBOARD'
  | 'MAPA'
  | 'PREVISAO'
  | 'VIGILANCIA_ENTOMOLOGICA'
  | 'VIGILANCIA_EPIDEMIOLOGICA'
  | 'RESPOSTA_OPERACIONAL'
  | 'RELATORIOS'
  | 'ETL'
  | 'ADMIN'
  | 'OBSERVABILIDADE'
  | 'DENUNCIA'
  | 'USUARIOS'
  | 'PARAMETROS'
  | 'AUDITORIA'

// Permissão granular no formato "RECURSO.ACAO"
export type Permission = `${PermissionResource}.${PermissionAction}`

/**
 * Mapeamento de Roles para Permissões
 * 
 * Define quais permissões cada role possui.
 * Isso permite herança e composição de permissões.
 */
export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  // ADMIN tem todas as permissões
  ADMIN: [
    // Dashboard
    'DASHBOARD.VIEW',
    'DASHBOARD.EXPORT',
    'DASHBOARD.ADMIN',
    
    // Mapa
    'MAPA.VIEW',
    'MAPA.EDIT',
    'MAPA.EXPORT',
    'MAPA.ADMIN',
    
    // Previsão
    'PREVISAO.VIEW',
    'PREVISAO.CREATE',
    'PREVISAO.EDIT',
    'PREVISAO.EXECUTE',
    'PREVISAO.EXPORT',
    
    // Vigilância Entomológica
    'VIGILANCIA_ENTOMOLOGICA.VIEW',
    'VIGILANCIA_ENTOMOLOGICA.CREATE',
    'VIGILANCIA_ENTOMOLOGICA.EDIT',
    'VIGILANCIA_ENTOMOLOGICA.DELETE',
    'VIGILANCIA_ENTOMOLOGICA.EXPORT',
    'VIGILANCIA_ENTOMOLOGICA.ADMIN',
    
    // Vigilância Epidemiológica
    'VIGILANCIA_EPIDEMIOLOGICA.VIEW',
    'VIGILANCIA_EPIDEMIOLOGICA.CREATE',
    'VIGILANCIA_EPIDEMIOLOGICA.EDIT',
    'VIGILANCIA_EPIDEMIOLOGICA.DELETE',
    'VIGILANCIA_EPIDEMIOLOGICA.EXPORT',
    'VIGILANCIA_EPIDEMIOLOGICA.ADMIN',
    
    // Resposta Operacional
    'RESPOSTA_OPERACIONAL.VIEW',
    'RESPOSTA_OPERACIONAL.CREATE',
    'RESPOSTA_OPERACIONAL.EDIT',
    'RESPOSTA_OPERACIONAL.DELETE',
    'RESPOSTA_OPERACIONAL.EXECUTE',
    'RESPOSTA_OPERACIONAL.ADMIN',
    
    // Relatórios
    'RELATORIOS.VIEW',
    'RELATORIOS.CREATE',
    'RELATORIOS.EXPORT',
    'RELATORIOS.ADMIN',
    
    // ETL
    'ETL.VIEW',
    'ETL.EXECUTE',
    'ETL.ADMIN',
    
    // Administração
    'ADMIN.VIEW',
    'ADMIN.CREATE',
    'ADMIN.EDIT',
    'ADMIN.DELETE',
    'ADMIN.ADMIN',
    
    // Observabilidade
    'OBSERVABILIDADE.VIEW',
    'OBSERVABILIDADE.ADMIN',
    
    // Denúncia (público)
    'DENUNCIA.VIEW',
    'DENUNCIA.CREATE',
    
    // Usuários
    'USUARIOS.VIEW',
    'USUARIOS.CREATE',
    'USUARIOS.EDIT',
    'USUARIOS.DELETE',
    
    // Parâmetros
    'PARAMETROS.VIEW',
    'PARAMETROS.EDIT',
    
    // Auditoria
    'AUDITORIA.VIEW',
    'AUDITORIA.EXPORT',
  ],

  // GESTOR tem permissões de leitura, relatórios e exportação
  GESTOR: [
    // Dashboard
    'DASHBOARD.VIEW',
    'DASHBOARD.EXPORT',
    
    // Mapa
    'MAPA.VIEW',
    'MAPA.EXPORT',
    
    // Previsão
    'PREVISAO.VIEW',
    'PREVISAO.EXECUTE',
    'PREVISAO.EXPORT',
    
    // Vigilância Entomológica
    'VIGILANCIA_ENTOMOLOGICA.VIEW',
    'VIGILANCIA_ENTOMOLOGICA.EXPORT',
    
    // Vigilância Epidemiológica
    'VIGILANCIA_EPIDEMIOLOGICA.VIEW',
    'VIGILANCIA_EPIDEMIOLOGICA.EXPORT',
    
    // Resposta Operacional
    'RESPOSTA_OPERACIONAL.VIEW',
    'RESPOSTA_OPERACIONAL.CREATE',
    'RESPOSTA_OPERACIONAL.EDIT',
    'RESPOSTA_OPERACIONAL.EXECUTE',
    
    // Relatórios
    'RELATORIOS.VIEW',
    'RELATORIOS.CREATE',
    'RELATORIOS.EXPORT',
    
    // Observabilidade
    'OBSERVABILIDADE.VIEW',
    
    // Denúncia
    'DENUNCIA.VIEW',
    
    // Usuários (apenas visualizar)
    'USUARIOS.VIEW',
    
    // Parâmetros (apenas visualizar)
    'PARAMETROS.VIEW',
    
    // Auditoria
    'AUDITORIA.VIEW',
    'AUDITORIA.EXPORT',
  ],

  // VIGILANCIA tem permissões operacionais de vigilância
  VIGILANCIA: [
    // Dashboard
    'DASHBOARD.VIEW',
    
    // Mapa
    'MAPA.VIEW',
    'MAPA.EXPORT',
    
    // Previsão
    'PREVISAO.VIEW',
    
    // Vigilância Entomológica
    'VIGILANCIA_ENTOMOLOGICA.VIEW',
    'VIGILANCIA_ENTOMOLOGICA.CREATE',
    'VIGILANCIA_ENTOMOLOGICA.EDIT',
    'VIGILANCIA_ENTOMOLOGICA.EXPORT',
    
    // Vigilância Epidemiológica
    'VIGILANCIA_EPIDEMIOLOGICA.VIEW',
    'VIGILANCIA_EPIDEMIOLOGICA.CREATE',
    'VIGILANCIA_EPIDEMIOLOGICA.EDIT',
    'VIGILANCIA_EPIDEMIOLOGICA.EXPORT',
    
    // Resposta Operacional
    'RESPOSTA_OPERACIONAL.VIEW',
    'RESPOSTA_OPERACIONAL.CREATE',
    
    // Relatórios
    'RELATORIOS.VIEW',
    'RELATORIOS.EXPORT',
    
    // Denúncia
    'DENUNCIA.VIEW',
  ],

  // CAMPO tem permissões básicas de coleta de dados
  CAMPO: [
    // Dashboard (apenas visualização básica)
    'DASHBOARD.VIEW',
    
    // Mapa (apenas visualização)
    'MAPA.VIEW',
    
    // Vigilância Entomológica (coleta de dados)
    'VIGILANCIA_ENTOMOLOGICA.VIEW',
    'VIGILANCIA_ENTOMOLOGICA.CREATE',
    
    // Vigilância Epidemiológica (coleta de dados)
    'VIGILANCIA_EPIDEMIOLOGICA.VIEW',
    'VIGILANCIA_EPIDEMIOLOGICA.CREATE',
    
    // Resposta Operacional (execução no campo)
    'RESPOSTA_OPERACIONAL.VIEW',
    'RESPOSTA_OPERACIONAL.EXECUTE',
    
    // Denúncia
    'DENUNCIA.VIEW',
    'DENUNCIA.CREATE',
  ],
}

/**
 * Verificar se usuário tem permissão específica
 */
export function hasPermission(userRoles: UserRole[], permission: Permission): boolean {
  if (!userRoles || userRoles.length === 0) return false
  
  // Verificar se alguma das roles do usuário tem a permissão
  return userRoles.some(role => {
    const rolePermissions = ROLE_PERMISSIONS[role] || []
    return rolePermissions.includes(permission)
  })
}

/**
 * Verificar se usuário tem todas as permissões
 */
export function hasAllPermissions(userRoles: UserRole[], permissions: Permission[]): boolean {
  return permissions.every(permission => hasPermission(userRoles, permission))
}

/**
 * Verificar se usuário tem pelo menos uma das permissões
 */
export function hasAnyPermission(userRoles: UserRole[], permissions: Permission[]): boolean {
  return permissions.some(permission => hasPermission(userRoles, permission))
}

/**
 * Obter todas as permissões de um conjunto de roles
 */
export function getPermissions(userRoles: UserRole[]): Permission[] {
  const allPermissions = new Set<Permission>()
  
  userRoles.forEach(role => {
    const rolePermissions = ROLE_PERMISSIONS[role] || []
    rolePermissions.forEach(p => allPermissions.add(p))
  })
  
  return Array.from(allPermissions)
}

/**
 * Verificar se usuário pode realizar ação em recurso
 */
export function can(
  userRoles: UserRole[], 
  action: PermissionAction, 
  resource: PermissionResource
): boolean {
  const permission: Permission = `${resource}.${action}`
  return hasPermission(userRoles, permission)
}

/**
 * Obter permissões faltantes
 */
export function getMissingPermissions(
  userRoles: UserRole[], 
  requiredPermissions: Permission[]
): Permission[] {
  return requiredPermissions.filter(p => !hasPermission(userRoles, p))
}

/**
 * Verificar nível de acesso a um recurso
 * Retorna a ação mais permissiva que o usuário pode realizar
 */
export function getAccessLevel(
  userRoles: UserRole[], 
  resource: PermissionResource
): PermissionAction | null {
  const actionOrder: PermissionAction[] = ['ADMIN', 'DELETE', 'EDIT', 'CREATE', 'EXECUTE', 'EXPORT', 'VIEW']
  
  for (const action of actionOrder) {
    if (can(userRoles, action, resource)) {
      return action
    }
  }
  
  return null
}

/**
 * Permissões agrupadas por recurso para UI
 */
export const PERMISSIONS_BY_RESOURCE: Record<PermissionResource, Permission[]> = {
  DASHBOARD: ['DASHBOARD.VIEW', 'DASHBOARD.EXPORT', 'DASHBOARD.ADMIN'],
  MAPA: ['MAPA.VIEW', 'MAPA.EDIT', 'MAPA.EXPORT', 'MAPA.ADMIN'],
  PREVISAO: ['PREVISAO.VIEW', 'PREVISAO.CREATE', 'PREVISAO.EDIT', 'PREVISAO.EXECUTE', 'PREVISAO.EXPORT'],
  VIGILANCIA_ENTOMOLOGICA: [
    'VIGILANCIA_ENTOMOLOGICA.VIEW',
    'VIGILANCIA_ENTOMOLOGICA.CREATE',
    'VIGILANCIA_ENTOMOLOGICA.EDIT',
    'VIGILANCIA_ENTOMOLOGICA.DELETE',
    'VIGILANCIA_ENTOMOLOGICA.EXPORT',
    'VIGILANCIA_ENTOMOLOGICA.ADMIN'
  ],
  VIGILANCIA_EPIDEMIOLOGICA: [
    'VIGILANCIA_EPIDEMIOLOGICA.VIEW',
    'VIGILANCIA_EPIDEMIOLOGICA.CREATE',
    'VIGILANCIA_EPIDEMIOLOGICA.EDIT',
    'VIGILANCIA_EPIDEMIOLOGICA.DELETE',
    'VIGILANCIA_EPIDEMIOLOGICA.EXPORT',
    'VIGILANCIA_EPIDEMIOLOGICA.ADMIN'
  ],
  RESPOSTA_OPERACIONAL: [
    'RESPOSTA_OPERACIONAL.VIEW',
    'RESPOSTA_OPERACIONAL.CREATE',
    'RESPOSTA_OPERACIONAL.EDIT',
    'RESPOSTA_OPERACIONAL.DELETE',
    'RESPOSTA_OPERACIONAL.EXECUTE',
    'RESPOSTA_OPERACIONAL.ADMIN'
  ],
  RELATORIOS: ['RELATORIOS.VIEW', 'RELATORIOS.CREATE', 'RELATORIOS.EXPORT', 'RELATORIOS.ADMIN'],
  ETL: ['ETL.VIEW', 'ETL.EXECUTE', 'ETL.ADMIN'],
  ADMIN: ['ADMIN.VIEW', 'ADMIN.CREATE', 'ADMIN.EDIT', 'ADMIN.DELETE', 'ADMIN.ADMIN'],
  OBSERVABILIDADE: ['OBSERVABILIDADE.VIEW', 'OBSERVABILIDADE.ADMIN'],
  DENUNCIA: ['DENUNCIA.VIEW', 'DENUNCIA.CREATE'],
  USUARIOS: ['USUARIOS.VIEW', 'USUARIOS.CREATE', 'USUARIOS.EDIT', 'USUARIOS.DELETE'],
  PARAMETROS: ['PARAMETROS.VIEW', 'PARAMETROS.EDIT'],
  AUDITORIA: ['AUDITORIA.VIEW', 'AUDITORIA.EXPORT'],
}
