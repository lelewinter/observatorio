---
tags: [sprite-generation, isometric-pixel-art, video-generation, veo, gamedev-assets, procedural-animation]
source: https://x.com/chongdashu/status/2037573384674930715?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Sprites Isométricos com IA + Walk Cycles Automáticos

## O que é
Pipeline: gerar 4 direções cardinais de sprite isométrico pixel art → derivar 4 diagonais via transformação → interpolar em walk cycle via vídeo (Veo 3.1). Resultado: spritesheet completo.

## Como implementar
**Pipeline de geração** (usando fal.ai orchestration):

```python
import fal
import json
from PIL import Image

CHARACTER_PROMPT = "knight in medieval armor, isometric view, pixel art style, 32x32 pixels"
DIRECTIONS = ["north", "west", "south", "east"]

def generate_cardinal_sprites():
    results = {}
    for direction in DIRECTIONS:
        prompt = f"{CHARACTER_PROMPT} facing {direction}"
        model = fal.Model("gpt-image-1.5-turbo", credentials=FAL_API_KEY)
        result = model.predict(prompt=prompt, num_inference_steps=30, aspect_ratio="1:1")
        removed_bg = remove_background(result["image_url"])
        results[direction] = removed_bg
    return results

def derive_diagonal_directions(cardinal_sprites):
    diagonals = {}
    diagonal_angles = {
        "northeast": (45, -45),
        "northwest": (45, 45),
        "southwest": (-45, 45),
        "southeast": (-45, -45)
    }

    for diagonal_dir, (flip_x, rotate) in diagonal_angles.items():
        base = cardinal_sprites["north"] if "north" in diagonal_dir else cardinal_sprites["south"]
        img = Image.open(base)
        if flip_x > 0:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if rotate != 0:
            img = img.rotate(rotate)
        output_path = f"sprite_{diagonal_dir}.png"
        img.save(output_path)
        diagonals[diagonal_dir] = output_path
    return diagonals

def generate_walk_cycle(all_sprites):
    frames = [all_sprites[d] for d in ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]]
    model = fal.Model("veo-3.1-motion", credentials=FAL_API_KEY)
    result = model.predict(frames=frames, motion_type="walk_cycle", duration_sec=2.0, num_interpolation_frames=4)
    return result["video_url"]

cardinal_sprites = generate_cardinal_sprites()
diagonal_sprites = derive_diagonal_directions(cardinal_sprites)
all_sprites = {**cardinal_sprites, **diagonal_sprites}
walk_video = generate_walk_cycle(all_sprites)
```

**Integrar em engine** (Godot 4):

```gdscript
extends AnimatedSprite2D

func _ready():
    var metadata = JSON.parse_string(ResourceLoader.load_as_text("res://assets/character_walk.json"))
    var spritesheet = load("res://assets/character_walk_spritesheet.png")
    frames = SpriteFrames.new()
    frames.add_animation("walk")

    var frame_size = Vector2(metadata["frame_width"], metadata["frame_height"])
    for i in range(metadata["total_frames"]):
        var atlas = AtlasTexture.new()
        atlas.atlas = spritesheet
        atlas.region = Rect2(Vector2(i % 8, floor(i / 8)) * frame_size, frame_size)
        frames.add_frame("walk", atlas)

    animation = "walk"
    play()
```

## Stack e requisitos
- **Modelos IA**: GPT Image 1.5, Veo 3.1, background remover API
- **Orquestração**: fal.ai SDK (Python)
- **Input**: prompt (50-100 palavras) + resolução (32x32 a 256x256)
- **Output**: PNG spritesheet + JSON metadata
- **Tempo**: ~10 min total (3-5 min cardinal + 2 min diagonals + 3-5 min video)
- **Custo**: $1-2 por personagem completo (cardinals + video generation)
- **Compatibilidade**: Godot 2D, Phaser, Construct

## Armadilhas e limitações
- **Inconsistência residual**: diagonals via transformação geométrica podem parecer "off" se cardinal tem detalhe assimétrico. Inspecionar + touchup manual
- **Animação walk genérica**: movimento neutro apenas. Customizações (corrida, dança) exigem mais iterações
- **Fundo removal imperfeito**: remove.bg deixa halos. Máscara manual se crítico
- **Custo video caro**: Veo 3.1 é custoso para batch production
- **Detalhe fino perde**: video-interpolation suaviza bordas (blurry em pixel art)
- **Sem sincro physics**: visual puro, hitbox programada separadamente
- **Performance em loop**: walk cycle curto mostra repetição óbvia. Cross-fade com segundo cycle

## Conexões
- [[spritesheet-generation]]
- [[pixel-art-procedural-generation]]
- [[walk-cycle-animation-gamedev]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com pipeline completo + código Godot
