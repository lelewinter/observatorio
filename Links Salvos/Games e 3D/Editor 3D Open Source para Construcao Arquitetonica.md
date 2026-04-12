---
date: 2026-03-23
tags: [3d-editor, open-source, webgpu, react-three-fiber, architecture, browser, csg, bvh]
source: https://github.com/pascalorg/editor
author: Pascal Editor Team
tipo: aplicacao
---

# Pascal Editor: Editor 3D Profissional, Grátis, No Browser (WebGPU)

## O que é
Pascal Editor é um **editor 3D completo em browser** para arquitetura e design de interiores, construído com **React Three Fiber** e **WebGPU**. Oferece funcionalidades que rivalizavam com Blender/Revit há poucos anos, mas roda *sem instalação, grátis e offline*.

Não é demo — é um *editor de produção* com: paredes, lajes, tetos, telhados, janelas, portas, operações booleanas em tempo real (CSG), instanced rendering para milhões de polígonos, undo/redo ilimitado, e export em GLTF/GLB.

## Por que importa agora
- **Sem licença paga:** Revit custa $2-5K/ano. Blender é grátis mas pesado. Pascal no browser = zero barreira
- **WebGPU é future:** Acesso direto ao GPU sem WebGL overhead. Performance bate desktop para arquitetura
- **Open source + monorepo:** Stack modular (@pascal/core, @pascal/viewer, @pascal/editor) permite fork e extensão
- **Colaboração mesh:** Histórico local via IndexedDB + JSON export facilita versionamento Git de projetos
- **Power user pronto:** Drag-drop é intuitivo, mas atalhos de teclado para profissionais (tipo Blender)

## Como funciona / Como implementar

### 1. Acesso e interface básica
**URL direto:** https://pascaleditor.org/ — abre no navegador sem signup

**Workflow básico:**
```
1. Criar novo projeto (localStorage persiste automaticamente)
2. Grid snapping ativado por padrão (alinha objetos)
3. Camera: Botão direito + drag = orbitar
4. Shift + scroll = zoom
5. Criar objetos: Menu Tools ou atalhos (W=wall, D=door, etc)
```

### 2. Stack técnico por camada

**Frontend:**
```
┌─ React (UI Components)
├─ React Three Fiber (Renderer abstraction over Three.js)
│  └─ WebGPU Backend (Chrome 113+, Edge 113+)
└─ Zustand ou Redux (State management de scenes)
```

**Rendering Pipeline:**
```
Node Schemas (dados) 
    ↓ (Turborepo @pascal-app/core)
State Management (Zustand)
    ↓ (camera, objects, materials)
React Three Fiber + WebGPU
    ↓ (Command buffers GPU)
Instanced Rendering + BVH
    ↓
60 FPS output (1M+ polygons)
```

**Engine CSG (Constructive Solid Geometry):**
- BVH acceleration (Bounding Volume Hierarchy)
- Boolean operations (union, subtract, intersect)
- Real-time preview vs final render
- Handles coplanar geometries sem z-fighting

**Storage:**
- IndexedDB para projetos (estrutura: scenes, objects, history)
- JSON export para versionamento Git
- PNG export para viewport snapshots

### 3. Arquitetura do monorepo

```
pascalorg/editor/
├── packages/
│   ├── @pascal-app/core/          ← Node schemas, systems
│   │   ├── src/nodes/             ← Wall, Slab, Roof, Door, Window
│   │   ├── src/systems/           ← Physics, CSG, Boolean ops
│   │   └── src/state/             ← Zustand store
│   └── @pascal-app/viewer/        ← React Three Fiber + WebGPU
│       ├── src/components/        ← 3D mesh renderers
│       └── src/effects/           ← Post-processing, shadows
├── apps/
│   └── editor/                    ← UI + Canvas integration
└── Turborepo config               ← Monorepo orchestration
```

### 4. Exemplo: Criar uma parede programaticamente

```javascript
// Usando @pascal-app/core (estrutura de dados)
import { createWallNode, addToScene } from '@pascal-app/core';

const wall = createWallNode({
  start: { x: 0, y: 0, z: 0 },
  end: { x: 5, y: 0, z: 0 },     // 5m de comprimento
  height: 3,                       // 3m altura
  thickness: 0.2,                  // 20cm espessura
  material: 'concrete'
});

// Renderizar via React Three Fiber
function WallMesh({ nodeId }) {
  const wallData = useSceneStore(state => 
    state.getNode(nodeId)
  );
  
  return (
    <mesh position={wallData.position}>
      <boxGeometry 
        args={[wallData.thickness, wallData.height, wallData.length]}
      />
      <meshStandardMaterial color="white" />
    </mesh>
  );
}
```

### 5. Export e integração com engines

```javascript
// Exportar para Babylon.js, Three.js ou Unreal
async function exportProject(format = 'gltf') {
  const scenes = useSceneStore.getState().getAllScenes();
  
  const gltf = await exportToGLTF(scenes);
  // ou: exportToBabylon(), exportToUSDZ()
  
  // Fazer download
  const blob = new Blob([gltf], { type: 'model/gltf+json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'my-project.gltf';
  a.click();
}
```

## Stack técnico completo
- **Rendering:** WebGPU (não WebGL) — acesso direto GPU
- **React framework:** React Three Fiber (abstraction layer)
- **3D Math:** Three.js (vetores, matrizes, quaternions)
- **State:** Zustand (lightweight, reactive)
- **Geometry:** BVH + CSG (boolean ops in real-time)
- **Storage:** IndexedDB (offline-first)
- **Monorepo:** Turborepo + pnpm workspaces
- **Build:** Vite ou webpack (fast HMR)
- **CI/CD:** GitHub Actions para testes + deploy
- **Browser support:** Chrome 113+, Edge 113+, Firefox experimental

## Código prático: Setup local

```bash
# 1. Clonar e instalar
git clone https://github.com/pascalorg/editor.git
cd editor
pnpm install

# 2. Modo dev (HMR ativado)
pnpm dev
# Abre em http://localhost:5173

# 3. Build para produção
pnpm build
# Outputs: dist/

# 4. Rodar testes (E2E + unit)
pnpm test

# 5. Contribuir
# - Adicionar novo tipo de objeto? Edite: packages/@pascal-app/core/src/nodes/
# - Novo efeito visual? Edite: packages/@pascal-app/viewer/src/effects/
```

### Estender com custom node

```typescript
// Adicionar novo tipo de objeto (ex: escada)
// File: packages/@pascal-app/core/src/nodes/StairNode.ts

import { Node } from './Node';

export interface StairData extends Node {
  type: 'stair';
  steps: number;
  height: number;
  width: number;
  riserHeight: number;
}

export function createStairNode(data: Partial<StairData>): StairData {
  return {
    id: crypto.randomUUID(),
    type: 'stair',
    steps: data.steps || 10,
    height: data.height || 3,
    width: data.width || 1,
    riserHeight: (data.height || 3) / (data.steps || 10),
    position: data.position || [0, 0, 0]
  };
}

// Renderizar no React Three Fiber
export function StairMesh({ node }: { node: StairData }) {
  return (
    <group position={node.position}>
      {Array.from({ length: node.steps }).map((_, i) => (
        <mesh key={i} position={[0, i * node.riserHeight, 0]}>
          <boxGeometry 
            args={[node.width, node.riserHeight * 0.1, 0.3]}
          />
          <meshStandardMaterial color="#8B7355" />
        </mesh>
      ))}
    </group>
  );
}
```

## Armadilhas e limitações

### 1. **WebGPU ainda é experimental**
Chrome/Edge suportam, mas Firefox está em beta. Safari não tem previsão. Se cliente usa Safari = não funciona. Fallback para WebGL é limitado em performance.

**Solução:** Testar em navegador alvo antes de confiar. Manter WebGL fallback por 2 anos.

### 2. **IndexedDB tem limite de quota**
Browser limita armazenamento local a ~50MB (Chrome) ou ~600MB (Edge). Projeto arquitetônico com texturas 4K pode exceeder.

```javascript
// Verificar quota disponível
navigator.storage.estimate().then(estimate => {
  const percentUsed = (estimate.usage / estimate.quota) * 100;
  console.log(`Espaço usado: ${percentUsed}%`);
  if (percentUsed > 80) {
    alert('Quase sem espaço. Exporte seu projeto!');
  }
});
```

### 3. **Sem colaboração real-time nativa**
Pascal é offline-first. Se 2 pessoas editam mesmo arquivo JSON git simultaneamente, conflito manual. Não há CRDT (Conflict-free Replicated Data Types) built-in.

**Workaround:** Usar CRDT library como Yjs + WebSocket (fora do escopo Pascal).

### 4. **Performance degrada com cenas muito grandes**
Instanced rendering ajuda (60 FPS com 1M polígonos), mas se você tem 10M polígonos + simulação physics, LLM vai falhar. Blender/Revit são melhores para projetos gigantescos.

**Sweet spot:** Até ~5M polígonos (apartamentos, casas, pequenos edifícios).

### 5. **Export GLTF pode perder informações**
Metadados arquitetônicos (tipo parede, espessura, material estrutural) não mapeiam perfeitamente para GLTF. Ao reimportar, você perde contexto arquitetônico.

**Solução:** Exportar *também* em JSON proprietário (inclui metadata), não só GLTF.

### 6. **Sem snapshots tipo Blender**
History via undo/redo é infinita, mas snapshots nomeados (ex: "v1.0-approved", "v1.1-client-feedback") não existem nativamente. Precisa fazer isso via Git.

## Conexões
- [[WebGPU e Future da Renderização Web]]
- [[Three.js e React Three Fiber Deep Dive]]
- [[Arquitetura em 3D para Não-Arquitetos]]
- [[Open Source Blender Alternatives]]
- [[Colaboração em 3D com CRDT (Yjs)]]
- [[Exportar 3D para Game Engines (Godot, Unity)]]

## Histórico
- 2026-03-23: Nota original
- 2026-04-11: Reescrita com arquitetura técnica, código prático, monorepo details e 6 armadilhas
