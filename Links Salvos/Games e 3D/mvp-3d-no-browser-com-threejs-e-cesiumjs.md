---
tags: [threejs, cesiumjs, geospatial, browser-game, weekend-project, vibe-coding]
source: https://x.com/lionmmdx/status/2038354575455830300?s=20
date: 2026-04-02
tipo: aplicacao
---

# Construir Simulador Voo em 48h com Three.js + CesiumJS

## O que é
Combinar Three.js (renderização) + CesiumJS (dados geoespaciais reais) para criar jogo de voo/simulação com terreno real do planeta, rodando inteiramente no browser.

## Como implementar
**Setup**:

```bash
npm create vite@latest flight-sim -- --template vanilla
cd flight-sim
npm install three cesium
npm run dev
```

**Integrar CesiumJS com Three.js**:

```javascript
import * as Cesium from 'cesium';
import * as THREE from 'three';

// Cesium inicializa com dados geoespaciais
const viewer = new Cesium.Viewer('cesium-container', {
    terrainProvider: Cesium.createWorldTerrain()
});

// Three.js para renderização customizada
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 100000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('three-canvas') });

// Converter coordenadas Cesium → Three.js
function cesiumToThreeCoords(cartographic) {
    const cartesian = Cesium.Cartographic.toCartesian(cartographic);
    return new THREE.Vector3(cartesian.x, cartesian.y, cartesian.z);
}

// Posição inicial: São Paulo, Brasil
const initialPosition = new Cesium.Cartographic.fromDegrees(-46.6333, -23.5505, 1000);
const playerPos = cesiumToThreeCoords(initialPosition);

// Avião (geometria simples)
const planeGeometry = new THREE.ConeGeometry(0.5, 2, 4);
const planeMaterial = new THREE.MeshStandardMaterial({ color: 0x1a1a2e });
const plane = new THREE.Mesh(planeGeometry, planeMaterial);
plane.position.copy(playerPos);
scene.add(plane);
```

**Física de voo** (simplificada):

```javascript
import * as CANNON from 'cannon-es';

const world = new CANNON.World();
world.gravity.set(0, -9.82, 0);

// Corpo do avião
const planeBody = new CANNON.Body({ mass: 1 });
const planeShape = new CANNON.Box(new CANNON.Vec3(0.5, 1, 0.5));
planeBody.addShape(planeShape);
world.addBody(planeBody);

// Estado do avião
let thrust = 0;
let pitch = 0;  // -1 a 1
let roll = 0;

// Input
const keys = {};
window.addEventListener('keydown', e => {
    keys[e.key] = true;
    if (e.key === 'w') thrust = Math.min(thrust + 0.1, 1);
    if (e.key === 's') thrust = Math.max(thrust - 0.1, 0);
});
window.addEventListener('keyup', e => keys[e.key] = false);

function updateFlight(delta) {
    // Pitch (nose up/down)
    if (keys['ArrowUp']) pitch = Math.max(pitch - 0.05, -1);
    if (keys['ArrowDown']) pitch = Math.min(pitch + 0.05, 1);
    if (!keys['ArrowUp'] && !keys['ArrowDown']) pitch *= 0.9;  // Damping

    // Roll (left/right)
    if (keys['ArrowLeft']) roll = Math.max(roll - 0.05, -1);
    if (keys['ArrowRight']) roll = Math.min(roll + 0.05, 1);
    if (!keys['ArrowLeft'] && !keys['ArrowRight']) roll *= 0.9;

    // Aplicar forças
    const forward = new CANNON.Vec3(0, 0, -1);
    const forceVector = forward.scale(thrust * 100);
    planeBody.applyForce(forceVector, planeBody.position);

    // Atualizar rotação baseado em pitch/roll
    planeBody.angularVelocity.x = pitch * 2;
    planeBody.angularVelocity.z = roll * 2;
}

function gameLoop(delta) {
    world.step(1 / 60, delta);
    updateFlight(delta);

    // Sincronizar posição avião
    plane.position.copy(planeBody.position);
    plane.quaternion.copy(planeBody.quaternion);

    // Câmera atrás do avião
    const cameraOffset = new THREE.Vector3(0, 1, 5);
    cameraOffset.applyQuaternion(plane.quaternion);
    camera.position.copy(plane.position).add(cameraOffset);
    camera.lookAt(plane.position);

    renderer.render(scene, camera);
}
```

**Deploy**:

```bash
# GitHub Pages (gratuito)
npm run build
# Commit + push para gh-pages branch
# Resultado: https://username.github.io/flight-sim/
```

## Stack e requisitos
- **Frontend**: Three.js (175 KB), CesiumJS (550 KB)
- **Física**: Cannon.js (50 KB) ou Skip (só gravidade básica)
- **Terreno**: Cesium World Terrain (free, tile-based streaming)
- **Gameplay**: ~300 linhas código para MVP
- **Performance**: 60 FPS em 1080p GPU moderna, 30 FPS mobile
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+
- **Deploy**: Vercel (free), GitHub Pages (free), Netlify (free)
- **Tempo desenvolvimento**: 6-12 horas para MVP (48h hardcore)

## Armadilhas e limitações
- **Terreno LOD**: CesiumJS carrega tiles dinamicamente. Lag inicial ao voar pra lugar novo
- **Sem colisão terrain**: avião passa **através** de montanha (só gravidade). Implementar próprio raycast
- **Performance escala**: além de 10km altitude, tile culling quebra, FPS cai
- **Sem multiplayer**: tudo client-side, não há servidor. Colocar múltiplos players requer WebSocket
- **Física simplista**: voo real é 6-DOF com lift/drag. Isso é só "puxar em direção pra frente"
- **Câmera fiddly**: sempre atrás do avião é bom pra gameplay, ruim pra visualização
- **Dados terreno real pode ser impreciso**: altitude pode estar ±50m errada
- **Sem combustível/damage**: MVP é infinito. Adicionar esses mecanicamente após
- **Tamanho bundle**: Three.js + Cesium = ~700 KB inicial, ~1.5 MB com terreno

## Conexões
- [[threejs-para-desenvolvimento-de-jogos]]
- [[physics-simulation-games]]
- [[vibe-coding-rapid-prototyping]]
- [[browser-game-deployment]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com código voo + deployment GitHub Pages
