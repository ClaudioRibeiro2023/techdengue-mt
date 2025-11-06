# Controle de Acesso e Roles - TechDengue

## 📋 Sumário
- [Visão Geral](#visão-geral)
- [Roles Disponíveis](#roles-disponíveis)
- [Acesso por Módulo](#acesso-por-módulo)
- [Configuração do Keycloak](#configuração-do-keycloak)
- [Scripts de Validação](#scripts-de-validação)
- [Troubleshooting](#troubleshooting)

---

## Visão Geral

O TechDengue utiliza **controle de acesso baseado em roles (RBAC)** através do Keycloak. Cada módulo e função da aplicação pode requerer uma ou mais roles para acesso.

### Fluxo de Autenticação
```
Usuário → Keycloak → JWT Token → Frontend verifica roles → Exibe menus/funções permitidos
```

---

## Roles Disponíveis

### 1. **ADMIN** (Administrador do Sistema)
- Acesso total a todos os módulos
- Funções administrativas (usuários, parâmetros, auditoria)
- Configuração de entidades e sistema

### 2. **GESTOR** (Gestor de Vigilância)
- Dashboard executivo
- Relatórios gerenciais
- Indicadores epidemiológicos
- Planejamento de ações

### 3. **VIGILANCIA** (Técnico de Vigilância Epidemiológica)
- Vigilância epidemiológica (casos, surtos, análise temporal)
- Vigilância entomológica (índices, armadilhas, vetores)
- Mapa vivo e camadas geográficas
- Cadastro e triagem de denúncias

### 4. **CAMPO** (Agente de Campo)
- ETL e integração de dados
- Resposta operacional (planejamento, execução, acompanhamento)
- Coleta entomológica
- Vistorias de campo

---

## Acesso por Módulo

### 📊 Dashboard Executivo
**Roles**: `ADMIN`, `GESTOR`

| Função | Roles |
|--------|-------|
| Visão Geral | ADMIN, GESTOR |
| Indicadores KPI | ADMIN, GESTOR |
| Análise Temporal | ADMIN, GESTOR |
| Comparativos | ADMIN, GESTOR |

---

### 🗺️ Mapa Vivo
**Roles**: `ADMIN`, `GESTOR`, `VIGILANCIA`

| Função | Roles |
|--------|-------|
| Visualização de Casos | ADMIN, GESTOR, VIGILANCIA |
| Camadas Geográficas | ADMIN, GESTOR, VIGILANCIA |
| Heatmap de Incidência | ADMIN, GESTOR, VIGILANCIA |
| Exportação de Dados | ADMIN, GESTOR |

---

### 🔮 Previsão & Simulação
**Roles**: `ADMIN`, `GESTOR`

| Função | Descrição | Roles |
|--------|-----------|-------|
| Nowcasting / Rt | Atraso de notificação e transmissibilidade | ADMIN, GESTOR |
| Forecast Semanal | Previsão casos próximas semanas | ADMIN, GESTOR |
| Risco Climático | Projeção de risco por clima | ADMIN, GESTOR |
| Cenários What-If | Simulador de intervenções | ADMIN, GESTOR |

---

### 🦟 Vigilância Entomológica
**Roles**: `ADMIN`, `VIGILANCIA`, `CAMPO`

| Função | Descrição | Roles |
|--------|-----------|-------|
| Índices Vetoriais | IIP, IBP, ID, monitoramento ovos | ADMIN, VIGILANCIA |
| Ovitrampas | Registro e monitoramento | ADMIN, VIGILANCIA, CAMPO |
| Armadilhas BG-Sentinel | Captura de adultos | ADMIN, VIGILANCIA, CAMPO |
| Armadilhas CDC | Monitoramento contínuo | ADMIN, VIGILANCIA, CAMPO |
| Pesquisa Larvária | Coleta depósitos positivos | ADMIN, VIGILANCIA, CAMPO |
| Adulticida | Pulverização (UBV) | ADMIN, CAMPO |
| Larvicida | Tratamento focal/perifocal | ADMIN, CAMPO |
| Pontos Estratégicos | Locais prioritários | ADMIN, VIGILANCIA |
| Resistência Larvicida | Bioensaios | ADMIN, VIGILANCIA |
| Coletas Entomológicas | Registro coletas campo | ADMIN, CAMPO |

---

### 📈 Vigilância Epidemiológica
**Roles**: `ADMIN`, `GESTOR`, `VIGILANCIA`

| Função | Descrição | Roles |
|--------|-----------|-------|
| Casos Notificados | SINAN e vigilância ativa | ADMIN, GESTOR, VIGILANCIA |
| Análise de Surtos | Detecção e investigação | ADMIN, GESTOR, VIGILANCIA |
| Séries Temporais | Tendências e sazonalidade | ADMIN, GESTOR, VIGILANCIA |
| Matriz Incidência | Por município e semana | ADMIN, GESTOR, VIGILANCIA |
| Classificação Final | Confirmados/descartados | ADMIN, VIGILANCIA |
| Óbitos | Letalidade e mortalidade | ADMIN, GESTOR, VIGILANCIA |

---

### ⚡ Resposta Operacional
**Roles**: `ADMIN`, `CAMPO`

| Função | Descrição | Roles |
|--------|-----------|-------|
| Triagem Demandas | Priorização de ações | ADMIN, CAMPO |
| Planejamento | Roteiros e recursos | ADMIN, CAMPO |
| Execução Campo | Check-in/out, GPS | ADMIN, CAMPO |
| Acompanhamento | Status e produtividade | ADMIN, CAMPO |
| Impacto/Resultado | Indicadores de resultado | ADMIN, CAMPO |

---

### 🔧 Administração
**Roles**: `ADMIN`

| Função | Descrição | Roles |
|--------|-----------|-------|
| Gestão de Usuários | Cadastro, roles, permissões | ADMIN |
| Parâmetros Sistema | Configurações globais | ADMIN |
| Entidades | Municípios, unidades, setores | ADMIN |
| Auditoria | Logs de acesso e alterações | ADMIN |

---

### 👁️ Observabilidade
**Roles**: `ADMIN`

| Função | Descrição | Roles |
|--------|-----------|-------|
| Métricas Sistema | Performance e uso | ADMIN |
| Logs Aplicação | Rastreamento de erros | ADMIN |
| Status Saúde | Uptime e health checks | ADMIN |
| Qualidade Dados | Completude e consistência | ADMIN |

---

### 📊 Relatórios
**Roles**: `ADMIN`, `GESTOR`, `VIGILANCIA`

**Acesso**: Todos com ADMIN, GESTOR ou VIGILANCIA podem gerar relatórios dos módulos que têm acesso.

---

### 📤 ETL e Integração
**Roles**: `ADMIN`, `CAMPO`

**Acesso**: Upload SINAN, importação shapefiles, sincronização APIs externas.

---

### 🚨 e-Denúncia
**Roles**: Público (sem autenticação)

**Acesso**: Formulário de denúncia de focos acessível sem login.

---

## Configuração do Keycloak

### Pré-requisitos
- Keycloak rodando em `http://localhost:8080`
- Acesso admin: `admin` / `admin123`
- Realm: `techdengue`
- Client: `techdengue-api`

---

### 1. Criar Realm (se não existir)

1. Acesse Keycloak Admin Console: `http://localhost:8080`
2. Login: `admin` / `admin123`
3. Dropdown superior esquerdo → **Add realm**
4. Name: `techdengue`
5. **Create**

---

### 2. Criar Client

1. No realm `techdengue` → **Clients** → **Create**
2. Configurações:
   ```
   Client ID: techdengue-api
   Client Protocol: openid-connect
   Root URL: http://localhost:6080
   Valid Redirect URIs: 
     - http://localhost:6080/*
     - http://localhost:6090/*  (para E2E)
   Web Origins: 
     - http://localhost:6080
     - http://localhost:6090
   ```
3. **Advanced Settings**:
   ```
   Access Token Lifespan: 15 minutes
   ```
4. **Save**

---

### 3. Criar Roles de Realm

1. **Realm Roles** → **Add Role**
2. Criar as 4 roles:

| Role Name | Description |
|-----------|-------------|
| ADMIN | Administrador do sistema |
| GESTOR | Gestor de vigilância |
| VIGILANCIA | Técnico de vigilância |
| CAMPO | Agente de campo |

---

### 4. Criar Grupos (Opcional mas Recomendado)

1. **Groups** → **New**
2. Criar grupos:

```
Administradores
  └─ Roles: ADMIN

Gestores
  └─ Roles: GESTOR, VIGILANCIA

Vigilância
  └─ Roles: VIGILANCIA

Campo
  └─ Roles: CAMPO
```

---

### 5. Criar Usuários

#### Exemplo: Usuário Admin Completo

1. **Users** → **Add user**
2. Configurações:
   ```
   Username: admin@techdengue.com
   Email: admin@techdengue.com
   First Name: Admin
   Last Name: TechDengue
   Email Verified: ON
   Enabled: ON
   ```
3. **Save**
4. Aba **Credentials**:
   ```
   Password: admin123
   Temporary: OFF
   ```
5. **Set Password**
6. Aba **Role Mappings**:
   - Selecione: `ADMIN`, `GESTOR`, `VIGILANCIA`, `CAMPO`
   - **Add selected**

#### Exemplo: Usuário Gestor

```
Username: gestor@techdengue.com
Password: gestor123
Roles: GESTOR, VIGILANCIA
```

#### Exemplo: Usuário Campo

```
Username: campo@techdengue.com  
Password: campo123
Roles: CAMPO
```

---

### 6. Verificar Token JWT

Use o script `ropc-check.js` para validar:

```bash
npm run ropc:check
```

**Input**:
```
Username: admin@techdengue.com
Password: admin123
```

**Output esperado**:
```json
{
  "realm_access": {
    "roles": ["ADMIN", "GESTOR", "VIGILANCIA", "CAMPO"]
  },
  "resource_access": {
    "techdengue-api": {
      "roles": []
    }
  }
}
```

---

## Scripts de Validação

### 1. `ropc-check.js` - Validação de Token

**Localização**: `scripts/ropc-check.js`

**Uso**:
```bash
npm run ropc:check
```

**Funcionalidade**:
- Faz login via Resource Owner Password Credentials (ROPC)
- Decodifica access_token JWT
- Exibe realm roles e client roles
- Valida se usuário tem acesso

**Exemplo de output**:
```
✓ Login successful!
✓ Token obtido e decodificado

Realm Roles: ADMIN, GESTOR, VIGILANCIA, CAMPO
Client Roles (techdengue-api): (nenhuma)

✓ Usuário admin@techdengue.com tem todas as 4 roles configuradas!
```

---

### 2. `kc_assign_roles.ps1` - Atribuir Roles via API

**Localização**: `scripts/kc_assign_roles.ps1`

**Uso**:
```powershell
.\scripts\kc_assign_roles.ps1
```

**Funcionalidade**:
- Busca usuário por email
- Lista roles disponíveis
- Atribui roles selecionadas
- Adiciona a grupos (opcional)

**Exemplo**:
```powershell
# Atribuir todas roles ao admin
Email: admin@techdengue.com
Roles: ADMIN,GESTOR,VIGILANCIA,CAMPO
```

---

## Troubleshooting

### ❌ Problema: Menu não aparece mesmo com role

**Causa**: Token não contém a role ou frontend não está lendo corretamente.

**Solução**:
1. Rodar `npm run ropc:check` e validar roles no token
2. Verificar `AuthContext.tsx` → método `hasRole`
3. Inspecionar `user.profile.realm_access.roles` no DevTools
4. Fazer logout/login para renovar token

---

### ❌ Problema: "Access Denied" na página

**Causa**: Rota protegida com `ProtectedRoute` mas usuário não tem role necessária.

**Solução**:
1. Verificar `App.tsx` → `requiredRoles` da rota
2. Confirmar que usuário tem a role no Keycloak
3. Verificar se está em modo E2E/DEMO (bypass ativo)

---

### ❌ Problema: Roles não aparecem no token

**Causa**: Roles não foram atribuídas ao usuário no Keycloak.

**Solução**:
1. Keycloak Admin → Users → buscar usuário
2. Aba **Role Mappings**
3. Selecionar roles em **Available Roles**
4. Clicar **Add selected**
5. Fazer logout/login no frontend

---

### ❌ Problema: Keycloak retorna "invalid_grant"

**Causa**: Credenciais incorretas ou client não configurado.

**Solução**:
1. Verificar username/password
2. Verificar se client `techdengue-api` existe
3. Verificar se **Direct Access Grants** está habilitado no client
4. Verificar se redirect URIs estão corretos

---

## Referências

- **Keycloak Admin**: http://localhost:8080
- **Frontend Dev**: http://localhost:6080
- **E2E Tests**: http://localhost:6090
- **Keycloak Docs**: https://www.keycloak.org/docs/latest/server_admin/
- **OIDC Spec**: https://openid.net/connect/

---

## Manutenção

### Adicionar Nova Role

1. Keycloak → **Realm Roles** → **Add Role**
2. Atualizar `frontend/src/config/auth.ts` → type `UserRole`
3. Atualizar `navigation/map.ts` → adicionar role nos módulos
4. Atualizar esta documentação

### Adicionar Novo Módulo com Controle de Acesso

1. Definir roles no `navigation/map.ts`:
   ```typescript
   {
     id: 'novo-modulo',
     name: 'Novo Módulo',
     roles: ['ADMIN', 'GESTOR'],
     functions: [...]
   }
   ```
2. Componentes usam `useAuth().hasAnyRole(['ADMIN', 'GESTOR'])`
3. Rotas protegidas com `<ProtectedRoute requiredRoles={['ADMIN', 'GESTOR']}>`

---

**Última atualização**: 06/11/2025  
**Versão**: 1.0.0
