import React, { useMemo } from 'react'
import { Mapa } from './pages/Mapa'
import { ETL } from './pages/ETL'
import { Operacional } from './pages/Operacional'
import { Relatorios } from './pages/Relatorios'
import { Admin } from './pages/Admin'

const routeMap: Record<string, React.FC> = {
  '/mapa': Mapa,
  '/etl': ETL,
  '/operacional': Operacional,
  '/relatorios': Relatorios,
  '/admin': Admin,
}

function pickRoute(pathname: string): React.FC {
  return routeMap[pathname] || Mapa
}

export function useRoutes() {
  return useMemo(() => {
    const C = pickRoute(window.location.pathname)
    return C
  }, [window.location.pathname])
}
