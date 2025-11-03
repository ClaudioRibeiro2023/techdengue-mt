# Verificar versão do schema e função update_updated_at_column

Write-Host "=== VERIFICAÇÃO SCHEMA ===" -ForegroundColor Cyan

# 1. Versão atual do schema
Write-Host "`n1. Versão atual do schema Flyway:" -ForegroundColor Yellow
docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT version, description, installed_on FROM flyway_schema_history ORDER BY installed_rank DESC LIMIT 5;"

# 2. Verificar se a função existe
Write-Host "`n2. Verificando função update_updated_at_column:" -ForegroundColor Yellow
$funcExists = docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT EXISTS(SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column');"
if ($funcExists -match "t") {
    Write-Host "  ✅ Função existe" -ForegroundColor Green
} else {
    Write-Host "  ❌ Função NÃO existe" -ForegroundColor Red
}

Write-Host ""
