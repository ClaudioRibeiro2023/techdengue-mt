import { Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { UserRole } from '@/config/auth'
import { Map, BarChart3, Upload, FileText, TrendingUp, Users, AlertTriangle, type LucideIcon } from 'lucide-react'
import { NAVIGATION } from '@/navigation/map'

export default function HomePage() {
  const { user, hasRole } = useAuth()

  const profile = user?.profile as { name?: string; preferred_username?: string } | undefined
  const userName = profile?.name || profile?.preferred_username || 'Usuário'

  const iconByModule: Record<string, LucideIcon> = {
    'mapa-vivo': Map,
    'dashboard-executivo': BarChart3,
    'etl-integracao': Upload,
    'relatorios': FileText,
  }

  const colorByModule: Record<string, string> = {
    'mapa-vivo': 'bg-blue-500',
    'dashboard-executivo': 'bg-green-500',
    'etl-integracao': 'bg-purple-500',
    'relatorios': 'bg-orange-500',
  }

  const features = NAVIGATION.modules
    .filter(m => m.topNav)
    .map(m => ({
      id: m.id,
      name: m.name,
      description: m.description,
      icon: iconByModule[m.id] || Map,
      href: m.path,
      color: colorByModule[m.id] || 'bg-slate-500',
      requiresRole: m.id === 'etl-integracao' ? 'ADMIN' : undefined,
    }))

  const stats = [
    { label: 'Casos Notificados', value: '1,234', icon: TrendingUp, change: '+12%' },
    { label: 'Atividades de Campo', value: '567', icon: Users, change: '+8%' },
    { label: 'Alertas Ativos', value: '23', icon: AlertTriangle, change: '-5%' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Bem-vindo, {userName}!
          </h1>
          <p className="text-lg text-gray-600">
            Sistema de Monitoramento e Controle do Aedes aegypti
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {stats.map((stat) => {
            const Icon = stat.icon
            return (
              <div
                key={stat.label}
                className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <Icon className="w-8 h-8 text-blue-600" />
                  <span className="text-sm font-medium text-green-600">
                    {stat.change}
                  </span>
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            )
          })}
        </div>

        {/* Feature Cards */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Módulos do Sistema
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature) => {
              const Icon = feature.icon
              const isDisabled = feature.requiresRole && !hasRole(feature.requiresRole as UserRole)

              return (
                <Link
                  key={feature.name}
                  to={feature.href}
                  className={`
                    bg-white rounded-xl shadow-md p-6 transition-all
                    ${isDisabled
                      ? 'opacity-50 cursor-not-allowed'
                      : 'hover:shadow-xl hover:-translate-y-1'
                    }
                  `}
                  onClick={(e) => isDisabled && e.preventDefault()}
                >
                  <div
                    className={`${feature.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}
                  >
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    {feature.description}
                  </p>
                  {feature.requiresRole && (
                    <span className="inline-block px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-600">
                      {feature.requiresRole}
                    </span>
                  )}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
