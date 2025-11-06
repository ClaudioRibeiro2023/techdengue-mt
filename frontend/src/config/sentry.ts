/**
 * Configuração do Sentry para monitoramento de erros em produção
 * Docs: https://docs.sentry.io/platforms/javascript/guides/react/
 */

// Tipos para o Sentry (evitar dependência completa)
interface SentryEvent {
  exception?: { values?: Array<{ value?: string }> }
  user?: unknown
}

type SentryHint = unknown

interface SentrySDK {
  init: (config: SentryConfig) => void
  BrowserTracing: new () => unknown
  Replay: new (options: { maskAllText?: boolean; blockAllMedia?: boolean }) => unknown
  captureException: (error: unknown, context?: { extra?: Record<string, unknown>; tags?: Record<string, string> }) => void
  captureMessage: (message: string, options?: { level?: 'info' | 'warning' | 'error'; extra?: Record<string, unknown>; tags?: Record<string, string> }) => void
  setContext: (name: string, context: Record<string, unknown>) => void
  setUser: (user: { id: string; email?: string; username?: string } | null) => void
  addBreadcrumb: (crumb: { message: string; data?: Record<string, unknown>; timestamp?: number }) => void
}

interface SentryWindow extends Window { Sentry?: SentrySDK }

interface SentryConfig {
  dsn: string
  environment: string
  release?: string
  tracesSampleRate: number
  replaysSessionSampleRate: number
  replaysOnErrorSampleRate: number
  integrations?: unknown[]
  beforeSend?: (event: SentryEvent, hint: SentryHint) => SentryEvent | null
  ignoreErrors?: string[]
}

/**
 * Inicializar Sentry (chamar no main.tsx ou App.tsx)
 * 
 * Importante: Adicionar script CDN no index.html primeiro:
 * <script src="https://browser.sentry-cdn.com/7.x.x/bundle.min.js"></script>
 */
export function initSentry() {
  // Apenas em produção
  if (!import.meta.env.PROD) {
    console.log('Sentry: Desabilitado em desenvolvimento')
    return
  }

  // Verificar se Sentry está disponível
  if (typeof window === 'undefined' || !(window as SentryWindow).Sentry) {
    console.warn('Sentry: SDK não encontrado. Adicione o script CDN no index.html')
    return
  }

  const Sentry = (window as SentryWindow).Sentry!
  
  // DSN do projeto (obter em sentry.io)
  const dsn = import.meta.env.VITE_SENTRY_DSN
  
  if (!dsn) {
    console.warn('Sentry: VITE_SENTRY_DSN não configurado')
    return
  }

  const config: SentryConfig = {
    dsn,
    environment: import.meta.env.MODE || 'production',
    release: import.meta.env.VITE_APP_VERSION || '1.0.0',
    
    // Performance monitoring
    tracesSampleRate: 0.1, // 10% das transações
    
    // Session replay
    replaysSessionSampleRate: 0.1, // 10% das sessões normais
    replaysOnErrorSampleRate: 1.0, // 100% das sessões com erro
    
    // Integrações
    integrations: [
      // BrowserTracing para performance
      new Sentry.BrowserTracing(),
      
      // Session Replay para debug visual
      new Sentry.Replay({
        maskAllText: true, // Ocultar texto sensível
        blockAllMedia: true, // Ocultar imagens/vídeos
      }),
    ],
    
    // Filtrar eventos antes de enviar
    beforeSend(event) {
      if (event.exception?.values?.some((e) => typeof e.value === 'string' && (
        e.value.includes('ResizeObserver') ||
        e.value.includes('Non-Error promise rejection')
      ))) {
        return null
      }
      if (typeof window !== 'undefined') {
        const user = getUserContext()
        if (user) {
          event.user = user as unknown
        }
      }
      return event
    },
    
    // Ignorar erros conhecidos
    ignoreErrors: [
      // Erros de browser/extensões
      'ResizeObserver loop',
      'Non-Error promise rejection',
      'Network request failed',
      'Failed to fetch',
      
      // Erros de extensões do Chrome
      'chrome-extension://',
      'moz-extension://',
      
      // Erros do React
      'Minified React error',
    ],
  }

  try {
    Sentry.init(config)
    console.log('Sentry: Inicializado com sucesso')
    
    // Adicionar contexto global
    Sentry.setContext('application', {
      name: 'TechDengue Frontend',
      version: import.meta.env.VITE_APP_VERSION || '1.0.0',
      environment: import.meta.env.MODE || 'production'
    })
  } catch (error) {
    console.error('Sentry: Erro ao inicializar', error)
  }
}

/**
 * Obter contexto do usuário para o Sentry (sem dados sensíveis)
 */
function getUserContext() {
  try {
    // Buscar dados do OIDC (Keycloak)
    const oidcKeys = Object.keys(localStorage).filter(k => k.startsWith('oidc.user:'))
    if (oidcKeys.length === 0) return null
    
    const oidcData = localStorage.getItem(oidcKeys[0])
    if (!oidcData) return null
    
    const user = JSON.parse(oidcData)
    const profile = user.profile || {}
    
    return {
      id: profile.sub || 'unknown', // ID único (não sensível)
      email: profile.email ? maskEmail(profile.email) : undefined, // Email mascarado
      username: profile.preferred_username || undefined,
      // Não incluir roles por privacidade
    }
  } catch {
    return null
  }
}

/**
 * Mascarar email para privacidade (ex: j***@example.com)
 */
function maskEmail(email: string): string {
  const [local, domain] = email.split('@')
  if (!local || !domain) return 'masked@email.com'
  
  const masked = local.charAt(0) + '***'
  return `${masked}@${domain}`
}

/**
 * Capturar erro manualmente
 */
export function captureError(error: Error, context?: Record<string, unknown>) {
  if (typeof window === 'undefined' || !(window as SentryWindow).Sentry) return
  const Sentry = (window as SentryWindow).Sentry!
  Sentry.captureException(error, {
    extra: context,
    tags: {
      source: 'manual'
    }
  })
}

/**
 * Capturar mensagem manualmente
 */
export function captureMessage(message: string, level: 'info' | 'warning' | 'error' = 'info', context?: Record<string, unknown>) {
  if (typeof window === 'undefined' || !(window as SentryWindow).Sentry) return
  const Sentry = (window as SentryWindow).Sentry!
  Sentry.captureMessage(message, {
    level,
    extra: context,
    tags: {
      source: 'manual'
    }
  })
}

/**
 * Definir usuário atual
 */
export function setUser(user: { id: string; email?: string; username?: string } | null) {
  if (typeof window === 'undefined' || !(window as SentryWindow).Sentry) return
  const Sentry = (window as SentryWindow).Sentry!
  if (user) {
    Sentry.setUser({
      id: user.id,
      email: user.email ? maskEmail(user.email) : undefined,
      username: user.username
    })
  } else {
    Sentry.setUser(null)
  }
}

/**
 * Adicionar breadcrumb (navegação/ação do usuário)
 */
export function addBreadcrumb(message: string, data?: Record<string, unknown>) {
  if (typeof window === 'undefined' || !(window as SentryWindow).Sentry) return
  const Sentry = (window as SentryWindow).Sentry!
  Sentry.addBreadcrumb({
    message,
    data,
    timestamp: Date.now() / 1000
  })
}
