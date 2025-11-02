#!/usr/bin/env python3
"""Test observability features across all APIs"""
import requests
import json
import uuid

APIs = [
    {"name": "epi-api", "url": "http://localhost:8000"},
    {"name": "campo-api", "url": "http://localhost:8001"},
    {"name": "relatorios-api", "url": "http://localhost:8002"},
]

print("=== TESTE DE OBSERVABILIDADE ===\n")

for api in APIs:
    print(f"\n🔍 Testando {api['name']}...")
    
    # 1. Test health endpoint
    print(f"  1. Health Check...")
    resp = requests.get(f"{api['url']}/api/health")
    if resp.status_code == 200:
        data = resp.json()
        print(f"     ✅ Status: {data.get('status', 'N/A')}")
        print(f"     ✅ Service: {data.get('service', 'N/A')}")
        version = data.get('version', 'N/A')
        print(f"     {'✅' if version != 'N/A' else '⚠️'} Version: {version}")
    else:
        print(f"     ❌ Failed: {resp.status_code}")
        continue
    
    # 2. Test X-Request-ID propagation
    print(f"  2. X-Request-ID Propagation...")
    custom_id = str(uuid.uuid4())
    resp = requests.get(
        f"{api['url']}/api/health",
        headers={"X-Request-ID": custom_id}
    )
    response_id = resp.headers.get('X-Request-ID')
    if response_id == custom_id:
        print(f"     ✅ Request ID propagated: {response_id}")
    else:
        print(f"     ❌ Request ID mismatch: sent={custom_id}, received={response_id}")
    
    # 3. Test auto-generated X-Request-ID
    print(f"  3. Auto-generated X-Request-ID...")
    resp = requests.get(f"{api['url']}/api/health")
    response_id = resp.headers.get('X-Request-ID')
    if response_id:
        print(f"     ✅ Auto-generated ID: {response_id}")
    else:
        print(f"     ❌ No X-Request-ID in response")
    
    # 4. Test Prometheus metrics endpoint
    print(f"  4. Prometheus Metrics...")
    resp = requests.get(f"{api['url']}/metrics")
    if resp.status_code == 200:
        content = resp.text
        
        # Check for key metrics
        metrics_found = []
        if 'http_requests_total' in content:
            metrics_found.append('http_requests_total')
        if 'http_request_duration_seconds' in content:
            metrics_found.append('http_request_duration_seconds')
        if 'http_requests_in_progress' in content:
            metrics_found.append('http_requests_in_progress')
        if 'http_errors_total' in content:
            metrics_found.append('http_errors_total')
        
        if len(metrics_found) >= 3:
            print(f"     ✅ Metrics available: {', '.join(metrics_found)}")
        else:
            print(f"     ⚠️  Only {len(metrics_found)} metrics found: {metrics_found}")
    else:
        print(f"     ❌ Metrics endpoint failed: {resp.status_code}")
    
    # 5. Test JSON structured logs (via test request)
    print(f"  5. Triggering request for log generation...")
    resp = requests.get(f"{api['url']}/api/health")
    print(f"     ✅ Request completed (check Docker logs for JSON format)")

print("\n" + "="*60)
print("✅ Observability tests completed!")
print("\nTo check JSON logs:")
for api in APIs:
    print(f"  docker logs infra-{api['name']}-1 --tail 5")
