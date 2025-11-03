import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import UserMenu from '@/components/auth/UserMenu'
import { Menu, X, Map, BarChart3, Upload, AlertTriangle, Settings, Sun, Moon, ChevronsLeft, ChevronsRight, ChevronRight, type LucideIcon } from 'lucide-react'
import { useMemo, useState } from 'react'
import { NAVIGATION } from '@/navigation/map'

export default function Header() {
  const { isAuthenticated } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [dark, setDark] = useState(false)
  const { pathname } = useLocation()

  const topModules = useMemo(() => NAVIGATION.modules.filter(m => m.topNav), [])

  const iconByModule: Record<string, LucideIcon> = {
    'mapa-vivo': Map,
    'dashboard-executivo': BarChart3,
    'etl-integracao': Upload,
    'relatorios': BarChart3,
  }

  function resolveActiveModule(path: string) {
    const mapByPrefix: Record<string, string> = {
      '/mapa': 'mapa-vivo',
      '/dashboard': 'dashboard-executivo',
      '/etl': 'etl-integracao',
      '/relatorios': 'relatorios',
      '/denuncia': 'e-denuncia',
    }
    const matched = Object.keys(mapByPrefix).find(p => path.startsWith(p))
    if (matched) return NAVIGATION.modules.find(m => m.id === mapByPrefix[matched])
    const segs = path.split('/').filter(Boolean)
    if (segs[0] === 'modulos' && segs[1]) return NAVIGATION.modules.find(m => m.id === segs[1])
    return undefined
  }
  const activeModule = useMemo(() => resolveActiveModule(pathname), [pathname])

  const toggleDark = () => {
    const next = !dark
    setDark(next)
    document.documentElement.classList.toggle('theme-dark', next)
  }

  const toggleSidebar = () => {
    document.documentElement.classList.toggle('sidebar-collapsed')
  }

  const toggleFunctions = () => {
    document.documentElement.classList.toggle('functions-collapsed')
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-[920]">
      <div className="px-3 sm:px-4 lg:px-6">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center gap-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: 'var(--brand-primary)' }}>
                <span className="text-2xl">🦟</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">TechDengue</h1>
                <p className="text-xs text-gray-500 hidden sm:block">Vigilância em Saúde</p>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation removed: SIVEPI usa apenas sidebars */}

          {/* Right Side */}
          <div className="flex items-center gap-2">
            {/* Collapses */}
            <button onClick={toggleSidebar} className="hidden md:inline-flex p-2 rounded-lg hover:bg-gray-100" title="Recolher menu principal">
              <ChevronsLeft className="w-5 h-5" />
            </button>
            <button onClick={toggleFunctions} className="hidden lg:inline-flex p-2 rounded-lg hover:bg-gray-100" title="Recolher painel de funções">
              <ChevronsRight className="w-5 h-5" />
            </button>

            {/* Dark mode */}
            <button onClick={toggleDark} className="p-2 rounded-lg hover:bg-gray-100" title="Alternar tema">
              {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>

            {/* Settings */}
            <Link to="/profile" className="p-2 rounded-lg hover:bg-gray-100" title="Configurações">
              <Settings className="w-5 h-5" />
            </Link>
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
                className="px-4 py-2 text-white rounded-lg transition-colors text-sm font-medium"
                style={{ background: 'var(--brand-primary)' }}
              >
                Entrar
              </Link>
            )}
          </div>
        </div>

        {/* Breadcrumb row */}
        {isAuthenticated && (
          <div className="h-12 flex items-center justify-between border-t border-gray-200">
            <nav className="flex items-center text-sm text-gray-500 gap-2">
              <Link to="/" className="hover:text-gray-700">SIVEPI</Link>
              <ChevronRight className="w-4 h-4" />
              {activeModule?.group && (
                <>
                  <span className="uppercase tracking-wider">{activeModule.group}</span>
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
              <span className="font-semibold text-gray-700">{activeModule?.name || 'Início'}</span>
            </nav>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 text-sm rounded-md border border-gray-200 hover:bg-gray-50">Filtros</button>
              <button className="px-3 py-1.5 text-sm rounded-md border border-gray-200 hover:bg-gray-50">Análise</button>
              <button className="px-3 py-1.5 text-sm rounded-md border border-gray-200 hover:bg-gray-50">Dados</button>
            </div>
          </div>
        )}

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
