# ⚡ Keycloak - Setup Rápido

## 🎯 Objetivo

Configurar autenticação e controle de acesso do TechDengue em **5 minutos**.

---

## ✅ Pré-requisitos

- Docker Desktop rodando
- Keycloak em `http://localhost:8080`
- Login admin: `admin` / `admin123`

---

## 🚀 Quick Start

### 1. Criar Realm (30 segundos)

```bash
# Acesse: http://localhost:8080
# Login: admin / admin123
# Dropdown topo esquerdo → "Add realm"
# Name: techdengue
# Create
```

### 2. Criar Client (1 minuto)

```yaml
Client ID: techdengue-api
Root URL: http://localhost:6080
Valid Redirect URIs: 
  - http://localhost:6080/*
  - http://localhost:6090/*
Web Origins: 
  - http://localhost:6080
  - http://localhost:6090
```

### 3. Criar Roles (1 minuto)

```
Realm Roles → Add Role:
  - ADMIN
  - GESTOR
  - VIGILANCIA
  - CAMPO
```

### 4. Criar Usuário Admin (2 minutos)

```yaml
Username: admin@techdengue.com
Email: admin@techdengue.com
Password: admin123  # Temporary: OFF
Role Mappings: ADMIN, GESTOR, VIGILANCIA, CAMPO
```

### 5. Testar (30 segundos)

```bash
npm run ropc:check
# Username: admin@techdengue.com
# Password: admin123
# ✓ Login successful!
```

---

## 🎓 Roles e Acesso

| Role | Acesso |
|------|--------|
| **ADMIN** | Tudo + Administração |
| **GESTOR** | Dashboard, Relatórios, Previsões |
| **VIGILANCIA** | Vigilância Epi/Ento, Mapa Vivo |
| **CAMPO** | ETL, Resposta Operacional, Coletas |

---

## 🔧 Scripts Úteis

### Validar Token
```bash
npm run ropc:check
```

### Atribuir Roles via Script (PowerShell)
```powershell
.\scripts\kc_assign_roles.ps1
```

---

## 📚 Documentação Completa

Para detalhes completos, veja: [`ROLES_E_ACESSO.md`](./ROLES_E_ACESSO.md)

---

## 🐛 Problemas Comuns

### Menu não aparece?

1. Rodar `npm run ropc:check` e verificar roles no token
2. Fazer logout/login no frontend
3. Verificar se roles estão atribuídas no Keycloak

### "Access Denied"?

1. Verificar roles necessárias na rota (ver `App.tsx`)
2. Confirmar usuário tem a role no Keycloak
3. Renovar token (logout/login)

### "invalid_grant"?

1. Verificar credenciais (username/password)
2. Verificar se client existe
3. Habilitar "Direct Access Grants" no client

---

## ⏱️ Checklist Completo

- [ ] Realm `techdengue` criado
- [ ] Client `techdengue-api` configurado
- [ ] 4 Roles criadas (ADMIN, GESTOR, VIGILANCIA, CAMPO)
- [ ] Usuário admin criado com todas roles
- [ ] Teste `npm run ropc:check` passou
- [ ] Login no frontend funcionou
- [ ] Menus aparecem corretamente

---

**Tempo total**: ~5 minutos  
**Dificuldade**: Fácil ⭐

Para produção, consulte a documentação completa!
