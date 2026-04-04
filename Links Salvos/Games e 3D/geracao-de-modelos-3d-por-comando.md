---
tags: [geracao-3d, text-to-3d, ia-generativa, glb-format, prototipagem, asset-generation]
source: https://x.com/omma_ai/status/2036651786443129086?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Modelos 3D via Prompt de Texto

## O que é
Ferramentas de IA que transformam descrição textual em modelo 3D completo, triangulado, texturizado e otimizado em formato GLB. Elimina etapas manuais de topologia, UV mapping e compressão.

## Como implementar
**Ferramentas recomendadas** (ranking por qualidade/velocidade):

| Ferramenta | Entrada | Velocidade | Custo | Qualidade | Melhor para |
|---|---|---|---|---|---|
| **Meshy.ai** | texto/imagem | 2-5 min | $10/10 créditos | ⭐⭐⭐⭐⭐ | assets simples, iteração rápida |
| **Tripo 3D** | texto/imagem | 1-2 min | free (limited) | ⭐⭐⭐⭐ | prototipagem, web 3D |
| **OpenAI Shap-E** | texto | 30 seg | $0.01-0.02/geração | ⭐⭐⭐ | testing, desenvolvimento |
| **Luma AI** | imagem | 3-10 min | $4/3.50 créditos | ⭐⭐⭐⭐ | realismo fotográfico |
| **Omma** | texto | instantâneo | web+API | ⭐⭐⭐ | composição em cena, iteração |

**Fluxo de implementação com Meshy.ai**:

1. **Criar account** (google/email) e obter API key via dashboard

2. **Fazer requisição**:
```bash
curl -X POST https://api.meshy.ai/v1/text-to-3d \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "fast",
    "prompt": "medieval iron sword with ornate leather grip",
    "art_style": "realistic",
    "negative_prompt": "blurry, low quality, cartoon"
  }'

# Resposta: {"result": {"model_url": "https://..../model.glb", "id": "xyz"}}
```

3. **Baixar e integrar**:
```python
import requests

response = requests.get("https://..../model.glb")
with open("sword.glb", "wb") as f:
    f.write(response.content)

# Usar em engine
# Unity: modelo → Drag-drop na Scene
# Godot 4: import GLB via ImportGLTF2 → use em 3D node
# Web: THREE.js loader
```

4. **Otimizar para produção**:
```bash
# Reduzir tamanho com ferramentas offline
# Draco compression via gltf-transform
npm install -g @gltf-transform/cli

gltf-transform compress sword.glb sword_compressed.glb
# Típico: 150MB → 15MB com Draco, mantendo qualidade visual

# Ou via Blender (GUI)
# File → Import GLB → Export GLB (ativar Draco compression)
```

**Workflow para game dev indie**:
- Prompt genérico → resultado → feedback → refino via Meshy iterations
- Melhor praticar: decompor em sub-assets (arma, armadura, acessório) em vez de tentar gerar character inteiro
- Exemplo real: "rusty metal bucket with rope handle, top-down view" (simples) vs "complete human knight with dynamic cloth" (complexo, failure-prone)

## Stack e requisitos
- **Entrada**: prompt (25-150 palavras, ser específico)
- **Formato saída**: GLB (triangulado, texturas baked em JPEG/PNG)
- **Resoluções**: 512x512 a 1024x1024 UV textures (maior = mais custo)
- **Custo Meshy**: $5 startup + $0.80/modelo fast, $1.20/modelo standard
- **Custo Shap-E (local)**: $0 (open source, requer GPU A100 ou similar para speed)
- **Tempo total**: entrada → uso em engine: 5-15 min (web) ou 2-3 min (local se você tem GPU)
- **Compatibilidade**: GLB universal — Unity, Unreal, Godot, Three.js, Babylon.js, PlayCanvas

## Armadilhas e limitações
- **Controle geométrico limitado**: não consegue especificar "exatamente 4 pernas", "simetria perfeita". Rede neural é estocástica
- **Detalhes finos falham**: logos, text, padrões repetitivos saem borrados. Use painting pós-geração em Blender se crítico
- **Hands e faces**: modelos humanoides têm problemas clássicos de IA (dedos deformados, faces estranhas). Inspecionar antes de usar
- **Topologia não-otimizada**: modelos saem com polígonos desnecessários. Remesher online (Instant Meshes, voxel remesh) melhora
- **Baked textures apenas**: sem material nodes. Se precisa de PBR procedural (normal maps, roughness), rebake em Substance ou Blender
- **Tamanho de arquivo**: GLB base 30-150MB antes de compressão. Necessário Draco para web/mobile
- **IP/Commercial use**: verificar ToS por ferramenta. Meshy permite uso comercial (paga), OpenAI tem restrições

## Conexões
- [[glb-format-3d-standard]]
- [[otimizacao-mesh-topologia]]
- [[asset-generation-pipeline-automatizado]]
- [[prototipagem-rapida-3d]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com comparação de ferramentas + stack técnico