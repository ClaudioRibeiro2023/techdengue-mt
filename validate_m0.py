#!/usr/bin/env python3
"""
Script consolidado de validação M0 (Fundações)
Executa todos os testes de forma automatizada e gera relatório
"""
import sys
import requests
import psycopg2
import json
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

results = {
    "timestamp": datetime.now().isoformat(),
    "tests": {},
    "summary": {"total": 0, "passed": 0, "failed": 0}
}

def record_test(category, test_name, passed, details=""):
    if category not in results["tests"]:
        results["tests"][category] = []
    
    results["tests"][category].append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    
    results["summary"]["total"] += 1
    if passed:
        results["summary"]["passed"] += 1
    else:
        results["summary"]["failed"] += 1

# ============================================================================
# 1. INFRAESTRUTURA DOCKER
# ============================================================================
def test_infrastructure():
    print_section("1. INFRAESTRUTURA DOCKER")
    
    services = [
        ("db", 5432),
        ("keycloak", 8080),
        ("minio", 9000),
        ("prism", 4010),
        ("epi-api", 8000),
        ("campo-api", 8001),
        ("relatorios-api", 8002),
    ]
    
    for service, port in services:
        try:
            if service in ["db"]:
                # DB check via psycopg2
                conn = psycopg2.connect(
                    'postgresql://techdengue:techdengue@localhost:5432/techdengue',
                    connect_timeout=3
                )
                conn.close()
                print_success(f"{service} (porta {port})")
                record_test("infrastructure", service, True, f"Porta {port} acessível")
            else:
                # HTTP check
                resp = requests.get(f"http://localhost:{port}", timeout=3)
                print_success(f"{service} (porta {port})")
                record_test("infrastructure", service, True, f"Porta {port} acessível")
        except Exception as e:
            print_error(f"{service} (porta {port}): {str(e)}")
            record_test("infrastructure", service, False, str(e))

# ============================================================================
# 2. BANCO DE DADOS E MIGRAÇÕES
# ============================================================================
def test_database():
    print_section("2. BANCO DE DADOS E MIGRAÇÕES")
    
    try:
        conn = psycopg2.connect('postgresql://techdengue:techdengue@localhost:5432/techdengue')
        cur = conn.cursor()
        
        # Tabelas
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
        tables = [row[0] for row in cur.fetchall()]
        expected_tables = ['atividade', 'audit_log', 'evidencia', 'indicador_epi', 'relatorio']
        
        for table in expected_tables:
            if table in tables:
                print_success(f"Tabela {table} existe")
                record_test("database", f"table_{table}", True)
            else:
                print_error(f"Tabela {table} não encontrada")
                record_test("database", f"table_{table}", False)
        
        # Migrações Flyway
        cur.execute("SELECT version, success FROM flyway_schema_history ORDER BY installed_rank")
        migrations = cur.fetchall()
        
        for version, success in migrations:
            if success:
                print_success(f"Migração V{version} aplicada")
                record_test("database", f"migration_V{version}", True)
            else:
                print_error(f"Migração V{version} falhou")
                record_test("database", f"migration_V{version}", False)
        
        # Hypertables
        cur.execute("SELECT hypertable_name FROM timescaledb_information.hypertables")
        hypertables = [row[0] for row in cur.fetchall()]
        
        if 'indicador_epi' in hypertables:
            print_success("Hypertable indicador_epi ativa")
            record_test("database", "hypertable_indicador_epi", True)
        else:
            print_error("Hypertable indicador_epi não encontrada")
            record_test("database", "hypertable_indicador_epi", False)
        
        conn.close()
        
    except Exception as e:
        print_error(f"Erro ao testar banco: {str(e)}")
        record_test("database", "connection", False, str(e))

# ============================================================================
# 3. KEYCLOAK OIDC
# ============================================================================
def test_keycloak():
    print_section("3. KEYCLOAK OIDC")
    
    try:
        # Discovery
        resp = requests.get("http://localhost:8080/realms/techdengue/.well-known/openid-configuration")
        if resp.status_code == 200:
            config = resp.json()
            print_success(f"Discovery endpoint: {config['issuer']}")
            record_test("keycloak", "discovery", True, config['issuer'])
        else:
            print_error(f"Discovery failed: {resp.status_code}")
            record_test("keycloak", "discovery", False, str(resp.status_code))
        
        # Token grant
        token_url = "http://localhost:8080/realms/techdengue/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": "techdengue-api",
            "client_secret": "nLAgeUX8fEEvsif0ooNANo38NDnTzcqs",
            "username": "admin@techdengue.com",
            "password": "admin123",
            "scope": "openid profile email roles"
        }
        
        resp = requests.post(token_url, data=data)
        if resp.status_code == 200:
            tokens = resp.json()
            print_success(f"Token obtido (expires in {tokens['expires_in']}s)")
            
            # Decode roles
            import base64
            payload = tokens['access_token'].split('.')[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            claims = json.loads(base64.b64decode(payload))
            roles = claims.get('realm_access', {}).get('roles', [])
            
            expected_roles = ['ADMIN', 'GESTOR', 'VIGILANCIA', 'CAMPO']
            roles_found = [r for r in roles if r in expected_roles]
            
            if len(roles_found) == 4:
                print_success(f"Roles corretas: {', '.join(roles_found)}")
                record_test("keycloak", "roles", True, ', '.join(roles_found))
            else:
                print_warning(f"Roles parciais: {', '.join(roles_found)}")
                record_test("keycloak", "roles", False, ', '.join(roles_found))
        else:
            print_error(f"Token grant failed: {resp.status_code}")
            record_test("keycloak", "token_grant", False, str(resp.status_code))
            
    except Exception as e:
        print_error(f"Erro ao testar Keycloak: {str(e)}")
        record_test("keycloak", "connection", False, str(e))

# ============================================================================
# 4. OBSERVABILIDADE (APIs)
# ============================================================================
def test_observability():
    print_section("4. OBSERVABILIDADE (APIs)")
    
    apis = [
        ("epi-api", "http://localhost:8000"),
        ("campo-api", "http://localhost:8001"),
        ("relatorios-api", "http://localhost:8002"),
    ]
    
    for api_name, base_url in apis:
        print(f"\n{Colors.YELLOW}Testando {api_name}...{Colors.RESET}")
        
        # Health
        try:
            resp = requests.get(f"{base_url}/api/health")
            if resp.status_code == 200:
                data = resp.json()
                print_success(f"Health: {data.get('status')}")
                record_test("observability", f"{api_name}_health", True)
            else:
                print_error(f"Health failed: {resp.status_code}")
                record_test("observability", f"{api_name}_health", False)
        except Exception as e:
            print_error(f"Health error: {str(e)}")
            record_test("observability", f"{api_name}_health", False, str(e))
        
        # X-Request-ID
        try:
            import uuid
            custom_id = str(uuid.uuid4())
            resp = requests.get(f"{base_url}/api/health", headers={"X-Request-ID": custom_id})
            response_id = resp.headers.get('X-Request-ID')
            if response_id == custom_id:
                print_success(f"X-Request-ID propagado")
                record_test("observability", f"{api_name}_request_id", True)
            else:
                print_error(f"X-Request-ID não propagado")
                record_test("observability", f"{api_name}_request_id", False)
        except Exception as e:
            print_error(f"X-Request-ID error: {str(e)}")
            record_test("observability", f"{api_name}_request_id", False, str(e))
        
        # Metrics
        try:
            resp = requests.get(f"{base_url}/metrics")
            if resp.status_code == 200:
                content = resp.text
                metrics = ['http_requests_total', 'http_request_duration_seconds', 
                          'http_requests_in_progress', 'http_errors_total']
                found = [m for m in metrics if m in content]
                if len(found) >= 3:
                    print_success(f"Métricas Prometheus ({len(found)}/4)")
                    record_test("observability", f"{api_name}_metrics", True, f"{len(found)}/4")
                else:
                    print_warning(f"Métricas parciais ({len(found)}/4)")
                    record_test("observability", f"{api_name}_metrics", False, f"{len(found)}/4")
            else:
                print_error(f"Metrics failed: {resp.status_code}")
                record_test("observability", f"{api_name}_metrics", False)
        except Exception as e:
            print_error(f"Metrics error: {str(e)}")
            record_test("observability", f"{api_name}_metrics", False, str(e))

# ============================================================================
# 5. PRISM (OpenAPI Mock)
# ============================================================================
def test_prism():
    print_section("5. PRISM (OpenAPI Mock)")
    
    try:
        # Auth validation
        resp = requests.get("http://localhost:4010/indicadores")
        if resp.status_code == 401:
            print_success("Validação de autenticação (401 sem token)")
            record_test("prism", "auth_validation", True)
        else:
            print_warning(f"Auth validation retornou {resp.status_code}")
            record_test("prism", "auth_validation", False, str(resp.status_code))
        
        # Mock response (payload válido)
        payload = {
            "localizacao": {"latitude": -15.5, "longitude": -56.1},
            "tipo_foco": "CAIXA_DAGUA",
            "descricao": "Validação prism"
        }
        resp = requests.post(
            "http://localhost:4010/denuncias",
            json=payload,
            headers={"Authorization": "Bearer fake-token"}
        )
        if resp.status_code in (200, 201):
            print_success("Mock response gerado (POST /denuncias)")
            record_test("prism", "mock_response", True)
        else:
            print_error(f"Mock failed: {resp.status_code}")
            record_test("prism", "mock_response", False, str(resp.status_code))
            
    except Exception as e:
        print_error(f"Erro ao testar Prism: {str(e)}")
        record_test("prism", "connection", False, str(e))

# ============================================================================
# MAIN
# ============================================================================
def main():
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"VALIDAÇÃO M0 (FUNDAÇÕES) - TechDengue")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}{Colors.RESET}\n")
    
    test_infrastructure()
    test_database()
    test_keycloak()
    test_observability()
    test_prism()
    
    # Summary
    print_section("RESUMO DA VALIDAÇÃO")
    
    total = results["summary"]["total"]
    passed = results["summary"]["passed"]
    failed = results["summary"]["failed"]
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total de testes: {total}")
    print(f"{Colors.GREEN}Aprovados: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Reprovados: {failed}{Colors.RESET}")
    print(f"Taxa de sucesso: {success_rate:.1f}%\n")
    
    # Save results
    with open('validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Resultados salvos em: validation_results.json\n")
    
    if failed == 0:
        print(f"{Colors.GREEN}{'='*70}")
        print(f"✅ M0 (FUNDAÇÕES) VALIDADO COM SUCESSO!")
        print(f"{'='*70}{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{'='*70}")
        print(f"❌ M0 TEM {failed} TESTE(S) FALHANDO")
        print(f"{'='*70}{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
