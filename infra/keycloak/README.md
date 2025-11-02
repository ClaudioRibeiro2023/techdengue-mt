# Keycloak Setup - TechDengue

Este diretório contém scripts e configurações para o Keycloak (OIDC Provider).

## Configuração Automática (Seed Script)

### Pré-requisitos

```bash
pip install requests
```

### Execução

Com o Keycloak rodando (via docker-compose):

```bash
python seed-keycloak.py
```

Ou especificando URL customizada:

```bash
python seed-keycloak.py --keycloak-url http://keycloak:8080
```

### O que o script cria

- **Realm**: `techdengue`
- **Client**: `techdengue-api`
  - Type: confidential
  - Service accounts enabled
  - PKCE (S256) habilitado
  - Redirect URIs: localhost:3000, 8000, 8001, 8002
- **Roles**: GESTOR, VIGILANCIA, CAMPO, ADMIN
- **Usuário de teste**: admin@techdengue.com / admin123
  - Roles: ADMIN, GESTOR

### Client Secret

Após executar o script, você verá o client secret gerado:

```
Client Secret: nLAgeUX8fEEvsif0ooNANo38NDnTzcqs
```

**Este secret já foi atualizado automaticamente nos arquivos `.env` das APIs.**

## Configuração Manual

Acesse o Admin Console: http://localhost:8080/admin

- Username: `admin`
- Password: `admin`

### 1. Criar Realm

1. Clique em "Create Realm"
2. Nome: `techdengue`
3. Enable

### 2. Criar Roles

Em `Realm roles`:
- GESTOR
- VIGILANCIA
- CAMPO
- ADMIN

### 3. Criar Client

Em `Clients` → `Create client`:

- Client ID: `techdengue-api`
- Client authentication: ON
- Authorization: ON
- Standard flow: ON
- Direct access grants: ON
- Service accounts roles: ON

**Settings:**
- Valid redirect URIs: `http://localhost:*`
- Web origins: `http://localhost:*`

**Credentials:**
- Copie o `Client secret` e atualize nos `.env` das APIs

### 4. Criar Usuários

Em `Users` → `Create user`:
- Username/Email: admin@techdengue.com
- Email verified: YES
- Set password: admin123 (temporary: NO)
- Role mappings: ADMIN, GESTOR

## Endpoints OIDC

- **Issuer**: `http://localhost:8080/realms/techdengue`
- **Well-known**: `http://localhost:8080/realms/techdengue/.well-known/openid-configuration`
- **Token**: `http://localhost:8080/realms/techdengue/protocol/openid-connect/token`
- **Auth**: `http://localhost:8080/realms/techdengue/protocol/openid-connect/auth`
- **UserInfo**: `http://localhost:8080/realms/techdengue/protocol/openid-connect/userinfo`

## Testar Autenticação

### Obter Token (Password Grant - Dev Only)

```bash
curl -X POST http://localhost:8080/realms/techdengue/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=techdengue-api" \
  -d "client_secret=nLAgeUX8fEEvsif0ooNANo38NDnTzcqs" \
  -d "username=admin@techdengue.com" \
  -d "password=admin123"
```

Resposta:
```json
{
  "access_token": "eyJhbGc...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGc...",
  "token_type": "Bearer"
}
```

### Validar Token

```bash
TOKEN="eyJhbGc..."
curl http://localhost:8080/realms/techdengue/protocol/openid-connect/userinfo \
  -H "Authorization: Bearer $TOKEN"
```

## Integração com Frontend

No frontend React, use uma biblioteca OIDC como `@react-keycloak/web` ou `oidc-client-ts`.

Exemplo de configuração:

```typescript
const keycloakConfig = {
  url: 'http://localhost:8080',
  realm: 'techdengue',
  clientId: 'techdengue-api'
}
```

## Integração com APIs (FastAPI)

Use `python-jose` para validar tokens JWT:

```python
from jose import jwt, JWTError
import requests

OIDC_ISSUER = "http://keycloak:8080/realms/techdengue"
JWKS_URL = f"{OIDC_ISSUER}/protocol/openid-connect/certs"

# Get JWKS
jwks = requests.get(JWKS_URL).json()

# Validate token
try:
    payload = jwt.decode(
        token,
        jwks,
        algorithms=["RS256"],
        audience="techdengue"
    )
    user_roles = payload.get("realm_access", {}).get("roles", [])
except JWTError:
    # Invalid token
    pass
```

## Troubleshooting

### "Keycloak not ready"
- Verifique se o container está rodando: `docker compose ps keycloak`
- Verifique logs: `docker compose logs keycloak`
- Aguarde ~30s após iniciar o Keycloak

### "Client secret inválido"
- Re-execute o seed script (safe, é idempotente)
- Ou copie manualmente do Admin Console → Clients → techdengue-api → Credentials

### "Token inválido nas APIs"
- Verifique se o `.env` está atualizado com o client_secret correto
- Verifique se as APIs estão usando `OIDC_ISSUER` correto (interno: `http://keycloak:8080`, externo: `http://localhost:8080`)

## Produção

⚠️ **Não use esta configuração em produção!**

Para produção:
- Use SSL/TLS (`sslRequired: external`)
- Troque senhas de admin
- Configure backup do banco de dados do Keycloak
- Use um DB externo (PostgreSQL) ao invés do H2 embutido
- Configure rate limiting e proteção contra brute force
- Revise redirect URIs e web origins
