# sync_quartz.ps1 — Sincroniza vault com Quartz e faz deploy
# Roda apos cada coleta de notas ou como scheduled task
# Execute: powershell -ExecutionPolicy Bypass -File sync_quartz.ps1

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$quartzDir = Join-Path $scriptDir "quartz"
$vaultPath = "C:\Users\leeew\Documentos\Vaults Obsidian\Claude"
$contentDir = Join-Path $quartzDir "content"

if (-not (Test-Path $quartzDir)) {
    Write-Error "Quartz nao configurado. Rode setup_quartz.ps1 primeiro."
    exit 1
}

Write-Host "[sync] Sincronizando vault -> Quartz..." -ForegroundColor Cyan

# Limpa content
if (Test-Path $contentDir) {
    Remove-Item -Recurse -Force $contentDir
}
New-Item -ItemType Directory -Path $contentDir | Out-Null

# Copia pastas relevantes
$foldersToSync = @("Links Salvos", "Daily Reviews")
foreach ($folder in $foldersToSync) {
    $src = Join-Path $vaultPath $folder
    if (Test-Path $src) {
        Copy-Item -Recurse -Force $src (Join-Path $contentDir $folder)
    }
}

# MOCs
Get-ChildItem -Path $vaultPath -Filter "MOC -*.md" | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $contentDir $_.Name)
}

# Index
$readmeSrc = Join-Path $vaultPath "README.md"
if (Test-Path $readmeSrc) {
    Copy-Item $readmeSrc (Join-Path $contentDir "index.md")
}

# Build e sync
Set-Location $quartzDir
Write-Host "[sync] Building..." -ForegroundColor Yellow
npx quartz build
Write-Host "[sync] Pushing to GitHub..." -ForegroundColor Yellow
npx quartz sync --no-pull

Write-Host "[sync] Pronto!" -ForegroundColor Green
