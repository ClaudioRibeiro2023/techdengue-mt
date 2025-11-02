import React from 'react'

const items = [
  { path: '/mapa', label: 'Mapa' },
  { path: '/etl', label: 'ETL' },
  { path: '/operacional', label: 'Operacional' },
  { path: '/relatorios', label: 'Relatórios' },
  { path: '/admin', label: 'Admin' }
]

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-56 bg-white border-r p-3">
      <nav className="space-y-1">
        {items.map(it => (
          <a key={it.path} href={it.path} className="block px-3 py-2 rounded hover:bg-slate-100">
            {it.label}
          </a>
        ))}
      </nav>
    </aside>
  )
}
