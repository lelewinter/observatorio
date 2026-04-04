---
tags: [webgpu, grass-simulation, compute-shader, rendering, browser-3d]
source: https://x.com/omma_ai/status/2036675595623621032?s=20
date: 2026-04-02
tipo: aplicacao
---

# Renderizar Grama 3D em Tempo Real via WebGPU

## O que é
WebGPU permite simulação de milhões de fios de grama interativos no browser via compute shaders. Grama reage a colisão com objetos (ex: esfera) em tempo real, 60+ FPS.

## Como implementar
**Requisitos WebGPU** (Chrome 113+, Edge 113+):

```javascript
// Detectar suporte
async function initWebGPU() {
    if (!navigator.gpu) {
        console.error('WebGPU não suportado');
        return false;
    }

    const adapter = await navigator.gpu.requestAdapter();
    const device = await adapter.requestDevice();
    const canvas = document.querySelector('canvas');
    const context = canvas.getContext('webgpu');

    context.configure({
        device: device,
        format: navigator.gpu.getPreferredCanvasFormat()
    });

    return { device, context, canvas };
}
```

**Grass Shader** (WGSL - WebGPU Shading Language):

```wgsl
// Compute shader para simular grama
@group(0) @binding(0) var<storage, read_write> grass_positions : array<vec4f>;
@group(0) @binding(1) var<uniform> sphere_pos : vec3f;
@group(0) @binding(2) var<uniform> sphere_radius : f32;

@compute @workgroup_size(256)
fn compute_grass(@builtin(global_invocation_id) id : vec3u) {
    let i = id.x;
    if (i >= arrayLength(&grass_positions)) { return; }

    var pos = grass_positions[i].xyz;
    let origin = grass_positions[i].w;  // Base Y

    // Distância da esfera
    let dist = distance(pos, sphere_pos);

    // Se colidir com esfera, desviar
    if (dist < sphere_radius) {
        let push_dir = normalize(pos - sphere_pos);
        pos += push_dir * (sphere_radius - dist) * 0.5;
    }

    // Gravidade: volta pra base
    let target = vec3f(pos.x, origin, pos.z);
    pos = mix(pos, target, 0.1);  // Interpolar 10% a cada frame

    // Wind: movimento senoidal
    let wind = sin(pos.x * 0.1 + global_time) * 0.05;
    pos.x += wind;

    grass_positions[i] = vec4f(pos, origin);
}
```

**Render Pipeline**:

```javascript
// Estrutura: cada fio é instância de uma geometria simple (quad ou cilindro)
const grassGeometry = new geometry(vertices, indices);  // 4 verts per grass blade

const grassBuffer = device.createBuffer({
    size: num_grass * 4 * 4,  // num_grass * vec4
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
    mappedAtCreation: true
});

// Escrever posições inicias da grama
const positions = new Float32Array(grassBuffer.getMappedRange());
for (let i = 0; i < num_grass; i++) {
    positions[i * 4] = Math.random() * 100 - 50;      // x
    positions[i * 4 + 1] = 0;                          // y (base)
    positions[i * 4 + 2] = Math.random() * 100 - 50;  // z
    positions[i * 4 + 3] = 0;                          // y base (store pra referência)
}
grassBuffer.unmap();

// Bind group para compute shader
const computeBindGroup = device.createBindGroup({
    layout: computePipeline.getBindGroupLayout(0),
    entries: [
        { binding: 0, resource: { buffer: grassBuffer } },
        { binding: 1, resource: { buffer: spherePosBuffer } },
        { binding: 2, resource: { buffer: sphereRadiusBuffer } }
    ]
});

// Render loop
function frame() {
    // Compute: atualizar grama
    const computePass = commandEncoder.beginComputePass();
    computePass.setPipeline(computePipeline);
    computePass.setBindGroup(0, computeBindGroup);
    computePass.dispatchWorkgroups(Math.ceil(num_grass / 256));
    computePass.end();

    // Render: desenhar grama
    const renderPass = commandEncoder.beginRenderPass(renderPassDescriptor);
    renderPass.setPipeline(renderPipeline);
    renderPass.setBindGroup(0, renderBindGroup);
    renderPass.draw(grassGeometry.vertices.length, num_grass);
    renderPass.end();

    device.queue.submit([commandEncoder.finish()]);
}
```

**Interatividade** (controlar esfera via input):

```javascript
const keys = {};
window.addEventListener('keydown', e => keys[e.key] = true);
window.addEventListener('keyup', e => keys[e.key] = false);

let spherePos = new Float32Array([0, 2, 0]);

function update() {
    if (keys['w']) spherePos[2] -= 0.1;
    if (keys['s']) spherePos[2] += 0.1;
    if (keys['a']) spherePos[0] -= 0.1;
    if (keys['d']) spherePos[0] += 0.1;

    // Upload nova posição para GPU
    device.queue.writeBuffer(spherePosBuffer, 0, spherePos);
}
```

## Stack e requisitos
- **Browser**: Chrome 113+, Edge 113+, Firefox 128+ (experimental)
- **GPU**: qualquer GPU moderna (NVIDIA, AMD, Intel Arc)
- **Input**: WebGPU API (nativa, sem libraria)
- **Num grass**: 100k-1M fios dependendo GPU
- **Performance**: 60+ FPS em 1080p com 500k grama (RTX 3080)
- **Custo**: $0 (WebGPU open standard)
- **Alternativa older**: usar WebGL compute via texture (mais lento, ~30 FPS)

## Armadilhas e limitações
- **Browser support restrito**: apenas Chrome/Edge/Firefox experimental (Feb 2026)
- **WebGPU ainda instável**: API pode mudar, código quebra com updates Chrome
- **Debugging shader** é difícil: error messages são genéricos
- **Memory limit**: máximo ~2GB buffer, limite de 1M instâncias típico
- **Mobile WebGPU**: não suportado ainda (Fevereiro 2026), use WebGL fallback
- **Physics fakes**: colisão grama-esfera é aproximação (push only), sem rotação realista
- **Vento/movimento**: senoidal é simplificação, grama real tem Perlin noise 3D (mais caro)
- **Texturing grass**: samplear texture por instância é custoso, bake color in vertex
- **Número de fios visual**: 500k fios parece denso, mas real grama tem bilhões
- **Interactivity lag**: delay entre move esfera e resposta grama = com 1M instances pode ter 50ms lag

## Conexões
- [[compute-shader-gpu-programming]]
- [[webgpu-graphics-api]]
- [[physics-simulation-games]]
- [[real-time-rendering-optimization]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com implementação WGSL completa
