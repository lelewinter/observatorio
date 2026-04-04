---
tags: [world-building, ia-generativa, asset-generation, scene-composition, game-design, threejs]
source: https://x.com/_ArcadeStudio_/status/2037083661347283237?s=20
date: 2026-04-02
tipo: aplicacao
---

# Montar Cenas 3D Completas com IA: Gerar → Posicionar → Renderizar

## O que é
Pipeline unificado no browser: gerar múltiplos assets via IA → arranjar em cena → renderizar em Three.js. "World Builder" coloca tudo em um lugar.

## Como implementar
**Fluxo manual com APIs separadas** (máximo controle):

```javascript
// 1. Gerar múltiplos assets (paralelo)
async function generateAssets(prompts) {
    const promises = prompts.map(p =>
        fetch('https://api.meshy.ai/v1/text-to-3d', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${API_KEY}` },
            body: JSON.stringify({
                prompt: p,
                mode: 'fast',
                model_type: 'mesh'
            })
        }).then(r => r.json())
    );

    return Promise.all(promises);
}

// 2. Montar cena declarativamente
const sceneConfig = {
    assets: [
        { model: 'tree_oak.glb', position: [0, 0, 0], scale: 1.5 },
        { model: 'rock_large.glb', position: [5, 0.5, -3], scale: 2.0 },
        { model: 'cottage.glb', position: [-10, 0, 5], scale: 1.0 }
    ],
    lighting: {
        sun: { color: 0xffffff, intensity: 1.0, position: [10, 20, 10] },
        ambient: { color: 0x404040, intensity: 0.5 }
    },
    camera: {
        position: [0, 5, 15],
        target: [0, 2, 0]
    }
};

// 3. Renderizar em Three.js
function buildScene(config) {
    const scene = new THREE.Scene();
    const loader = new GLTFLoader();

    // Load assets
    config.assets.forEach(async (asset) => {
        loader.load(asset.model, (gltf) => {
            const model = gltf.scene;
            model.position.set(...asset.position);
            model.scale.set(asset.scale, asset.scale, asset.scale);
            scene.add(model);
        });
    });

    // Setup lighting
    const sun = new THREE.DirectionalLight(
        config.lighting.sun.color,
        config.lighting.sun.intensity
    );
    sun.position.set(...config.lighting.sun.position);
    scene.add(sun);

    const ambient = new THREE.AmbientLight(
        config.lighting.ambient.color,
        config.lighting.ambient.intensity
    );
    scene.add(ambient);

    return scene;
}
```

**Fluxo integrado via plataforma (Arcade.Studio, Spline)**:

1. **Dashboard** → escolher "World Builder"
2. **Asset Generator**: digitar 5 prompts simultâneos
   - "oak tree, detailed bark, full canopy"
   - "large granite rock"
   - "medieval stone cottage"
   - "wild grass and flowers"
   - "fence posts wooden"
3. **Positioning UI**: drag-drop cada ativo no viewport (visto de cima inicialmente)
4. **Lighting**: sliders para sun angle, intensity, ambient color
5. **Render**: captura final em PNG 1080p ou 4K
6. **Export**: JSON (cena) + GLB collection (todos assets) + screenshot

**Batch production workflow**:

```bash
# Script para gerar 10 cenas diferentes
for i in {1..10}; do
  # Prompt variável por cena (seed random)
  BIOME=$([ $((i % 3)) -eq 0 ] && echo "forest" || echo "rocky_plain")
  SEASON=$([ $((i % 2)) -eq 0 ] && echo "autumn" || echo "summer")

  curl -X POST https://arcade.studio/api/world-batch \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
      "assets": [
        "single oak tree in '$BIOME', '$SEASON'",
        "surrounding rocks and stones",
        "grass ground"
      ],
      "style": "game-ready",
      "output_format": "glb"
    }' > "scene_$i.json"
done

# Resultado: 10 cenas completas em 30-60 minutos
```

## Stack e requisitos
- **UI/Platform**: Arcade.Studio, Spline, PlayCanvas (cada com pricing próprio)
- **Backend IA**: Meshy, Tripo 3D, Point-E (para geração paralela)
- **Rendering**: Three.js, WebGL 2
- **Browser**: Chrome/Firefox/Safari modern (WebGL 2)
- **Asset limit**: 20-50 objetos por cena antes de performance drop
- **Tempo cena**: 5-30 min (geração) + 5-10 min (positioning/lighting)
- **Custo geração**: $0.50-2 por asset (Meshy) × número de assets
- **Custo plataforma**: $0 (Arcade free tier) ou $50+/mês (Pro)
- **Output**: JSON cena + GLB bundle + PNG render + GLTF para import

## Armadilhas e limitações
- **Geração em paralelo**: esperar 50 assets ao mesmo tempo é lento (15-30 min). Batch em grupos de 10
- **Posicionamento manual**: UI de drag-drop 3D é fiddly em navegador (considerar voto por teclado)
- **Lighting é trial-and-error**: 3-5 iterações típicas pra ficar bom
- **Asset incompatibilidade**: objetos gerados podem ter escala/topologia inconsistente (árvore huge, cerca tiny)
- **Sem detalhe fino**: não consegue especificar "folhas com textura realista" — tudo é genérico
- **Perf degrada rapidamente**: > 100 objetos = 5-15 FPS no browser
- **Sem animação**: tudo estático (ou animação procedural básica)
- **Exportação limitada**: JSON de cena é proprietário (hard migrar pra Blender/Unreal)
- **Colaboração zero**: tudo local, sem multiuser editing

## Conexões
- [[geracao-3d-com-ia-no-browser]]
- [[asset-pipeline-game-dev]]
- [[three-js-para-desenvolvimento-de-jogos]]
- [[prototipagem-rapida-game-design]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para workflow prático + batch production