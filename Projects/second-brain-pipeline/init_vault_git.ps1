# init_vault_git.ps1 — Inicializa git no vault e conecta ao GitHub
# Execute UMA VEZ: powershell -ExecutionPolicy Bypass -File init_vault_git.ps1

$ErrorActionPreference = "Stop"
$vaultPath = "C:\Users\leeew\Documentos\Vaults Obsidian\Claude"

Write-Host ""
Write-Host "=== Inicializando Git no Vault ===" -ForegroundColor Cyan
Write-Host ""

Set-Location $vaultPath

# ── Criar .gitignore ────────────────────────────────────────────────────────
$gitignore = @"
# Obsidian internals
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/graph.json
.obsidian/hotkeys.json
.obsidian/cache/
.obsidian/workspace-*

# Pipeline internals
Projects/second-brain-pipeline/state.json
Projects/second-brain-pipeline/logs/
Projects/second-brain-pipeline/quartz/
Projects/second-brain-pipeline/__pycache__/

# Game studio (nao publicar)
src/
assets/
design/
production/
tools/
docs/engine-reference/

# Sistema
.DS_Store
Thumbs.db
*.tmp
"@

$gitignore | Set-Content -Path (Join-Path $vaultPath ".gitignore") -Encoding UTF8
Write-Host "[1/4] .gitignore criado" -ForegroundColor Green

# ── Git init ────────────────────────────────────────────────────────────────
if (-not (Test-Path (Join-Path $vaultPath ".git"))) {
    git init
    Write-Host "[2/4] Git inicializado" -ForegroundColor Green
} else {
    Write-Host "[2/4] Git ja inicializado, pulando" -ForegroundColor Yellow
}

# ── Configurar remote ──────────────────────────────────────────────────────
$existingRemote = git remote 2>&1
if ($existingRemote -notcontains "origin") {
    git remote add origin https://github.com/lelewinter/observatorio.git
    Write-Host "[3/4] Remote 'origin' adicionado" -ForegroundColor Green
} else {
    git remote set-url origin https://github.com/lelewinter/observatorio.git
    Write-Host "[3/4] Remote 'origin' atualizado" -ForegroundColor Yellow
}

# ── Primeiro commit ─────────────────────────────────────────────────────────
git add -A
git commit -m "init: vault inicial com notas existentes"
git branch -M main
git push -u origin main

Write-Host "[4/4] Primeiro push feito!" -ForegroundColor Green
Write-Host ""
Write-Host "Vault conectado a https://github.com/lelewinter/observatorio" -ForegroundColor Cyan
Write-Host "O pipeline agora faz auto-commit a cada nota nova/atualizada." -ForegroundColor Cyan
Write-Host ""
