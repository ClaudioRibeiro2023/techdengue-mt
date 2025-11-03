import { Link, useLocation } from 'react-router-dom'
import { useMemo } from 'react'
import { NAVIGATION } from '@/navigation/map'
import type { AppModule, FunctionItem, NavCategory } from '@/navigation/types'

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

  if (!module) return null

  return (
    <aside id="app-submenu" data-app-nav="secondary" className="hidden lg:block w-72 border-r bg-white/80 backdrop-blur-sm">
      <div className="p-4 border-b">
        <div className="text-xs uppercase text-gray-500">Módulos</div>
        <div className="font-semibold text-gray-900">{module.name}</div>
        {module.description && (
          <div className="text-xs text-gray-500 mt-1">{module.description}</div>
        )}
      </div>

      <div className="p-3 space-y-6">
        {Object.entries(groups).map(([cat, items]) => (
          <div key={cat}>
            <div className="text-[10px] tracking-wide font-semibold text-gray-500 uppercase px-2 mb-2">
              {categoryLabel[cat as NavCategory] || cat}
            </div>
            <nav className="flex flex-col gap-1">
              {items.map(it => (
                <Link
                  key={it.id}
                  to={it.path.includes(':') ? '#' : it.path}
                  className="px-3 py-2 rounded-md text-sm text-gray-700 hover:bg-gray-100"
                  title={it.name}
                >
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
