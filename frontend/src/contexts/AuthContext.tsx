import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, UserManager } from 'oidc-client-ts'
import { oidcConfig, UserRole } from '@/config/auth'
import { logger } from '@/utils/logger'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: () => Promise<void>
  logout: () => Promise<void>
  hasRole: (role: UserRole) => boolean
  hasAnyRole: (roles: UserRole[]) => boolean
  getAccessToken: () => Promise<string | null>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

let userManager: UserManager | null = null

const getUserManager = (): UserManager => {
  if (!userManager) {
    userManager = new UserManager(oidcConfig)
  }
  return userManager
}

function RealAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const manager = getUserManager()

    manager.getUser().then((loadedUser) => {
      setUser(loadedUser)
      setIsLoading(false)
      if (loadedUser) {
        const profile = loadedUser.profile as { email?: string; preferred_username?: string }
        logger.auth('login', {
          userId: profile.email || profile.preferred_username,
          sessionStart: new Date(loadedUser.profile.iat! * 1000).toISOString()
        })
      }
    }).catch((error: unknown) => {
      logger.error('Failed to load user', {}, error as Error)
      setIsLoading(false)
    })

    const handleUserLoaded = (loadedUser: User) => {
      setUser(loadedUser)
      logger.auth('token-renewed', { timestamp: new Date().toISOString() })
    }
    const handleUserUnloaded = () => {
      setUser(null)
      logger.auth('logout')
    }
    const handleAccessTokenExpiring = () => {
      logger.warn('Token expirando em breve')
    }
    const handleAccessTokenExpired = () => {
      logger.auth('token-expired')
      setUser(null)
    }
    const handleSilentRenewError = (error: Error) => {
      logger.error('Erro ao renovar token silenciosamente', {}, error)
    }

    manager.events.addUserLoaded(handleUserLoaded)
    manager.events.addUserUnloaded(handleUserUnloaded)
    manager.events.addAccessTokenExpiring(handleAccessTokenExpiring)
    manager.events.addAccessTokenExpired(handleAccessTokenExpired)
    manager.events.addSilentRenewError(handleSilentRenewError)

    return () => {
      manager.events.removeUserLoaded(handleUserLoaded)
      manager.events.removeUserUnloaded(handleUserUnloaded)
      manager.events.removeAccessTokenExpiring(handleAccessTokenExpiring)
      manager.events.removeAccessTokenExpired(handleAccessTokenExpired)
      manager.events.removeSilentRenewError(handleSilentRenewError)
    }
  }, [])

  const login = async () => {
    try { await getUserManager().signinRedirect() } catch (error) { console.error('Login failed:', error); throw error }
  }

  const logout = async () => {
    const manager = getUserManager()
    let user: User | null = null
    try {
      user = await manager.getUser()
      if (!user || !user.id_token) user = await manager.signinSilent()
    } catch (e) { /* no-op */ }

    const postLogout = oidcConfig.post_logout_redirect_uri || `${window.location.origin}/`
    const endSession = oidcConfig.metadata?.end_session_endpoint
    if (endSession) {
      const params = new URLSearchParams()
      params.set('post_logout_redirect_uri', postLogout)
      if (user?.id_token) params.set('id_token_hint', user.id_token)
      else params.set('client_id', oidcConfig.client_id)
      try { await manager.removeUser() } catch (e) { void e }
      window.location.href = `${endSession}?${params.toString()}`
      return
    }
    try { await manager.removeUser() } catch (e) { void e }
    window.location.href = postLogout
  }

  const hasRole = (role: UserRole): boolean => {
    if (!user) {
      logger.roleCheck('deny', role, { reason: 'user not authenticated' })
      return false
    }
    
    const profile = user.profile as { email?: string; preferred_username?: string; realm_access?: { roles?: string[] } }
    const profileRoles = profile?.realm_access?.roles || []
    let tokenRoles: string[] = []
    
    try {
      const token = (user as unknown as { access_token?: string }).access_token
      if (token) {
        const payloadPart = token.split('.')[1]
        if (payloadPart) {
          const json = JSON.parse(atob(payloadPart.replace(/-/g, '+').replace(/_/g, '/')))
          const ra = (json && json.realm_access && Array.isArray(json.realm_access.roles)) ? json.realm_access.roles : []
          const rc = (json && json.resource_access && oidcConfig.client_id && json.resource_access[oidcConfig.client_id] && Array.isArray(json.resource_access[oidcConfig.client_id].roles)) ? json.resource_access[oidcConfig.client_id].roles : []
          tokenRoles = [...ra, ...rc]
        }
      }
    } catch (e) {
      logger.error('Erro ao decodificar token para verificação de role', { role }, e as Error)
    }

    const all = new Set<string>([...profileRoles, ...tokenRoles].map(r => String(r)))
    const hasAccess = all.has(role)
    
    logger.roleCheck(
      hasAccess ? 'grant' : 'deny',
      role,
      {
        userId: profile.email || profile.preferred_username,
        availableRoles: Array.from(all),
        source: tokenRoles.length > 0 ? 'token' : 'profile'
      }
    )
    
    return hasAccess
  }
  const hasAnyRole = (roles: UserRole[]): boolean => {
    if (!user) {
      logger.roleCheck('deny', roles, { reason: 'user not authenticated' })
      return false
    }
    
    const result = roles.some((role) => hasRole(role))
    
    if (!result) {
      const profile = user.profile as { email?: string; preferred_username?: string }
      logger.roleCheck('deny', roles, {
        userId: profile.email || profile.preferred_username,
        reason: 'none of the required roles matched'
      })
    }
    
    return result
  }
  const getAccessToken = async (): Promise<string | null> => {
    try {
      return (await getUserManager().getUser())?.access_token || null
    } catch (error) {
      logger.error('Failed to get access token', {}, error as Error)
      return null
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user && !user.expired,
    isLoading,
    login,
    logout,
    hasRole,
    hasAnyRole,
    getAccessToken,
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

function BypassAuthProvider({ children }: { children: ReactNode }) {
  const MODE = import.meta.env.MODE
  const ALL: UserRole[] = ['ADMIN', 'GESTOR', 'VIGILANCIA', 'CAMPO']
  const parseRoles = (): UserRole[] => {
    if (MODE !== 'e2e') return ALL
    let roles: string[] = []
    try {
      const ls = typeof window !== 'undefined' ? window.localStorage.getItem('e2e-roles') : null
      if (ls) roles = ls.split(',').map(s => s.trim().toUpperCase()).filter(Boolean)
      if (!roles.length && typeof window !== 'undefined') {
        const q = new URLSearchParams(window.location.search).get('roles')
        if (q) roles = q.split(',').map(s => s.trim().toUpperCase()).filter(Boolean)
      }
    } catch { /* no-op */ }
    const valid = roles.filter(r => (ALL as string[]).includes(r)) as UserRole[]
    return valid.length ? valid : ALL
  }
  const hasRole = (role: UserRole): boolean => {
    if (MODE === 'e2e') return parseRoles().includes(role)
    return true
  }
  const hasAnyRole = (roles: UserRole[]): boolean => {
    if (MODE === 'e2e') {
      const eff = parseRoles()
      return roles.some(r => eff.includes(r))
    }
    return true
  }
  const value: AuthContextType = {
    user: null,
    isAuthenticated: true,
    isLoading: false,
    login: async () => {},
    logout: async () => {},
    hasRole,
    hasAnyRole,
    getAccessToken: async () => null,
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'
  const MODE = import.meta.env.MODE
  const OVERRIDE = DEMO_MODE || MODE === 'e2e'
  return OVERRIDE ? <BypassAuthProvider>{children}</BypassAuthProvider> : <RealAuthProvider>{children}</RealAuthProvider>
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export { getUserManager }
