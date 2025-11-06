Param(
  [string]$KeycloakUrl = 'http://localhost:8080',
  [string]$Realm = 'techdengue',
  [string]$AdminUser = 'admin',
  [string]$AdminPass = 'admin',
  [string]$FrontendClientId = 'techdengue-frontend',
  [string]$RedirectUri = 'http://localhost:6080/auth/callback',
  [string]$PostLogoutUris = 'http://localhost:6080/*',
  [string]$WebOrigin = 'http://localhost:6080',
  [string]$TestUserEmail = 'admin@techdengue.com',
  [string]$TestUserPassword = 'admin123'
)

$ErrorActionPreference = 'Stop'

function Write-Step($msg){ Write-Host ("[+] " + $msg) -ForegroundColor Cyan }
function Write-Ok($msg){ Write-Host ("[OK] " + $msg) -ForegroundColor Green }
function Write-Warn($msg){ Write-Host ("[!] " + $msg) -ForegroundColor Yellow }

Write-Step "Obtendo token de administrador..."
$tokenResp = Invoke-RestMethod -Method Post -Uri "$KeycloakUrl/realms/master/protocol/openid-connect/token" -ContentType 'application/x-www-form-urlencoded' -Body "grant_type=password&client_id=admin-cli&username=$AdminUser&password=$AdminPass"
$adminToken = $tokenResp.access_token
if(-not $adminToken){ throw 'Falha ao obter token admin' }
$auth = @{ Authorization = "Bearer $adminToken" }
Write-Ok "Token admin obtido"

Write-Step "Criando/Atualizando client SPA: $FrontendClientId"
$existing = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/clients?clientId=$FrontendClientId"
if(-not $existing -or $existing.Count -eq 0){
  $payload = [ordered]@{
    clientId = $FrontendClientId
    name = 'TechDengue Frontend SPA'
    protocol = 'openid-connect'
    publicClient = $true
    standardFlowEnabled = $true
    implicitFlowEnabled = $false
    directAccessGrantsEnabled = $false
    serviceAccountsEnabled = $false
    redirectUris = @($RedirectUri)
    webOrigins = @($WebOrigin)
    attributes = @{ 'post.logout.redirect.uris' = $PostLogoutUris; 'pkce.code.challenge.method' = 'S256' }
  } | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Method Post -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/clients" -Body $payload | Out-Null
  Write-Ok "Client criado: $FrontendClientId"
}else{
  $cid = $existing[0].id
  $client = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/clients/$cid"
  $client.publicClient = $true
  $client.standardFlowEnabled = $true
  $client.implicitFlowEnabled = $false
  $client.directAccessGrantsEnabled = $false
  $client.redirectUris = @($RedirectUri)
  $client.webOrigins = @($WebOrigin)
  if(-not $client.attributes){ $client | Add-Member -NotePropertyName attributes -NotePropertyValue @{} }
  $client.attributes.'post.logout.redirect.uris' = $PostLogoutUris
  $client.attributes.'pkce.code.challenge.method' = 'S256'
  $json = $client | ConvertTo-Json -Depth 12
  Invoke-RestMethod -Method Put -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/clients/$cid" -Body $json | Out-Null
  Write-Ok "Client atualizado: $FrontendClientId"
}

Write-Step "Garantindo usuário de teste: $TestUserEmail"
$users = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/users?username=$([uri]::EscapeDataString($TestUserEmail))&exact=true"
if(-not $users -or $users.Count -eq 0){
  $u = [ordered]@{
    username = $TestUserEmail
    email = $TestUserEmail
    enabled = $true
    emailVerified = $true
  } | ConvertTo-Json -Depth 6
  Invoke-RestMethod -Method Post -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/users" -Body $u | Out-Null
  Start-Sleep -Milliseconds 300
  $users = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/users?username=$([uri]::EscapeDataString($TestUserEmail))&exact=true"
  Write-Ok "Usuário criado"
} else {
  Write-Ok "Usuário já existe"
}
$uid = $users[0].id

# Habilita usuário e reseta senha
Invoke-RestMethod -Method Put -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/users/$uid" -Body (@{ enabled=$true; emailVerified=$true } | ConvertTo-Json) | Out-Null
$pwd = @{ type='password'; value=$TestUserPassword; temporary=$false } | ConvertTo-Json
Invoke-RestMethod -Method Put -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/users/$uid/reset-password" -Body $pwd | Out-Null
Write-Ok "Senha definida para $TestUserEmail"

Write-Ok "Configuração do Keycloak concluída com sucesso."
