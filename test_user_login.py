#!/usr/bin/env python3
import requests, base64, json

username = 'techdengue'
password = 'techdengue'
realm = 'techdengue'
client_id = 'techdengue-api'
client_secret = 'nLAgeUX8fEEvsif0ooNANo38NDnTzcqs'

token_url = f'http://localhost:8080/realms/{realm}/protocol/openid-connect/token'

resp = requests.post(token_url, data={
    'grant_type': 'password',
    'client_id': client_id,
    'client_secret': client_secret,
    'username': username,
    'password': password,
    'scope': 'openid profile email roles'
})

print('HTTP', resp.status_code)
if resp.status_code != 200:
    print(resp.text)
    raise SystemExit(1)

tokens = resp.json()
print('Access token length:', len(tokens.get('access_token','')))
print('Refresh token length:', len(tokens.get('refresh_token','')))

# Decode JWT payload (no verify) to inspect roles
parts = tokens['access_token'].split('.')
payload = parts[1] + '=' * ((4 - len(parts[1]) % 4) % 4)
claims = json.loads(base64.b64decode(payload.encode('utf-8')).decode('utf-8'))
print('preferred_username:', claims.get('preferred_username'))
roles = claims.get('realm_access', {}).get('roles', [])
print('roles:', ', '.join(roles))
print('\nOK')
