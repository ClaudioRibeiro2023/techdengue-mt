/**
 * Logger utilitário para monitoramento e debugging
 * Nível de log controlado por variável de ambiente
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error'
type LogContext = Record<string, unknown>

interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  context?: LogContext
  stack?: string
}

class Logger {
  private enabled: boolean
  private minLevel: LogLevel

  constructor() {
    // Habilitar logs em desenvolvimento ou quando VITE_ENABLE_LOGS=true
    this.enabled = import.meta.env.DEV || import.meta.env.VITE_ENABLE_LOGS === 'true'
    this.minLevel = (import.meta.env.VITE_LOG_LEVEL as LogLevel) || 'info'
  }

  private shouldLog(level: LogLevel): boolean {
    if (!this.enabled) return false
    
    const levels: LogLevel[] = ['debug', 'info', 'warn', 'error']
    const currentLevelIndex = levels.indexOf(this.minLevel)
    const messageLevelIndex = levels.indexOf(level)
    
    return messageLevelIndex >= currentLevelIndex
  }

  private formatMessage(level: LogLevel, message: string, context?: LogContext): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context
    }
  }

  private log(level: LogLevel, message: string, context?: LogContext, error?: Error) {
    if (!this.shouldLog(level)) return

    const entry = this.formatMessage(level, message, context)
    
    if (error) {
      entry.stack = error.stack
    }

    // Console output com cores
    const styles: Record<LogLevel, string> = {
      debug: 'color: #6b7280',
      info: 'color: #3b82f6',
      warn: 'color: #f59e0b',
      error: 'color: #ef4444; font-weight: bold'
    }

    const prefix = `[${entry.level.toUpperCase()}] ${entry.timestamp}`
    
    console.log(
      `%c${prefix}`,
      styles[level],
      entry.message,
      entry.context || ''
    )

    if (entry.stack) {
      console.error(entry.stack)
    }

    // Em produção, enviar para serviço de monitoramento
    if (import.meta.env.PROD && level === 'error') {
      this.sendToMonitoring(entry)
    }
  }

  private sendToMonitoring(entry: LogEntry) {
    // Integração com Sentry
    interface Sdk {
      captureException: (error: unknown, options?: { level?: string; extra?: Record<string, unknown>; tags?: Record<string, string> }) => void
      captureMessage: (message: string, options?: { level?: string; extra?: Record<string, unknown>; tags?: Record<string, string> }) => void
    }
    interface W extends Window { Sentry?: Sdk }
    if (typeof window !== 'undefined' && (window as W).Sentry) {
      const Sentry = (window as W).Sentry as Sdk
      
      try {
        if (entry.level === 'error') {
          if (entry.stack) {
            // Capturar erro com stack trace
            Sentry.captureException(new Error(entry.message), {
              level: 'error',
              extra: entry.context,
              tags: {
                source: 'logger'
              }
            })
          } else {
            // Capturar mensagem de erro
            Sentry.captureMessage(entry.message, {
              level: 'error',
              extra: entry.context,
              tags: {
                source: 'logger'
              }
            })
          }
        } else if (entry.level === 'warn') {
          Sentry.captureMessage(entry.message, {
            level: 'warning',
            extra: entry.context,
            tags: {
              source: 'logger'
            }
          })
        }
      } catch { void 0 }
    }
    
    // Backup local para análise
    try {
      const logs = JSON.parse(localStorage.getItem('error-logs') || '[]')
      logs.push(entry)
      // Manter apenas os últimos 50 erros
      if (logs.length > 50) logs.shift()
      localStorage.setItem('error-logs', JSON.stringify(logs))
    } catch { void 0 }
  }

  debug(message: string, context?: LogContext) {
    this.log('debug', message, context)
  }

  info(message: string, context?: LogContext) {
    this.log('info', message, context)
  }

  warn(message: string, context?: LogContext) {
    this.log('warn', message, context)
  }

  error(message: string, context?: LogContext, error?: Error) {
    this.log('error', message, context, error)
  }

  // Log específico para verificação de roles
  roleCheck(action: 'check' | 'grant' | 'deny', role: string | string[], context?: LogContext) {
    const message = action === 'check' 
      ? `Verificando role(s): ${Array.isArray(role) ? role.join(', ') : role}`
      : action === 'grant'
      ? `Acesso concedido para role(s): ${Array.isArray(role) ? role.join(', ') : role}`
      : `Acesso negado para role(s): ${Array.isArray(role) ? role.join(', ') : role}`

    this.log(action === 'deny' ? 'warn' : 'debug', message, context)
  }

  // Log específico para autenticação
  auth(event: 'login' | 'logout' | 'token-expired' | 'token-renewed', context?: LogContext) {
    const messages = {
      login: 'Usuário autenticado',
      logout: 'Usuário desconectado',
      'token-expired': 'Token expirou',
      'token-renewed': 'Token renovado'
    }

    this.log(event === 'token-expired' ? 'warn' : 'info', messages[event], context)
  }

  // Log específico para navegação
  navigation(action: 'view' | 'access-denied', path: string, context?: LogContext) {
    const message = action === 'view'
      ? `Navegando para: ${path}`
      : `Acesso negado à rota: ${path}`

    this.log(action === 'access-denied' ? 'warn' : 'debug', message, context)
  }
}

// Singleton
export const logger = new Logger()

// Utilitário para limpar logs antigos
export function clearErrorLogs() {
  try {
    localStorage.removeItem('error-logs')
    logger.info('Logs de erro limpos')
  } catch (e) {
    // Silenciar
  }
}

// Utilitário para exportar logs
export function exportErrorLogs(): LogEntry[] {
  try {
    return JSON.parse(localStorage.getItem('error-logs') || '[]')
  } catch {
    return []
  }
}
