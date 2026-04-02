# setup_git_vault.ps1 — Inicializa git no vault e conecta ao GitHub
# Execute: powershell -ExecutionPolicy Bypass -File setup_git_vault.ps1
#
# Pre-requisito: git instalado e autenticado no GitHub
# (gh auth login, ou git credential manager, ou SSH key)

$ErrorActionPreference = "Stop"
$vaultPath = "C:\Users\leeew\Documentos\Vaults Obsidian\Claude"

Write-Host ""
Write-Host "=== Setup Git no Vault Obsidian ===" -ForegroundColor Cyan
Write-Host ""

Set-Location $vaultPath

# ── Step 1: Inicializar git se necessario ───────────────────────────────────
if (-not (Test-Path ".git")) {
    Write-Host "[1/4] Inicializando git..." -ForegroundColor Yellow
    git init
    git branch -M main
} else {
    Write-Host "[1/4] Git ja inicializado" -ForegroundColor Green
}

# ── Step 2: Criar .gitignore ────────────────────────────────────────────────
Write-Host "[2/4] Criando .gitignore..." -ForegroundColor Yellow

$gitignore = @"
# Obsidian internals
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache/
.obsidian/plugins/smart-connections/.smart-connections/

# Pipeline state
Projects/second-brain-pipeline/state.json
Projects/second-brain-pipeline/logs/
Projects/second-brain-pipeline/__pycache__/
Projects/second-brain-pipeline/quartz/

# OS
.DS_Store
Thumbs.db
desktop.ini

# Temp
*.tmp
*.swp
"@

$gitignore | Set-Content -Path ".gitignore" -Encoding UTF8

# ── Step 3: Conectar ao remote ──────────────────────────────────────────────
Write-Host "[3/4] Conectando ao GitHub..." -ForegroundColor Yellow

$remote = git remote 2>&1
if ($remote -match "origin") {
    git remote set-url origin "https://github.com/lelewinter/observatorio.git"
} else {
    git remote add origin "https://github.com/lelewinter/observatorio.git"
}

# ── Step 4: Primeiro commit e push ──────────────────────────────────────────
Write-Host "[4/4] Primeiro commit..." -ForegroundColor Yellow

git add -A
git commit -m "init: vault Observatorio"
git push -u origin main

Write-Host ""
Write-Host "=== Pronto! ===" -ForegroundColor Green
Write-Host ""
Write-Host "O vault agora esta conectado a https://github.com/lelewinter/observatorio"
Write-Host "Toda nota criada pelo pipeline sera commitada e pushada automaticamente."
Write-Host ""
Write-Host "Para verificar: git log --oneline -5"
Write-Host ""
