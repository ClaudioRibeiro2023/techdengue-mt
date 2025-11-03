import { Link, useLocation } from 'react-router-dom'
import { useMemo } from 'react'
import { NAVIGATION } from '@/navigation/map'
import Icon from '@/components/ui/Icon'
import type { AppModule } from '@/navigation/types'

function resolveActiveModule(pathname: string): AppModule | undefined {
  const segs = pathname.split('/').filter(Boolean)
  if (['mapa', 'dashboard', 'etl', 'relatorios', 'denuncia'].includes(segs[0])) {
    const map: Record<string, string> = {
      mapa: 'mapa-vivo',
      dashboard: 'dashboard-executivo',
      etl: 'etl-integracao',
      relatorios: 'relatorios',
      denuncia: 'e-denuncia',
    }
    return NAVIGATION.modules.find(m => m.id === map[segs[0]])
  }
  if (segs[0] === 'modulos' && segs[1]) {
    return NAVIGATION.modules.find(m => m.id === segs[1])
  }
  return undefined
}

export default function ModuleTopbar() {
  const { pathname } = useLocation()

  const module = useMemo(() => resolveActiveModule(pathname), [pathname])

  const isActive = (path: string) => {
    if (path.includes(':')) return false
    // Exact match or starts with path
    return pathname === path || pathname.startsWith(path + '/')
  }

  if (!module || !module.functions?.length) return null

  return (
    <div id="app-topbar" data-app-nav="tertiary" className="sticky top-0 z-20 bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60 border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="h-12 flex items-center gap-2 overflow-x-auto no-scrollbar">
          {module.functions.map(fn => (
            <Link
              key={fn.id}
              to={fn.path.includes(':') ? '#' : fn.path}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm hover:bg-gray-100 whitespace-nowrap ${
                isActive(fn.path) ? 'active text-blue-600 font-semibold' : 'text-gray-700'
              }`}
              title={fn.name}
              onClick={e => fn.path.includes(':') && e.preventDefault()}
            >
              {fn.icon && <Icon name={fn.icon} size={14} />}
              {fn.name}
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
