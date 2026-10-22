# Super Hermes — Install Prism skills into Hermes Agent (PowerShell)
#
# Manual/offline path. With the Hermes Skills Hub, no clone is needed:
#   hermes skills install Cranot/super-hermes/skills/prism-scan
$ErrorActionPreference = "Stop"

# Check if Hermes Agent appears to be installed
$HermesDir = Join-Path $env:USERPROFILE ".hermes"
if (-not (Test-Path $HermesDir) -and -not (Get-Command hermes -ErrorAction SilentlyContinue)) {
    Write-Host "Warning: Hermes Agent not detected (~/.hermes/ not found)." -ForegroundColor Yellow
    Write-Host "Install Hermes first: https://github.com/NousResearch/hermes-agent" -ForegroundColor Yellow
    Write-Host "Continuing anyway (skills will be ready when Hermes is installed)..." -ForegroundColor Yellow
    Write-Host ""
}

$SkillDir = Join-Path $env:USERPROFILE ".hermes\skills"
$PrismDir = Join-Path $env:USERPROFILE ".hermes\prisms"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# The 7 proven prisms live inside the prism-scan skill so that a Skills Hub
# install ships them with the skill. They are still copied to ~/.hermes/prisms/
# below, so the standalone system-prompt path is unchanged.
$PrismSrc = Join-Path $ScriptDir "skills\prism-scan\references"

Write-Host "Installing Super Hermes skills..." -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
New-Item -ItemType Directory -Force -Path $PrismDir | Out-Null

foreach ($skill in @("prism-scan", "prism-full", "prism-3way", "prism-discover", "prism-reflect")) {
    $target = Join-Path $SkillDir $skill
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse -Force (Join-Path $ScriptDir "skills\$skill") $target
}
Copy-Item -Force "$PrismSrc\*.md" "$PrismDir\"

Write-Host ""
Write-Host "Done. 5 skills + 7 proven prisms installed." -ForegroundColor Green
Write-Host "  Skills: $SkillDir" -ForegroundColor Gray
Write-Host "  Prisms: $PrismDir" -ForegroundColor Gray
Write-Host ""
Write-Host "Usage (inside Hermes Agent):"
Write-Host "  /prism-scan       Structural analysis with auto-generated lens"
Write-Host "  /prism-full       Multi-pass pipeline with adversarial self-correction"
Write-Host "  /prism-3way       WHERE/WHEN/WHY — three operations + synthesis"
Write-Host "  /prism-discover   Map all possible analysis domains"
Write-Host "  /prism-reflect    Self-aware analysis with constraint transparency"
