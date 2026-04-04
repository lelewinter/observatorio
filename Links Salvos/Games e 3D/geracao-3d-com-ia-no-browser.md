---
tags: [3d-web, ia-generativa, text-to-3d, threejs, game-design, prototipagem]
source: https://x.com/_ArcadeStudio_/status/2037442244878414049?s=20
date: 2026-04-02
tipo: aplicacao
---

# Prototipar Cenas 3D Completas via IA no Browser

## O que é
Pipeline end-to-end de geração 3D no navegador: prompt → IA gera objeto → posiciona em cena → renderiza via Three.js. Zero instalação, zero espera por render farm.

## Como implementar
**Ferramentas existentes** (maior facilidade):
- **Arcade.Studio**: interface "World Builder", drag-drop + prompts
- **Spline.design**: editor visual web com geração via IA
- **Leonardo.AI Scene Gen**: prototipagem rápida de cenas
- **PlayCanvas + Custom Gen**: build seu own com JavaScript

**Setup custom com Three.js + IA (mais controle)**:

```javascript
// setup Three.js scene
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Gerar objeto 3D via API (exemplo Meshy)
async function generateAndPlace(prompt) {
    const response = await fetch('https://api.meshy.ai/v1/text-to-3d', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${API_KEY}` },
        body: JSON.stringify({
            prompt: prompt,
            mode: 'fast',
            art_style: 'realistic'
        })
    });

    const { result } = await response.json();
    const modelUrl = result.model_url;

    // Carregar GLB em scene via Three.js
    const loader = new GLTFLoader();
    loader.load(modelUrl, (gltf) => {
        const model = gltf.scene;
        scene.add(model);

        // Posicionar/rotacionar
        model.position.set(0, 0, 0);
        model.scale.set(1, 1, 1);

        // Renderizar
        animate();
    });
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

// Usar
generateAndPlace("wooden medieval chair with ornate carvings");
```

**Workflow de iteração rápida**:

1. **Text → 3D**: digitar prompt, gerar modelo (1-5 min)
2. **Posicionar**: drag-drop no viewport da cena
3. **Ajustar material**: acesso a shader básico ou material presets (metallic, wood, concrete)
4. **Render**: captura PNG/WebGL em tempo real
5. **Export**: GLB para Unity/Godot, ou JSON de cena para reuso

**Performance tips**:
- Usar WebGL 2 (fall back pra WebGL 1 em mobile)
- Limitar modelos simultâneos (max 5-10 em browser moderno)
- Usar LOD: reduzir vértices em distância > 50m
- Bake texturas se possível (menos overhead de shader)

## Stack e requisitos
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+ (WebGL 2)
- **GPU**: qualquer GPU moderna (desktop/laptop)
- **API backend**: Meshy, Tripo 3D, Luma AI (cada um com pricing próprio)
- **Frontend libs**: Three.js 150+ KB, Babylon.js 300+ KB
- **Entrada**: texto (30-150 palavras)
- **Saída**: GLB renderizado no browser + PNG screenshot
- **Performance**: 60 FPS para 5-10 objetos, 15-30 FPS para 50+ objetos
- **Custo**: $0 setup + $0.50-2.00 por geração (Meshy/Tripo)

## Armadilhas e limitações
- **Browser limitations**: limite de VRAM (2-4 GB typical), sem acesso a GPU compute nativo
- **Qualidade vs speed**: Three.js WebGL é 5-10x mais lento que Unreal/Unity native
- **Sem full material editing**: acesso limitado a shader nodes (não é Substance Painter)
- **Colaboração ausente**: não há "multiuser realtime" (cada browser é isolado)
- **Instabilidade em scene complexity**: > 100 objetos + dynamic lights = 5-10 FPS
- **UX fiddly**: carregar modelos pode ser lento se API responde devagar (sem fallback)
- **Exportação limitada**: GLB é padrão, FBX/USD requerem conversor externo
- **Sem versioning**: salvar cena é JSON manual, não há git-like undo

## Conexões
- [[three-js-para-desenvolvimento-de-jogos]]
- [[webgl-vs-webgpu-rendering]]
- [[ia-generativa-3d-trends]]
- [[prototipagem-rapida-game-design]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com setup prático + performance tips