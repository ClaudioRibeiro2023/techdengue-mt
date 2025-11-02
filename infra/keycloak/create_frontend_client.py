#!/usr/bin/env python3
"""Create a dedicated public SPA client for the frontend with PKCE S256."""
import requests

BASE_URL = 'http://localhost:8080'
REALM = 'techdengue'
CLIENT_ID = 'techdengue-frontend'
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'

REDIRECTS = [
    'http://localhost:3000/*',
]
ORIGINS = [
    'http://localhost:3000',
]

def tok():
    r = requests.post(f"{BASE_URL}/realms/master/protocol/openid-connect/token", data={
        'client_id': 'admin-cli', 'username': ADMIN_USER, 'password': ADMIN_PASS, 'grant_type': 'password'
    })
    r.raise_for_status()
    return r.json()['access_token']

def headers(t):
    return {"Authorization": f"Bearer {t}", "Content-Type": "application/json"}

def main():
    t = tok()
    # Exists?
    q = requests.get(f"{BASE_URL}/admin/realms/{REALM}/clients?clientId={CLIENT_ID}", headers=headers(t))
    q.raise_for_status()
    if q.json():
        print('✓ Client already exists:', CLIENT_ID)
        return

    cfg = {
        'clientId': CLIENT_ID,
        'name': 'TechDengue Frontend',
        'protocol': 'openid-connect',
        'publicClient': True,
        'standardFlowEnabled': True,
        'implicitFlowEnabled': False,
        'directAccessGrantsEnabled': False,
        'serviceAccountsEnabled': False,
        'authorizationServicesEnabled': False,
        'redirectUris': REDIRECTS,
        'webOrigins': ORIGINS,
        'attributes': {'pkce.code.challenge.method': 'S256'},
        'defaultClientScopes': ['web-origins','acr','profile','roles','email'],
        'optionalClientScopes': ['address','phone','offline_access','microprofile-jwt']
    }
    r = requests.post(f"{BASE_URL}/admin/realms/{REALM}/clients", headers=headers(t), json=cfg)
    if r.status_code == 201:
        print('✓ Created client:', CLIENT_ID)
    elif r.status_code == 409:
        print('✓ Client already exists:', CLIENT_ID)
    else:
        raise SystemExit(f"Create failed: {r.status_code} {r.text}")

if __name__ == '__main__':
    main()
