import React, { useMemo } from 'react'
import { Layout } from './components/Layout'
import { useRoutes } from './routes'

export const App: React.FC = () => {
  const RouteEl = useRoutes()
  return (
    <Layout>
      <RouteEl />
    </Layout>
  )
}
