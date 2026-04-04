---
tags: [conceito, game-dev, pixel-art, spritesheet, animation, assets]
date: 2026-04-02
tipo: conceito
aliases: [Spritesheet Composition, Animation Frames, Tile Grid]
---
# Spritesheet Generation: Organização de Frames em Grid Otimizado

## O que é

Technique de agregar múltiplos frames 2D (32x32, 64x64 pixels cada) em uma única imagem grande (512x512 ou maior) usando grid regular, acompanhado de metadados (JSON ou XML) que mapeia cada frame com name, posição (x,y), duração, flags (flip, blend mode).

Diferencia-se de armazenar frames individuais porque: (1) memória eficiente (um PNG grande < múltiplas PNGs pequenas), (2) carregamento único, (3) facilita swapping em shader/GPU, (4) padrão universal em engines (Godot, Unity, Unreal).

## Como funciona

**Exemplo visual:**

```
Spritesheet 512x512 (8x8 grid de frames 64x64):

[idle_1] [idle_2] [walk_1] [walk_2] [walk_3] [walk_4] [jump_1] [jump_2]
[fall_1] [fall_2] [attack_1] [attack_2] [block_1] [block_2] [hurt_1] [hurt_2]
...
```

**Metadados (JSON):**

```json
{
  "idle": [
    {"index": 0, "x": 0, "y": 0, "width": 64, "height": 64, "duration_ms": 200},
    {"index": 1, "x": 64, "y": 0, "width": 64, "height": 64, "duration_ms": 200}
  ],
  "walk": [
    {"index": 2, "x": 128, "y": 0, "width": 64, "height": 64, "duration_ms": 100, "flip_h": false},
    {"index": 3, "x": 192, "y": 0, "width": 64, "height": 64, "duration_ms": 100, "flip_h": false},
    {"index": 4, "x": 256, "y": 0, "width": 64, "height": 64, "duration_ms": 100, "flip_h": false},
    {"index": 5, "x": 320, "y": 0, "width": 64, "height": 64, "duration_ms": 100, "flip_h": false}
  ],
  "jump": [...]
}
```

**Algoritmo de Composição:**

```python
def compose_spritesheet(animations: dict, frame_size: int = 64, frames_per_row: int = 8) -> tuple[Image, dict]:
    """
    Input:
      animations = {
        "idle": [Image, Image],
        "walk": [Image, Image, Image, Image],
        ...
      }
    Output:
      (spritesheet_image, metadata_dict)
    """

    # Step 1: Calcular dimensões
    total_frames = sum(len(frames) for frames in animations.values())
    rows_needed = (total_frames + frames_per_row - 1) // frames_per_row
    spritesheet_width = frames_per_row * frame_size
    spritesheet_height = rows_needed * frame_size

    # Step 2: Criar canvas (RGBA pra suportar transparência)
    spritesheet = Image.new("RGBA", (spritesheet_width, spritesheet_height), (0, 0, 0, 0))

    # Step 3: Preencher frames no grid
    metadata = {}
    global_frame_idx = 0

    for anim_name, frames in animations.items():
        metadata[anim_name] = []

        for frame_idx, frame_img in enumerate(frames):
            # Calcular posição no grid
            grid_x = global_frame_idx % frames_per_row
            grid_y = global_frame_idx // frames_per_row
            pixel_x = grid_x * frame_size
            pixel_y = grid_y * frame_size

            # Redimensionar se necessário (usando NEAREST neighbor pra manter pixel art nítida)
            frame_resized = frame_img.resize((frame_size, frame_size), Image.Resampling.NEAREST)

            # Coolar frame na posição
            spritesheet.paste(frame_resized, (pixel_x, pixel_y), frame_resized)

            # Registrar metadados
            metadata[anim_name].append({
                "index": global_frame_idx,
                "x": pixel_x,
                "y": pixel_y,
                "width": frame_size,
                "height": frame_size,
                "duration_ms": 100,  # Default; pode ser customizado
                "flip_h": False,
                "flip_v": False
            })

            global_frame_idx += 1

    return spritesheet, metadata

# Usar
frames_dict = {
    "idle": [Image.open("idle_1.png"), Image.open("idle_2.png")],
    "walk": [Image.open(f"walk_{i}.png") for i in range(1, 5)],
}
spritesheet, metadata = compose_spritesheet(frames_dict, frame_size=64)
spritesheet.save("character.png")
with open("character.json", "w") as f:
    json.dump(metadata, f)
```

**Otimizações:**

1. **Horizontal Flip Reuse:** Se animação "walk_left" é espelho de "walk_right", armazene apenas um e use flag `flip_h: true`:
```json
"walk_left": [
  {"index": 2, "flip_h": true},
  {"index": 3, "flip_h": true},
  ...
]
```

2. **Atlasing Inteligente:** Preencher vazios com frames adicionais (bonus frames) ou usar algoritmo de bin packing pra spritesheet não retangular:
```python
from rectpack import newPacker

def intelligent_pack(frames: list, max_width: int = 2048):
    """Usar packing algorithm (guillotine/maximal) pra minimizar desperdício"""
    packer = newPacker(mode=packer.MODE_MAXIMAL_RECTANGLE)
    packer.add_bin(max_width, max_width)

    for idx, frame in enumerate(frames):
        w, h = frame.size
        packer.add_rect(w, h, rid=idx)

    packer.pack()

    # Resultado: retângulos posicionados eficientemente
    positions = {}
    for rect in packer.rect_list():
        bid, (x, y, w, h), rid = rect
        positions[rid] = (x, y)

    return positions
```

3. **Compressão:** PNG é bom pra pixel art (lossless), mas se spritesheet for gigante (2048x2048+), considerar WebP.

## Pra que serve

**Game Engines (Godot, Unity, Pygame):** Standard format para importar animações 2D. Melhor do que assets individuais.

**Renderização eficiente em GPU:** Single texture bind vs. multiple; GPU adora isso.

**Prototipação rápida:** Agregar múltiplas animações num arquivo simplifica workflow (1 PNG + 1 JSON vs. 20 arquivos).

**Distribuição:** Spritesheet é fácil de compartilhar (1 arquivo), vs. pasta com 50 PNGs.

**Quando NÃO usar:**
- Sprites muito grandes (> 512x512 cada). Spritesheet ficaria gigante e ineficiente.
- Animações com many variations (100+ frames). Considerar atlasing dinâmico ou streaming de frames.
- Arte vetorial (SVG). Spritesheet é exclusivamente raster.

## Exemplo prático

**Cenário:** Game de plataforma com personagem de 4 animações × 3 variações (normal, fire power-up, ice power-up) = 12 totais.

**Setup:**

```python
from PIL import Image
import json

# Carregar todas as animações
animations_base = {
    "idle": ["idle_1.png", "idle_2.png"],
    "run": ["run_1.png", "run_2.png", "run_3.png", "run_4.png"],
    "jump": ["jump_1.png"],
    "fall": ["fall_1.png"]
}

character_variants = {
    "normal": {"color": (255, 200, 100)},
    "fire": {"color": (255, 100, 50)},
    "ice": {"color": (150, 200, 255)}
}

# Gerar spritesheet para cada variante
for variant_name, variant_config in character_variants.items():
    # Carregar e colorizar frames
    frames = {}
    for anim_name, frame_files in animations_base.items():
        frames[anim_name] = []
        for file_path in frame_files:
            img = Image.open(f"assets/base/{file_path}").convert("RGBA")
            # Aplicar colorização (shader effect local)
            img_colorized = colorize_image(img, variant_config["color"])
            frames[anim_name].append(img_colorized)

    # Compor spritesheet
    spritesheet, metadata = compose_spritesheet(frames, frame_size=64)

    # Salvar
    output_name = f"character_{variant_name}"
    spritesheet.save(f"assets/sprites/{output_name}.png")
    with open(f"assets/sprites/{output_name}.json", "w") as f:
        json.dump(metadata, f)

    print(f"✓ Gerado: {output_name}.png ({spritesheet.size})")

# Resultado:
# character_normal.png (512x256)
# character_normal.json
# character_fire.png (512x256)
# character_fire.json
# character_ice.png (512x256)
# character_ice.json
```

**Uso em Godot:**

```gdscript
extends AnimatedSprite2D

var spritesheets = {}

func _ready():
    # Carregar spritesheet + metadata
    for variant in ["normal", "fire", "ice"]:
        var sprite_path = f"res://assets/sprites/character_{variant}.png"
        var meta_path = f"res://assets/sprites/character_{variant}.json"

        var texture = load(sprite_path)
        var metadata_json = FileAccess.open(meta_path, FileAccess.READ).get_as_text()
        var metadata = JSON.parse_string(metadata_json)

        # Registrar animações
        for anim_name in metadata.keys():
            for frame_data in metadata[anim_name]:
                var frame_tex = AtlasTexture.new()
                frame_tex.atlas = texture
                frame_tex.region = Rect2(frame_data["x"], frame_data["y"],
                                         frame_data["width"], frame_data["height"])

                add_frame(anim_name, frame_tex, frame_data["duration_ms"] / 1000.0)

        spritesheets[variant] = {"texture": texture, "metadata": metadata}

    # Iniciar com idle
    play("idle")

func change_variant(variant_name: String):
    """Switch entre variantes (normal/fire/ice)"""
    set_sprite_frames(spritesheets[variant_name]["metadata"])
    play("idle")

func _process(delta):
    if Input.is_action_pressed("ui_right"):
        play("run")
    elif Input.is_action_pressed("ui_up"):
        play("jump")
    else:
        play("idle")
```

---
*Conceito extraído em 2026-04-02*
