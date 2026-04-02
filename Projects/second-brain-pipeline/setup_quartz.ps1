# setup_quartz.ps1 — Configura Quartz para publicar vault como site
# Execute: powershell -ExecutionPolicy Bypass -File setup_quartz.ps1
#
# Pre-requisitos:
#   - Node.js 20+ (https://nodejs.org)
#   - Git instalado
#   - Conta no GitHub

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$quartzDir = Join-Path $scriptDir "quartz"
$vaultPath = "C:\Users\leeew\Documentos\Vaults Obsidian\Claude"

Write-Host ""
Write-Host "=== Quartz Setup para Second Brain ===" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Clonar Quartz ──────────────────────────────────────────────────
if (-not (Test-Path $quartzDir)) {
    Write-Host "[1/5] Clonando Quartz..." -ForegroundColor Yellow
    git clone https://github.com/jackyzha0/quartz.git $quartzDir
} else {
    Write-Host "[1/5] Quartz ja existe, pulando clone" -ForegroundColor Green
}

Set-Location $quartzDir

# ── Step 2: Instalar dependencias ───────────────────────────────────────────
Write-Host "[2/5] Instalando dependencias..." -ForegroundColor Yellow
npm ci

# ── Step 3: Copiar conteudo do vault ────────────────────────────────────────
Write-Host "[3/5] Sincronizando conteudo do vault..." -ForegroundColor Yellow
$contentDir = Join-Path $quartzDir "content"

# Limpa content anterior
if (Test-Path $contentDir) {
    Remove-Item -Recurse -Force $contentDir
}
New-Item -ItemType Directory -Path $contentDir | Out-Null

# Copia apenas as pastas relevantes do vault (sem game studio, sem Projects)
$foldersToSync = @(
    "Links Salvos",
    "Daily Reviews"
)

foreach ($folder in $foldersToSync) {
    $src = Join-Path $vaultPath $folder
    if (Test-Path $src) {
        Copy-Item -Recurse -Force $src (Join-Path $contentDir $folder)
        Write-Host "  Copiado: $folder" -ForegroundColor Gray
    }
}

# Copia MOCs da raiz
Get-ChildItem -Path $vaultPath -Filter "MOC -*.md" | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $contentDir $_.Name)
    Write-Host "  Copiado: $($_.Name)" -ForegroundColor Gray
}

# Copia index (README como index)
$readmeSrc = Join-Path $vaultPath "README.md"
if (Test-Path $readmeSrc) {
    Copy-Item $readmeSrc (Join-Path $contentDir "index.md")
}

# ── Step 4: Configurar quartz.config.ts ─────────────────────────────────────
Write-Host "[4/5] Configurando quartz.config.ts..." -ForegroundColor Yellow

$quartzConfig = @'
import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

const config: QuartzConfig = {
  configuration: {
    pageTitle: "Second Brain",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "pt-BR",
    baseUrl: "lelewinter.github.io/observatorio",
    ignorePatterns: [
      "private",
      "templates",
      ".obsidian",
      "Projects",
      "PDFs",
      "Scheduled",
    ],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Inter",
        body: "Inter",
        code: "JetBrains Mono",
      },
      colors: {
        lightMode: {
          light: "#faf8f8",
          lightgray: "#e5e5e5",
          gray: "#b8b8b8",
          darkgray: "#4e4e4e",
          dark: "#2b2b2b",
          secondary: "#284b63",
          tertiary: "#84a59d",
          highlight: "rgba(143, 159, 169, 0.15)",
          textHighlight: "#fff23688",
        },
        darkMode: {
          light: "#161618",
          lightgray: "#393639",
          gray: "#646464",
          darkgray: "#d4d4d4",
          dark: "#ebebec",
          secondary: "#7b97aa",
          tertiary: "#84a59d",
          highlight: "rgba(143, 159, 169, 0.15)",
          textHighlight: "#fff23688",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlBlock: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSSFeed: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.NotFoundPage(),
    ],
  },
}

export default config
'@

$quartzConfigPath = Join-Path $quartzDir "quartz.config.ts"
$quartzConfig | Set-Content -Path $quartzConfigPath -Encoding UTF8

Write-Host "[5/5] Pronto!" -ForegroundColor Green
Write-Host ""
Write-Host "=== Proximos passos manuais ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Conecte o Quartz ao repo:" -ForegroundColor White
Write-Host "   cd $quartzDir"
Write-Host "   git remote set-url origin https://github.com/lelewinter/observatorio.git"
Write-Host ""
Write-Host "2. Build e deploy:" -ForegroundColor White
Write-Host "   npx quartz build"
Write-Host "   npx quartz sync --no-pull"
Write-Host ""
Write-Host "3. No GitHub: Settings > Pages > Source: 'GitHub Actions'" -ForegroundColor White
Write-Host ""
Write-Host "=== Para testar localmente ===" -ForegroundColor Cyan
Write-Host "   cd $quartzDir"
Write-Host "   npx quartz build --serve"
Write-Host "   Abra http://localhost:8080"
Write-Host ""
