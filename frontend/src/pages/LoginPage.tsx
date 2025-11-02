import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { LogIn } from 'lucide-react'

export default function LoginPage() {
  const { isAuthenticated, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = location.state?.from?.pathname || '/'

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, from])

  const handleLogin = () => {
    login()
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-cyan-50">
      <div className="max-w-md w-full bg-white shadow-2xl rounded-2xl p-8 m-4">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-4xl">🦟</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            TechDengue
          </h1>
          <p className="text-gray-600">
            Plataforma de Vigilância em Saúde
          </p>
        </div>

        <div className="space-y-4">
          <button
            onClick={handleLogin}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <LogIn className="w-5 h-5" />
            Entrar com Keycloak
          </button>
        </div>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Sistema de monitoramento e controle do Aedes aegypti</p>
          <p className="mt-2">Secretaria de Estado de Saúde de Mato Grosso</p>
        </div>
      </div>
    </div>
  )
}
