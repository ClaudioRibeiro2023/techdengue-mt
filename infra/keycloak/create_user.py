#!/usr/bin/env python3
"""Create or update a user in Keycloak realm 'techdengue' and assign realm roles.
Usage:
  python create_user.py --username techdengue --password techdengue [--email user@example.com] [--roles ADMIN GESTOR VIGILANCIA CAMPO]
Requires: requests
"""
import argparse
import sys
from typing import List

try:
    import requests
except Exception:
    print("Please install requests: pip install requests")
    sys.exit(1)

KEYCLOAK_URL_DEFAULT = "http://localhost:8080"
REALM = "techdengue"


def get_admin_token(base_url: str, admin_user: str, admin_pass: str) -> str:
    resp = requests.post(
        f"{base_url}/realms/master/protocol/openid-connect/token",
        data={
            "client_id": "admin-cli",
            "username": admin_user,
            "password": admin_pass,
            "grant_type": "password",
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def find_user(base_url: str, token: str, username: str):
    r = requests.get(
        f"{base_url}/admin/realms/{REALM}/users?username={username}", headers=get_headers(token)
    )
    r.raise_for_status()
    users = r.json()
    return users[0] if users else None


def create_user(base_url: str, token: str, username: str, password: str, email: str):
    user_cfg = {
        "username": username,
        "email": email,
        "emailVerified": True,
        "enabled": True,
        "credentials": [
            {"type": "password", "value": password, "temporary": False}
        ],
    }
    r = requests.post(
        f"{base_url}/admin/realms/{REALM}/users",
        headers=get_headers(token),
        json=user_cfg,
    )
    if r.status_code not in (201, 409):
        raise RuntimeError(f"Create user failed: {r.status_code} {r.text}")
    if r.status_code == 201:
        print(f"✓ Created user '{username}'")
    else:
        print(f"✓ User '{username}' already exists")

    # Get user id
    user = find_user(base_url, token, username)
    if not user:
        raise RuntimeError("User not found after create")

    # Ensure password
    resp = requests.put(
        f"{base_url}/admin/realms/{REALM}/users/{user['id']}/reset-password",
        headers=get_headers(token),
        json={"type": "password", "value": password, "temporary": False},
    )
    if resp.status_code in (204, 201):
        print("✓ Password set")
    else:
        print(f"! Password set response: {resp.status_code} {resp.text}")

    return user["id"]


def assign_roles(base_url: str, token: str, user_id: str, role_names: List[str]):
    # Get all roles
    r = requests.get(
        f"{base_url}/admin/realms/{REALM}/roles", headers=get_headers(token)
    )
    r.raise_for_status()
    all_roles = {role["name"]: role for role in r.json()}

    payload = [
        {"id": all_roles[name]["id"], "name": name}
        for name in role_names
        if name in all_roles
    ]
    if not payload:
        print("! No matching roles to assign")
        return

    resp = requests.post(
        f"{base_url}/admin/realms/{REALM}/users/{user_id}/role-mappings/realm",
        headers=get_headers(token),
        json=payload,
    )
    if resp.status_code == 204:
        print(f"✓ Roles assigned: {', '.join(role_names)}")
    else:
        print(f"! Role assign response: {resp.status_code} {resp.text}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--keycloak-url", default=KEYCLOAK_URL_DEFAULT)
    p.add_argument("--admin-user", default="admin")
    p.add_argument("--admin-pass", default="admin")
    p.add_argument("--username", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--email", default=None)
    p.add_argument(
        "--roles",
        nargs="*",
        default=["ADMIN", "GESTOR", "VIGILANCIA", "CAMPO"],
    )
    args = p.parse_args()

    base_url = args.keycloak_url.rstrip("/")
    email = args.email or f"{args.username}@techdengue.com"

    token = get_admin_token(base_url, args.admin_user, args.admin_pass)
    user_id = create_user(base_url, token, args.username, args.password, email)
    assign_roles(base_url, token, user_id, args.roles)

    print("\n✓ Done.")


if __name__ == "__main__":
    sys.exit(main())
