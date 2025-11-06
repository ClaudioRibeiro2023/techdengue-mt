# Script para testar upload de fotos
# Cria uma imagem PNG pequena de teste e faz upload

# Criar imagem de teste 100x100 pixels (PNG mínimo)
$pngBytes = [byte[]]@(
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
    0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x64,  # 100x100
    0x08, 0x02, 0x00, 0x00, 0x00, 0xFF, 0x80, 0x02, 0x03
)

$testImagePath = "$PSScriptRoot\test_image.png"
[System.IO.File]::WriteAllBytes($testImagePath, $pngBytes)

Write-Host "Imagem de teste criada: $testImagePath" -ForegroundColor Green

# Testar upload
Write-Host "`nTestando upload para http://localhost:8000/api/upload/foto..." -ForegroundColor Cyan

try {
    $form = @{
        file = Get-Item -Path $testImagePath
    }
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/upload/foto" `
        -Method Post `
        -Form $form
    
    Write-Host "`n✓ Upload bem-sucedido!" -ForegroundColor Green
    Write-Host "Resposta:" -ForegroundColor Yellow
    $response | ConvertTo-Json -Depth 3
    
    # Limpar arquivo de teste
    Remove-Item $testImagePath -Force
    Write-Host "`n✓ Arquivo de teste removido" -ForegroundColor Green
    
} catch {
    Write-Host "`n✗ Erro no upload:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host $_.ErrorDetails.Message
}
