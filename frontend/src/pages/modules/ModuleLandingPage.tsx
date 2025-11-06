import { useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { NAVIGATION } from '@/navigation/map'

export default function ModuleLandingPage() {
  const { moduleId } = useParams()

  const mod = useMemo(() => NAVIGATION.modules.find(m => m.id === moduleId), [moduleId])

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">{mod?.name || 'Módulo'}</h1>
        {mod?.description && (
          <p className="page-subtitle">{mod.description}</p>
        )}
      </div>

      <div className="content-section">
        <p>Selecione uma função no painel lateral.</p>
      </div>
    </>
  )
}
