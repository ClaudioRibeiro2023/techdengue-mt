# 📚 Documentação TechDengue - Frontend

## 🎯 Visão Geral

Documentação completa do frontend da plataforma TechDengue, incluindo autenticação, controle de acesso, testes e guias de deploy.

---

## 📖 Índice de Documentos

### 🔐 Autenticação e Controle de Acesso

#### [ROLES_E_ACESSO.md](./ROLES_E_ACESSO.md) ⭐ PRINCIPAL
**Tamanho**: ~470 linhas | **Tempo de leitura**: 15 minutos

Documentação completa sobre RBAC (Role-Based Access Control):
- 4 roles do sistema (ADMIN, GESTOR, VIGILANCIA, CAMPO)
- Matriz de acesso por módulo (10 módulos, 33 funções)
- Configuração completa do Keycloak (passo-a-passo)
- Troubleshooting de problemas comuns
- Scripts de validação

**👥 Audiência**: Desenvolvedores, DevOps, Admins de Sistema

---

#### [KEYCLOAK_SETUP_RAPIDO.md](./KEYCLOAK_SETUP_RAPIDO.md) ⚡ QUICK START
**Tamanho**: ~120 linhas | **Tempo de leitura**: 5 minutos

Setup rápido de autenticação:
- Configuração em 5 passos (realm, client, roles, usuário, teste)
- Checklist completo
- Problemas comuns e soluções rápidas

**👥 Audiência**: DevOps, Admins iniciantes

---

### 🛠️ Desenvolvimento e Testes

#### [DEMO_E2E_MODES.md](./DEMO_E2E_MODES.md)
**Tamanho**: ~310 linhas | **Tempo de leitura**: 10 minutos

Guia de modos especiais de execução:
- DEMO mode (apresentações sem backend)
- E2E mode (testes automatizados)
- Quando usar cada modo
- Configuração de ambientes
- Migração de flags antigas

**👥 Audiência**: Desenvolvedores, QA

---

### ✅ Validação e Deploy

#### [CHECKLIST_VALIDACAO_PRODUCAO.md](./CHECKLIST_VALIDACAO_PRODUCAO.md)
**Tamanho**: ~380 linhas | **Tempo de leitura**: 15 minutos

Checklist completo para deploy em produção:
- Validação de Keycloak e roles
- Build de produção
- Testes de login e navegação
- Validação de proteção de rotas
- Fluxos completos por perfil
- Performance e segurança
- Suite E2E completa

**👥 Audiência**: DevOps, QA, Tech Leads

---

## 🎓 Guias Por Persona

### 👨‍💻 Para Desenvolvedores

**Começar aqui**:
1. [DEMO_E2E_MODES.md](./DEMO_E2E_MODES.md) - entender bypass
2. [ROLES_E_ACESSO.md](./ROLES_E_ACESSO.md) - saber quais roles usar no código
3. Scripts de teste: `npm run test:e2e`

**Casos comuns**:
- Adicionar nova role → ROLES_E_ACESSO.md seção "Manutenção"
- Adicionar novo módulo → ROLES_E_ACESSO.md seção "Manutenção"
- Rodar testes → DEMO_E2E_MODES.md seção "E2E Mode"

---

### 🚀 Para DevOps/Admins

**Começar aqui**:
1. [KEYCLOAK_SETUP_RAPIDO.md](./KEYCLOAK_SETUP_RAPIDO.md) - setup inicial 5 min
2. [CHECKLIST_VALIDACAO_PRODUCAO.md](./CHECKLIST_VALIDACAO_PRODUCAO.md) - antes de deploy
3. [ROLES_E_ACESSO.md](./ROLES_E_ACESSO.md) - referência completa

**Casos comuns**:
- Criar usuário → KEYCLOAK_SETUP_RAPIDO.md seção "Criar Usuários"
- Atribuir roles → usar script `kc_assign_roles.ps1`
- Validar token → `npm run ropc:check`
- Troubleshooting → ROLES_E_ACESSO.md seção "Troubleshooting"

---

### 🧪 Para QA/Testers

**Começar aqui**:
1. [DEMO_E2E_MODES.md](./DEMO_E2E_MODES.md) - como rodar testes
2. [CHECKLIST_VALIDACAO_PRODUCAO.md](./CHECKLIST_VALIDACAO_PRODUCAO.md) - testes manuais
3. [ROLES_E_ACESSO.md](./ROLES_E_ACESSO.md) - matriz de acesso para casos de teste

**Casos comuns**:
- Rodar testes E2E → `npm run test:e2e`
- Testar roles → usar E2E mode com `e2e-roles` no localStorage
- Validar menus → ROLES_E_ACESSO.md seção "Acesso por Módulo"

---

## 🔧 Scripts Úteis

### Validação de Token
```bash
npm run ropc:check
```
Valida login e exibe roles do usuário.

### Testes E2E Completos
```bash
npm run test:e2e
```
Roda 76+ testes em 5 browsers diferentes.

### Testes E2E Específicos
```bash
# Apenas mobile
npm run test:e2e -- e2e/mobile.spec.ts

# Apenas roles
npm run test:e2e -- e2e/roles.spec.ts

# Apenas navegação
npm run test:e2e -- e2e/navigation.spec.ts
```

### Atribuir Roles (PowerShell)
```powershell
.\scripts\kc_assign_roles.ps1
```

---

## 📊 Arquitetura de Acesso

```
Usuario → Keycloak → JWT Token → Frontend
                        ↓
                  realm_access.roles
                        ↓
              AuthContext.hasRole()
                        ↓
           Filtra Menus/Rotas/Funções
```

### 4 Roles Principais

```
ADMIN ────────► Tudo (10 módulos)
                │
GESTOR ───────► Dashboard, Mapa, Previsão, Vigi Epi/Ento, Relatórios
                │
VIGILANCIA ──► Vigi Epi/Ento, Mapa, Relatórios
                │
CAMPO ────────► ETL, Resposta Op, Vigi Ento (parcial)
```

---

## 🗂️ Estrutura de Pastas

```
frontend/
├── docs/
│   ├── README.md                         ← Você está aqui
│   ├── ROLES_E_ACESSO.md                 ← Referência completa
│   ├── KEYCLOAK_SETUP_RAPIDO.md          ← Quick start
│   ├── DEMO_E2E_MODES.md                 ← Modos especiais
│   └── CHECKLIST_VALIDACAO_PRODUCAO.md   ← Validação deploy
│
├── e2e/
│   ├── navigation.spec.ts                ← Testes navegação
│   ├── roles.spec.ts                     ← Testes roles
│   ├── mobile.spec.ts                    ← Testes mobile
│   ├── collapse.spec.ts                  ← Testes persistência
│   ├── darkmode.spec.ts                  ← Testes dark mode
│   ├── auth.spec.ts                      ← Testes autenticação
│   └── dashboard.spec.ts                 ← Testes dashboard
│
├── scripts/
│   ├── ropc-check.js                     ← Validação token
│   └── kc_assign_roles.ps1               ← Atribuir roles
│
└── src/
    ├── contexts/AuthContext.tsx          ← Controle autenticação
    ├── components/auth/ProtectedRoute.tsx ← Proteção rotas
    └── navigation/map.ts                 ← Mapa navegação + roles
```

---

## 📈 Estatísticas

| Métrica | Valor |
|---------|-------|
| **Documentos** | 5 |
| **Total de linhas** | ~1.280 |
| **Testes E2E** | 76+ |
| **Browsers testados** | 5 |
| **Módulos documentados** | 10 |
| **Funções mapeadas** | 33 |
| **Roles definidas** | 4 |
| **Scripts de automação** | 2 |

---

## 🔄 Fluxo de Trabalho

### 1. Desenvolvimento
```
Ler DEMO_E2E_MODES.md → Configurar ambiente → Desenvolver → Testar E2E
```

### 2. Configuração Keycloak
```
Ler KEYCLOAK_SETUP_RAPIDO.md → Setup 5 min → Validar com ropc:check
```

### 3. Deploy
```
Seguir CHECKLIST_VALIDACAO_PRODUCAO.md → Build → Testes → Deploy
```

---

## ❓ FAQ

### Onde encontro a matriz completa de roles?
[ROLES_E_ACESSO.md](./ROLES_E_ACESSO.md) seção "Acesso por Módulo"

### Como criar um novo usuário no Keycloak?
[KEYCLOAK_SETUP_RAPIDO.md](./KEYCLOAK_SETUP_RAPIDO.md) seção "Criar Usuários"

### Como rodar apenas os testes mobile?
```bash
npm run test:e2e -- e2e/mobile.spec.ts
```

### Menu não aparece para o usuário?
[ROLES_E_ACESSO.md](./ROLES_E_ACESSO.md) seção "Troubleshooting" → "Menu não aparece"

### Como validar se roles estão corretas?
```bash
npm run ropc:check
```

---

## 🆘 Suporte

### Problemas Comuns

| Problema | Documento | Seção |
|----------|-----------|-------|
| Menu não aparece | ROLES_E_ACESSO.md | Troubleshooting |
| Token sem roles | ROLES_E_ACESSO.md | Troubleshooting |
| Access Denied | ROLES_E_ACESSO.md | Troubleshooting |
| Teste E2E falhando | DEMO_E2E_MODES.md | Verificação Rápida |
| Deploy falhando | CHECKLIST_VALIDACAO_PRODUCAO.md | Checklist Final |

---

## 📅 Atualizações

| Data | Versão | Mudanças |
|------|--------|----------|
| 06/11/2025 | 1.0.0 | Documentação inicial completa |

---

## 🎯 Próximos Passos

Após ler esta documentação:

1. **DevOps**: Seguir KEYCLOAK_SETUP_RAPIDO.md
2. **Desenvolvedores**: Explorar DEMO_E2E_MODES.md
3. **QA**: Usar CHECKLIST_VALIDACAO_PRODUCAO.md
4. **Todos**: Consultar ROLES_E_ACESSO.md como referência

---

**Manutenção da documentação**: Esta pasta deve ser atualizada sempre que houver mudanças em roles, módulos ou procedimentos de deploy.

**Contribuindo**: Para adicionar/atualizar documentação, seguir o padrão existente e atualizar este README.

---

**Última atualização**: 06/11/2025  
**Mantido por**: Equipe TechDengue
