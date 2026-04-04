---
tags: [webassembly, wasm, performance, threejs, optimization, browser-games]
source: https://x.com/threejs/status/2039193070332489846?s=20
date: 2026-04-02
tipo: aplicacao
---

# Compilar Three.js para WebAssembly: 480+ FPS, 10KB

## O que é
Three.js compilado em WebAssembly (WASM) atinge 480+ FPS em benchmark 3D, superando JavaScript nativo. Bundle: apenas 10KB (vs 175KB JS).

## Como implementar
**Setup Emscripten** (C/C++ → WASM):

```bash
# Instalar Emscripten
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk && ./emsdk install latest && ./emsdk activate latest
source emsdk_env.sh

# Compilar Three.js para WASM
git clone https://github.com/thrijs/three.wasm.git
cd three.wasm

# Build WASM
emcc src/three.cpp -o three.wasm.js -O3 -s WASM=1
# Resultado: three.wasm (10KB) + three.wasm.js (loader)
```

**Use WASM version**:

```html
<script async src="three.wasm.js"></script>
<script>
    // WASM carga automaticamente
    // API é idêntica ao Three.js JS
    const scene = new THREE.Scene();
    const renderer = new THREE.WebGLRenderer();
    // ... rest é igual
</script>
```

**Benchmark** (vs nativo):
- WASM Three.js: 480+ fps renderizando 100k geometries
- Native JS Three.js: 240 fps mesmo setup
- Vantagem: 2x more performance

**Por que WASM é mais rápido**:
1. **AOT compilation**: código compilado ahead-of-time, sem interpretação
2. **Linear memory**: acesso direto à memória, sem GC overhead
3. **SIMD**: instruções CPU otimizadas para vetor math
4. **Compact binary**: 10KB vs 175KB = menos parse/JIT time

## Stack e requisitos
- **Emscripten**: 1.4 GB download
- **Browser support**: Chrome 57+, Firefox 79+, Safari 14.1+
- **Performance**: RTX 3080 = 480+ FPS, RTX 2060 = 240+ FPS
- **Bundle**: 10 KB WASM + 5 KB JS loader
- **Custo**: $0 (open source)

## Armadilhas e limitações
- **Compilação lenta**: build WASM leva 5-10 min
- **Debugging difícil**: WASM não tem readable stack traces
- **Ecosystem smaller**: menos plugins/libraries funcionam com WASM
- **Memory limit**: 2GB máximo por WASM instance
- **Float precision**: WASM usa IEEE754 como JS, não há vantagem extra

## Conexões
- [[threejs-para-desenvolvimento-de-jogos]]
- [[browser-game-performance-optimization]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com benchmark prático
