import { Outlet } from 'react-router-dom'
import Header from './Header'
import ModuleTopbar from '@/components/navigation/ModuleTopbar'
import ModuleSidebar from '@/components/navigation/ModuleSidebar'

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <ModuleTopbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex gap-6">
          <ModuleSidebar />
          <main className="flex-1 py-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
