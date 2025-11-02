#!/usr/bin/env python3
"""
Update Keycloak client 'techdengue-api' to be a Public client (SPA) with PKCE S256
- publicClient: true
- standardFlowEnabled: true
- directAccessGrantsEnabled: true (kept for CLI tests)
- serviceAccountsEnabled: false
- authorizationServicesEnabled: false
- attributes.pkce.code.challenge.method: S256
"""
import sys
import requests

BASE_URL = 'http://localhost:8080'
REALM = 'techdengue'
CLIENT_ID = 'techdengue-api'
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'


def get_admin_token():
    r = requests.post(f"{BASE_URL}/realms/master/protocol/openid-connect/token", data={
        'client_id': 'admin-cli',
        'username': ADMIN_USER,
        'password': ADMIN_PASS,
        'grant_type': 'password'
    })
    r.raise_for_status()
    return r.json()['access_token']


def headers(tok):
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


def find_client(tok):
    r = requests.get(f"{BASE_URL}/admin/realms/{REALM}/clients?clientId={CLIENT_ID}", headers=headers(tok))
    r.raise_for_status()
    arr = r.json()
    return arr[0] if arr else None


def update_client(tok, client_uuid):
    # Fetch current
    r = requests.get(f"{BASE_URL}/admin/realms/{REALM}/clients/{client_uuid}", headers=headers(tok))
    r.raise_for_status()
    cfg = r.json()

    # Apply updates
    cfg.update({
        'publicClient': True,
        'standardFlowEnabled': True,
        'directAccessGrantsEnabled': True,
        'serviceAccountsEnabled': False,
        'authorizationServicesEnabled': False,
    })
    attrs = cfg.get('attributes', {})
    attrs['pkce.code.challenge.method'] = 'S256'
    cfg['attributes'] = attrs

    # Persist
    put = requests.put(f"{BASE_URL}/admin/realms/{REALM}/clients/{client_uuid}", headers=headers(tok), json=cfg)
    put.raise_for_status()


def main():
    tok = get_admin_token()
    cli = find_client(tok)
    if not cli:
        print("Client not found")
        sys.exit(1)
    update_client(tok, cli['id'])

    # Read back a few fields
    final = requests.get(f"{BASE_URL}/admin/realms/{REALM}/clients/{cli['id']}", headers=headers(tok)).json()
    print("publicClient:", final.get('publicClient'))
    print("standardFlowEnabled:", final.get('standardFlowEnabled'))
    print("directAccessGrantsEnabled:", final.get('directAccessGrantsEnabled'))
    print("serviceAccountsEnabled:", final.get('serviceAccountsEnabled'))
    print("authorizationServicesEnabled:", final.get('authorizationServicesEnabled'))
    print("pkce:", final.get('attributes', {}).get('pkce.code.challenge.method'))


if __name__ == '__main__':
    main()
