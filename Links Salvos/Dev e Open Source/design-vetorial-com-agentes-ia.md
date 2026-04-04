---
tags: [design, vetorial, ia, ícones, svg, ilustracao]
source: https://x.com/author/status/123
date: 2026-04-02
tipo: aplicacao
---

# Gerar Ícones e Vetores com Agentes de IA

## O que é

Modelos de IA generativa (Midjourney, DALL-E, Leonardo) geram gráficos vetoriais (SVG) a partir de descrição. Elimina trabalho manual de design.

## Como implementar

**Prompt estruturado:**
```
"Ícone SVG de database, estilo flat, cores azul #3B82F6 e branco,
64x64px, traço 2px, fundo transparente"
```

**Com API Leonardo:**
```python
import requests

def generate_icon(description):
    r = requests.post("https://api.leonardo.ai/v1/generation", json={
        "prompt": description,
        "format": "svg",
        "size": "512"  # Upscale depois
    }, headers={"Authorization": f"Bearer {KEY}"})
    return r.json()["url"]

icon = generate_icon("storage icon, flat, blue and white")
```

**Local (Stable Diffusion):**
```bash
# Setup via Automatic1111
python launch.py --listen 0.0.0.0

# Prompt via API
curl http://localhost:7860/api/txt2img \
  -H "Content-Type: application/json" \
  -d '{"prompt":"flat database icon","steps":20,"cfg_scale":7}'
```

**PNG → SVG (vectorizar):**
```bash
# Instalar Potrace
sudo apt install potrace

# Converter
potrace icon.png -s -o icon.svg

# Cleanup automático (Inkscape)
inkscape icon.svg \
  --actions="EditSelectAll;ObjectSimplifyPath;SelectionUnionSet" \
  -o icon_clean.svg
```

**Sistema de ícones:**
```python
icons = ["storage", "network", "security", "database", "cloud", "server"]

for icon_name in icons:
    prompt = f"{icon_name} icon, flat, minimal, blue, 512x512"
    url = generate_icon(prompt)
    # Salvar como SVG
    # Vectorizar se necessário
    print(f"✓ {icon_name}")
```

## Stack e requisitos

- **API**: Leonardo.AI, DALL-E, Midjourney
- **Local**: Stable Diffusion
- **Conversion**: Potrace, Inkscape
- **Output**: SVG, PNG

## Armadilhas

1. **Propriedade intelectual**: Verificar licença (comercial ou não).
2. **Qualidade**: Raster→SVG perde detalhes. Refinar manualmente é necessário.
3. **Consistência**: Prompts precise=estilos consistentes. Template reutilizável.

## Conexões

- [[design-generativo-por-ia]] - UI completo com IA
- [[conversao-html-para-react-com-vibe-coding]] - Integrar em React

## Histórico

- 2026-04-02: Reescrita com implementação
