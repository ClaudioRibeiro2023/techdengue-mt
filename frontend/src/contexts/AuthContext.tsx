import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, UserManager } from 'oidc-client-ts'
import { oidcConfig, UserRole } from '@/config/auth'

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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const manager = getUserManager()

    // Load user from storage on mount
    manager.getUser().then((loadedUser) => {
      setUser(loadedUser)
      setIsLoading(false)
    }).catch((error: unknown) => {
      console.error('Failed to load user:', error)
      setIsLoading(false)
    })

    // Listen for user loaded event
    const handleUserLoaded = (loadedUser: User) => {
      setUser(loadedUser)
    }

    // Listen for user unloaded event
    const handleUserUnloaded = () => {
      setUser(null)
    }

    // Listen for access token expiring
    const handleAccessTokenExpiring = () => {
      console.log('Access token expiring...')
    }

    // Listen for access token expired
    const handleAccessTokenExpired = () => {
      console.log('Access token expired')
      setUser(null)
    }

    // Listen for silent renew error
    const handleSilentRenewError = (error: Error) => {
      console.error('Silent renew error:', error)
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
    try {
      const manager = getUserManager()
      await manager.signinRedirect()
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      const manager = getUserManager()
      await manager.signoutRedirect()
    } catch (error) {
      console.error('Logout failed:', error)
      throw error
    }
  }

  const hasRole = (role: UserRole): boolean => {
    if (!user) return false
    const roles = (user.profile as any)?.realm_access?.roles || []
    return roles.includes(role)
  }

  const hasAnyRole = (roles: UserRole[]): boolean => {
    if (!user) return false
    return roles.some((role) => hasRole(role))
  }

  const getAccessToken = async (): Promise<string | null> => {
    try {
      const manager = getUserManager()
      const currentUser = await manager.getUser()
      return currentUser?.access_token || null
    } catch (error) {
      console.error('Failed to get access token:', error)
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

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export { getUserManager }
