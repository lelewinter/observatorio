---
tags: [game-dev, awesome-list, open-source, engines, assets, github-resources]
source: https://x.com/sukh_saroy/status/2038847905239617649?s=20
date: 2026-04-02
tipo: aplicacao
---

# GameDev-Resources: Referência com licenças + código histórico compilável

## O que é
Repositório GitHub (4.5K stars, 91 contributors) listando **todas** ferramentas de game dev com rótulos de licença (free/paid/OSS) + fonte histórica compilável (Doom, Quake 1-3, Wolfenstein, Diablo). Diferencial: labels de custo = zero atrito de decisão. Exemplo: "qual editor 2D? Aseprite ($20), PiskelApp (free), PyxelEdit ($10)".

## Como implementar

**Estrutura padrão para navegar + selecionar ferramentas:**

```markdown
# GameDev-Resources Stack Selection Guide

Baseado em: https://github.com/Kavex/GameDev-Resources

## 1️⃣ GAME ENGINES

### 2D Only
| Engine | License | Best For | Cost | Notes |
|--------|---------|----------|------|-------|
| **Godot** | MIT | Indie 2D+3D | Free | Hot reload, script debugging, Web export |
| **LÖVE** | ZLIB | 2D Lua | Free | Lightweight, easy learning curve |
| **Raylib** | ZLIB | C/C++ 2D | Free | Minimalist API, no dependencies |
| **Phaser** | MIT | Browser 2D | Free | Great for web games |
| **GameMaker** | Commercial | Rapid 2D | $99-499/yr | Drag-drop friendly |

**Escolhido para este projeto**: Godot 4.1
- Razão: Open-source + web export + 2D-first design
- Setup: instalado em `C:\games\Godot_v4.1.1_win64.exe`

### 3D + Multi
| Engine | License | Best For | Cost |
|--------|---------|----------|------|
| **Unity** | Commercial | 3D, mobile | Free (até $1M revenue) |
| **Unreal** | Commercial | AAA 3D | Free (até $1M revenue) |
| **Bevy** | MIT | Rust 3D | Free |
| **Godot** | MIT | 2D+3D hybrid | Free |

## 2️⃣ PIXEL ART & SPRITES

| Tool | License | Cost | Platform | Best For |
|------|---------|------|----------|----------|
| **Aseprite** | Commercial | $20 (one-time) | Win/Mac/Linux | Industry standard, animations |
| **PiskelApp** | MIT | Free | Web | Browser-based, no install |
| **PyxelEdit** | Commercial | $10 | Win/Mac | Tilesets, batch editing |
| **GIMP** | GPL | Free | All | Powerful but overkill |

**Escolhido**: Aseprite ($20 é worth investment)
- Instalado via: choco install aseprite (ou manual download)
- Atalhos: Ctrl+Alt+N (new), Ctrl+E (export)

## 3️⃣ TILESETS & LEVEL DESIGN

| Tool | License | Cost | Workflow |
|------|---------|------|----------|
| **Tiled** | BSD | Free | Standard de facto, exporta JSON |
| **OGMO** | MIT | Free | Lightweight, tile grid focused |
| **Crocotile 3D** | Commercial | $25 | Voxel-based 3D |

**Escolhido**: Tiled (integração perfeita com Godot)
- Download: mapeditor.org
- Godot import: Tools > Import Tiled Maps

## 4️⃣ FREE ASSETS (ao não quer fazer do zero)

| Source | License | Best For | Volume |
|--------|---------|----------|--------|
| **Kenney.nl** | CC0 | Tilesets, characters | ~1000 assets |
| **OpenGameArt** | CC0, CC-BY | Diverse | ~5000+ assets |
| **Pixelboy/Stardust** | CC0 | Retro | 500+ |
| **Freesound.org** | Various | Audio SFX | 700K+ |

**Pipeline**: Buscar aqui antes de criar do zero
- Kenney para tilesets iniciais
- OpenGameArt para diversidade
- Sempre verificar licença (CC0 = libre)

## 5️⃣ AUDIO

| Tool | License | Purpose | Cost |
|------|---------|---------|------|
| **Audacity** | AGPL | Recording, editing | Free |
| **LMMS** | GPL | Composition, chiptune | Free |
| **FamiTracker** | GPL | 8-bit music | Free |
| **Reaper** | Commercial | Pro mixing | $60 |

**Pipeline pessoal**:
- SFX: OpenGameArt (free) + Freesound.org
- Música: LMMS ou buscar artistas em OpenGameArt

## 6️⃣ CÓDIGO HISTÓRICO COMPILÁVEL

**Valor educacional**: Estudar engines seminais **diretamente no código**

Disponível em GameDev-Resources:

```bash
# Clonar repositório histórico
git clone https://github.com/id-Software/Doom
cd Doom
# Seguir README para compilação

# O que aprender estudando Doom:
# - Sector-based level representation
# - Raycasting vs modern rasterization
# - Memory management em ambiente 16-bit
# - Input handling e game loop primitivo
```

| Game | Year | Language | Size | Learning |
|------|------|----------|------|----------|
| **Doom** | 1993 | C | ~60KB | Raycasting, level design |
| **Quake** | 1996 | C | ~200KB | 3D rendering, BSP trees |
| **Quake III** | 1999 | C | 1MB | Competitive game architecture |
| **Wolfenstein 3D** | 1992 | C | ~40KB | Foundational raycasting |
| **Diablo** | 1996 | C++ | ~5MB | Isometric rendering, network |

**Como estudar:**
1. Compilar localmente (seguir instruções README)
2. Usar debugger (GDB, Visual Studio)
3. Mapear estruturas principais:
   - Niveau data structures
   - Rendering pipeline
   - Collision / physics
4. Documentar em forma própria (anotações)

Exemplo estudo Doom:

```c
// Estrutura de setor (level building block)
typedef struct {
    fixed_t floorheight;      // Floor Z height
    fixed_t ceilingheight;    // Ceiling Z height
    int floorpic;             // Floor flat texture
    int ceilingpic;           // Ceiling texture
    int lightlevel;           // Lighting
    int special;              // Special type (door, etc)
} sector_t;

// Questão de aprendizado:
// Por que Doom usa "sectors" em vez de "meshes" como 3D moderno?
// Resposta: Constraints de memória 1993 + raycasting technique
```

## Stack e requisitos

**Setup recomendado (custo $0 ou $20 Aseprite):**

```
Engine: Godot 4.1 (free)
Art: Aseprite ($20 ou PiskelApp free)
Tiles: Tiled (free)
Audio: LMMS (free) + Freesound.org
Level Design: Tiled (free)
Version Control: Git + GitHub (free)
Total cost: $20 (optional)
```

**Para estudar código histórico:**
- Compiler: GCC/Clang (free) ou MSVC Community (free)
- IDE: VSCode (free) ou Visual Studio Community (free)
- Debugger: GDB (free) ou LLDB (free)

## Armadilhas e limitações

**GameDev-Resources limitations:**
- **Volume**: 40+ engines listadas = choice paralysis ("qual escolho?")
- **Atualização**: Alguns links desatualizam (mas comunidade corrige 2-3x/mês)
- **Comparação**: Lista diz "o que existe" não "qual é melhor"
- **Profundidade**: Cada ferramenta tem 1-3 linhas (não tuto)

**Quando usar vs não usar:**

✓ USE para:
- Discovery ("não sabia que existia")
- Validação ("está em awesome-list = confiável")
- Alternativas ("preciso descobrir 3+ opções")

✗ NÃO use para:
- Tutorial/aprendizado profundo (usar docs originais)
- Benchmarks (use seu próprio hardware)
- Decisão FINAL (sempre teste 2-3 pessoalmente)

**Compilar código histórico:**
- Doom é straightforward (C puro, ~1h setup)
- Quake requer MAIS trabalho (custom build system)
- Diablo NÃO é open-source ainda (licensed)
- Modern engines: Godot/Unity bem documentados (comece lá)

**Armadilha comum:** "Vou estudar Doom pra virar melhor programador"
- Armadilha: Engine moderno usa paradigmas MUITO diferentes
- Realidade: Doom teaches **constraints** (memória), não **modern** design
- Melhor use: Estudar UM aspecto específico (raycasting, octrees)

## Conexões
- [[recursos-curados-para-game-dev]]
- [[repositorios-open-source-curados-centralizam-recursos-de-desenvolvimento-de-jogo]]
- [[github-fun-with-cv-tutorials-collidingscopes]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação prática