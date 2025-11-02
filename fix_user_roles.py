#!/usr/bin/env python3
"""Fix user roles in Keycloak"""
import requests

KEYCLOAK_URL = "http://localhost:8080"
REALM = "techdengue"
USERNAME = "admin@techdengue.com"

# Get admin token
print("Getting admin token...")
token_resp = requests.post(
    f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
    data={
        "client_id": "admin-cli",
        "username": "admin",
        "password": "admin",
        "grant_type": "password"
    }
)
token = token_resp.json()['access_token']
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Get user ID
print(f"Getting user ID for {USERNAME}...")
users_resp = requests.get(
    f"{KEYCLOAK_URL}/admin/realms/{REALM}/users?username={USERNAME}",
    headers=headers
)
users = users_resp.json()
if not users:
    print(f"❌ User {USERNAME} not found")
    exit(1)

user_id = users[0]['id']
print(f"✅ User ID: {user_id}")

# Get available realm roles
print("Getting realm roles...")
roles_resp = requests.get(
    f"{KEYCLOAK_URL}/admin/realms/{REALM}/roles",
    headers=headers
)
all_roles = {role['name']: role for role in roles_resp.json()}

# Assign roles
roles_to_assign = ['ADMIN', 'GESTOR', 'VIGILANCIA', 'CAMPO']
print(f"Assigning roles: {roles_to_assign}")

roles_payload = [
    {"id": all_roles[role]['id'], "name": role}
    for role in roles_to_assign
    if role in all_roles
]

assign_resp = requests.post(
    f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/role-mappings/realm",
    headers=headers,
    json=roles_payload
)

if assign_resp.status_code == 204:
    print("✅ Roles assigned successfully!")
else:
    print(f"❌ Failed to assign roles: {assign_resp.status_code}")
    print(assign_resp.text)

# Verify
verify_resp = requests.get(
    f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/role-mappings/realm",
    headers=headers
)
assigned_roles = [role['name'] for role in verify_resp.json()]
print(f"✅ User now has roles: {assigned_roles}")
