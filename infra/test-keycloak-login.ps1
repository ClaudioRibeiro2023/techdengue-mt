Param(
  [string]$KeycloakUrl = 'http://localhost:8080',
  [string]$Realm = 'techdengue',
  [string]$ClientId = 'techdengue-frontend',
  [string]$RedirectUri = 'http://localhost:6080/auth/callback',
  [string]$Username = 'admin@techdengue.com',
  [string]$Password = 'admin123'
)

$ErrorActionPreference = 'Stop'
try { Add-Type -AssemblyName System.Web } catch {}

function New-CodeVerifier {
  $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~'
  $rand = New-Object System.Random
  -join (1..64 | ForEach-Object { $chars[$rand.Next(0,$chars.Length)] })
}
function New-CodeChallenge($verifier){
  $sha256 = [System.Security.Cryptography.SHA256]::Create()
  $hash = $sha256.ComputeHash([System.Text.Encoding]::ASCII.GetBytes($verifier))
  $b64 = [Convert]::ToBase64String($hash)
  $b64.TrimEnd('=',' ').Replace('+','-').Replace('/','_')
}

$verifier = New-CodeVerifier
$global:verifier = $verifier # persist for token exchange
$challenge = New-CodeChallenge $verifier
$state = [Guid]::NewGuid().ToString('N')
$nonce = [Guid]::NewGuid().ToString('N')
$redirEnc = [uri]::EscapeDataString($RedirectUri)

$authUrl = "$KeycloakUrl/realms/$Realm/protocol/openid-connect/auth?client_id=$ClientId&redirect_uri=$redirEnc&response_type=code&scope=openid%20profile%20email&code_challenge_method=S256&code_challenge=$challenge&state=$state&nonce=$nonce"

Write-Host "[+] GET auth URL"
$response = Invoke-WebRequest -Uri $authUrl -SessionVariable web -Method Get

$content = $response.Content
$actionMatch = [regex]::Match($content, 'action="([^"]*login-actions/[^"]*)"')
if(-not $actionMatch.Success){
  Write-Error 'Login form action not found.'
}
$action = $actionMatch.Groups[1].Value
if(-not $action.StartsWith('http')){ $action = "$KeycloakUrl$action" }

# Parse hidden inputs
$inputs = [regex]::Matches($content, '<input[^>]+type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"[^>]*>')
$form = @{}
foreach($m in $inputs){
  $name = $m.Groups[1].Value
  $value = $m.Groups[2].Value
  $form[$name] = $value
}
$form['username'] = $Username
$form['password'] = $Password

Write-Host "[+] POST credentials"
try {
  # Properly encode as application/x-www-form-urlencoded
  $pairs = @()
  foreach($k in $form.Keys){ $pairs += ( [uri]::EscapeDataString($k) + '=' + [uri]::EscapeDataString([string]$form[$k]) ) }
  $formBody = [string]::Join('&', $pairs)
  $resp2 = Invoke-WebRequest -Uri $action -WebSession $web -Method Post -ContentType 'application/x-www-form-urlencoded' -Body $formBody -MaximumRedirection 0 -ErrorAction Stop
  $status = [int]$resp2.StatusCode
  $location = $resp2.Headers['Location']
} catch {
  $resp2 = $_.Exception.Response
  $status = [int]$resp2.StatusCode
  $location = $resp2.Headers['Location']
}

Write-Host ("Status: " + $status)
Write-Host ("Location: " + $location)

if(!($status -eq 302 -and $location -like "$RedirectUri*")){
  Write-Host "[!] Login not completed. See status and location above." -ForegroundColor Yellow
  exit 1
}

# Extract authorization code
$uri = [uri]$location
$qs = [System.Web.HttpUtility]::ParseQueryString($uri.Query)
$code = $qs['code']
if(-not $code){ Write-Host '[!] No authorization code returned.' -ForegroundColor Yellow; exit 1 }
Write-Host '[OK] Authorization code received.' -ForegroundColor Green

# Exchange code for tokens
Write-Host '[+] Exchanging code for tokens (PKCE)'
$tokenUrl = "$KeycloakUrl/realms/$Realm/protocol/openid-connect/token"
$body = "grant_type=authorization_code&client_id=$ClientId&code=$code&redirect_uri=$([uri]::EscapeDataString($RedirectUri))&code_verifier=$verifier"
$tok = Invoke-RestMethod -Method Post -Uri $tokenUrl -ContentType 'application/x-www-form-urlencoded' -Body $body
if(-not $tok.id_token){ Write-Host '[!] Token response missing id_token.' -ForegroundColor Yellow; exit 1 }
$idShort = $tok.id_token.Substring(0,16)
Write-Host ("[OK] Tokens acquired. id_token prefix: " + $idShort + '...') -ForegroundColor Green

# Trigger logout with id_token_hint
Write-Host '[+] Calling end_session with id_token_hint'
$end = "$KeycloakUrl/realms/$Realm/protocol/openid-connect/logout?post_logout_redirect_uri=$([uri]::EscapeDataString($RedirectUri))&id_token_hint=$([uri]::EscapeDataString($tok.id_token))"
try { $resp3 = Invoke-WebRequest -Uri $end -Method Get -MaximumRedirection 0 -ErrorAction Stop } catch { $resp3 = $_.Exception.Response }
$st3 = [int]$resp3.StatusCode
$loc3 = $resp3.Headers['Location']
Write-Host ("Logout Status: " + $st3)
if($loc3){ Write-Host ("Logout Location: " + $loc3) }
Write-Host '[OK] End-to-end flow executed.' -ForegroundColor Green
