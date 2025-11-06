#!/usr/bin/env python3
"""
Seed Keycloak with TechDengue realm and clients.
Requires: pip install requests
Usage: python seed-keycloak.py [--keycloak-url http://localhost:8080]
"""
import argparse
import json
import sys
import time

try:
    import requests
except ImportError:
    print("Error: requests module not found")
    print("Install: pip install requests")
    sys.exit(1)

class KeycloakSeeder:
    def __init__(self, base_url: str, admin_user: str = "admin", admin_pass: str = "admin"):
        self.base_url = base_url.rstrip('/')
        self.admin_user = admin_user
        self.admin_pass = admin_pass
        self.token = None
        
    def wait_for_keycloak(self, timeout: int = 60):
        """Wait for Keycloak to be ready."""
        print(f"Waiting for Keycloak at {self.base_url}...")
        start = time.time()
        while time.time() - start < timeout:
            try:
                # Try to get admin token as health check
                resp = requests.get(f"{self.base_url}/", timeout=2)
                if resp.status_code in [200, 404]:  # 404 is ok, means server is up
                    print("✓ Keycloak is ready")
                    return True
            except:
                pass
            time.sleep(2)
        print("✗ Keycloak not ready after timeout")
        return False
    
    def get_admin_token(self):
        """Get admin access token."""
        print("Getting admin token...")
        resp = requests.post(
            f"{self.base_url}/realms/master/protocol/openid-connect/token",
            data={
                "client_id": "admin-cli",
                "username": self.admin_user,
                "password": self.admin_pass,
                "grant_type": "password"
            }
        )
        resp.raise_for_status()
        self.token = resp.json()['access_token']
        print("✓ Got admin token")
        return self.token
    
    def headers(self):
        """Get authorization headers."""
        if not self.token:
            self.get_admin_token()
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def realm_exists(self, realm_name: str) -> bool:
        """Check if realm exists."""
        resp = requests.get(
            f"{self.base_url}/admin/realms/{realm_name}",
            headers=self.headers()
        )
        return resp.status_code == 200
    
    def create_realm(self):
        """Create TechDengue realm."""
        realm_name = "techdengue"
        
        if self.realm_exists(realm_name):
            print(f"✓ Realm '{realm_name}' already exists")
            return
        
        print(f"Creating realm '{realm_name}'...")
        realm_config = {
            "realm": realm_name,
            "enabled": True,
            "displayName": "TechDengue",
            "displayNameHtml": "<b>TechDengue</b> - Vigilância em Saúde",
            "sslRequired": "none",  # dev only
            "registrationAllowed": False,
            "loginWithEmailAllowed": True,
            "duplicateEmailsAllowed": False,
            "resetPasswordAllowed": True,
            "editUsernameAllowed": False,
            "bruteForceProtected": True,
            "permanentLockout": False,
            "maxFailureWaitSeconds": 900,
            "minimumQuickLoginWaitSeconds": 60,
            "waitIncrementSeconds": 60,
            "quickLoginCheckMilliSeconds": 1000,
            "maxDeltaTimeSeconds": 43200,
            "failureFactor": 5,
            "accessTokenLifespan": 300,
            "accessTokenLifespanForImplicitFlow": 900,
            "ssoSessionIdleTimeout": 1800,
            "ssoSessionMaxLifespan": 36000,
            "offlineSessionIdleTimeout": 2592000,
            "accessCodeLifespan": 60,
            "accessCodeLifespanUserAction": 300,
            "accessCodeLifespanLogin": 1800,
            "actionTokenGeneratedByAdminLifespan": 43200,
            "actionTokenGeneratedByUserLifespan": 300,
        }
        
        resp = requests.post(
            f"{self.base_url}/admin/realms",
            headers=self.headers(),
            json=realm_config
        )
        resp.raise_for_status()
        print(f"✓ Created realm '{realm_name}'")
    
    def create_roles(self):
        """Create realm roles."""
        realm_name = "techdengue"
        roles = ["GESTOR", "VIGILANCIA", "CAMPO", "ADMIN"]
        
        print("Creating realm roles...")
        for role in roles:
            resp = requests.post(
                f"{self.base_url}/admin/realms/{realm_name}/roles",
                headers=self.headers(),
                json={"name": role, "description": f"Papel {role}"}
            )
            if resp.status_code == 201:
                print(f"  ✓ Created role '{role}'")
            elif resp.status_code == 409:
                print(f"  ✓ Role '{role}' already exists")
            else:
                print(f"  ✗ Failed to create role '{role}': {resp.status_code}")
    
    def create_client(self):
        """Create techdengue-api client."""
        realm_name = "techdengue"
        client_id = "techdengue-api"
        
        print(f"Creating client '{client_id}'...")
        
        client_config = {
            "clientId": client_id,
            "name": "TechDengue API",
            "description": "Backend APIs (epi, campo, relatorios)",
            "enabled": True,
            "protocol": "openid-connect",
            "publicClient": False,
            "bearerOnly": False,
            "standardFlowEnabled": True,
            "implicitFlowEnabled": False,
            "directAccessGrantsEnabled": True,
            "serviceAccountsEnabled": True,
            "authorizationServicesEnabled": True,
            "redirectUris": [
                "http://localhost:6080/*",
                "http://localhost:8000/*",
                "http://localhost:8001/*",
                "http://localhost:8002/*"
            ],
            "webOrigins": [
                "http://localhost:6080",
                "http://localhost:8000",
                "http://localhost:8001",
                "http://localhost:8002"
            ],
            "attributes": {
                "pkce.code.challenge.method": "S256"
            },
            "defaultClientScopes": [
                "web-origins",
                "acr",
                "profile",
                "roles",
                "email"
            ],
            "optionalClientScopes": [
                "address",
                "phone",
                "offline_access",
                "microprofile-jwt"
            ]
        }
        
        resp = requests.post(
            f"{self.base_url}/admin/realms/{realm_name}/clients",
            headers=self.headers(),
            json=client_config
        )
        
        if resp.status_code == 201:
            print(f"✓ Created client '{client_id}'")
            # Get client to retrieve secret
            clients = requests.get(
                f"{self.base_url}/admin/realms/{realm_name}/clients?clientId={client_id}",
                headers=self.headers()
            ).json()
            
            if clients:
                client_uuid = clients[0]['id']
                secret_resp = requests.get(
                    f"{self.base_url}/admin/realms/{realm_name}/clients/{client_uuid}/client-secret",
                    headers=self.headers()
                )
                if secret_resp.status_code == 200:
                    secret = secret_resp.json()['value']
                    print(f"  Client Secret: {secret}")
                    print(f"  Update your .env files with: OIDC_CLIENT_SECRET={secret}")
        elif resp.status_code == 409:
            print(f"✓ Client '{client_id}' already exists")
        else:
            print(f"✗ Failed to create client: {resp.status_code} - {resp.text}")
    
    def create_test_user(self):
        """Create a test user."""
        realm_name = "techdengue"
        username = "admin@techdengue.com"
        
        print(f"Creating test user '{username}'...")
        
        user_config = {
            "username": username,
            "email": username,
            "emailVerified": True,
            "enabled": True,
            "firstName": "Admin",
            "lastName": "TechDengue",
            "credentials": [{
                "type": "password",
                "value": "admin123",
                "temporary": False
            }],
            "realmRoles": ["ADMIN", "GESTOR"]
        }
        
        resp = requests.post(
            f"{self.base_url}/admin/realms/{realm_name}/users",
            headers=self.headers(),
            json=user_config
        )
        
        if resp.status_code == 201:
            print(f"✓ Created user '{username}' (password: admin123)")
        elif resp.status_code == 409:
            print(f"✓ User '{username}' already exists")
        else:
            print(f"✗ Failed to create user: {resp.status_code}")
    
    def seed_all(self):
        """Run all seeding steps."""
        print("\n=== Seeding Keycloak for TechDengue ===\n")
        
        if not self.wait_for_keycloak():
            return False
        
        try:
            self.get_admin_token()
            self.create_realm()
            self.create_roles()
            self.create_client()
            self.create_test_user()
            
            print("\n✓ Keycloak seeding completed successfully!")
            print(f"\nAccess Keycloak Admin Console: {self.base_url}/admin")
            print(f"  Username: {self.admin_user}")
            print(f"  Password: {self.admin_pass}")
            print(f"\nRealm: techdengue")
            print(f"Test user: admin@techdengue.com / admin123")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"\n✗ Error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Seed Keycloak with TechDengue configuration")
    parser.add_argument(
        "--keycloak-url",
        default="http://localhost:8080",
        help="Keycloak base URL (default: http://localhost:8080)"
    )
    parser.add_argument(
        "--admin-user",
        default="admin",
        help="Admin username (default: admin)"
    )
    parser.add_argument(
        "--admin-pass",
        default="admin",
        help="Admin password (default: admin)"
    )
    
    args = parser.parse_args()
    
    seeder = KeycloakSeeder(args.keycloak_url, args.admin_user, args.admin_pass)
    success = seeder.seed_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
