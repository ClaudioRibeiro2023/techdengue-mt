import { Outlet } from 'react-router-dom'
import Header from './Header'
import AppSidebar from '@/components/navigation/AppSidebar'
import ModuleSidebar from '@/components/navigation/ModuleSidebar'

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <AppSidebar />
        <ModuleSidebar />
        <main className="flex-1 p-6">
          <div className="mx-auto w-full max-w-[1400px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
