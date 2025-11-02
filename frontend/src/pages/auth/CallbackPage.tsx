import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUserManager } from '@/contexts/AuthContext'

export default function CallbackPage() {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Prevent double-processing in React 18 StrictMode (mount -> unmount -> mount)
        const params = new URLSearchParams(window.location.search)
        const state = params.get('state') || ''
        const guardKey = `oidc-callback-processed:${state}`
        if (sessionStorage.getItem(guardKey)) {
          navigate('/', { replace: true })
          return
        }
        sessionStorage.setItem(guardKey, '1')

        const manager = getUserManager()
        const user = await manager.signinRedirectCallback()
        
        // Get the return URL from state or default to home
        const returnUrl = (user.state as any)?.returnUrl || '/'
        navigate(returnUrl, { replace: true })
      } catch (err) {
        console.error('Callback error:', err)
        setError(err instanceof Error ? err.message : 'Authentication failed')
      }
    }

    handleCallback()
  }, [navigate])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <div className="text-center">
            <div className="text-red-600 text-5xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Erro de Autenticação
            </h1>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Voltar para Home
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Processando autenticação...</p>
      </div>
    </div>
  )
}
