$ErrorActionPreference='Stop'
$kc='http://localhost:8080'
$realm='techdengue'
$client='techdengue-frontend'
$user='admin@techdengue.com'
$pass='admin123'
$redir='http://localhost:6080/'

Write-Host '[+] Requesting token (ROPC)'
$tok = Invoke-RestMethod -Method Post -Uri "$kc/realms/$realm/protocol/openid-connect/token" -ContentType 'application/x-www-form-urlencoded' -Body "grant_type=password&client_id=$client&username=$user&password=$pass&scope=openid profile email"
if(-not $tok.id_token){ throw 'No id_token in token response' }
$idShort = $tok.id_token.Substring(0,16)
Write-Host ("[OK] Token acquired. id_token prefix: " + $idShort + '...')

Write-Host '[+] Calling logout with id_token_hint'
$logoutUrl = "$kc/realms/$realm/protocol/openid-connect/logout?post_logout_redirect_uri=$([uri]::EscapeDataString($redir))&id_token_hint=$([uri]::EscapeDataString($tok.id_token))"
try { $resp = Invoke-WebRequest -Uri $logoutUrl -Method Get -MaximumRedirection 0 -ErrorAction Stop } catch { $resp = $_.Exception.Response }
$st = [int]$resp.StatusCode
$loc = $resp.Headers['Location']
Write-Host ('Status: ' + $st)
if($loc){ Write-Host ('Location: ' + $loc) } else { Write-Host 'No redirect header' }
