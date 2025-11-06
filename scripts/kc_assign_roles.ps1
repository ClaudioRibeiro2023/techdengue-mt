param(
  [string]$KC = "http://localhost:8080",
  [string]$Realm = "techdengue",
  [string]$Admin = "",
  [string]$Pass = "",
  [string]$TargetUsername = "",
  [string]$TargetEmail = "",
  [string]$Roles = "ADMIN,GESTOR,VIGILANCIA,CAMPO",
  [string]$GroupName = "FULL_ACCESS"
)

$ErrorActionPreference = 'Stop'

$body = "client_id=admin-cli&grant_type=password&username=$Admin&password=$Pass"
$token = (Invoke-RestMethod -Method Post -Uri "$KC/realms/master/protocol/openid-connect/token" -ContentType 'application/x-www-form-urlencoded' -Body $body).access_token
if (-not $token) { throw 'Failed to obtain admin token' }
$headers = @{ Authorization = "Bearer $token" }

# Resolve user
$userList = @()
if ($TargetUsername) {
  $userList = Invoke-RestMethod -Headers $headers -Uri "$KC/admin/realms/$Realm/users?username=$TargetUsername" -Method Get
}
if ((-not $userList) -or ($userList.Count -eq 0)) {
  if ($TargetEmail) {
    $userList = Invoke-RestMethod -Headers $headers -Uri "$KC/admin/realms/$Realm/users?email=$TargetEmail" -Method Get
  }
}
if ((-not $userList) -or ($userList.Count -eq 0)) { throw "User not found: $TargetUsername / $TargetEmail" }
$uid = ($userList | Select-Object -First 1).id

# Ensure roles exist
$roleNames = $Roles -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
foreach ($rn in $roleNames) {
  try {
    $null = Invoke-RestMethod -Headers $headers -Uri "$KC/admin/realms/$Realm/roles/$rn" -Method Get
  } catch {
    $roleObj = @{ name = $rn; description = $rn }
    Invoke-RestMethod -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } -Uri "$KC/admin/realms/$Realm/roles" -Method Post -Body ($roleObj | ConvertTo-Json)
  }
}

# Collect role representations
$roleObjs = @()
foreach ($rn in $roleNames) {
  $roleObjs += Invoke-RestMethod -Headers $headers -Uri "$KC/admin/realms/$Realm/roles/$rn" -Method Get
}

# Assign roles to user
Invoke-RestMethod -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } -Uri "$KC/admin/realms/$Realm/users/$uid/role-mappings/realm" -Method Post -Body ($roleObjs | ConvertTo-Json)

# Add group membership if present
if ($GroupName) {
  try {
    $groups = Invoke-RestMethod -Headers $headers -Uri "$KC/admin/realms/$Realm/groups?search=$GroupName" -Method Get
    if ($groups -and $groups.Count -gt 0) {
      $gid = $groups[0].id
      try { Invoke-RestMethod -Headers $headers -Uri "$KC/admin/realms/$Realm/users/$uid/groups/$gid" -Method Put -ContentType 'application/json' } catch { }
    }
  } catch { }
}

# Terminate sessions
Invoke-RestMethod -Headers $headers -Uri "$KC/admin/realms/$Realm/users/$uid/logout" -Method Post

Write-Output "OK: Assigned roles [$($roleNames -join ', ')] to user $TargetUsername / $TargetEmail and terminated sessions."
