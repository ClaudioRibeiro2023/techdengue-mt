import { Link, useLocation } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import { NAVIGATION } from '@/navigation/map'
import Icon from '@/components/ui/Icon'
import pkg from '../../../package.json'

const GROUP_ORDER = ['Web Mapas', 'Dados', 'Vigilância', 'Operações', 'Serviços Técnicos', 'Sistema', 'Outros']

export default function AppSidebar() {
  const { pathname } = useLocation()
  const [query, setQuery] = useState('')

  const items = useMemo(() => NAVIGATION.modules.map(m => ({
    id: m.id,
    name: m.name,
    path: m.path,
    icon: m.icon,
    badge: m.badge,
    group: m.group || 'Outros',
  })), [])

  const isActive = (path: string) => pathname === path || pathname.startsWith(path + '/')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return items
    return items.filter(it => it.name.toLowerCase().includes(q))
  }, [items, query])

  const grouped = useMemo(() => {
    const groups: Record<string, typeof filtered> = {}
    for (const item of filtered) {
      const g = item.group
      if (!groups[g]) groups[g] = []
      groups[g].push(item)
    }
    return groups
  }, [filtered])

  const orderedGroupEntries = useMemo(() => {
    const entries = Object.entries(grouped)
    return entries.sort((a, b) => GROUP_ORDER.indexOf(a[0]) - GROUP_ORDER.indexOf(b[0]))
  }, [grouped])

  useEffect(() => {
    const root = document.documentElement
    const body = document.body
    const sidebar = document.getElementById('app-sidebar')

    const getFocusable = () => Array.from((sidebar?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )) || [])

    const onKeyDown = (e: KeyboardEvent) => {
      if (!root.classList.contains('mobile-sidebar-open')) return
      if (e.key === 'Escape') {
        root.classList.remove('mobile-sidebar-open')
        e.preventDefault()
        return
      }
      if (e.key !== 'Tab') return
      const focusable = getFocusable()
      if (focusable.length === 0) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      const active = document.activeElement as HTMLElement | null
      if (e.shiftKey) {
        if (!active || active === first) {
          last.focus()
          e.preventDefault()
        }
      } else {
        if (!active || active === last) {
          first.focus()
          e.preventDefault()
        }
      }
    }

    const observer = new MutationObserver(() => {
      const open = root.classList.contains('mobile-sidebar-open')
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

  return (
    <aside id="app-sidebar" data-app-nav="primary">
      <div className="app-sidebar-inner">
        <div className="app-brand">
          <div className="app-brand-row">
            <button
              className="collapse-btn"
              aria-label="Recolher menu principal"
              aria-expanded="true"
              title="Recolher menu"
              onClick={(e) => {
                const next = document.documentElement.classList.toggle('sidebar-collapsed')
                e.currentTarget.setAttribute('aria-expanded', (!next).toString())
              }}
            >
              <Icon name="ChevronsLeft" size={16} className="icon-left" />
              <Icon name="ChevronsRight" size={16} className="icon-right" />
            </button>
            <span className="brand-name">SIVEPI</span>
          </div>
          <span className="brand-sub">Sistema Integrado de Vigilância</span>
        </div>

        <div className="app-search">
          <input
            type="text"
            placeholder="Buscar aplicações..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>

        {orderedGroupEntries.map(([groupName, groupItems]) => (
          <div key={groupName} className="app-group" data-group={groupName}>
            <div className="app-section">{groupName}</div>
            <nav className="app-nav">
              {groupItems.map(it => (
                <Link
                  key={it.id}
                  to={it.path}
                  className={isActive(it.path) ? 'active' : ''}
                  title={it.name}
                >
                  {it.icon && <Icon name={it.icon} size={16} />}
                  <span className="label">{it.name}</span>
                  {it.badge && <span className="badge">{it.badge}</span>}
                </Link>
              ))}
            </nav>
          </div>
        ))}

        <div className="app-footer">
          <div className="legal">
            <div className="product">TechDengue</div>
            <div className="meta">v{pkg.version} · © {new Date().getFullYear()}</div>
            <div className="rights">Todos os direitos reservados</div>
          </div>
          <div className="links">
            <Link to="/docs" title="Documentação" className="footer-link">
              <Icon name="BookOpen" size={14} />
              <span>Documentação</span>
            </Link>
            <Link to="/lgpd" title="LGPD" className="footer-link">
              <Icon name="ShieldCheck" size={14} />
              <span>LGPD</span>
            </Link>
          </div>
        </div>
      </div>
    </aside>
  )
}
