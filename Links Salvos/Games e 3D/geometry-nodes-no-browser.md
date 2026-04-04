---
tags: [modelagem-procedural, geometry-nodes, webgpu, node-graph, 3d-web, editor-parametrico]
source: https://x.com/alelepd/status/2036758865170346069?s=20
date: 2026-04-02
tipo: aplicacao
---

# Modelagem 3D Procedural Diretamente no Browser

## O que é
Sistema de node graphs (como Blender's Geometry Nodes) executado no navegador via WebGPU/WebGL. Crie e deforque geometrias 3D de forma não-destrutiva usando programação visual sem instalar Blender.

## Como implementar
**Arquitetura de uma engine de Geometry Nodes web-based**:

1. **Parser visual (frontend)**:
```typescript
// Definir nós em declaração JSON
const nodeGraph = {
  nodes: [
    {
      id: "input_cube",
      type: "Mesh.Primitive",
      params: { shape: "cube", vertices: 8 }
    },
    {
      id: "subdivide",
      type: "Mesh.Subdivide",
      params: { levels: 3 },
      inputs: { mesh: "input_cube.output" }
    },
    {
      id: "twist",
      type: "Geometry.Transform.Twist",
      params: { angle: 45, axis: "Z" },
      inputs: { geometry: "subdivide.output" }
    }
  ]
};

// Renderizar cada nó em tela como caixa visual
const renderer = new NodeGraphRenderer(container, nodeGraph);
renderer.on("nodeParamChange", (nodeId, param) => {
  recompute(nodeGraph);
});
```

2. **Engine de execução (WebGPU)**:
```typescript
// Computar grafo em topological order (DAG)
async function evaluateGraph(graph) {
  const cache = new Map(); // Memoization

  for (let node of topologicalSort(graph.nodes)) {
    const inputMeshes = node.inputs.map(inp =>
      cache.get(inp.nodeId)?.output
    );

    // Executar nó em GPU via compute shader
    const output = await executeNode(node, inputMeshes);
    cache.set(node.id, output);
  }

  return cache.get(graph.outputNode);
}

// Shaders de geometria (exemplo: subdivide)
const subdivideShader = `
@compute @workgroup_size(8)
fn subdivide(@builtin(global_invocation_id) id: vec3u) {
  let triangle_id = id.x;
  if (triangle_id >= triangleCount) { return; }

  // Ler vértices do triângulo original
  let v0 = vertices[triangles[triangle_id].a];
  let v1 = vertices[triangles[triangle_id].b];
  let v2 = vertices[triangles[triangle_id].c];

  // Criar 3 novos vértices no meio das arestas
  let e01 = mix(v0, v1, 0.5);
  let e12 = mix(v1, v2, 0.5);
  let e20 = mix(v2, v0, 0.5);

  // Escrever 4 novos triângulos
  // (v0, e01, e20), (v1, e12, e01), (v2, e20, e12), (e01, e12, e20)
}
`;
```

3. **Exportar resultado**:
```typescript
async function exportToGLB(finalGeometry) {
  const gltf = {
    scene: {
      nodes: [{
        mesh: 0,
        translation: [0, 0, 0],
        rotation: [0, 0, 0, 1]
      }],
      extensions: {}
    },
    meshes: [{
      primitives: [{
        attributes: { POSITION: 0, NORMAL: 1 },
        indices: 2,
        material: 0
      }]
    }],
    materials: [{ pbrMetallicRoughness: { baseColorFactor: [0.8, 0.8, 0.8, 1] } }],
    bufferViews: [ /* geometry data */ ]
  };

  return GLTFExporter.export(gltf);
}
```

**Ferramentas prontas**:
- **Omma.ai**: implementação proprietária, interface web, node picker visual
- **Three.js + CustomNodes**: roll your own com Three.js (template público no GitHub)
- **Spline.design**: web 3D editor com nós paramétricos (não open source)

**Fluxo prático**:
1. Abrir editor no browser (sem download)
2. Drag-and-drop nós: Primitive → Subdivide → Twist → Extrude
3. Ajustar sliders e ver resultados em tempo real (60 FPS em GPU moderna)
4. Export GLB ou JSON do grafo
5. Importar em Godot/Unreal ou guardar JSON para reuso

## Stack e requisitos
- **Browser**: Chrome 113+ ou Firefox 119+ (WebGPU suporte)
- **GPU**: qualquer GPU moderna (NVIDIA, AMD, Intel Arc) — WebGPU é backend agnóstico
- **Dependências típicas**: Three.js, Babylon.js ou custom WebGPU runtime
- **Entrada**: texto (nó picker) ou JSON (grafo importado)
- **Saída**: GLB, JSON (programa), PNG (screenshot)
- **Performance**: 60 FPS para grafos simples (20-30 nós), 15-30 FPS para complexos (100+ nós)
- **Custo**: $0 (open source) ou $10-50/mês (ferramentas comerciais)

## Armadilhas e limitações
- **Latência de compile**: cada ajuste de parâmetro recompila shaders (100-500ms em GPU).  Usar debouncing na UI
- **Erros silenciosos**: compute shaders em WebGPU não têm stack traces legíveis. Usar validation layers agressivas
- **Geometria limite**: máximo 2^31 vértices por buffer. Acima disso, fragmentar em multi-meshes
- **Operações complexas lentas**: operações como remeshing ou suavização Laplaciana são O(n²), inviável em tempo real acima de 100k triângulos
- **Falta de preview rápido**: não há "ocular remota" — tudo renderiza local (BOM para web, ruim para colaboração)
- **Node library limitada**: não tem centenas de nós como Blender. Implementar nó novo = escrever shader
- **UX é minefield**: drag-drop nós é intuitivo mas conexão de pins é fiddly. Exigir testes com usuários reais

## Conexões
- [[procedural-mesh-generation]]
- [[webgpu-3d-graphics]]
- [[shader-graphs-node-system]]
- [[geracao-procedural-de-personagens-e-mapas-isometricos]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com arquitetura técnica + implementação prática