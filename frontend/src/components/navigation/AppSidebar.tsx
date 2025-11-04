import { Link, useLocation } from 'react-router-dom'
import { useMemo, useState } from 'react'
import { NAVIGATION } from '@/navigation/map'
import Icon from '@/components/ui/Icon'

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

  const toggleSidebar = () => {
    document.documentElement.classList.toggle('sidebar-collapsed')
  }

  return (
    <aside id="app-sidebar" data-app-nav="primary">
      <div className="app-sidebar-inner">
        <div className="app-brand">
          <div className="app-brand-row">
            <button
              className="collapse-btn"
              aria-label="Recolher menu principal"
              title="Recolher menu"
              onClick={toggleSidebar}
            >
              <Icon name="ChevronsLeft" size={16} />
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
            <div className="meta">v0.1.0 · © 2025</div>
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
