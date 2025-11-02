import requests

# Test Keycloak authentication
print("=== TESTE KEYCLOAK OIDC ===\n")

# 1. Check OIDC discovery
print("1. OIDC Discovery endpoint:")
response = requests.get("http://localhost:8080/realms/techdengue/.well-known/openid-configuration")
if response.status_code == 200:
    config = response.json()
    print(f"   ✅ Issuer: {config['issuer']}")
    print(f"   ✅ Authorization endpoint: {config['authorization_endpoint']}")
    print(f"   ✅ Token endpoint: {config['token_endpoint']}")
else:
    print(f"   ❌ Error: {response.status_code}")

# 2. Get token with password grant (test user)
print("\n2. Testing password grant with test user:")
token_url = "http://localhost:8080/realms/techdengue/protocol/openid-connect/token"
data = {
    "grant_type": "password",
    "client_id": "techdengue-api",
    "client_secret": "nLAgeUX8fEEvsif0ooNANo38NDnTzcqs",
    "username": "admin@techdengue.com",
    "password": "admin123",
    "scope": "openid profile email roles"
}

response = requests.post(token_url, data=data)
if response.status_code == 200:
    tokens = response.json()
    print(f"   ✅ Access token received (length: {len(tokens['access_token'])})")
    print(f"   ✅ Refresh token received (length: {len(tokens['refresh_token'])})")
    print(f"   ✅ Expires in: {tokens['expires_in']}s")
    
    # Decode token to check roles
    import base64
    import json
    
    # Parse JWT (simple decode without verification for testing)
    parts = tokens['access_token'].split('.')
    if len(parts) == 3:
        # Decode payload
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = base64.b64decode(payload)
        claims = json.loads(decoded)
        
        print(f"   ✅ User: {claims.get('preferred_username', 'N/A')}")
        print(f"   ✅ Email: {claims.get('email', 'N/A')}")
        
        roles = claims.get('realm_access', {}).get('roles', [])
        print(f"   ✅ Roles: {', '.join([r for r in roles if r in ['ADMIN', 'GESTOR', 'VIGILANCIA', 'CAMPO']])}")
else:
    print(f"   ❌ Error: {response.status_code}")
    print(f"   {response.text}")

print("\n✅ Teste Keycloak concluído!")
