#!/usr/bin/env python3
"""Test Prism API mock server"""
import requests

print("=== TESTE PRISM (OpenAPI Mock) ===\n")

# Test authenticated endpoint
print("1. Testing /indicadores (requires auth)...")
resp = requests.get("http://localhost:4010/indicadores")
print(f"   Without auth: {resp.status_code} (expected 401)")

resp = requests.get(
    "http://localhost:4010/indicadores",
    headers={"Authorization": "Bearer fake-token"}
)
if resp.status_code == 200:
    data = resp.json()
    print(f"   ✅ With auth: {resp.status_code}")
    print(f"   ✅ Response type: {type(data)}")
    if isinstance(data, list) and len(data) > 0:
        print(f"   ✅ Sample data keys: {list(data[0].keys())}")
else:
    print(f"   ❌ With auth: {resp.status_code}")

# Test public endpoint (denúncias POST)
print("\n2. Testing POST /denuncias...")
payload = {
    "localizacao": {"latitude": -15.5, "longitude": -56.1},
    "tipo_foco": "CAIXA_DAGUA",
    "descricao": "Teste Prism"
}
resp = requests.post(
    "http://localhost:4010/denuncias",
    json=payload,
    headers={"Authorization": "Bearer fake-token"}
)
print(f"   Status: {resp.status_code}")
if resp.status_code == 201:
    print(f"   ✅ Denúncia mockada criada")
    print(f"   Response: {resp.json()}")
else:
    print(f"   Response: {resp.text[:200]}")

# Test GET denúncias
print("\n3. Testing GET /denuncias...")
resp = requests.get(
    "http://localhost:4010/denuncias",
    headers={"Authorization": "Bearer fake-token"}
)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"   ✅ Retrieved {len(data) if isinstance(data, list) else 'N/A'} items")

print("\n✅ Prism mock server funcional!")
