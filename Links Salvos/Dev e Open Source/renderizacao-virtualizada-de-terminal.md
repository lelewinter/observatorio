---
tags: [terminal, rendering, performance, ui, virtualizacao, gpu, wezterm, alacritty, ghostty]
source: https://dasroot.net/posts/2026/02/wezterm-gpu-acceleration-opengl-vulkan/ | https://wezterm.com/ | https://github.com/wezterm/wezterm
date: 2026-04-02
tipo: aplicacao
---

# Renderização Virtualizada de Terminal: GPU Acceleration & High-Performance TUIs (2026)

## O que é

Renderização virtualizada de terminal é a técnica de desenhar **apenas as linhas visíveis** na viewport, em vez de renderizar toda a buffer histórica. Combinado com aceleração GPU (OpenGL, Vulkan), permite TUIs (Terminal User Interfaces) com 10k+ linhas de dados, 144Hz refresh rates, e sem lag perceptível. Emuladores como WezTerm, Alacritty e Ghostty implementam isso nativamente em 2026.

Historicamente, terminais como xterm renderizavam a tela inteira a cada frame, limitando performance em dados grandes. A virtualização quebra esse gargalo.

## Por que importa agora

1. **TUIs modernas exigem performance**: Data browsers, log viewers, dashboards de monitoramento precisam scrollar 50k linhas sem travar.
2. **High refresh rates**: Monitores 144Hz são comuns. Terminais GPU-acelerados aproveitam; CPU-only fica no 60Hz.
3. **Economia de energia**: GPU render é mais eficiente que CPU rasterizing; laptops ganham horas de bateria.
4. **Integração com ferramentas dev**: Rust/Go/Python CLI tools rodando em WezTerm ou Alacritty lucram com rendering otimizado.

Leticia estuda em terminal (neovim, CLI tools). Um emulador otimizado melhora a experiência de feedback visual sem distração.

## Como implementar

### 1. Virtualização de Scroll Buffer

A ideia: manter buffer histórico completo em RAM, mas renderizar apenas linhas visíveis.

```python
# Conceito básico de virtualização
class VirtualizedTerminal:
    def __init__(self, width=80, height=24):
        self.width = width
        self.height = height
        self.scroll_offset = 0
        self.buffer = []  # linhas históricas
        self.viewport = []  # o que está visível agora
    
    def add_line(self, line):
        """Adiciona linha ao buffer."""
        self.buffer.append(line[:self.width])  # truncar se necessário
    
    def render(self):
        """Renderiza apenas as linhas visíveis."""
        start = max(0, self.scroll_offset)
        end = min(len(self.buffer), self.scroll_offset + self.height)
        self.viewport = self.buffer[start:end]
        
        for i, line in enumerate(self.viewport):
            print(f"{line}")
    
    def scroll_down(self):
        """Scroll para baixo (apenas muda offset, não re-renderiza tudo)."""
        if self.scroll_offset < len(self.buffer) - self.height:
            self.scroll_offset += 1
    
    def scroll_up(self):
        """Scroll para cima."""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
    
    def page_down(self):
        """Page Down: scroll 24 linhas."""
        self.scroll_offset = min(self.scroll_offset + self.height, 
                                len(self.buffer) - self.height)

# Usar com 10k linhas
terminal = VirtualizedTerminal(80, 24)
for i in range(10000):
    terminal.add_line(f"Line {i}: " + "x" * 70)

# Scroll é instantâneo (apenas offset muda)
for _ in range(100):
    terminal.scroll_down()
    terminal.render()  # renderiza 24 linhas, não 10k
```

### 2. GPU Rendering com OpenGL (WezTerm Internals)

WezTerm usa OpenGL para rasterizar glyphs (caracteres) em textures, depois compositor para scale/rotate. Aproximadamente assim:

```glsl
// Vertex shader (pseudo-OpenGL)
#version 330 core

layout (location = 0) in vec2 position;
layout (location = 1) in vec2 texCoord;

uniform mat4 projection;

out vec2 TexCoord;

void main()
{
    gl_Position = projection * vec4(position, 0.0, 1.0);
    TexCoord = texCoord;
}

// Fragment shader (renderizar caractere)
#version 330 core

in vec2 TexCoord;
uniform sampler2D fontAtlas;
uniform vec4 foregroundColor;
uniform vec4 backgroundColor;

out vec4 FragColor;

void main()
{
    float alpha = texture(fontAtlas, TexCoord).r;
    vec4 fgColor = vec4(foregroundColor.rgb, foregroundColor.a * alpha);
    vec4 bgColor = backgroundColor;
    
    // Blend: opaque background, transparent foreground
    FragColor = mix(bgColor, fgColor, alpha);
}
```

**Fluxo em WezTerm (2026)**:

1. **Glyph Rasterization**: Fonte é rasterizada para textura (atlas) uma vez, reutilizada.
2. **Vertex Generation**: Para cada caractere visível, cria quad (2 triângulos) no GPU.
3. **Batch Rendering**: Todos os quads renderizados em uma chamada draw (batching reduz overhead).
4. **Compositor**: Aplica scaling, rotation, effects (blur, shadow) em GPU também.

### 3. Comparação: CPU vs GPU Rendering (Benchmarks 2026)

| Emulador | Método | 256 cores, 2000 linhas scroll | RAM (idle) | FPS (144Hz display) |
|----------|--------|-------------------------------|-----------|-------------------|
| **WezTerm** | GPU (OpenGL/Vulkan) | 50ms | 380MB | 142 FPS |
| **Alacritty** | GPU (OpenGL) | 35ms | 30MB | 144 FPS |
| **Kitty** | GPU (proprietary) | 45ms | 60MB | 140 FPS |
| **Ghostty** | GPU (Metal/OpenGL) | 40ms | 85MB | 143 FPS |
| **xterm** | CPU (pure rasterize) | 500ms+ | 15MB | 60 FPS (capped) |

**Insights**:
- Alacritty: velocidade pura (engine mínimo), mas menos features.
- WezTerm: feature-rich (tabs, panes, ligatures), GPU otimizado.
- Ghostty (novo 2024): Apple Metal para macOS, muito rápido, cross-platform growth.

### 4. Técnicas de Otimização

#### 4a. Damage Tracking

Não re-renderizar a tela inteira; apenas regiões que mudaram.

```rust
// Pseudo-Rust (WezTerm style)
struct Terminal {
    buffer: Vec<Line>,
    damage: Rect,  // área que mudou
}

impl Terminal {
    fn update_cell(&mut self, col: usize, row: usize, cell: Cell) {
        self.buffer[row][col] = cell;
        // Expande damage rect para incluir célula
        self.damage.union_with(Rect::cell(col, row));
    }
    
    fn render(&self) {
        // Renderiza apenas self.damage
        for row in self.damage.top..self.damage.bottom {
            for col in self.damage.left..self.damage.right {
                gpu.render_cell(col, row, self.buffer[row][col]);
            }
        }
        self.damage = Rect::empty();  // reset
    }
}
```

#### 4b. Layer Composition

Terminal tem múltiplas camadas: background, text, selection, cursor. Renderizar separadamente, depois composite:

```python
# Pipeline em camadas
layers = {
    'background': render_background_layer(),     # muda raramente
    'text': render_text_layer(),                 # muda sempre
    'selection': render_selection_layer(),       # muda em mouse drag
    'cursor': render_cursor_layer(),             # pisca
}

# Composite: camadas em ordem, com blending
final_framebuffer = layers['background']
final_framebuffer.blend(layers['text'], BlendMode.OVER)
final_framebuffer.blend(layers['selection'], BlendMode.MULTIPLY)
final_framebuffer.blend(layers['cursor'], BlendMode.SCREEN)

gpu.swap_buffers(final_framebuffer)
```

#### 4c. Font Caching & Ligatures

Fontes modernas (Fira Code, JetBrains Mono) incluem ligatures (`=>`, `<->`). Renderizar é caro; WezTerm cacheia:

```rust
// Font ligature cache
struct GlyphCache {
    single_glyphs: HashMap<(char, Style), GlyphInfo>,
    ligatures: HashMap<(String, Style), GlyphInfo>,
}

fn get_glyph(&self, text: &str, style: Style) -> GlyphInfo {
    if let Some(lig) = self.ligatures.get(&(text.to_string(), style)) {
        return lig.clone();  // hit: usar ligature pre-renderizada
    }
    
    if text.len() == 1 {
        return self.single_glyphs[&(text.chars().next().unwrap(), style)].clone();
    }
    
    // Miss: rasterizar novo glyph, cachear para próxima vez
    let glyph = rasterize(text, style);
    self.ligatures.insert((text.to_string(), style), glyph.clone());
    glyph
}
```

## Stack e requisitos

### Hardware Mínimo

- **CPU**: Intel i5 / Ryzen 5 (qualquer um, GPU faz o trabalho).
- **GPU**: 
  - NVIDIA: GeForce GTX 1050+ (2GB VRAM suficiente).
  - AMD: Radeon RX 5500+ ou equivalente.
  - Intel: iGPU (UHD 630+) funciona, mas lento.
  - Apple: M1+ (Metal native, muito rápido).

### Software

```bash
# WezTerm (recomendado para Leticia — multiplexer + GPU native)
# Download: https://wezfurlong.org/wezterm/install/index.html
# Config: ~/.config/wezterm/wezterm.lua

-- Arquivo de config WezTerm (Lua)
local config = wezterm.config_builder()

config.enable_wayland = true           -- Linux: usar Wayland se disponível
config.prefer_egl = true               -- Forçar OpenGL on Linux
config.front_end = "OpenGL"            -- Ou "WebGpu" para melhor compat
config.gpu_adapters = { ... }          -- Auto-detect GPU
config.max_fps = 144                   -- Sync com refresh rate
config.animation_fps = 60              -- Smooth scroll/blink

config.font = wezterm.font("JetBrains Mono", { weight = "Medium" })
config.font_size = 12.0

return config
```

```bash
# Alacritty (alternativa minimalista)
# Install: cargo install alacritty --features=wayland,x11-clipboard
# Config: ~/.config/alacritty/alacritty.toml

[window]
opacity = 0.95
padding = { x = 10, y = 10 }

[font]
family = "JetBrains Mono"
size = 12.0

[colors]
theme = "Dracula"
```

### Dependências

- **Linux**: libxkbcommon, freetype (para rasterização).
- **macOS**: nenhuma (tudo integrado).
- **Windows**: Visual C++ Redistributables (geralmente pré-instalado).

## Armadilhas e limitações

### Técnicas

1. **GPU Driver crashes**: Drivers NVIDIA/AMD instáveis causam terminal "freeze" ou reboot. Atualizar driver primeiro passo.

2. **Compositing overhead**: Renderizar em múltiplas camadas depois composite pode ser mais lento que uma única renderização se mal feito. WezTerm resolve com damage tracking; alternativas podem não.

3. **Font rendering inconsistencies**: Diferentes platforms (Linux Wayland vs X11, macOS, Windows) podem renderizar glyphs ligeiramente diferentes. Não é bug, é limitation do rendering engine.

4. **Context switches**: Se terminal (GPU) + outro app (CPU) dividem GPU, context switch pode causar lag. Menos problema em GPU modernas (many cores), mais em iGPUs antigas.

### Práticas

5. **High refresh rates em laptop**: 144Hz renderização drena bateria. Use `--sync-to-monitor` para WezTerm, ou capped 60Hz em bateria.

6. **Terminal history limits**: Algumas apps (ex: `less`, `vim`) assumem buffer finito. Terminal com 10M linhas pode quebrar behavior esperado. Leticia deve configurar scrollback_lines sensato (~10k é padrão, suficiente).

7. **Color degradation em compression**: Se usar terminal em SSH com streaming de video (ex: cloud IDE), compressão pode degradar cores. True Color (24-bit) exige banda suficiente.

8. **Selection performance**: Drag de selection em 10k linhas pode causar lag se não usar damage tracking. WezTerm otimiza; terminais simples podem não.

### Conceituais

9. **GPU Virtualization (remote)**: Quando rodando em VPS, terminal local não consegue acesso GPU. Nesses casos, CPU rendering é único opção; lag é esperado.

10. **Overkill para 80x24**: Terminal minúsculo (como padrão VT100) não aproveita otimizações GPU. WezTerm + Alacritty brilham em alta-res displays (4K+), múltiplos panes, heavy scrolling.

## Conexões

- [[terminal-multiplexer-tmux-vs-wezterm|Terminal Multiplexers: tmux vs WezTerm]] — orquestração de panes/tabs além de rendering
- [[cli-tools-rust-alacritty-starship|CLI Tools em Rust: Alacritty, Starship, ripgrep]] — ferramentas que lucram com terminal otimizado
- [[obsidian-vault-em-cli-com-fzf-telescope|Vault Obsidian em CLI com fzf/telescope]] — caso de uso: TUI navegador de notas

## Histórico

- 2026-04-02: Nota criada (reescrita minimalista)
- 2026-04-11: Expansão profunda com GPU rendering details, benchmarks 2026, code examples OpenGL/Rust
