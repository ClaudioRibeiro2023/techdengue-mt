import { Link, useLocation } from 'react-router-dom'
import { useEffect, useMemo } from 'react'
import { NAVIGATION } from '@/navigation/map'
import type { AppModule, FunctionItem, NavCategory } from '@/navigation/types'
import Icon from '@/components/ui/Icon'
import { useAuth } from '@/contexts/AuthContext'

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
  const { hasAnyRole } = useAuth()
  const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

  const module = useMemo(() => resolveActiveModule(pathname), [pathname])
  const visibleFunctions = useMemo(() => {
    const list = module?.functions || []
    return list.filter(fn => DEMO_MODE || !fn.roles || hasAnyRole(fn.roles))
  }, [module, hasAnyRole, DEMO_MODE])
  const groups = useMemo(() => groupByCategory(visibleFunctions), [visibleFunctions])

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

  useEffect(() => {
    const root = document.documentElement
    const body = document.body
    const subnav = document.getElementById('app-submenu')

    const getFocusable = () => Array.from((subnav?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )) || [])

    const onKeyDown = (e: KeyboardEvent) => {
      if (!root.classList.contains('mobile-submenu-open')) return
      if (e.key === 'Escape') {
        root.classList.remove('mobile-submenu-open')
        e.preventDefault()
        return
      }
      if (e.key !== 'Tab') return
      const focusable = getFocusable()
      if (!focusable.length) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      const active = document.activeElement as HTMLElement | null
      if (e.shiftKey) {
        if (!active || active === first) {
          last.focus(); e.preventDefault()
        }
      } else {
        if (!active || active === last) {
          first.focus(); e.preventDefault()
        }
      }
    }

    const observer = new MutationObserver(() => {
      const open = root.classList.contains('mobile-submenu-open')
      if (open) {
        body.style.overflow = 'hidden'
        const focusable = getFocusable()
        if (focusable.length) focusable[0].focus()
        document.addEventListener('keydown', onKeyDown)
      } else {
        body.style.overflow = ''
        document.removeEventListener('keydown', onKeyDown)
      }
    })

    observer.observe(root, { attributes: true, attributeFilter: ['class'] })
    return () => {
      observer.disconnect()
      document.removeEventListener('keydown', onKeyDown)
      body.style.overflow = ''
    }
  }, [])

  if (!module) return null
  if (!DEMO_MODE && module.roles && !hasAnyRole(module.roles)) return null

  return (
    <aside id="app-submenu" data-app-nav="secondary" className="hidden lg:block">
      <div className="module-header">
        <div className="submenu-header-row">
          <button
            className="collapse-btn"
            aria-label="Recolher submenu"
            aria-expanded="true"
            title="Recolher"
            onClick={(e) => {
              const next = document.documentElement.classList.toggle('subnav-collapsed')
              e.currentTarget.setAttribute('aria-expanded', (!next).toString())
              localStorage.setItem('subnav-collapsed', next ? '1' : '0')
            }}
          >
            <Icon name="ChevronsLeft" size={16} className="icon-left" />
            <Icon name="ChevronsRight" size={16} className="icon-right" />
          </button>
          <div>
            <div className="module-label">Módulos</div>
            <div className="module-name">{module.name}</div>
          </div>
        </div>
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
                  aria-current={isActive(it.path) ? 'page' : undefined}
                  title={it.name}
                  onClick={e => it.path.includes(':') && e.preventDefault()}
                >
                  {it.icon && <Icon name={it.icon} size={16} />}
                  <div className="link-text">
                    <span className="label">{it.name}</span>
                    {it.subtitle && <span className="item-subtitle">{it.subtitle}</span>}
                  </div>
                  <span className="item-category">{categoryLabel[((it.category || 'OPERACIONAL') as NavCategory)]}</span>
                </Link>
              ))}
            </nav>
          </div>
        ))}
      </div>
    </aside>
  )
}
