---
tags: [pixel-art, game-dev, ia-generativa, assets, workflow, producao-criativa]
source: https://x.com/asynkimo/status/2036874617462116768?s=20
date: 2026-04-02
tipo: aplicacao
---
# Pipeline Acelerado de Sprite Animation: Foto → Pixel Art → Spritesheet Jogável

## O que é
Workflow que transforma fotos de referência (pessoas, objetos, personagens) em assets 2D completos e animados (idle, run, jump) em pixel art, prontos para engines de jogo (Godot, Pygame, Unity) em ~20-30 minutos. Reduz ciclo de prototipação de "2-3 dias de work humano" para "30 min + custo de API IA".

## Como implementar

**Arquitetura completa (5 etapas):**

```
Foto de referência (JPG)
  ↓
1. Geração de spritesheet base (Midjourney/Stable Diffusion com prompt técnico)
  ↓
2. Extração de silhueta + cores dominantes (Python PIL/OpenCV)
  ↓
3. Geração de frames animados (8-16 poses distintas)
  ↓
4. Composição em spritesheet (grid com metadata JSON)
  ↓
5. Validação + exportação pra engine (Godot/Pygame)
```

**Etapa 1: Geração de Spritesheet Base**

Use Midjourney ou Stable Diffusion com prompt estruturado:

```
Prompt para Midjourney:

"pixel art spritesheet, [PERSONAGEM] 16x16 pixel character,
isometric view, vibrant colors, 8 animation frames:
idle(2), walk_left(2), walk_right(2), jump(2),
nostalgia 8bit style, detailed features,
clear silhouette --niji 6 --style expressive --s 750"
```

**Key técnicas de prompt:**
- **Tamanho explícito:** "16x16 pixel", "32x32 pixel" (engine típica em 2D é 32-64px).
- **Poses necessárias:** Nomear cada pose (idle, walk, jump, attack, etc.) para geração consistente.
- **Aspecto artístico:** "8bit", "pixel art retro", "vibrant colors" direciona estilo.
- **Consistência:** Mencionar personagem por nome/descrição em CADA prompt (com diferentes poses) pra manter coerência visual.

```python
import anthropic
import json
from pathlib import Path

class SpriteGenerator:
    def __init__(self, reference_photo_path: str):
        self.reference_photo = Path(reference_photo_path)
        self.client = anthropic.Anthropic()

    def analyze_reference(self):
        """Usar Claude pra extrair características da foto"""
        prompt = f"""
        Analise essa foto de referência e descreva em JSON:
        - Cor dominante (RGB)
        - Silhueta/forma (quadrada, esbelta, musculosa)
        - Características únicas (chapéu, arma, coroa)
        - Proporções (altura/largura ratio)
        - Estilo recomendado (cartoon, realista, abstrato)

        Retorne JSON puro, nada mais.
        """
        # Claude vision call (não incluído aqui por brevidade)
        pass

    def generate_midjourney_prompts(self):
        """Gerar 16 prompts Midjourney para as 16 poses"""
        prompt_template = """
        Gere 16 prompts diferentes para Midjourney que produzam
        um spritesheet coerente de personagem pixel art.

        Personagem: {character_name}
        Características: {characteristics}

        Poses necessárias:
        - idle (2 frames): parado olhando pra câmera, parado olhando pro lado
        - walk (4 frames): 4-frame walk cycle
        - jump (2 frames): preparação (crouch), pulo (ascendendo)
        - attack (2 frames): preparação de ataque, ataque conectado
        - hit (2 frames): reação de dano, queda
        - fall (2 frames): queda, caído

        Cada prompt deve:
        1. Especificar tamanho exato do pixel (32x32)
        2. Nomear a pose específica
        3. Detalhar ângulo/perspectiva
        4. Manter estilo visual consistente

        Retorne JSON com lista de 16 prompts.
        """

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt_template}]
        )

        return json.loads(response.content[0].text)

    def generate_stable_diffusion_local(self, prompt: str):
        """Usar Stable Diffusion local se não quiser Midjourney"""
        from diffusers import StableDiffusionPipeline
        import torch

        model_id = "runwayml/stable-diffusion-v1-5"
        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16).to("cuda")

        image = pipe(prompt, height=512, width=512, guidance_scale=7.5).images[0]
        return image
```

**Etapa 2: Extração de Silhueta + Cores (Python)**

Após gerar spritesheet base com IA, você precisa otimizar e extrair cores:

```python
from PIL import Image
import numpy as np
from scipy import ndimage

def extract_silhouette(image_path: str):
    """Extrair silhueta preta com fundo branco"""
    img = Image.open(image_path).convert("RGBA")
    img_array = np.array(img)

    # Detectar pixels não-transparentes
    alpha = img_array[:, :, 3]
    silhouette = np.where(alpha > 127, 0, 255).astype(np.uint8)

    return Image.fromarray(silhouette, mode='L')

def get_dominant_colors(image_path: str, n_colors: int = 8):
    """Extrair paleta de cores do sprite"""
    from sklearn.cluster import KMeans

    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img).reshape(-1, 3)

    kmeans = KMeans(n_clusters=n_colors, random_state=42)
    kmeans.fit(img_array)

    colors = kmeans.cluster_centers_.astype(int)
    return colors  # Lista de RGB

def posterize_to_colors(image_path: str, colors: np.ndarray):
    """Remapear imagem para usar apenas 8 cores (estilo retro)"""
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img).reshape(-1, 3)

    # K-NN: cada pixel → cor mais próxima
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(colors)
    distances, indices = nn.kneighbors(img_array)

    posterized = colors[indices].reshape(img.height, img.width, 3)
    return Image.fromarray(posterized.astype(np.uint8))
```

**Etapa 3: Geração de Frames Animados**

Se o Midjourney/Stable Diffusion não gerou todos os frames, use interpolação + IA:

```python
def generate_missing_frames(base_sprite: Image, pose: str, n_frames: int = 4):
    """Gerar frames intermediários de animação"""
    # Opção 1: Interpolação simples (se tiver frame inicial + final)
    # Opção 2: Usar IA pra criar poses intermediárias
    # Opção 3: Usar AnimateDiff (modelo especializado em animação)

    from diffusers import AnimateDiffPipeline
    import torch

    model_id = "guoyww/animatediff-motion-adapter-v1-5-2"
    pipe = AnimateDiffPipeline.from_pretrained(model_id, torch_dtype=torch.float16)

    prompt = f"pixel art character {pose}, smooth animation cycle"
    frames = pipe(prompt, num_inference_steps=20, num_frames=n_frames).frames

    return frames  # List de PIL Images

def create_walk_cycle(sprite_image: Image, direction: str = "right"):
    """Gerar 4-frame walk cycle a partir de sprite static"""
    # Método: modificar sprite com shift, tilt, flex
    # Frame 1: perna esquerda avançada
    # Frame 2: ambas pernas retas
    # Frame 3: perna direita avançada
    # Frame 4: ambas pernas retas (voltando ao frame 2)

    width, height = sprite_image.size
    frames = []

    # Usar PIL transformations + AI-based morphing
    for i in range(4):
        angle = (i / 4) * 360  # Ciclo completo
        frame = sprite_image.rotate(angle * 0.1, center=(width//2, height//2), fillcolor=(255, 255, 255))
        frames.append(frame)

    return frames
```

**Etapa 4: Composição em Spritesheet**

Arranjar frames em grid + gerar metadata:

```python
from PIL import Image
import json

def create_spritesheet(frames_dict: dict, output_path: str):
    """
    frames_dict: {
        "idle": [Image, Image],
        "walk": [Image, Image, Image, Image],
        "jump": [Image, Image],
        ...
    }
    """
    # Parâmetros
    frame_width, frame_height = 64, 64
    frames_per_row = 8

    # Calcular tamanho total
    total_frames = sum(len(frames) for frames in frames_dict.values())
    rows = (total_frames + frames_per_row - 1) // frames_per_row
    spritesheet_width = frames_per_row * frame_width
    spritesheet_height = rows * frame_height

    # Criar canvas
    spritesheet = Image.new("RGBA", (spritesheet_width, spritesheet_height), (0, 0, 0, 0))

    # Preencher com frames
    metadata = {}
    frame_index = 0

    for animation_name, frames in frames_dict.items():
        metadata[animation_name] = []

        for frame_num, frame in enumerate(frames):
            x = (frame_index % frames_per_row) * frame_width
            y = (frame_index // frames_per_row) * frame_height

            # Redimensionar frame se necessário
            frame_resized = frame.resize((frame_width, frame_height), Image.Resampling.NEAREST)
            spritesheet.paste(frame_resized, (x, y), frame_resized)

            # Registrar metadata
            metadata[animation_name].append({
                "index": frame_index,
                "x": x,
                "y": y,
                "width": frame_width,
                "height": frame_height,
                "duration_ms": 100  # Duração padrão por frame
            })

            frame_index += 1

    # Salvar spritesheet
    spritesheet.save(output_path)

    # Salvar metadata (JSON)
    metadata_path = output_path.replace(".png", ".json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata

# Uso
frames = {
    "idle": [Image.open("idle_1.png"), Image.open("idle_2.png")],
    "walk": [Image.open(f"walk_{i}.png") for i in range(4)],
    "jump": [Image.open(f"jump_{i}.png") for i in range(2)]
}

metadata = create_spritesheet(frames, "character_spritesheet.png")
```

**Etapa 5: Exportar pra Engine (Godot GDScript)**

```gdscript
# Em Godot
extends AnimatedSprite2D

var spritesheet_metadata = {}

func _ready():
    # Carregar metadata
    var file = FileAccess.open("res://assets/character_spritesheet.json", FileAccess.READ)
    spritesheet_metadata = JSON.parse_string(file.get_as_text())

    # Configurar texture
    texture = load("res://assets/character_spritesheet.png")

    # Adicionar animações programaticamente
    for anim_name in spritesheet_metadata.keys():
        var frames_data = spritesheet_metadata[anim_name]
        var animation = Animation.new()

        for frame_data in frames_data:
            var frame = AtlasTexture.new()
            frame.atlas = texture
            frame.region = Rect2(frame_data["x"], frame_data["y"], frame_data["width"], frame_data["height"])
            add_frame(anim_name, frame, frame_data["duration_ms"] / 1000.0)

    play("idle")

func _process(delta):
    if Input.is_action_pressed("ui_right"):
        play("walk")
        flip_h = false
    elif Input.is_action_pressed("ui_left"):
        play("walk")
        flip_h = true
    else:
        play("idle")
```

## Stack e requisitos

**APIs/Serviços:**
- Midjourney ($30-120/mês subscriçao) ou Stable Diffusion local (zero custo, requer GPU).
- Anthropic Claude API (~$0.001-$0.01 por imagem análise, negligível).

**Bibliotecas Python:**
- `pillow` (PIL), `numpy`, `opencv-python` (processamento de imagem)
- `scikit-learn` (k-means, extração de cores)
- `diffusers` (Stable Diffusion local)
- `anthropic` (Claude API)

**Hardware:**
- GPU NVIDIA (RTX 3060+ recomendado) se rodar Stable Diffusion local.
- CPU suficiente (composição de spritesheet é leve).

**Engines alvo:** Godot, Pygame, Unity (importar PNG + metadata JSON).

## Armadilhas e limitações

**Inconsistência Visual Entre Poses:** Cada geração Midjourney/SD é independente. Personagem pode ter cor/proporção ligeiramente diferente em "walk" vs. "jump". **Mitigação:**
- Usar mesma seed (Midjourney) ou referência strong em prompt.
- Aplicar post-processing uniforme (posterização, ajuste de cores) em todas as poses.
- Fazer spot-check visual; regenerar poses inconsistentes.

**Qualidade de Animação:** Interpolação simples (shift/rotate) não produz ciclos de walk fluidos. **Mitigação:**
- Usar AnimateDiff ou pipeline especializado em síntese de movimento.
- Ou pedir ao Midjourney que gere explicitamente "4-frame walk cycle" vs. poses individuais.
- Testar no engine e ajustar duração de frames (100ms padrão; pode ser 80-150ms).

**Limitações de Tamanho:** Pixel art muito pequena (16x16) tem detalhe limitado. Fotos com features finas (cabelo, expressão) podem não sair legível. **Mitigação:**
- Aumentar tamanho (32x32, 64x64) se possível.
- Simplificar características na foto de referência (sugerir ao IA "cartoon style, simplified").

**Tempo de Geração:** Stable Diffusion local leva 5-10s por frame. Com 16 poses = 80-160s. Midjourney é mais rápido (~1min por prompt). **Mitigação:**
- Reusar frames onde possível (flip horizontalmente para walk left vs. walk right).
- Gerar em paralelo (múltiplos prompts simultâneos).

**Dependência de Prompt Engineering:** Qualidade final é 80% prompt, 20% modelo. Prompt ruim = sprite ruim. **Mitigação:**
- Iterar prompts (testar 3-5 variações de cada pose).
- Usar referências similares de sprites existentes no prompt ("inspired by Celeste pixel art").

## Conexões

- [[llm-para-automacao-criativa]] - geração de prompts estruturados
- [[producao-criativa-como-processo-estatistico]] - iteração de qualidade visual
- [[sintese-de-video-com-avatares]] - extensão pra personagens 3D animados

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Nota reescrita e enriquecida pelo pipeline de curadoria