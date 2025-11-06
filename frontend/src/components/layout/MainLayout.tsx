import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import Header from './Header'
import AppSidebar from '@/components/navigation/AppSidebar'
import ModuleSidebar from '@/components/navigation/ModuleSidebar'
import { WebMapProvider } from '@/modules/webmap/context'
import WebMapFiltersPanel from '@/modules/webmap/WebMapFiltersPanel'
import WebMapLayersPanel from '@/modules/webmap/WebMapLayersPanel'

export default function MainLayout() {
  const closeMobileSidebar = () => {
    document.documentElement.classList.remove('mobile-sidebar-open')
  }

  const closeMobileSubnav = () => {
    document.documentElement.classList.remove('mobile-submenu-open')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <WebMapProvider>
        <StateRestorer />
        <Header />
        <div className="flex">
          <div className="mobile-overlay" onClick={closeMobileSidebar} aria-hidden="true" />
          <div className="mobile-overlay-subnav" onClick={closeMobileSubnav} aria-hidden="true" />
          <AppSidebar />
          <ModuleSidebar />
          <main className="flex-1 overflow-auto">
            <Outlet />
          </main>
          <WebMapFiltersPanel />
          <WebMapLayersPanel />
        </div>
      </WebMapProvider>
    </div>
  )
}

function StateRestorer() {
  useEffect(() => {
    const root = document.documentElement
    const setClass = (cls: string, key: string) => {
      const val = localStorage.getItem(key)
      if (val === '1') root.classList.add(cls)
      else root.classList.remove(cls)
    }
    setClass('sidebar-collapsed', 'sidebar-collapsed')
    setClass('subnav-collapsed', 'subnav-collapsed')
    setClass('filters-collapsed', 'filters-collapsed')

    // Sync aria-expanded on collapse buttons
    const sync = (selector: string, cls: string) => {
      const btn = document.querySelector<HTMLButtonElement>(selector)
      if (btn) btn.setAttribute('aria-expanded', (!root.classList.contains(cls)).toString())
    }
    sync('#app-sidebar .app-brand .collapse-btn', 'sidebar-collapsed')
    sync('#app-submenu .collapse-btn', 'subnav-collapsed')
    sync('.filters-panel .filters-header .collapse-btn', 'filters-collapsed')
  }, [])
  return null
}
