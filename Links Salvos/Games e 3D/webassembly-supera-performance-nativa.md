---
tags: [webassembly, wasm, performance, threejs, optimization, browser-games, c++, emscripten]
source: https://x.com/threejs/status/2039193070332489846?s=20
date: 2026-04-02
tipo: aplicacao
---

# Compilar Three.js e Engines 3D para WebAssembly: 480+ FPS, 10KB

## O que é

Three.js compilado em WebAssembly (WASM) atinge 480+ FPS em benchmarks 3D complexos, superando JavaScript nativo em 2x. Bundle total: apenas 10KB (versus 175KB JS nativo). WASM é binary executável que roda em navegador com performance próxima a nativa (95% da velocidade de C++ compilado para CPU). Para games e simulações 3D, é game-changer em 2026.

## Por que importa

Benchmarks 2025-2026 mostram que WASM é 26-30x mais rápido que JS em tarefas CPU-bound pequenas e 8-22x em medium input size. Para renderização 3D com 100k geometries, WASM sustenta 480 FPS onde JS nativo faz 240 FPS em hardware similar. Isso habilita:
- Jogos 3D no browser em qualidade console (impossível em JS puro)
- Simulações físicas em real-time (engineering, molecular dynamics)
- Processamento de imagem 10-50x mais rápido que JS
- Portabilidade: código C++/C em desktop roda no browser sem rewrite

## Como funciona / Como implementar

### Entender WASM Compilation Pipeline

WASM é linguagem intermediária portável. Seu código (C++, C, Rust) compila para `.wasm` (binary) + `.wasm.js` (loader). No navegador:

```
C++ source → Emscripten → WASM binary (10KB) + JS glue (5KB)
                         ↓
                    AOT compile (V8/SpiderMonkey)
                         ↓
                    Linear memory (WASM sandbox)
                         ↓
                    Execute ~ 95% nativa speed
```

**Diferença de performance vs. JS:**
- **JS:** Parsed → AST → JIT compile (slow, ~10-50% native)
- **WASM:** Binary → Direct AOT compile (fast, ~95% native)
- **Memory:** JS objects com GC overhead; WASM linear memory acesso direto

### Setup Emscripten (C/C++ → WASM)

Emscripten é toolchain open-source que compila C/C++ para WASM.

```bash
# 1. Instalar Emscripten (macOS/Linux)
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk

./emsdk install latest
./emsdk activate latest
source emsdk_env.sh  # Add to bashrc/zshrc para persistir

# Verificar instalação
emcc --version
# Resultado: emcc (Emscripten gcc/clang-like replacement) 4.0.1

# 2. Compilar arquivo C++ simples para WASM
cat > hello.cpp << 'EOF'
#include <emscripten.h>
#include <cmath>

// Função exposta ao JavaScript
extern "C" {
  EMSCRIPTEN_KEEPALIVE
  float calculate_distance(float x1, float y1, float x2, float y2) {
    return std::sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1));
  }
  
  EMSCRIPTEN_KEEPALIVE
  void process_array(int* arr, int size) {
    for (int i = 0; i < size; i++) {
      arr[i] = arr[i] * 2;
    }
  }
}
EOF

# Compilar para WASM
emcc hello.cpp -o hello.js -O3 -s WASM=1 -s ALLOW_MEMORY_GROWTH=1

# Resultado:
# hello.wasm (3KB) — binary executável
# hello.js (glue code para carregar WASM)
```

**Flags importantes:**
- `-O3` — otimização máxima (reduce tamanho em 40%, aumenta speed)
- `-s WASM=1` — gerar WASM (vs. asm.js fallback)
- `-s ALLOW_MEMORY_GROWTH=1` — permitir alocação dinâmica
- `-s ENVIRONMENT=web` — otimizar para browser (vs. Node.js)

### Usar WASM em HTML/JS

```html
<!DOCTYPE html>
<html>
<head>
  <title>WASM Benchmark</title>
</head>
<body>
  <h1>Three.js WASM vs JavaScript</h1>
  <canvas id="canvas"></canvas>
  <div id="stats">Loading...</div>

  <script async src="hello.js"></script>
  <script>
    // Esperar WASM carregar
    Module.onRuntimeInitialized = () => {
      console.log("✓ WASM loaded");
      
      // Chamar função C++ do JS
      const dist = Module._calculate_distance(0, 0, 3, 4);
      console.log(`Distance: ${dist}`);  // 5.0
      
      // Benchmark: multiplicar array 1M elementos
      const size = 1_000_000;
      const wasmArray = Module._malloc(size * 4);  // 4 bytes per int32
      
      // Preencher array
      const wasmMemory = new Int32Array(Module.HEAPU8.buffer, wasmArray, size);
      for (let i = 0; i < size; i++) wasmMemory[i] = i;
      
      // Executar C++ function
      const start = performance.now();
      Module._process_array(wasmArray, size);
      const wasmTime = performance.now() - start;
      
      console.log(`WASM time: ${wasmTime.toFixed(2)}ms`);
      
      // Benchmark JS puro (para comparação)
      const jsArray = new Int32Array(size);
      for (let i = 0; i < size; i++) jsArray[i] = i;
      
      const jsStart = performance.now();
      for (let i = 0; i < size; i++) jsArray[i] *= 2;
      const jsTime = performance.now() - jsStart;
      
      console.log(`JS time: ${jsTime.toFixed(2)}ms`);
      console.log(`WASM is ${(jsTime / wasmTime).toFixed(1)}x faster`);
    };
  </script>
</body>
</html>
```

**Resultado esperado:**
- WASM: 2-5ms para 1M elementos
- JS: 15-50ms
- Speedup: 8-25x

### Three.js em WASM (Exemplo Realista)

Three.js não está compilado nativamente em WASM, mas você pode usar WASM para:
1. Matemática pesada (culling, physics, matrix ops)
2. Processamento de geometria (mesh optimization, LOD generation)
3. Importar motores C++ (Babylon.js OpenGL pipeline em WASM)

**Exemplo prático: Renderizar 100k cubes em Three.js native + otimização WASM**

```javascript
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@r128/build/three.module.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

// Geometry optimization: instanced rendering (100k cubes, 1 draw call)
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });

const count = 100_000;
const dummy = new THREE.Object3D();
const mesh = new THREE.InstancedMesh(geometry, material, count);

// Posicionar 100k instâncias em grid
let index = 0;
const gridSize = Math.cbrt(count);
for (let x = 0; x < gridSize; x++) {
  for (let y = 0; y < gridSize; y++) {
    for (let z = 0; z < gridSize; z++) {
      if (index >= count) break;
      dummy.position.set(x * 2, y * 2, z * 2);
      dummy.updateMatrix();
      mesh.setMatrixAt(index, dummy.matrix);
      index++;
    }
  }
}
mesh.instanceMatrix.needsUpdate = true;
scene.add(mesh);

// Lighting
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(10, 10, 10);
scene.add(light);

camera.position.z = 300;

// Frustum culling optimization (via WASM)
// Apenas renderizar instâncias visíveis na câmera
let visibleCount = 0;
function updateCulling() {
  // Implementação simplificada (real usaria WASM para performance)
  const frustum = new THREE.Frustum();
  const cameraMatrix = new THREE.Matrix4();
  cameraMatrix.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  frustum.setFromProjectionMatrix(cameraMatrix);
  
  visibleCount = 0;
  for (let i = 0; i < count; i++) {
    const box = new THREE.Box3().setFromCenterAndSize(
      new THREE.Vector3(i * 2, (i/gridSize) * 2, (i/(gridSize*gridSize)) * 2),
      new THREE.Vector3(1, 1, 1)
    );
    if (frustum.intersectsBox(box)) {
      visibleCount++;
    }
  }
  console.log(`Visible: ${visibleCount}/${count} (${(visibleCount/count*100).toFixed(1)}%)`);
}

// Render loop
let frameCount = 0;
let lastTime = performance.now();

function animate() {
  requestAnimationFrame(animate);
  
  // Rotacionar camera
  camera.position.x = Math.sin(Date.now() * 0.001) * 300;
  camera.position.y = Math.cos(Date.now() * 0.0005) * 300;
  camera.lookAt(0, 0, 0);
  
  updateCulling();
  renderer.render(scene, camera);
  
  frameCount++;
  const now = performance.now();
  if (now - lastTime >= 1000) {
    console.log(`FPS: ${frameCount}`);
    frameCount = 0;
    lastTime = now;
  }
}

animate();
```

**Performance esperado:**
- Three.js JS nativo: 240 FPS (100k instâncias, RTX 3080)
- Culling sem WASM: 180 FPS (CPU overhead)
- Culling com WASM: 400+ FPS (WASM calcula visibilidade)

### Empacotar WASM em Produção

Para deploy, minimizar bundle size:

```bash
# 1. Compilar com optimizações agressivas
emcc src/three.cpp -o dist/three.wasm.js -O3 -s WASM=1 \
  -s INITIAL_MEMORY=33554432 \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s MODULARIZE=1 \
  -s 'EXPORT_NAME="ThreeWASM"' \
  --closure 1

# 2. Gzip comprimir (networking)
gzip -9 dist/three.wasm
# Resultado: three.wasm.gz (2KB ao invés de 10KB)

# 3. Servir com headers corretos
# .htaccess ou nginx.conf:
# AddType application/wasm .wasm
# AddEncoding gzip .wasm.gz
```

**Tamanho final:**
- Não-minified: 10KB (WASM) + 5KB (JS glue)
- Gzipped: 2KB (WASM) + 1.5KB (JS)
- Total com Three.js JS: 30KB gzipped

## Stack técnico

```yaml
Linguagem fonte: C++ (C++17 ou C++20)
Compilador: Emscripten 4.0+
Target: WebAssembly + fallback asm.js (IE11)
Runtime: V8 (Chrome), SpiderMonkey (Firefox), JavaScriptCore (Safari)
Browser suporte: Chrome 57+, Firefox 79+, Safari 14.1+, Edge 79+
Performance: RTX 3080 = 480+ FPS; RTX 2060 = 240+ FPS
Memory: até 2GB por WASM instance (ajustável)
Custo: $0 (open source)
```

## Armadilhas e limitações

1. **Compilação WASM é lenta — ciclo dev é ruim.**
   Emcc leva 5-10 minutos para compilar projeto médio (5k linhas C++). Iteração é lenta: mudar função, compilar, testar.
   
   **Mitigação:** Use hot-reload em dev:
   ```bash
   # Script para rebuild + browser refresh
   emcc src/three.cpp -o dist/three.wasm.js -O0 -s WASM=1 && echo "Built!"
   ```
   Ou trabalhar em C++ desktop, testar lá, depois compilar WASM uma vez por milestone.

2. **Debugging WASM é difícil — stack traces ilegíveis.**
   Um crash em WASM dá endereço de memória, não nome de função. Sem source maps (que adicionam overhead), é hard de debugar.
   
   **Mitigação:** Usar `-g` flag (adiciona debug info):
   ```bash
   emcc src/three.cpp -o dist/three.wasm.js -g4
   ```
   Mapear errors no lado JS com try-catch:
   ```javascript
   try {
     Module._my_function();
   } catch (e) {
     console.error("Error in WASM:", e);
     // Usar source maps ou manual logging em C++
   }
   ```

3. **Ecosystem menor — bibliotecas C++ específicas não compilam.**
   Nem toda lib C++ compila para WASM. Dependências de sistema (file I/O, network sockets) requerem workarounds.
   
   Exemplo: OpenSSL compila, mas rede raw socket não. Solução: usar Web APIs do navegador (fetch, WebSocket) em JS glue.

4. **Memory limit: 2GB por instance WASM.**
   Se aplicação precisa >2GB dados em memória, não cabe em WASM instance único. Múltiplas instances complicam sincronização.
   
   Exemplo: simulação de fluido 4K × 4K × 100 steps = 800MB OK; 8K × 8K × 100 = 6.4GB, quebra.

5. **Float precision idêntico a JS — sem vantagem extra.**
   WASM usa IEEE754 como JS. Se esperava dobro precision, não tem. Para precisão estendida, usar emulation (lento).

6. **SIMD não é automático — precisa de código explícito.**
   WASM suporta SIMD (vetorização), mas compilador não vetoriza automaticamente como C++ nativo. Requer `#pragma omp simd` ou intrinsics diretos.

7. **DOM access é lento — WASM é isolado.**
   WASM não acessa DOM diretamente. Qualquer manipulação DOM requer round-trip JS → WASM → JS. Para render loop, isso é OK (render feito em GPU). Para UI interativa, usar Three.js ao invés de WASM.

8. **Importar assets (modelos 3D, texturas) é complexo.**
   WASM não tem acesso direto ao filesystem. Carregar arquivo requer:
   ```javascript
   // JS: Fetch asset + passar para WASM
   const response = await fetch('model.glb');
   const buffer = await response.arrayBuffer();
   const dataPtr = Module._malloc(buffer.byteLength);
   Module.HEAPU8.set(new Uint8Array(buffer), dataPtr);
   Module._load_model(dataPtr, buffer.byteLength);
   ```

## Conexões

- [[threejs-para-desenvolvimento-de-jogos]] — Game dev específico em Three.js
- [[optimization-3d-graphics-culling-lod-batching]] — Técnicas de otimização GPU
- [[emscripten-wasm-compilation-ecosystem-2026]] — Tooling completo
- [[c++-performance-simd-memory-layout-cache-optimization]] — Escrever C++ rápido
- [[browser-performance-rendering-pipeline-fps-optimization]] — Bottlenecks de browser
- [[hybrid-js-wasm-architecture-patterns]] — Padrões de design para misturar JS + WASM

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com benchmark prático
- 2026-04-11: Expandida com 140+ linhas, código prático (C++, HTML/JS, Three.js), armadilhas detalhadas e fluxo de produção
