import { Link, useLocation } from 'react-router-dom'
import { useEffect, useMemo, useRef, useState } from 'react'
import type { KeyboardEvent as ReactKeyboardEvent } from 'react'
import { NAVIGATION } from '@/navigation/map'
import Icon from '@/components/ui/Icon'
import type { AppModule, FunctionItem } from '@/navigation/types'
import { useAuth } from '@/contexts/AuthContext'

function resolveActiveModule(pathname: string): AppModule | undefined {
  const segs = pathname.split('/').filter(Boolean)
  
  if (['mapa', 'dashboard', 'etl', 'relatorios', 'denuncia', 'docs', 'lgpd'].includes(segs[0])) {
    const map: Record<string, string> = {
      mapa: 'mapa-vivo',
      dashboard: 'dashboard-executivo',
      etl: 'etl-integracao',
      relatorios: 'relatorios',
      denuncia: 'e-denuncia',
      docs: 'documentacao',
      lgpd: 'lgpd',
    }
    const mappedId = map[segs[0]]
    return NAVIGATION.modules.find(m => m.id === mappedId)
  }
  
  if (segs[0] === 'modulos' && segs[1]) {
    return NAVIGATION.modules.find(m => m.id === segs[1])
  }
  
  return undefined
}

export default function ModuleFunctionsPanel() {
  const location = useLocation()
  const { pathname, search } = location
  const { hasAnyRole } = useAuth()
  const [query, setQuery] = useState('')
  const searchRef = useRef<HTMLInputElement | null>(null)
  const [favorites, setFavorites] = useState<Set<string>>(new Set())
  const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

  // Load favorites from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem('nav-favorites:v1')
      if (raw) setFavorites(new Set(JSON.parse(raw)))
    } catch { void 0 }
  }, [])

  const toggleFavorite = (id: string) => {
    setFavorites(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      try { localStorage.setItem('nav-favorites:v1', JSON.stringify(Array.from(next))) } catch { void 0 }
      return next
    })
  }

  const module = useMemo(() => {
    return resolveActiveModule(pathname)
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
    const q = query.trim().toLowerCase()
    for (const fn of module.functions) {
      if (!DEMO_MODE && fn.roles && !hasAnyRole(fn.roles)) continue
      if (!fn.category) continue
      if (q) {
        const source = (fn.name + ' ' + (fn.subtitle || '')).toLowerCase()
        if (!source.includes(q)) continue
      }
      if (!by[fn.category]) by[fn.category] = []
      by[fn.category].push(fn)
    }
    return by
  }, [module, hasAnyRole, query, DEMO_MODE])

  const favoritesList = useMemo(() => {
    if (!module?.functions) return [] as FunctionItem[]
    const q = query.trim().toLowerCase()
    return module.functions.filter(fn => {
      if (!favorites.has(fn.id)) return false
      if (!DEMO_MODE && fn.roles && !hasAnyRole(fn.roles)) return false
      if (q) {
        const source = (fn.name + ' ' + (fn.subtitle || '')).toLowerCase()
        if (!source.includes(q)) return false
      }
      return true
    })
  }, [module, favorites, hasAnyRole, query, DEMO_MODE])

  const onGridKeyDown = (e: ReactKeyboardEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement
    if (!target || !target.closest('.functions-grid')) return
    if (!(target instanceof HTMLAnchorElement)) return
    const container = target.closest('.functions-grid') as HTMLElement | null
    if (!container) return
    const items = Array.from(container.querySelectorAll<HTMLAnchorElement>('a.function-card'))
    const index = items.indexOf(target)
    if (index < 0) return

    const move = (delta: number) => {
      const next = items[index + delta]
      if (next) { next.focus(); e.preventDefault() }
    }

    const computeColumns = () => {
      // Count first row items by top offset
      const tops = items.map(el => el.getBoundingClientRect().top)
      const first = tops[0]
      let cols = 1
      for (let i = 1; i < tops.length; i++) {
        if (Math.abs(tops[i] - first) < 2) cols++
        else break
      }
      return cols
    }

    switch (e.key) {
      case 'ArrowRight':
        move(1)
        break
      case 'ArrowLeft':
        move(-1)
        break
      case 'ArrowDown': {
        const cols = computeColumns()
        move(cols)
        break
      }
      case 'ArrowUp': {
        const cols = computeColumns()
        move(-cols)
        break
      }
      case 'Home':
        if (items[0]) { items[0].focus(); e.preventDefault() }
        break
      case 'End':
        if (items[items.length - 1]) { items[items.length - 1].focus(); e.preventDefault() }
        break
      default:
        break
    }
  }

  if (!module || !module.functions?.length) return null
  if (!DEMO_MODE && module.roles && !hasAnyRole(module.roles)) return null

  return (
    <div className="module-functions-panel" id="module-functions-panel">
      <div className="functions-header">
        <button
          className="collapse-btn"
          aria-label="Recolher painel de ferramentas"
          aria-expanded="true"
          aria-controls="module-functions-panel"
          title="Recolher"
          onClick={(e) => {
            const next = document.documentElement.classList.toggle('functions-collapsed')
            e.currentTarget.setAttribute('aria-expanded', (!next).toString())
            localStorage.setItem('functions-collapsed', next ? '1' : '0')
          }}
        >
          <Icon name="ChevronsLeft" size={20} className="icon-left" />
          <Icon name="ChevronsRight" size={20} className="icon-right" />
        </button>
        <h2>Ferramentas</h2>
        <input
          ref={searchRef}
          type="search"
          placeholder="Buscar ferramentas..."
          aria-label="Buscar ferramentas"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="functions-search"
        />
      </div>

      {favoritesList.length > 0 && (
        <div className="functions-section">
          <div className="functions-section-title">Favoritos</div>
          <div className="functions-grid" onKeyDown={onGridKeyDown}>
            {favoritesList.map(fn => (
              <Link
                key={fn.id}
                to={fn.path.includes(':') ? '#' : fn.path}
                className={`function-card ${isActive(fn.path) ? 'active' : ''}`}
                aria-current={isActive(fn.path) ? 'page' : undefined}
                title={fn.subtitle ? `${fn.name} - ${fn.subtitle}` : fn.name}
                onClick={e => fn.path.includes(':') && e.preventDefault()}
              >
                <button
                  type="button"
                  className={`function-fav ${favorites.has(fn.id) ? 'on' : ''}`}
                  aria-pressed={favorites.has(fn.id)}
                  aria-label={favorites.has(fn.id) ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
                  onClick={(e) => { e.preventDefault(); e.stopPropagation(); toggleFavorite(fn.id) }}
                >
                  <Icon name="Star" size={14} />
                </button>
                <div className="function-icon">
                  {fn.icon && <Icon name={fn.icon} size={20} />}
                </div>
                <div className="function-label">{fn.name}</div>
                {fn.subtitle && (
                  <div className="function-subtitle">{fn.subtitle}</div>
                )}
                {fn.category && (
                  <div className="function-category">{fn.category}</div>
                )}
              </Link>
            ))}
          </div>
        </div>
      )}

      {CATEGORY_ORDER.filter(cat => grouped[cat]?.length).map(cat => (
        <div key={cat} className="functions-section">
          <div className="functions-section-title">{cat}</div>
          <div className="functions-grid" onKeyDown={onGridKeyDown}>
            {grouped[cat]!.map(fn => (
              <Link
                key={fn.id}
                to={fn.path.includes(':') ? '#' : fn.path}
                className={`function-card ${isActive(fn.path) ? 'active' : ''}`}
                aria-current={isActive(fn.path) ? 'page' : undefined}
                title={fn.subtitle ? `${fn.name} - ${fn.subtitle}` : fn.name}
                onClick={e => fn.path.includes(':') && e.preventDefault()}
              >
                <button
                  type="button"
                  className={`function-fav ${favorites.has(fn.id) ? 'on' : ''}`}
                  aria-pressed={favorites.has(fn.id)}
                  aria-label={favorites.has(fn.id) ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
                  onClick={(e) => { e.preventDefault(); e.stopPropagation(); toggleFavorite(fn.id) }}
                >
                  <Icon name="Star" size={14} />
                </button>
                <div className="function-icon">
                  {fn.icon && <Icon name={fn.icon} size={20} />}
                </div>
                <div className="function-label">{fn.name}</div>
                {fn.subtitle && (
                  <div className="function-subtitle">{fn.subtitle}</div>
                )}
                {fn.category && (
                  <div className="function-category">{fn.category}</div>
                )}
              </Link>
            ))}
          </div>
        </div>
      ))}

      {CATEGORY_ORDER.every(cat => !grouped[cat]?.length) && (
        <div className="functions-section functions-empty">
          <div className="functions-empty-message">Nenhuma ferramenta encontrada.</div>
        </div>
      )}
    </div>
  )
}

// Keyboard shortcut: Ctrl+K focuses the search
export function ModuleFunctionsPanelHotkeys() {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        const input = document.querySelector<HTMLInputElement>('.module-functions-panel .functions-header input[type="search"]')
        if (input) { e.preventDefault(); input.focus() }
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])
  return null
}
