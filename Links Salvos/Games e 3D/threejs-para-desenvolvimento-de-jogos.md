---
tags: [threejs, game-development, web-games, javascript, browser-game]
source: https://x.com/cluckworksgames/status/2038280201008758944?s=20
date: 2026-04-02
tipo: aplicacao
---

# Desenvolver Jogos em Three.js: Setup Browser → Steam

## O que é
Three.js é biblioteca WebGL que permite criar jogos 3D rodando no browser (240+ FPS) e empacotar em `.exe` (Electron) para distribuição via Steam ou desktop.

## Como implementar
**Setup inicial** (Node.js requerido):

```bash
npm create vite@latest my-game -- --template vanilla
cd my-game
npm install three
npm run dev  # localhost:5173 com hot reload
```

**Estrutura básica jogo 3D**:

```javascript
import * as THREE from 'three';

// Cena
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// Geometria + material
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshStandardMaterial({ color: 0x0088ff });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Lighting
const light = new THREE.DirectionalLight(0xffffff, 1);
light.castShadow = true;
scene.add(light);

// Input
const keys = {};
window.addEventListener('keydown', (e) => keys[e.key] = true);
window.addEventListener('keyup', (e) => keys[e.key] = false);

// Game loop
function animate() {
    requestAnimationFrame(animate);

    // Update: movimento controlado por input
    if (keys['w']) cube.position.z -= 0.1;
    if (keys['s']) cube.position.z += 0.1;
    if (keys['a']) cube.position.x -= 0.1;
    if (keys['d']) cube.position.x += 0.1;

    // Render
    renderer.render(scene, camera);
}
animate();

// Responsive
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
```

**Adicionar física** (Cannon.js):

```bash
npm install cannon-es
```

```javascript
import * as CANNON from 'cannon-es';

// Mundo física
const world = new CANNON.World();
world.gravity.set(0, -9.82, 0);

// Corpo físico do cube
const body = new CANNON.Body({ mass: 1 });
const shape = new CANNON.Box(new CANNON.Vec3(0.5, 0.5, 0.5));
body.addShape(shape);
world.addBody(body);

// Sincronizar position do cube com physics body
function animate() {
    world.step(1 / 60);  // 60 fps physics
    cube.position.copy(body.position);
    cube.quaternion.copy(body.quaternion);
    renderer.render(scene, camera);
}
```

**Deploy em 3 caminhos**:

1. **Web (gratuito)**:
```bash
npm run build
# Deploy em Vercel
npm install -g vercel
vercel
# URL: https://my-game.vercel.app/
```

2. **Desktop executável** (Electron):
```bash
npm install electron --save-dev
npx electron-builder
# Resultado: my-game.exe (Windows), .app (Mac), .AppImage (Linux)
```

3. **Steam** (via Electron):
```bash
# 1. Certificado Steamworks ($100 uma vez)
# 2. Build Electron com icone/screenshots
# 3. Upload via Steamworks dashboard
# Resultado: store page listado ao lado de Unity/Unreal games
```

## Stack e requisitos
- **Framework**: Three.js, alternativas: Babylon.js, Cesium.js
- **Física**: Cannon.js (pure JS) ou Rapier (Rust WASM, mais fast)
- **Animação**: Tween.js, glTF animations nativas
- **Rendering**: WebGL 2 (todos browsers modernos) ou WebGPU (Chrome 113+)
- **Build tool**: Vite, Webpack, Parcel (Vite é fastest)
- **Desktop**: Electron (mainstream) ou Tauri (mais leve)
- **Performance**: 240+ FPS em 1080p GPU moderna (RTX 2060+), 30-60 FPS mobile
- **Bundle size**: ~175 KB Three.js, ~50 KB Cannon, total ~400 KB minificado

## Armadilhas e limitações
- **Sem asset pipeline**: não há editor visual. Importar modelos Blender via glTF é manual
- **Shaders em string**: escrever GLSL inline é fiddly (use template literals)
- **Debugging confuso**: threejs errors nem sempre têm stack trace legível
- **Performance gotchas**: geometrias não-instanced causam draw call bloat
- **Mobile performance**: precisa LOD + texture compression (ETC2, ASTC) manual
- **Tamanho arquivo**: build de jogo com 100 assets = 5-10 MB sem otimização
- **Compatibilidade Electron**: precisa webpack/vite config extra (node integration desabilitado)
- **Steam rejeita binaries teste**: não pode fazer builds indefinidas, limite de 10/dia típico
- **Sem editor integrado**: ferramenta visual para designer de níveis tem que vir de fora (Blender export)

## Conexões
- [[webgl-vs-webgpu-rendering]]
- [[physics-simulation-games]]
- [[asset-pipeline-gamedev]]
- [[game-distribution-web-vs-native]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com setup prático + 3 caminhos deploy
