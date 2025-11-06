const fetchFn = globalThis.fetch

function b64urlDecode(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/')
  const pad = s.length % 4 ? 4 - (s.length % 4) : 0
  s += '='.repeat(pad)
  return globalThis.Buffer.from(s, 'base64').toString('utf8')
}

async function main() {
  const KC = globalThis.process.env.KEYCLOAK_URL || 'http://localhost:8080'
  const REALM = globalThis.process.env.KEYCLOAK_REALM || 'techdengue'
  const CLIENT_ID = globalThis.process.env.KEYCLOAK_CLIENT_ID || 'techdengue-api'
  const USER = globalThis.process.env.KC_USER || globalThis.process.env.KEYCLOAK_USER || ''
  const PASS = globalThis.process.env.KC_PASS || globalThis.process.env.KEYCLOAK_PASS || ''
  const CLIENT_SECRET = globalThis.process.env.KEYCLOAK_CLIENT_SECRET || ''

  if (!USER || !PASS) {
    console.error('Missing KC_USER/KC_PASS environment variables.')
    globalThis.process.exit(2)
  }

  if (!fetchFn) {
    console.error('global fetch not available. Use Node 18+ or set up polyfill.')
    globalThis.process.exit(2)
  }

  const url = `${KC}/realms/${REALM}/protocol/openid-connect/token`
  const params = new URLSearchParams()
  params.set('grant_type', 'password')
  params.set('client_id', CLIENT_ID)
  params.set('username', USER)
  params.set('password', PASS)
  if (CLIENT_SECRET) params.set('client_secret', CLIENT_SECRET)

  const res = await fetchFn(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString(),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    console.error(`Token request failed: ${res.status} ${res.statusText}\n${text}`)
    globalThis.process.exit(1)
  }

  const data = await res.json()
  const access = data.access_token
  if (!access) {
    console.error('No access_token in response')
    console.log(JSON.stringify(data, null, 2))
    globalThis.process.exit(1)
  }

  const payload = JSON.parse(b64urlDecode(access.split('.')[1] || ''))
  const username = payload.preferred_username || payload.email || '(unknown)'
  const realmRoles = (payload.realm_access && payload.realm_access.roles) || []
  const clientRoles = (payload.resource_access && payload.resource_access[CLIENT_ID] && payload.resource_access[CLIENT_ID].roles) || []
  const exp = payload.exp ? new Date(payload.exp * 1000).toISOString() : '(n/a)'

  console.log('ROPC OK')
  console.log(`User: ${username}`)
  console.log(`Realm roles: ${realmRoles.join(', ')}`)
  console.log(`Client roles (${CLIENT_ID}): ${clientRoles.join(', ')}`)
  console.log(`Expires at: ${exp}`)
}

main().catch((e) => { console.error(e); globalThis.process.exit(1) })
