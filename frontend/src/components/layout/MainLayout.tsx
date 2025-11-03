import { Outlet } from 'react-router-dom'
import Header from './Header'
import AppSidebar from '@/components/navigation/AppSidebar'
import ModuleFunctionsPanel from '@/components/navigation/ModuleFunctionsPanel'

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <AppSidebar />
        <ModuleFunctionsPanel />
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
