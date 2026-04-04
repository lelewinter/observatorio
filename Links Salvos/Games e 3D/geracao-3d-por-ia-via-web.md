---
tags: [text-to-3d, image-to-3d, ia-generativa, threejs, single-view-reconstruction, web]
source: https://x.com/_ArcadeStudio_/status/2036715023314116729?s=20
date: 2026-04-02
tipo: aplicacao
---

# Converter Texto ou Imagem em Modelo 3D Renderizado na Web

## O que é
Dois pipelines: **Text-to-3D** (prompt → geometria) e **Image-to-3D** (foto → reconstrução volumétrica), ambos renderizados em Three.js no browser. Sem instalar Blender.

## Como implementar
**Text-to-3D (gerar do zero)**:

```bash
# Via API (Meshy, Tripo, Point-E)
curl -X POST https://api.tripoai.com/v1/generate-model \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "a bronze statue of a phoenix with wings spread",
    "style": "realistic",
    "model_type": "mesh"
  }'

# Resposta: {"model_id": "xyz", "download_url": "...model.glb"}
```

**Image-to-3D (reconstruir de foto)**:

```python
# Usar framework como Shap-E ou LRM (Large Reconstruction Model)
import torch
from PIL import Image
from lrm import LRMModel

model = LRMModel.from_pretrained("facebook/lrm-large")
image = Image.open("phone.jpg")

# Single-view 3D reconstruction (100-500ms em GPU)
mesh = model.reconstruct(image,
                        num_steps=32,
                        guidance_scale=7.5)

mesh.export_glb("output.glb")
```

**Renderizar em Three.js**:

```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 16/9, 0.1, 100);
const renderer = new THREE.WebGLRenderer({ antialias: true });

// Lighting
const light = new THREE.HemisphereLight(0xffffff, 0x404040, 1);
scene.add(light);

// Load gerado modelo
const loader = new GLTFLoader();
loader.load('output.glb', (gltf) => {
    const model = gltf.scene;

    // Auto-center e scale
    const bbox = new THREE.Box3().setFromObject(model);
    const center = bbox.getCenter(new THREE.Vector3());
    model.position.sub(center);

    const size = bbox.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const scale = 2 / maxDim;
    model.scale.multiplyScalar(scale);

    scene.add(model);
    animate();
});

// Controles de estilo via shader
// (neural rendering para cartoon/sketch/realista)
const styles = {
    realistic: { roughness: 0.5, metallic: 0.1 },
    cartoon: { roughness: 0.9, metallic: 0.0, outline: true },
    sketch: { wireframe: true, color: 0x333333 }
};

function applyStyle(style) {
    model.traverse((node) => {
        if (node.isMesh) {
            Object.assign(node.material, styles[style]);
        }
    });
}

function animate() {
    requestAnimationFrame(animate);
    model.rotation.y += 0.005;
    renderer.render(scene, camera);
}
```

**Workflow completo**:

1. Escolher modal: texto ou imagem
2. Enviar para API ou local inference
3. Carregar GLB em Three.js scene
4. Ajustar lighting/material presets
5. Capturar PNG ou exportar GLB

## Stack e requisitos
- **Frontend**: Three.js, Babylon.js, ou o-3D (alternatives)
- **Backend IA**: Meshy, Tripo 3D, Luma, Point-E, LRM
- **Browser**: WebGL 2 suporte (Chrome 90+, Firefox 88+)
- **Tempo Text-to-3D**: 2-10 min (web API) ou 30-300s (local LRM)
- **Tempo Image-to-3D**: 5-30 min (Luma) ou 100-500ms (LRM local)
- **Entrada**: prompt 30-150 palavras ou JPG/PNG até 4K
- **Saída**: GLB + viewport Three.js + PNG screenshot
- **VRAM local (opcional)**: RTX 3060 min para LRM, RTX 4080 ideal
- **Custo cloud**: $0.50-5 por geração (Meshy/Tripo/Luma)
- **Custo local**: $0 (LRM open source)

## Armadilhas e limitações
- **Text-to-3D ambiguidade**: "phoenix" pode gerar aves muito diferentes. Iteração é necessária
- **Image-to-3D monoview error**: profundidade é inferida, não medida. Reflexos/transparência causam artefatos
- **Mesh quality variável**: topologia pode ser pesada ou ter buracos. Remeshing em Blender se crítico
- **Three.js limitations**: sem materials PBR completos (apenas albedo + normal)
- **Estilização limitada**: neural rendering no browser é básico (cartoon/wireframe apenas)
- **Performance web**: 50+ objetos = < 30 FPS
- **UX fragility**: se API está slow, user vê spinner longo (experiência ruim)
- **Falta colaboração**: sem multiuser real-time (cada tab é isolada)
- **No animation**: modelos estáticos, sem skeletal animation ou armature

## Conexões
- [[single-view-3d-reconstruction]]
- [[three-js-para-desenvolvimento-de-jogos]]
- [[material-system-pbr-web]]
- [[geracao-3d-com-ia-no-browser]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com implementação prática