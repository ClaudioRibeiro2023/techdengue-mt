import { Link, useLocation } from 'react-router-dom'
import { useMemo } from 'react'
import { NAVIGATION } from '@/navigation/map'
import Icon from '@/components/ui/Icon'

export default function AppSidebar() {
  const { pathname } = useLocation()

  const items = useMemo(() => NAVIGATION.modules.map(m => ({
    id: m.id,
    name: m.name,
    path: m.path,
    icon: m.icon,
  })), [])

  const isActive = (path: string) => pathname === path || pathname.startsWith(path + '/')

  return (
    <aside id="app-sidebar" data-app-nav="primary">
      <div className="app-sidebar-inner">
        <div className="app-brand">
          <span className="brand-name">SIVEPI</span>
          <span className="brand-sub">Sistema Integrado de Vigilância</span>
        </div>

        <nav className="app-nav">
          {items.map(it => (
            <Link
              key={it.id}
              to={it.path}
              className={isActive(it.path) ? 'active' : ''}
              title={it.name}
            >
              {it.icon && <Icon name={it.icon} size={18} />}
              <span className="label">{it.name}</span>
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  )
}
