import React from 'react'
import { useUser } from '../lib/auth'

export const Navbar: React.FC = () => {
  const user = useUser()
  return (
    <header className="h-14 px-4 border-b bg-white flex items-center justify-between">
      <div className="font-semibold">TechDengue — Edital-Core</div>
      <div className="text-sm text-slate-600">Olá, {user.name}</div>
    </header>
  )
}
