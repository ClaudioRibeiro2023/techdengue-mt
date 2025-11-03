import { Link, useLocation } from 'react-router-dom'
import { useMemo, useState } from 'react'
import { NAVIGATION } from '@/navigation/map'
import Icon from '@/components/ui/Icon'

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

  return (
    <aside id="app-sidebar" data-app-nav="primary">
      <div className="app-sidebar-inner">
        <div className="app-brand">
          <span className="brand-name">SIVEPI</span>
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

        {Object.entries(grouped).map(([groupName, groupItems]) => (
          <div key={groupName} className="app-group">
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
      </div>
    </aside>
  )
}
