---
tags: [3d, world-model, tempo-real, ia, ambiente]
date: 2026-04-02
tipo: aplicacao
---
# Implementar Mundo Interativo 3D Proceduralmente em Tempo Real

## O que é
Gerar mundos 3D via procedural generation + IA em real-time. Objetos/terreno gerados conforme o usuário explora.

## Como implementar
```javascript
import * as THREE from 'three';
import { Perlin } from 'perlin-noise';

class ProceduralWorld {
    constructor() {
        this.scene = new THREE.Scene();
        this.perlin = new Perlin();
    }
    
    generateTerrain(chunkX, chunkZ) {
        const geometry = new THREE.PlaneGeometry(256, 256, 32, 32);
        const vertices = geometry.attributes.position.array;
        
        for (let i = 0; i < vertices.length; i += 3) {
            const x = vertices[i] + chunkX * 256;
            const z = vertices[i + 2] + chunkZ * 256;
            const height = this.perlin.get(x * 0.01, z * 0.01) * 50;
            vertices[i + 1] = height;
        }
        
        geometry.computeVertexNormals();
        const mesh = new THREE.Mesh(geometry, new THREE.MeshPhong());
        return mesh;
    }
    
    update(playerPos) {
        const chunkX = Math.floor(playerPos.x / 256);
        const chunkZ = Math.floor(playerPos.z / 256);
        
        for (let x = chunkX - 1; x <= chunkX + 1; x++) {
            for (let z = chunkZ - 1; z <= chunkZ + 1; z++) {
                const chunk = this.generateTerrain(x, z);
                this.scene.add(chunk);
            }
        }
    }
}
```

## Stack e requisitos
- Three.js: rendering
- Perlin Noise: geração procedural
- Opcional: Claude para NPCs/narrative

## Histórico
- 2026-04-02: Reescrita
