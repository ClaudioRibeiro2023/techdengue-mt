Param(
  [string]$KeycloakUrl = 'http://localhost:8080',
  [string]$Realm = 'techdengue',
  [string]$AdminUser = 'admin',
  [string]$AdminPass = 'admin',
  [string]$NewUsername = 'adm',
  [string]$NewPassword = 'adm123',
  [string]$Email = 'adm@techdengue.com'
)

$ErrorActionPreference = 'Stop'

function Log([string]$m){ Write-Host ("[+] " + $m) -ForegroundColor Cyan }
function Ok([string]$m){ Write-Host ("[OK] " + $m) -ForegroundColor Green }
function Warn([string]$m){ Write-Host ("[!] " + $m) -ForegroundColor Yellow }

Log "Obtendo token admin..."
$token = (Invoke-RestMethod -Method Post -Uri "$KeycloakUrl/realms/master/protocol/openid-connect/token" -ContentType 'application/x-www-form-urlencoded' -Body "grant_type=password&client_id=admin-cli&username=$AdminUser&password=$AdminPass").access_token
if(-not $token){ throw 'Falha ao obter token admin' }
$auth = @{ Authorization = "Bearer $token" }
Ok "Token admin obtido"

# Busca ou cria usuário
Log "Garantindo usuário '$NewUsername'..."
$users = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/users?username=$([uri]::EscapeDataString($NewUsername))&exact=true"
if(-not $users -or $users.Count -eq 0){
  $payload = [ordered]@{
    username = $NewUsername
    email = $Email
    enabled = $true
    emailVerified = $true
  } | ConvertTo-Json -Depth 6
  Invoke-RestMethod -Method Post -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/users" -Body $payload | Out-Null
  Start-Sleep -Milliseconds 300
  $users = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/users?username=$([uri]::EscapeDataString($NewUsername))&exact=true"
  Ok "Usuário criado: $NewUsername"
} else {
  Ok "Usuário já existe: $NewUsername"
}
$uid = $users[0].id

# Habilita e marca email verificado
Invoke-RestMethod -Method Put -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/users/$uid" -Body (@{ enabled=$true; emailVerified=$true; email=$Email } | ConvertTo-Json) | Out-Null

# Define senha
Log "Definindo senha..."
$pwd = @{ type='password'; value=$NewPassword; temporary=$false } | ConvertTo-Json
Invoke-RestMethod -Method Put -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/users/$uid/reset-password" -Body $pwd | Out-Null
Ok "Senha definida"

# Atribui roles de realm
$desiredRoles = @('ADMIN','GESTOR','VIGILANCIA','CAMPO')
Log "Atribuindo roles: $($desiredRoles -join ', ')"
$current = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/users/$uid/role-mappings/realm"
$currentNames = @()
if($current){ $currentNames = $current | ForEach-Object { $_.name } }
$missing = @()
foreach($r in $desiredRoles){
  if($currentNames -notcontains $r){
    try {
      $role = Invoke-RestMethod -Method Get -Headers $auth -Uri "$KeycloakUrl/admin/realms/$Realm/roles/$r"
      $missing += (@{ id=$role.id; name=$role.name })
    } catch {
      Warn "Role não encontrada: $r (ignorando)"
    }
  }
}
if($missing.Count -gt 0){
  $json = $missing | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers ($auth + @{ 'Content-Type'='application/json' }) -Uri "$KeycloakUrl/admin/realms/$Realm/users/$uid/role-mappings/realm" -Body $json | Out-Null
  Ok "Roles atribuídas"
} else {
  Ok "Todas as roles já presentes"
}

Ok "Usuário '$NewUsername' pronto para login."
