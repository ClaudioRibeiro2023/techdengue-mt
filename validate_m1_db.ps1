# Script de validação do banco M1
# Verifica se V012 foi aplicada e se dados MT foram importados

Write-Host "=== VALIDAÇÃO M1 - DATABASE ===" -ForegroundColor Cyan
Write-Host ""

# 1. Listar tabelas
Write-Host "1. Verificando tabelas existentes..." -ForegroundColor Yellow
docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;"

Write-Host ""
Write-Host "2. Verificando tabelas específicas M1..." -ForegroundColor Yellow

# 2. Verificar tabelas municipios_ibge
$tableCheck = docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'municipios_ibge');"
if ($tableCheck -match "t") {
    Write-Host "  ✅ municipios_ibge existe" -ForegroundColor Green
    
    # Contar registros
    $count = docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT COUNT(*) FROM municipios_ibge;"
    Write-Host "     Registros: $count (esperado: 141)" -ForegroundColor White
} else {
    Write-Host "  ❌ municipios_ibge NÃO existe" -ForegroundColor Red
}

# 3. Verificar municipios_geometrias
$tableCheck = docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'municipios_geometrias');"
if ($tableCheck -match "t") {
    Write-Host "  ✅ municipios_geometrias existe" -ForegroundColor Green
    
    $count = docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT COUNT(*) FROM municipios_geometrias;"
    Write-Host "     Registros: $count (esperado: 141)" -ForegroundColor White
} else {
    Write-Host "  ❌ municipios_geometrias NÃO existe" -ForegroundColor Red
}

# 4. Verificar liraa_classificacao
$tableCheck = docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'liraa_classificacao');"
if ($tableCheck -match "t") {
    Write-Host "  ✅ liraa_classificacao existe" -ForegroundColor Green
    
    $count = docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT COUNT(*) FROM liraa_classificacao;"
    Write-Host "     Registros: $count (esperado: 107)" -ForegroundColor White
} else {
    Write-Host "  ❌ liraa_classificacao NÃO existe" -ForegroundColor Red
}

# 5. Verificar casos_sinan
$tableCheck = docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'casos_sinan');"
if ($tableCheck -match "t") {
    Write-Host "  ✅ casos_sinan existe" -ForegroundColor Green
    
    $count = docker exec infra-db-1 psql -U techdengue -d techdengue -t -c "SELECT COUNT(*) FROM casos_sinan;"
    Write-Host "     Registros: $count (esperado: ~6000)" -ForegroundColor White
} else {
    Write-Host "  ❌ casos_sinan NÃO existe" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== FIM VALIDAÇÃO ===" -ForegroundColor Cyan
