Param(
  [string]$KeycloakUrl = 'http://localhost:8080',
  [string]$Realm = 'techdengue',
  [string]$ClientId = 'techdengue-frontend'
)

$ErrorActionPreference='Stop'

$token = (Invoke-RestMethod -Method Post -Uri "$KeycloakUrl/realms/master/protocol/openid-connect/token" -ContentType 'application/x-www-form-urlencoded' -Body "grant_type=password&client_id=admin-cli&username=admin&password=admin").access_token
$auth = @{ Authorization = "Bearer $token" }

$clients = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/clients?clientId=$ClientId"
if(-not $clients -or $clients.Count -eq 0){ throw "Client $ClientId not found" }
$cid = $clients[0].id
$client = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/clients/$cid"

$client.redirectUris = @(
  'http://localhost:6080/auth/callback',
  'http://localhost:6081/auth/callback',
  'http://localhost:6082/auth/callback'
)
$client.webOrigins = @(
  'http://localhost:6080',
  'http://localhost:6081',
  'http://localhost:6082'
)
if(-not $client.attributes){ $client | Add-Member -NotePropertyName attributes -NotePropertyValue @{} }
$client.attributes.'post.logout.redirect.uris' = "http://localhost:6080/*\nhttp://localhost:6081/*\nhttp://localhost:6082/*"
$client.attributes.'pkce.code.challenge.method' = 'S256'
$client.publicClient = $true
$client.standardFlowEnabled = $true
$client.implicitFlowEnabled = $false

$clientJson = $client | ConvertTo-Json -Depth 12
Invoke-RestMethod -Method Put -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/clients/$cid" -Body $clientJson | Out-Null
Write-Host "[OK] Client updated with multiple localhost ports"
