"""
Load Testing for M1 - Performance validation
Validates p95 ≤ 4s for all endpoints

Usage:
    python load_test_m1.py

Requirements:
    pip install requests numpy matplotlib
"""
import time
import requests
import statistics
import json
from pathlib import Path
from typing import List, Dict
import numpy as np


class LoadTester:
    """Load tester for M1 endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.results = {}
        
    def measure_request(self, method: str, endpoint: str, **kwargs) -> float:
        """Measure single request latency"""
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        
        latency = (time.time() - start) * 1000  # Convert to ms
        
        if response.status_code not in (200, 201):
            print(f"Warning: {endpoint} returned {response.status_code}")
        
        return latency
    
    def run_test(
        self,
        name: str,
        method: str,
        endpoint: str,
        iterations: int = 100,
        **kwargs
    ) -> Dict:
        """Run load test for an endpoint"""
        print(f"\nTesting {name}...")
        latencies = []
        
        for i in range(iterations):
            try:
                latency = self.measure_request(method, endpoint, **kwargs)
                latencies.append(latency)
                
                if (i + 1) % 10 == 0:
                    print(f"  Progress: {i + 1}/{iterations}")
            except Exception as e:
                print(f"  Error on iteration {i + 1}: {e}")
        
        if not latencies:
            return {
                "name": name,
                "error": "All requests failed"
            }
        
        # Calculate percentiles
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        avg = statistics.mean(latencies)
        
        result = {
            "name": name,
            "iterations": len(latencies),
            "avg_ms": round(avg, 2),
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2),
            "p99_ms": round(p99, 2),
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
            "p95_target_4s": p95 <= 4000,
            "status": "✅ PASS" if p95 <= 4000 else "❌ FAIL"
        }
        
        self.results[name] = result
        return result
    
    def print_results(self):
        """Print formatted results"""
        print("\n" + "="*80)
        print("LOAD TEST RESULTS - M1 PERFORMANCE")
        print("="*80)
        print(f"{'Endpoint':<40} {'p50':<10} {'p95':<10} {'p99':<10} {'Status':<10}")
        print("-"*80)
        
        for name, result in self.results.items():
            if "error" in result:
                print(f"{name:<40} ERROR: {result['error']}")
            else:
                p50 = f"{result['p50_ms']}ms"
                p95 = f"{result['p95_ms']}ms"
                p99 = f"{result['p99_ms']}ms"
                status = result['status']
                print(f"{name:<40} {p50:<10} {p95:<10} {p99:<10} {status:<10}")
        
        print("="*80)
        
        # Summary
        total = len([r for r in self.results.values() if "error" not in r])
        passed = len([r for r in self.results.values() 
                     if "error" not in r and r.get("p95_target_4s", False)])
        
        print(f"\nSummary: {passed}/{total} endpoints passed (p95 ≤ 4s)")
        print(f"Pass Rate: {passed/total*100:.1f}%\n")
        
    def save_results(self, filepath: str = "load_test_results.json"):
        """Save results to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to {filepath}")


def main():
    """Run all M1 load tests"""
    print("M1 Load Testing - Starting...")
    print("Target: p95 ≤ 4000ms (4 seconds)")
    
    tester = LoadTester()
    
    # Test 1: GET /mapa/camadas (small dataset)
    tester.run_test(
        name="GET /mapa/camadas (100 features)",
        method="GET",
        endpoint="/mapa/camadas",
        params={
            "tipo_camada": "incidencia",
            "competencia_inicio": "202401",
            "competencia_fim": "202401",
            "max_features": 100
        },
        iterations=50
    )
    
    # Test 2: GET /mapa/camadas (large dataset)
    tester.run_test(
        name="GET /mapa/camadas (1000 features)",
        method="GET",
        endpoint="/mapa/camadas",
        params={
            "tipo_camada": "incidencia",
            "competencia_inicio": "202401",
            "competencia_fim": "202401",
            "max_features": 1000
        },
        iterations=30
    )
    
    # Test 3: GET /mapa/camadas (with clustering)
    tester.run_test(
        name="GET /mapa/camadas (clustering)",
        method="GET",
        endpoint="/mapa/camadas",
        params={
            "tipo_camada": "incidencia",
            "competencia_inicio": "202401",
            "competencia_fim": "202401",
            "cluster": "true",
            "max_features": 10000
        },
        iterations=30
    )
    
    # Test 4: GET /mapa/municipios
    tester.run_test(
        name="GET /mapa/municipios",
        method="GET",
        endpoint="/mapa/municipios",
        iterations=50
    )
    
    # Test 5: GET /etl/epi/competencias
    tester.run_test(
        name="GET /etl/epi/competencias",
        method="GET",
        endpoint="/etl/epi/competencias",
        iterations=50
    )
    
    # Test 6: GET /health (baseline)
    tester.run_test(
        name="GET /health",
        method="GET",
        endpoint="/health",
        iterations=100
    )
    
    # Test relatórios-api
    tester_relatorios = LoadTester(base_url="http://localhost:8002/api")
    
    # Test 7: GET /relatorios/epi01 (PDF)
    tester_relatorios.run_test(
        name="GET /relatorios/epi01 (PDF)",
        method="GET",
        endpoint="/relatorios/epi01",
        params={
            "competencia_inicio": "202401",
            "competencia_fim": "202401",
            "formato": "pdf"
        },
        iterations=20
    )
    
    # Test 8: GET /relatorios/epi01 (CSV)
    tester_relatorios.run_test(
        name="GET /relatorios/epi01 (CSV)",
        method="GET",
        endpoint="/relatorios/epi01",
        params={
            "competencia_inicio": "202401",
            "competencia_fim": "202401",
            "formato": "csv"
        },
        iterations=30
    )
    
    # Merge results
    tester.results.update(tester_relatorios.results)
    
    # Print and save
    tester.print_results()
    tester.save_results()


if __name__ == "__main__":
    main()
