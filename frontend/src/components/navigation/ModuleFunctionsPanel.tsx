import { Link, useLocation } from 'react-router-dom'
import { useMemo } from 'react'
import { NAVIGATION } from '@/navigation/map'
import Icon from '@/components/ui/Icon'
import type { AppModule, FunctionItem } from '@/navigation/types'

const DEFAULT_MODULE_ID = 'mapa-vivo'

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

export default function ModuleFunctionsPanel() {
  const location = useLocation()
  const { pathname, search } = location

  const module = useMemo(() => {
    return (
      resolveActiveModule(pathname) ||
      NAVIGATION.modules.find(m => m.id === DEFAULT_MODULE_ID)
    )
  }, [pathname])

  const isActive = (path: string) => {
    if (path.includes(':')) return false
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

  const CATEGORY_ORDER: Array<NonNullable<FunctionItem['category']>> = [
    'ANALISE',
    'MAPEAMENTO',
    'INDICADORES',
    'CONTROLE',
    'OPERACIONAL',
  ]

  const grouped = useMemo(() => {
    const by: Record<string, FunctionItem[]> = {}
    if (!module?.functions) return by
    for (const fn of module.functions) {
      if (!fn.category) continue
      if (!by[fn.category]) by[fn.category] = []
      by[fn.category].push(fn)
    }
    return by
  }, [module])

  if (!module || !module.functions?.length) return null

  return (
    <div className="module-functions-panel">
      <div className="functions-header">
        <h2>Ferramentas</h2>
        <button
          className="collapse-btn"
          title="Recolher"
          onClick={() => document.documentElement.classList.toggle('functions-collapsed')}
        >
          <Icon name="ChevronLeft" size={20} />
        </button>
      </div>

      {CATEGORY_ORDER.filter(cat => grouped[cat]?.length).map(cat => (
        <div key={cat} className="functions-section">
          <div className="functions-section-title">{cat}</div>
          <div className="functions-grid">
            {grouped[cat]!.map(fn => (
              <Link
                key={fn.id}
                to={fn.path.includes(':') ? '#' : fn.path}
                className={`function-card ${isActive(fn.path) ? 'active' : ''}`}
                title={fn.name}
                onClick={e => fn.path.includes(':') && e.preventDefault()}
              >
                <div className="function-icon">
                  {fn.icon && <Icon name={fn.icon} size={20} />}
                </div>
                <div className="function-label">{fn.name}</div>
                {fn.category && (
                  <div className="function-category">{fn.category}</div>
                )}
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
