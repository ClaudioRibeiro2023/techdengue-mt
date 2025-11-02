import { UserManagerSettings } from 'oidc-client-ts'

const KEYCLOAK_URL = import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080'
const KEYCLOAK_REALM = import.meta.env.VITE_KEYCLOAK_REALM || 'techdengue'
const KEYCLOAK_CLIENT_ID = import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'techdengue-api'

const APP_URL = import.meta.env.VITE_APP_URL || window.location.origin

export const oidcConfig: UserManagerSettings = {
  authority: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}`,
  client_id: KEYCLOAK_CLIENT_ID,
  redirect_uri: `${APP_URL}/auth/callback`,
  post_logout_redirect_uri: `${APP_URL}/`,
  silent_redirect_uri: `${APP_URL}/auth/silent-renew`,
  response_type: 'code',
  scope: 'openid profile email roles',
  automaticSilentRenew: true,
  loadUserInfo: true,
  monitorSession: true,
  revokeTokensOnSignout: true,
  filterProtocolClaims: true,
  // No client_secret = PKCE will be used automatically
  metadata: {
    issuer: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}`,
    authorization_endpoint: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/auth`,
    token_endpoint: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/token`,
    userinfo_endpoint: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/userinfo`,
    end_session_endpoint: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/logout`,
    jwks_uri: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/certs`,
  }
}

export const ROLE_ADMIN = 'ADMIN'
export const ROLE_GESTOR = 'GESTOR'
export const ROLE_VIGILANCIA = 'VIGILANCIA'
export const ROLE_CAMPO = 'CAMPO'

export type UserRole = typeof ROLE_ADMIN | typeof ROLE_GESTOR | typeof ROLE_VIGILANCIA | typeof ROLE_CAMPO
