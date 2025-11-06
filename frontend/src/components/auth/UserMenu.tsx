import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { LogOut, User, Shield, ChevronDown } from 'lucide-react'

export default function UserMenu() {
  const { user, logout } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  const userName = user?.profile?.name || (user?.profile as { preferred_username?: string })?.preferred_username || 'Usuário'
  const userEmail = user?.profile?.email || ''
  const userRoles = (user?.profile as { realm_access?: { roles?: string[] } })?.realm_access?.roles || []

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = async () => {
    setIsOpen(false)
    
    try {
      // Usa o logout do OIDC que já inclui o id_token_hint automaticamente
      await logout()
    } catch (error) {
      console.error('Logout failed:', error)
      // Fallback: limpa storage e redireciona para home
      localStorage.clear()
      sessionStorage.clear()
      window.location.href = '/'
    }
  }

  const handleProfile = () => {
    setIsOpen(false)
    navigate('/profile')
  }

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
          {userName.charAt(0).toUpperCase()}
        </div>
        <div className="hidden md:block text-left">
          <div className="text-sm font-medium text-gray-900">{userName}</div>
          <div className="text-xs text-gray-500">{userEmail}</div>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
          {/* User Info */}
          <div className="px-4 py-3 border-b border-gray-100">
            <div className="text-sm font-medium text-gray-900">{userName}</div>
            {userEmail && (
              <div className="text-xs text-gray-500">{userEmail}</div>
            )}
          </div>

          {/* Roles */}
          {userRoles.length > 0 && (
            <div className="px-4 py-2 border-b border-gray-100">
              <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                <Shield className="w-3 h-3" />
                <span>Permissões:</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {userRoles.map((role: string) => (
                  <span
                    key={role}
                    className="inline-block px-2 py-0.5 text-xs font-medium rounded bg-blue-100 text-blue-700"
                  >
                    {role}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Menu Items */}
          <button
            onClick={handleProfile}
            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <User className="w-4 h-4" />
            <span>Meu Perfil</span>
          </button>

          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sair</span>
          </button>
        </div>
      )}
    </div>
  )
}
