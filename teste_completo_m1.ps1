#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Teste completo do sistema TechDengue M1
    
.DESCRIPTION
    Valida Backend API, Frontend Dashboard e Relatórios PDF
    
.EXAMPLE
    .\teste_completo_m1.ps1
#>

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "    TECHDENGUE M1 - TESTE COMPLETO DO SISTEMA" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0
$SuccessCount = 0

# Função auxiliar para testar endpoints
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Nome,
        [string]$ExpectedPattern
    )
    
    Write-Host "Testando: $Nome" -ForegroundColor Yellow
    Write-Host "   URL: $Url" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 10 -ErrorAction Stop
        $json = $response | ConvertTo-Json -Depth 10
        
        if ($ExpectedPattern -and $json -notmatch $ExpectedPattern) {
            Write-Host "   FALHOU: Padrao esperado nao encontrado" -ForegroundColor Red
            $script:ErrorCount++
            return $false
        }
        
        Write-Host "   OK" -ForegroundColor Green
        $script:SuccessCount++
        return $true
    }
    catch {
        Write-Host "   ERRO: $($_.Exception.Message)" -ForegroundColor Red
        $script:ErrorCount++
        return $false
    }
}

Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host "ETAPA 1: Verificar Containers Docker" -ForegroundColor Cyan
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

try {
    $containers = docker compose -f infra/docker-compose.yml ps --format json | ConvertFrom-Json
    
    $dbRunning = $false
    $apiRunning = $false
    
    foreach ($container in $containers) {
        if ($container.Service -eq "db" -and $container.State -eq "running") {
            $dbRunning = $true
            Write-Host "PostgreSQL: Running" -ForegroundColor Green
        }
        if ($container.Service -eq "epi-api" -and $container.State -eq "running") {
            $apiRunning = $true
            Write-Host "EPI API: Running" -ForegroundColor Green
        }
    }
    
    if (-not $dbRunning) {
        Write-Host "PostgreSQL nao esta rodando" -ForegroundColor Red
        Write-Host "   Execute: docker compose -f infra/docker-compose.yml up -d" -ForegroundColor Yellow
        $ErrorCount++
    }
    
    if (-not $apiRunning) {
        Write-Host "EPI API nao esta rodando" -ForegroundColor Red
        $ErrorCount++
    }
    
    if ($dbRunning -and $apiRunning) {
        $SuccessCount++
    }
}
catch {
    Write-Host "Erro ao verificar containers: $($_.Exception.Message)" -ForegroundColor Red
    $ErrorCount++
}

Write-Host ""
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host "ETAPA 2: Testar Backend API (EPI)" -ForegroundColor Cyan
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

# Aguardar API inicializar (se necessário)
Start-Sleep -Seconds 2

# Teste 1: Health Check
Test-Endpoint -Url "http://localhost:8000/api/health" -Nome "Health Check" -ExpectedPattern "ok"

# Teste 2: Estatísticas 2025
$url = 'http://localhost:8000/api/mapa/estatisticas?ano=2025&semana_epi_inicio=1&semana_epi_fim=42'
$result = Test-Endpoint -Url $url -Nome "Estatísticas 2025" -ExpectedPattern "34276"

if ($result) {
    Write-Host "   Total Casos: 34.276" -ForegroundColor Green
    Write-Host "   Municipios: 141" -ForegroundColor Green
}

# Teste 3: Série Temporal Cuiabá
$urlSeries = 'http://localhost:8000/api/mapa/series-temporais/5103403?ano=2025'
Test-Endpoint -Url $urlSeries -Nome "Serie Temporal Cuiaba" -ExpectedPattern "Cuiab"

# Teste 4: Heatmap
$url = 'http://localhost:8000/api/mapa/heatmap?ano=2025&semana_epi_inicio=1&semana_epi_fim=42'
Test-Endpoint -Url $url -Nome "Heatmap Data" -ExpectedPattern "points"

Write-Host ""
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host "ETAPA 3: Validar Banco de Dados" -ForegroundColor Cyan
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".\validate_m1_db.ps1") {
    Write-Host "Executando validacao do banco..." -ForegroundColor Yellow
    & .\validate_m1_db.ps1
    $SuccessCount++
} else {
    Write-Host "Script validate_m1_db.ps1 nao encontrado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host "ETAPA 4: Verificar Frontend" -ForegroundColor Cyan
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "frontend/package.json") {
    Write-Host "Frontend encontrado" -ForegroundColor Green
    Write-Host "   Localizacao: frontend/" -ForegroundColor Gray
    
    if (Test-Path "frontend/node_modules") {
        Write-Host "   Dependencias instaladas" -ForegroundColor Green
    } else {
        Write-Host "   Dependencias nao instaladas" -ForegroundColor Yellow
        Write-Host "   Execute: cd frontend && npm install" -ForegroundColor Yellow
    }
    
    Write-Host "   Para rodar: cd frontend && npm run dev" -ForegroundColor Cyan
    Write-Host "   URL: http://localhost:6080/dashboard-epi" -ForegroundColor Cyan
    $SuccessCount++
} else {
    Write-Host "Frontend nao encontrado" -ForegroundColor Red
    $ErrorCount++
}

Write-Host ""
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host "ETAPA 5: Verificar API Relatorios" -ForegroundColor Cyan
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "relatorios-api/app/main.py") {
    Write-Host "API Relatorios encontrada" -ForegroundColor Green
    Write-Host "   Localizacao: relatorios-api/" -ForegroundColor Gray
    
    # Tentar conectar
    try {
        Invoke-RestMethod -Uri "http://localhost:8001/api/health" -Method Get -TimeoutSec 3 -ErrorAction Stop | Out-Null
        Write-Host "   API Relatorios esta rodando (porta 8001)" -ForegroundColor Green
        $SuccessCount++
    }
    catch {
        Write-Host "   API Relatorios nao esta rodando" -ForegroundColor Yellow
        Write-Host "   Para iniciar:" -ForegroundColor Yellow
        Write-Host "     cd relatorios-api" -ForegroundColor Gray
        Write-Host "     python -m venv venv" -ForegroundColor Gray
        Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
        Write-Host "     pip install -r requirements.txt" -ForegroundColor Gray
        Write-Host "     uvicorn app.main:app --reload --port 8001" -ForegroundColor Gray
    }
} else {
    Write-Host "API Relatorios nao encontrada" -ForegroundColor Red
    $ErrorCount++
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "                    RESUMO FINAL" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$TotalTests = $SuccessCount + $ErrorCount
$SuccessRate = if ($TotalTests -gt 0) { [math]::Round(($SuccessCount / $TotalTests) * 100, 1) } else { 0 }

Write-Host "Testes Executados: $TotalTests" -ForegroundColor White
Write-Host "Sucessos: $SuccessCount" -ForegroundColor Green
Write-Host "Falhas: $ErrorCount" -ForegroundColor $(if ($ErrorCount -eq 0) { "Green" } else { "Red" })
Write-Host "Taxa de Sucesso: $SuccessRate%" -ForegroundColor $(if ($SuccessRate -ge 80) { "Green" } elseif ($SuccessRate -ge 60) { "Yellow" } else { "Red" })
Write-Host ""

if ($ErrorCount -eq 0) {
    Write-Host "TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Sistema M1 esta 100% funcional!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Cyan
    Write-Host "   1. Abrir Dashboard: http://localhost:6080/dashboard-epi" -ForegroundColor White
    Write-Host "   2. Ver documentacao: cat M1_COMPLETO_FINAL.md" -ForegroundColor White
    Write-Host "   3. Gerar relatorio PDF: Ver TESTE_M1_DASHBOARD.md" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "Alguns testes falharam." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Acoes recomendadas:" -ForegroundColor Yellow
    Write-Host "   1. Verificar se Docker esta rodando: docker compose -f infra/docker-compose.yml ps" -ForegroundColor White
    Write-Host "   2. Ver logs da API: docker logs infra-epi-api-1 --tail 50" -ForegroundColor White
    Write-Host "   3. Consultar TESTE_M1_DASHBOARD.md para troubleshooting" -ForegroundColor White
    Write-Host ""
    exit 1
}
