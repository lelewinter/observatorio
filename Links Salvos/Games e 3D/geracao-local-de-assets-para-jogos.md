---
tags: [asset-generation, stable-diffusion, electron, local-ai, inpainting, gamedev]
source: https://x.com/developedbyed/status/2038566894970527861?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Assets de Jogo com IA Local (Stable Diffusion + Electron)

## O que é
App desktop (Electron) que roda Stable Diffusion localmente para gerar tiles, sprites, inpainting sem serviços em nuvem. Zero assinatura, privacidade total, sem lag.

## Como implementar
**Setup ambiente** (Python + Stable Diffusion WebUI):

```bash
# Opção 1: AUTOMATIC1111 WebUI (mais completo)
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
cd stable-diffusion-webui
./webui.sh  # Linux/Mac ou webui.bat Windows

# Resultado: localhost:7860 com UI web
```

**Electron wrapper**:

```javascript
// main.js - Electron
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let webui_process;

function startStableDiffusion() {
    webui_process = spawn('python', ['launch.py'], {
        cwd: path.join(__dirname, 'stable-diffusion-webui'),
        stdio: 'ignore'
    });
}

app.on('ready', () => {
    startStableDiffusion();

    const win = new BrowserWindow({
        width: 1400,
        height: 900,
        webPreferences: { nodeIntegration: false }
    });

    // Aguardar WebUI iniciar
    setTimeout(() => {
        win.loadURL('http://localhost:7860');
    }, 5000);
});
```

**Workflow de geração** (com prompts otimizados para gamedev):

```
[Geração de Tiles]
Prompt: "isometric dungeon floor tile, stone brick, 64x64, pixel art style"
Steps: 20
Guidance: 7.5
Sampler: DPM++ 2M
Output: PNG (exportar direto em spritesheetformat)
```

```
[Inpainting - Corrigir Artefato]
Base image: tile_floor_01.png
Mask: (selecionar área errada)
Prompt: "fix that corner, stone brick texture"
Steps: 15
Denoising strength: 0.75
Resultado: tile_floor_01_fixed.png
```

```
[Geração de Walk Cycle]
Base: knight_idle.png
Prompt: "knight walking left, full body, pixel art, 4 frames"
Modelo: ControlNet (pose control) ou Pix2Pix
Resultado: knight_walk_01.png, knight_walk_02.png, ...
```

**Integração com Godot**:

```gdscript
extends Node

# Diretório com assets gerados
const ASSET_DIR = "res://assets/generated"

func load_tileset():
    var tileset = TileSet.new()
    var files = list_files(ASSET_DIR)

    for f in files:
        if f.ends_with(".png"):
            var img = Image.new()
            img.load(ASSET_DIR + "/" + f)

            var texture = ImageTexture.create_from_image(img)
            tileset.add_tile(f, texture)  # Simplificado

    return tileset

func list_files(dir: String) -> PackedStringArray:
    var files = PackedStringArray()
    var dir_access = DirAccess.open(dir)

    if dir_access:
        dir_access.list_dir_begin()
        var file_name = dir_access.get_next()
        while file_name != "":
            if not file_name.starts_with("."):
                files.append(file_name)
            file_name = dir_access.get_next()

    return files
```

**Performance + requisitos**:

```
GPU: RTX 3060 (12GB) minimo, RTX 4080 ideal
Tempo geração:
  - tile simples: 10-20s
  - personagem: 30-60s
  - inpainting: 15-30s
Memória: ~8GB RAM + 12GB VRAM
Bundle tamanho: Stable Diffusion model ~4GB download
```

## Stack e requisitos
- **IA backend**: Stable Diffusion v1.5 ou SDXL (mais pesado)
- **UI orchestration**: AUTOMATIC1111 WebUI (open source)
- **Desktop wrapper**: Electron
- **Game engine**: Godot, Unity, GameMaker (todos aceitam PNG)
- **GPU necessária**: RTX 3060+ ou AMD equivalent
- **Modelos adicionais**:
  - ControlNet: pose guiding (gerar personagens com direções específicas)
  - TileGAN: consistency entre tiles adjacentes
  - Pix2Pix: style transfer (manter estilo coerente)
- **Custo**: $0 (software open source)

## Armadilhas e limitações
- **Modelo size**: SDXL é 6GB (muito pesado), v1.5 é 4GB
- **Consistência tile**: gerar tiles separadamente nem sempre alinha nas bordas. Usar ControlNet ou manual tweaking
- **Inpainting quality**: depende muito do seed e prompt. 5-10 tentativas típicas pra ficar bom
- **VRAM memory leak**: deixar WebUI rodando 24h causa lentidão. Reiniciar periodicamente
- **Geração é lenta**: 30-60s por asset é impraticável pra batch 100+ sprites
- **Controle criativo limitado**: prompt é impreciso. "Knight, medieval, isometric" pode virar elfo ou orc
- **IP/Copyright**: modelos Stable Diffusion treinados em internet. Output pode conter "similarities" a artistas existentes
- **Sem fundo alpha**: gera backgrounds. Remover fundo via Python + rembg ou Photoshop
- **Performance GPU segue**: sem GPU dedicada, geração vira inviável (horas por tile)

## Conexões
- [[stable-diffusion-local-setup]]
- [[controlnet-pose-guidance]]
- [[asset-pipeline-gamedev]]
- [[geracao-local-de-assets-para-jogos]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com Electron + Godot integration
