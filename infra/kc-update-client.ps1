Param(
  [string]$KeycloakUrl = 'http://localhost:8080',
  [string]$Realm = 'techdengue',
  [string]$ClientId = 'techdengue-frontend',
  [bool]$DirectAccessGrantsEnabled = $true
)

$ErrorActionPreference='Stop'

$token = (Invoke-RestMethod -Method Post -Uri "$KeycloakUrl/realms/master/protocol/openid-connect/token" -ContentType 'application/x-www-form-urlencoded' -Body "grant_type=password&client_id=admin-cli&username=admin&password=admin").access_token
$auth = @{ Authorization = "Bearer $token" }

$clients = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/clients?clientId=$ClientId"
if(-not $clients -or $clients.Count -eq 0){ throw "Client $ClientId not found" }
$cid = $clients[0].id
$client = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/clients/$cid"
$client.directAccessGrantsEnabled = $DirectAccessGrantsEnabled
$clientJson = $client | ConvertTo-Json -Depth 12
Invoke-RestMethod -Method Put -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/clients/$cid" -Body $clientJson | Out-Null
Write-Host "[OK] Client updated: directAccessGrantsEnabled=$DirectAccessGrantsEnabled"
