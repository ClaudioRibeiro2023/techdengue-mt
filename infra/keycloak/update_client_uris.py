#!/usr/bin/env python3
import requests

BASE_URL = 'http://localhost:8080'
REALM = 'techdengue'
CLIENT_ID = 'techdengue-api'
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin'

ADD_REDIRECTS = [
    'http://localhost:3000/*',
    'http://192.168.10.113:3000/*',
    'http://172.26.16.1:3000/*',
]
ADD_ORIGINS = [
    'http://localhost:3000',
    'http://192.168.10.113:3000',
    'http://172.26.16.1:3000',
]


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


def main():
    tok = get_admin_token()
    q = requests.get(f"{BASE_URL}/admin/realms/{REALM}/clients?clientId={CLIENT_ID}", headers=headers(tok))
    q.raise_for_status()
    arr = q.json()
    if not arr:
        print('Client not found')
        return
    cid = arr[0]['id']

    cfg = requests.get(f"{BASE_URL}/admin/realms/{REALM}/clients/{cid}", headers=headers(tok)).json()

    redirects = set(cfg.get('redirectUris', []) + ADD_REDIRECTS)
    origins = set(cfg.get('webOrigins', []) + ADD_ORIGINS)
    cfg['redirectUris'] = sorted(redirects)
    cfg['webOrigins'] = sorted(origins)

    put = requests.put(f"{BASE_URL}/admin/realms/{REALM}/clients/{cid}", headers=headers(tok), json=cfg)
    put.raise_for_status()

    final = requests.get(f"{BASE_URL}/admin/realms/{REALM}/clients/{cid}", headers=headers(tok)).json()
    print('redirectUris:', final.get('redirectUris'))
    print('webOrigins:', final.get('webOrigins'))


if __name__ == '__main__':
    main()
