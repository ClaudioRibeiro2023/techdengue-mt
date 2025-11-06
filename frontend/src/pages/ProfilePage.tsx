import { useAuth } from '@/contexts/AuthContext'
import { User, Mail, Shield, Key, Calendar } from 'lucide-react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export default function ProfilePage() {
  const { user } = useAuth()

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Carregando perfil...</p>
      </div>
    )
  }

  type KeycloakProfile = {
    name?: string
    preferred_username?: string
    email?: string
    email_verified?: boolean
    realm_access?: { roles?: string[] }
    sub?: string
  }
  const profile = user.profile as KeycloakProfile
  const userName = profile.name || profile.preferred_username || 'Não informado'
  const userEmail = profile.email || 'Não informado'
  const userRoles = profile.realm_access?.roles || []
  
  const tokenExpiry = user.expires_at
    ? format(new Date(user.expires_at * 1000), "PPpp", { locale: ptBR })
    : 'Não disponível'

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center text-white text-3xl font-semibold">
              {userName.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{userName}</h1>
              <p className="text-gray-600">{userEmail}</p>
            </div>
          </div>
        </div>

        {/* Profile Info */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Informações do Perfil
          </h2>
          
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <User className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-gray-500">Nome de Usuário</div>
                <div className="text-gray-900">{profile.preferred_username || 'Não informado'}</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-gray-500">Email</div>
                <div className="text-gray-900">{userEmail}</div>
                {profile.email_verified && (
                  <span className="inline-block mt-1 px-2 py-0.5 text-xs font-medium rounded bg-green-100 text-green-700">
                    Verificado
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Key className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-gray-500">Subject ID</div>
                <div className="text-gray-900 text-xs font-mono break-all">{profile.sub}</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-gray-500">Token Expira em</div>
                <div className="text-gray-900">{tokenExpiry}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Roles */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-gray-700" />
            <h2 className="text-xl font-semibold text-gray-900">
              Permissões e Papéis
            </h2>
          </div>

          {userRoles.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {userRoles.map((role: string) => (
                <span
                  key={role}
                  className="inline-block px-3 py-1.5 text-sm font-medium rounded-lg bg-blue-100 text-blue-700"
                >
                  {role}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">Nenhum papel atribuído</p>
          )}

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-sm font-medium text-blue-900 mb-2">
              Sobre os Papéis
            </h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li><strong>ADMIN:</strong> Acesso total ao sistema</li>
              <li><strong>GESTOR:</strong> Gerenciamento e relatórios</li>
              <li><strong>VIGILANCIA:</strong> Monitoramento epidemiológico</li>
              <li><strong>CAMPO:</strong> Atividades de campo e registro</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
