# 🔍 Configuração do Sentry - Monitoramento de Erros

## 🎯 Visão Geral

Sentry é a plataforma de monitoramento de erros e performance para o frontend TechDengue em produção.

**O que monitora**:
- ✅ Erros JavaScript não tratados
- ✅ Erros de autenticação e roles
- ✅ Performance de navegação
- ✅ Session replays (gravação visual)
- ✅ Breadcrumbs de ações do usuário

---

## 📋 Pré-requisitos

1. Conta no Sentry (https://sentry.io)
2. Projeto criado no Sentry
3. DSN do projeto (fornecido pelo Sentry)

---

## 🚀 Setup Rápido (5 minutos)

### Passo 1: Criar Projeto no Sentry

1. Acessar https://sentry.io
2. Criar novo projeto
3. Escolher **React** como plataforma
4. Copiar o **DSN** fornecido

### Passo 2: Adicionar CDN ao index.html

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>TechDengue</title>
  
  <!-- Sentry SDK (antes de outros scripts) -->
  <script 
    src="https://browser.sentry-cdn.com/7.119.0/bundle.min.js"
    integrity="sha384-..."
    crossorigin="anonymous"
  ></script>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
```

**Nota**: Verificar a versão mais recente em https://docs.sentry.io/platforms/javascript/install/cdn/

### Passo 3: Configurar Variável de Ambiente

```bash
# .env.production
VITE_SENTRY_DSN=https://your-dsn@sentry.io/project-id
VITE_APP_VERSION=1.0.0
```

### Passo 4: Inicializar no main.tsx

```tsx
// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { initSentry } from './config/sentry'

// Inicializar Sentry antes de tudo
initSentry()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### Passo 5: Testar

```bash
# Build de produção
npm run build

# Preview
npm run preview

# No console DevTools:
throw new Error('Teste Sentry')
```

Verificar erro no dashboard do Sentry em ~30 segundos.

---

## 🎨 Integração Automática

O Sentry já está integrado ao sistema de logging:

```typescript
import { logger } from '@/utils/logger'

// Erro automático para Sentry
logger.error('Falha ao carregar dados', { userId: 123 })

// Role check negado (enviado ao Sentry)
logger.roleCheck('deny', 'ADMIN', { reason: 'insufficient roles' })

// Navegação negada
logger.navigation('access-denied', '/admin', { reason: 'not authenticated' })
```

**Todos os logs de nível `error` e `warn` são enviados ao Sentry automaticamente em produção.**

---

## 📊 Funcionalidades Configuradas

### 1. Error Tracking

**Captura automática**:
- Erros JavaScript não tratados
- Promise rejections
- Erros do React (Error Boundaries)

**Contexto capturado**:
- Stack trace completo
- Navegador e versão
- URL da página
- Usuário (ID e email mascarado)
- Breadcrumbs de ações

### 2. Performance Monitoring

**Taxa de amostragem**: 10% das transações

**Rastreado**:
- Tempo de carregamento de páginas
- Navegação entre rotas
- Requisições de API
- Renderização de componentes

### 3. Session Replay

**Gravação visual** de sessões:
- 10% das sessões normais
- 100% das sessões com erro

**Privacidade**:
- ✅ Texto mascarado (dados sensíveis)
- ✅ Imagens bloqueadas
- ✅ Email mascarado (j***@example.com)
- ✅ Roles não incluídas

### 4. Breadcrumbs

Histórico de ações antes do erro:
- Cliques em botões
- Navegação entre páginas
- Requisições de API
- Verificações de role
- Mudanças de estado

---

## 🛡️ Privacidade e Segurança

### Dados Mascarados

```typescript
// Email: joao@example.com
// Enviado ao Sentry: j***@example.com

// Senha: NUNCA é capturada
// Token JWT: NUNCA é capturado
```

### Erros Ignorados

```typescript
// Lista de erros que NÃO são enviados:
- ResizeObserver loop
- Network request failed
- chrome-extension:// (extensões do browser)
- Minified React error #...
```

### Filtragem Customizada

```typescript
// beforeSend hook (src/config/sentry.ts)
beforeSend(event, hint) {
  // Filtrar erros de desenvolvimento
  if (event.exception?.values?.some(e => 
    e.value?.includes('ResizeObserver')
  )) {
    return null // Não enviar
  }
  
  return event
}
```

---

## 🔧 Configuração Avançada

### Ajustar Taxa de Amostragem

```typescript
// src/config/sentry.ts
const config = {
  // Performance (padrão: 10%)
  tracesSampleRate: 0.1, // 0.0 = desligado, 1.0 = 100%
  
  // Session Replay
  replaysSessionSampleRate: 0.1, // 10% das sessões
  replaysOnErrorSampleRate: 1.0, // 100% se houver erro
}
```

**Atenção**: Taxa maior = mais custos no Sentry.

### Adicionar Tags Customizadas

```typescript
import { addBreadcrumb } from '@/config/sentry'

function handleExport() {
  addBreadcrumb('Exportação iniciada', {
    format: 'PDF',
    records: 1500
  })
  
  exportToPDF()
}
```

### Capturar Erro Manualmente

```typescript
import { captureError, captureMessage } from '@/config/sentry'

try {
  riskyOperation()
} catch (error) {
  captureError(error as Error, {
    operation: 'riskyOperation',
    userId: user.id
  })
}

// Ou mensagem simples
captureMessage('Operação incomum detectada', 'warning', {
  userId: user.id
})
```

---

## 📈 Monitoramento no Dashboard

### Alertas Configurados

**Alertas recomendados**:
1. **Erro novo**: Enviar email quando erro nunca visto antes
2. **Pico de erros**: Se erros aumentarem 300% em 1 hora
3. **Performance degradada**: Se tempo de carregamento > 5s

### Métricas Importantes

**Acessar em Sentry → Issues**:
- Total de erros únicos
- Total de ocorrências
- Usuários afetados
- Browsers mais problemáticos

**Acessar em Sentry → Performance**:
- Tempo médio de carregamento
- Páginas mais lentas
- Requisições API mais lentas

---

## 🐛 Troubleshooting

### Sentry não inicializa

**Problema**: `Sentry: SDK não encontrado`

**Solução**:
1. Verificar se script CDN está no `index.html`
2. Verificar CORS/CSP headers
3. Verificar se DSN está configurado

```bash
# Verificar variável
echo $VITE_SENTRY_DSN
```

### Erros não aparecem no Sentry

**Causas comuns**:
1. Está em desenvolvimento (`import.meta.env.PROD = false`)
2. Erro está na lista de ignorados
3. Taxa de amostragem = 0

**Debug**:
```javascript
// Console DevTools
console.log('Sentry ativo?', window.Sentry !== undefined)
console.log('Produção?', import.meta.env.PROD)
console.log('DSN configurado?', import.meta.env.VITE_SENTRY_DSN)
```

### Muito consumo de quota

**Problema**: Atingindo limite do plano Sentry

**Soluções**:
1. Reduzir `tracesSampleRate` de 0.1 para 0.05
2. Reduzir `replaysSessionSampleRate` de 0.1 para 0.05
3. Adicionar mais erros à lista de ignorados
4. Usar `beforeSend` para filtrar mais agressivamente

---

## 📊 Exemplos Práticos

### Exemplo 1: Erro de API

```typescript
// AuthContext.tsx
try {
  const token = await getAccessToken()
} catch (error) {
  logger.error('Failed to get access token', {}, error as Error)
  // Automaticamente enviado ao Sentry ✅
}
```

**No Sentry verá**:
- Mensagem: "Failed to get access token"
- Stack trace completo
- URL: /dashboard
- Usuário: j***@example.com
- Browser: Chrome 118
- Breadcrumbs: últimas 10 ações

### Exemplo 2: Role Check Negado

```typescript
// AuthContext.tsx (hasRole)
if (!hasAccess) {
  logger.roleCheck('deny', 'ADMIN', {
    userId: user.email,
    requiredRole: 'ADMIN',
    availableRoles: ['GESTOR']
  })
  // Automaticamente enviado ao Sentry ✅
}
```

**No Sentry verá**:
- Mensagem: "Acesso negado para role: ADMIN"
- Context: usuário tem apenas GESTOR
- Frequência: quantas vezes isso ocorre
- Quais usuários são mais afetados

### Exemplo 3: Performance Lenta

**No Sentry → Performance**:
- Transação: /dashboard
- Duração: 8.5s (muito lento!)
- Breakdown:
  - API /estatisticas: 6.2s
  - Render: 2.1s
  - Total: 8.5s

**Ação**: Otimizar endpoint `/estatisticas`

---

## 🔄 Integração com CI/CD

### Upload de Source Maps

Para stack traces mais precisos:

```bash
# .github/workflows/frontend-ci.yml
- name: Upload Source Maps to Sentry
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: your-org
    SENTRY_PROJECT: techdengue-frontend
  run: |
    npm install -g @sentry/cli
    sentry-cli releases new ${{ github.sha }}
    sentry-cli releases files ${{ github.sha }} upload-sourcemaps ./dist/assets
    sentry-cli releases finalize ${{ github.sha }}
```

### Criar Release no Sentry

```bash
# Ao fazer deploy
SENTRY_RELEASE=$(git rev-parse --short HEAD)
echo "VITE_APP_VERSION=$SENTRY_RELEASE" >> .env.production
```

---

## ✅ Checklist de Deploy

Antes de ativar Sentry em produção:

- [ ] Projeto criado no Sentry
- [ ] DSN configurado em `.env.production`
- [ ] Script CDN adicionado ao `index.html`
- [ ] `initSentry()` chamado no `main.tsx`
- [ ] Testar erro em ambiente de preview
- [ ] Verificar erro aparece no Sentry (~30s)
- [ ] Configurar alertas (email/Slack)
- [ ] Revisar taxa de amostragem (custo vs visibilidade)
- [ ] Configurar integração com Slack (opcional)
- [ ] Documentar para a equipe

---

## 📚 Referências

- [Sentry Docs - React](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Sentry Performance](https://docs.sentry.io/product/performance/)
- [Sentry Session Replay](https://docs.sentry.io/product/session-replay/)
- [Best Practices](https://docs.sentry.io/platforms/javascript/best-practices/)

---

**Última atualização**: 06/11/2025  
**Versão**: 1.0.0
