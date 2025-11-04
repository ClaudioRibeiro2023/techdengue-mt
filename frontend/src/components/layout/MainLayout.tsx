import { Outlet } from 'react-router-dom'
import Header from './Header'
import AppSidebar from '@/components/navigation/AppSidebar'
import ModuleFunctionsPanel from '@/components/navigation/ModuleFunctionsPanel'
import { WebMapProvider } from '@/modules/webmap/context'

export default function MainLayout() {
  const closeMobileSidebar = () => {
    document.documentElement.classList.remove('mobile-sidebar-open')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <WebMapProvider>
        <Header />
        <div className="flex">
          <div className="mobile-overlay" onClick={closeMobileSidebar} aria-hidden="true" />
          <AppSidebar />
          <ModuleFunctionsPanel />
          <main className="flex-1 overflow-auto">
            <Outlet />
          </main>
        </div>
      </WebMapProvider>
    </div>
  )
}
