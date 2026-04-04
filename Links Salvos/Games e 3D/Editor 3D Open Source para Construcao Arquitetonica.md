---
date: 2026-03-23
tags: [3d-editor, open-source, webgpu, react-three-fiber, architecture, browser]
source: https://x.com/EHuanglu/status/2035783372463652970?s=20
tipo: aplicacao
---

# Pascal Editor: Editor 3D Profissional, Grátis, No Browser

## O que é
Editor 3D completo (tipo Blender) rodando inteiramente no navegador via WebGPU. Criar cenas arquitetônicas, desenhar geometria, undo/redo completo, dados salvos localmente.

## Como implementar
**Acesso**: https://pascalw.me (abre direto, zero instalação)

**Use intuitivo**: drag-drop para criar objetos, grid para alinhamento, câmera 3D controlada por mouse/teclado

**Exportar**: models em GLTF/GLB para usar em game engines

## Stack e requisitos
- **Browser**: Chrome 113+, Edge 113+ (WebGPU suport)
- **Framework**: React Three Fiber + WebGPU
- **Storage**: IndexedDB (browser local)
- **Custo**: $0
- **Performance**: 60 FPS em GPU moderna

## Armadilhas e limitações
- **Browser-only**: sem desktop app robustez
- **Sem colaboração**: offline-first, sem multiuser
- **Modelos simples**: complexidade menor que Blender
- **WebGPU ainda instável**: Chrome updates podem quebrar

## Conexões
- [[webgpu-3d-graphics]]
- [[open-source-3d-tools]]

## Histórico
- 2026-03-23: Nota original
- 2026-04-02: Reescrita para quick reference
