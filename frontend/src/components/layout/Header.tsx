import { Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import UserMenu from '@/components/auth/UserMenu'
import { Menu, X, Map, BarChart3, Upload, FileText, AlertTriangle, type LucideIcon } from 'lucide-react'
import { useMemo, useState } from 'react'
import { NAVIGATION } from '@/navigation/map'

export default function Header() {
  const { isAuthenticated } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const topModules = useMemo(() => NAVIGATION.modules.filter(m => m.topNav), [])

  const iconByModule: Record<string, LucideIcon> = {
    'mapa-vivo': Map,
    'dashboard-executivo': BarChart3,
    'etl-integracao': Upload,
    'relatorios': FileText,
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center gap-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🦟</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">TechDengue</h1>
                <p className="text-xs text-gray-500 hidden sm:block">Vigilância em Saúde</p>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation */}
          {isAuthenticated && (
            <nav className="hidden md:flex items-center gap-1">
              {topModules.map((mod) => {
                const Icon = iconByModule[mod.id] || Map
                return (
                  <Link
                    key={mod.id}
                    to={mod.path}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
                  >
                    <Icon className="w-4 h-4" />
                    {mod.name}
                  </Link>
                )
              })}
            </nav>
          )}

          {/* Right Side */}
          <div className="flex items-center gap-3">
            {/* e-Denúncia - Sempre visível (público) */}
            <Link
              to="/denuncia"
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-semibold shadow-sm"
            >
              <AlertTriangle className="w-4 h-4" />
              <span className="hidden sm:inline">Denunciar</span>
            </Link>

            {isAuthenticated ? (
              <>
                <UserMenu />
                {/* Mobile Menu Button */}
                <button
                  onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                  className="md:hidden p-2 rounded-lg hover:bg-gray-100"
                >
                  {isMobileMenuOpen ? (
                    <X className="w-6 h-6" />
                  ) : (
                    <Menu className="w-6 h-6" />
                  )}
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Entrar
              </Link>
            )}
          </div>
        </div>

        {/* Mobile Navigation */}
        {isAuthenticated && isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <nav className="flex flex-col gap-2">
              {topModules.map((mod) => {
                const Icon = iconByModule[mod.id] || Map
                return (
                  <Link
                    key={mod.id}
                    to={mod.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
                  >
                    <Icon className="w-5 h-5" />
                    {mod.name}
                  </Link>
                )
              })}
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
