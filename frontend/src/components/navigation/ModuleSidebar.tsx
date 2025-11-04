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
    '/docs': 'documentacao',
    '/lgpd': 'lgpd',
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

const CATEGORY_ORDER: NavCategory[] = ['ANALISE', 'MAPEAMENTO', 'INDICADORES', 'CONTROLE', 'OPERACIONAL']

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
  const location = useLocation()
  const { pathname, search } = location

  const module = useMemo(() => resolveActiveModule(pathname), [pathname])
  const groups = useMemo(() => groupByCategory(module?.functions || []), [module])

  const isActive = (path: string) => {
    if (path.includes(':')) return false
    // support query params matching
    const [base, q] = path.split('?')
    if (!(pathname === base || pathname.startsWith(base + '/'))) return false
    if (!q) return true
    const target = new URLSearchParams(q)
    const current = new URLSearchParams(search)
    for (const [k, v] of target.entries()) {
      if (current.get(k) !== v) return false
    }
    return true
  }

  if (!module) return null

  return (
    <aside id="app-submenu" data-app-nav="secondary" className="hidden lg:block">
      <div className="module-header">
        <div className="module-label">Módulos</div>
        <div className="module-name">{module.name}</div>
        {module.description && (
          <div className="module-description">{module.description}</div>
        )}
      </div>

      <div className="p-3">
        {CATEGORY_ORDER.filter(c => groups[c]?.length).map((cat) => (
          <div key={cat} className="category-section">
            <div className="category-title">{categoryLabel[cat]}</div>
            <nav>
              {groups[cat]!.map(it => (
                <Link
                  key={it.id}
                  to={it.path.includes(':') ? '#' : it.path}
                  className={isActive(it.path) ? 'active' : ''}
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
