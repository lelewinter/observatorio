---
tags: [geracao-3d, o-voxel, trellis, image-to-3d, pbr, open-source]
source: https://x.com/ihtesham2005/status/2038549375794995614?s=20
date: 2026-04-02
tipo: aplicacao
---

# Converter Foto em Asset 3D com PBR em <100ms

## O que é
TRELLIS.2 (Microsoft, 4B parâmetros) transforma imagem 2D em malha 3D texturizada com materiais PBR em tempo real, via representação O-Voxel (voxel esparso orientado). Output: GLB pronto para production.

## Como implementar
**Setup local (GPU NVIDIA requerida)**:

```bash
# Clone modelo open source
git clone https://huggingface.co/microsoft/TRELLIS-2-4B
cd TRELLIS-2

# Instalar deps
pip install torch torchvision transformers diffusers pillow
pip install cuda-python  # Para aceleração CUDA

# Download checkpoint (4.2 GB)
huggingface-cli download microsoft/TRELLIS-2-4B \
  --cache-dir ./checkpoints
```

**Inferência via Python**:

```python
import torch
from trellis import TRELLISModel

# Carregar modelo
model = TRELLISModel.from_pretrained("microsoft/TRELLIS-2-4B",
                                     torch_dtype=torch.float16)
model.to("cuda")

# Input: imagem (PIL Image ou path)
from PIL import Image
image = Image.open("object.jpg")

# Gerar 3D (99ms em RTX 3080)
with torch.no_grad():
    outputs = model.generate(
        images=[image],
        text_prompts=["a detailed 3d model"],  # opcional, melhora resultado
        num_steps=28,  # mais steps = mais qualidade/tempo
        guidance_scale=7.5
    )

# Output: O-Voxel internal representation
o_voxel = outputs[0].geometry

# Converter para GLB com PBR
mesh = o_voxel.to_mesh()
mesh.apply_material_pbr(outputs[0].materials)
mesh.export_glb("output.glb")
```

**Alternativa: Web (sem instalação)**:
- Hugging Face Space: [microsoft/TRELLIS-2-demo](https://huggingface.co/spaces/microsoft/TRELLIS-2-demo)
- Carregar imagem → aguardar 5-30 seg → download GLB

**Integração em pipeline**:

```bash
# Batch processing (múltiplas imagens)
for img in assets/fotos/*.jpg; do
  python inference.py --input "$img" --output "output/$(basename "$img" .jpg).glb"
done

# Resultado: 50 imagens → 50 GLBs texturizados em ~10 min
```

**Qualidade + Iteração**:

```python
# Parâmetros de controle:
# - num_steps: 14 (rápido, 50ms) a 28 (qualidade, 100ms)
# - guidance_scale: 1.0 (ignore prompts) a 15.0 (força demais)
# - negative_prompt: "blurry, low quality" (evitar artefatos)

outputs = model.generate(
    images=[image],
    text_prompts=["highly detailed model, clean geometry"],
    negative_prompts=["blurry, noisy, deformed"],
    num_steps=28,
    guidance_scale=8.0
)
```

**Otimização pós-geração**:

```bash
# Reduzir tamanho de GLB (100-300 MB → 10-50 MB)
gltf-transform compress output.glb output_compressed.glb

# Inspeccionar/editar em Blender se necessário
# (raramente, output é usável direto em 95% dos casos)
```

## Stack e requisitos
- **GPU mínima**: RTX 3060 (12 GB VRAM) para FP16. RTX 4090 ideal
- **Memória RAM**: 16 GB mínimo
- **Tempo inferência**: 50-100ms TRELLIS-2-4B em GPU moderna
- **Input**: imagem JPEG/PNG (qualquer resolução, rescalado internamente a 512x768)
- **Output**: GLB (inclui géometria + texturas RGB + mapas normais + roughness/metallic)
- **Licença**: MIT open source
- **Custo**: $0 (local) ou free (Hugging Face demo)
- **Compatibilidade**: Blender, Unity, Unreal, Godot, Three.js (GLTF 2.0)

## Armadilhas e limitações
- **Ambiguidade de profundidade**: sem múltiplas vistas, profundidade é "adivinhar" (ótimo para objetos simples, falha em estruturas complexas)
- **Reflexos e transparência**: vidro, metal polido geram geometria estranha. Usar prompts negativos fortes
- **Topologia não-otimizada**: mesh pode ter triângulos desnecessários. Remeshing via Instant Meshes melhora
- **Fidelidade fina limitada**: detalhes muito pequenos (fios, parafusos) podem ser perdidos. Se crítico, fazer retopo manual em Blender
- **PBR é 90% automático**: texturas são baked, não procedurais. Se quer Substance Designer nodes, rebake é necessário
- **Erro de escala**: modelo não sabe se objeto é 1cm ou 1m. Reescalar manualmente em engine
- **Características antropomórficas**: rostos humanoides saem deformados (problema clássico). Usar prompts genéricos
- **Requer GPU CUDA**: CPU inference é ~1000x mais lento (inviável)
- **Tamanho do modelo**: 4.2 GB checkpoint + runtime PyTorch = ~6-8 GB disco + RAM

## Conexões
- [[voxel-representation-geometry]]
- [[pbr-texturing-materiais-3d]]
- [[image-to-3d-generation-landscape]]
- [[geracao-3d-por-comando-texto]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com setup prático + otimizações