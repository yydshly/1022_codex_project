$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path $PSScriptRoot -Parent
$workspaceDirectory = Split-Path (Split-Path $projectDirectory -Parent) -Parent
$webDirectory = Join-Path $projectDirectory 'web'
$logDirectory = Join-Path $workspaceDirectory '_upstream'
$previewUrl = 'http://127.0.0.1:8049/'
if (-not (Test-Path -LiteralPath (Join-Path $webDirectory 'live/build-info.json'))) {
    throw 'Run setup_runtime.py, build_runtime.py and package_web.py first.'
}
$existingResponse = $null
try { $existingResponse = Invoke-WebRequest -Uri $previewUrl -TimeoutSec 2 -UseBasicParsing } catch {}
if ($null -ne $existingResponse) {
    if ($existingResponse.Content -notmatch 'RENDER ATLAS') {
        throw 'Port 8049 serves another page; check that service first.'
    }
    Write-Output ($previewUrl + '#live-demo')
    exit 0
}
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$previewProcess = Start-Process -FilePath (Get-Command python).Source `
    -ArgumentList @('-m', 'http.server', '8049', '--bind', '127.0.0.1', '--directory', ('"' + $webDirectory + '"')) `
    -WorkingDirectory $workspaceDirectory -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $logDirectory 'webgpu-preview.out.log') `
    -RedirectStandardError (Join-Path $logDirectory 'webgpu-preview.err.log')
$previewProcess.Id | Set-Content -LiteralPath (Join-Path $logDirectory 'webgpu-preview.pid')
Write-Output ($previewUrl + '#live-demo')
