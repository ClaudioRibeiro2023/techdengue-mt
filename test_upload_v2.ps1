# Script para testar upload de fotos - versão com PNG válido
# Cria uma imagem PNG 1x1 válida

# PNG 1x1 pixel vermelho válido (mínimo possível)
$pngBytes = [byte[]]@(
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 width x height
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53, 0xDE,  # bit depth, color type, CRC
    0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41, 0x54,  # IDAT chunk
    0x08, 0x99, 0x63, 0xF8, 0xCF, 0xC0, 0x00, 0x00,  # compressed image data
    0x03, 0x01, 0x01, 0x00, 0x18, 0xDD, 0x8D, 0xB4,  # + CRC
    0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,  # IEND chunk
    0xAE, 0x42, 0x60, 0x82
)

$testImagePath = "$PSScriptRoot\test_image.png"
[System.IO.File]::WriteAllBytes($testImagePath, $pngBytes)

Write-Host "Imagem PNG válida criada: $testImagePath" -ForegroundColor Green
Write-Host "Tamanho: $($pngBytes.Length) bytes" -ForegroundColor Cyan

# Testar upload usando curl para melhor controle de headers
Write-Host "`nTestando upload com curl..." -ForegroundColor Cyan

$curlOutput = & curl -X POST "http://localhost:8000/api/upload/foto" `
    -F "file=@$testImagePath;type=image/png" `
    -H "Accept: application/json" `
    -s -w "`n%{http_code}"

$lines = $curlOutput -split "`n"
$httpCode = $lines[-1]
$response = $lines[0..($lines.Length - 2)] -join "`n"

if ($httpCode -eq "200") {
    Write-Host "`n✓ Upload bem-sucedido!" -ForegroundColor Green
    Write-Host "Resposta:" -ForegroundColor Yellow
    $response | ConvertFrom-Json | ConvertTo-Json -Depth 3
    
    # Tentar baixar a foto
    $uploadData = $response | ConvertFrom-Json
    $photoPath = $uploadData.url
    Write-Host "`nTestando download da foto: $photoPath" -ForegroundColor Cyan
    
    $downloadResponse = curl -s "http://localhost:8000/api/upload/foto/$photoPath" -o "$PSScriptRoot\downloaded_image.png" -w "%{http_code}"
    
    if ($downloadResponse -eq "200") {
        Write-Host "✓ Download bem-sucedido!" -ForegroundColor Green
        $downloadedSize = (Get-Item "$PSScriptRoot\downloaded_image.png").Length
        Write-Host "Tamanho baixado: $downloadedSize bytes" -ForegroundColor Cyan
        Remove-Item "$PSScriptRoot\downloaded_image.png" -Force
    } else {
        Write-Host "✗ Erro no download (HTTP $downloadResponse)" -ForegroundColor Red
    }
    
} else {
    Write-Host "`n✗ Erro no upload (HTTP $httpCode)" -ForegroundColor Red
    Write-Host $response
}

# Limpar arquivo de teste
Remove-Item $testImagePath -Force
Write-Host "`n✓ Arquivo de teste removido" -ForegroundColor Green
