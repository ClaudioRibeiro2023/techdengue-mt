import { Link, useLocation } from 'react-router-dom'
import { useMemo } from 'react'
import { NAVIGATION } from '@/navigation/map'
import type { AppModule, FunctionItem, NavCategory } from '@/navigation/types'
import Icon from '@/components/ui/Icon'

function resolveActiveModule(pathname: string): AppModule | undefined {
  // Map pages to module IDs
  const mapByPrefix: Record<string, string> = {
    '/mapa': 'mapa-vivo',
    '/dashboard': 'dashboard-executivo',
    '/etl': 'etl-integracao',
    '/relatorios': 'relatorios',
    '/denuncia': 'e-denuncia',
  }
  const matchedPrefix = Object.keys(mapByPrefix).find(p => pathname.startsWith(p))
  if (matchedPrefix) return NAVIGATION.modules.find(m => m.id === mapByPrefix[matchedPrefix])

  // /modulos/:moduleId
  const segs = pathname.split('/').filter(Boolean)
  if (segs[0] === 'modulos' && segs[1]) {
    return NAVIGATION.modules.find(m => m.id === segs[1])
  }
  return undefined
}

const categoryLabel: Record<NavCategory, string> = {
  ANALISE: 'Análise',
  MAPEAMENTO: 'Mapeamento',
  INDICADORES: 'Indicadores',
  CONTROLE: 'Controle',
  OPERACIONAL: 'Operacional',
}

function groupByCategory(items: FunctionItem[]) {
  const groups: Record<string, FunctionItem[]> = {}
  for (const it of items) {
    const cat = it.category || 'OPERACIONAL'
    groups[cat] = groups[cat] || []
    groups[cat].push(it)
  }
  return groups
}

export default function ModuleSidebar() {
  const { pathname } = useLocation()

  const module = useMemo(() => resolveActiveModule(pathname), [pathname])
  const groups = useMemo(() => groupByCategory(module?.functions || []), [module])

  const isActive = (path: string) => {
    if (path.includes(':')) return false
    // Exact match or starts with path
    return pathname === path || pathname.startsWith(path + '/')
  }

  if (!module) return null

  return (
    <aside id="app-submenu" data-app-nav="secondary" className="hidden lg:block w-72 border-r bg-white/80 backdrop-blur-sm">
      <div className="module-header p-4 border-b bg-gradient-to-b from-gray-50 to-white">
        <div className="module-label text-xs uppercase text-gray-500">Módulos</div>
        <div className="module-name font-semibold text-gray-900">{module.name}</div>
        {module.description && (
          <div className="module-description text-xs text-gray-500 mt-1">{module.description}</div>
        )}
      </div>

      <div className="p-3 space-y-6">
        {Object.entries(groups).map(([cat, items]) => (
          <div key={cat} className="category-section">
            <div className="category-title text-[10px] tracking-wide font-semibold text-gray-500 uppercase px-2 mb-2">
              {categoryLabel[cat as NavCategory] || cat}
            </div>
            <nav className="flex flex-col gap-1">
              {items.map(it => (
                <Link
                  key={it.id}
                  to={it.path.includes(':') ? '#' : it.path}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm hover:bg-gray-100 transition-all ${
                    isActive(it.path) 
                      ? 'active bg-blue-50 text-blue-600 font-semibold border-l-3 border-blue-600' 
                      : 'text-gray-700'
                  }`}
                  title={it.name}
                  onClick={e => it.path.includes(':') && e.preventDefault()}
                >
                  {it.icon && <Icon name={it.icon} size={16} />}
                  {it.name}
                </Link>
              ))}
            </nav>
          </div>
        ))}
      </div>
    </aside>
  )
}
