---
tags: [3d, world-model, tempo-real, ia, ambiente, procedural, generacao]
date: 2026-04-02
tipo: aplicacao
source: https://www.meta.com/blog/worldgen-3d-world-generation-reality-labs-generative-ai-research/
---
# Implementar Mundo Interativo 3D Proceduralmente em Tempo Real

## O que é

Sistema de geração de mundos 3D em tempo real que combina procedural generation clássica com IA moderna. Dois paradigmas convergem em 2025-2026:

1. **Procedural clássico**: Perlin noise, fractals, e algoritmos determinísticos para terreno, vegetação, arquitetura (Minecraft-style, infinitamente escalável)
2. **IA-first (novo)**: Modelos generativos como Meta WorldGen e Google Genie 3 que geram mundos navegáveis a partir de prompts em linguagem natural, com semântica entendida e objetos posicionados inteligentemente

Cores e materiais são gerados via diffusion models, objetos são decompostos por cena (separação automática de foreground/background), e a estrutura inteira é otimizada para renderização em tempo real em game engines.

## Por que importa agora

- **WorldGen (Meta, 2025)**: Transformar texto → mundo interativo com layout inteligente, sem edição manual
- **Genie 3 (Google DeepMind, 2025)**: Primeira world model em tempo real real com 24 FPS, gerando ambientes navegáveis dinamicamente
- **Custo de desenvolvimento**: Cai drasticamente. Antes: artistas 3D passavam semanas criando um mapa. Agora: um prompt e iteração automática.
- **Casos práticos**: Games indie, ambientes VR, datasets de treinamento sintéticos, simuladores para ML, prototipia rápida de level design

## Como funciona / Como implementar

### Abordagem 1: Procedural Clássico (Controle total, menor custo computacional)

```javascript
// Three.js + Perlin Noise para mundo infinito com chunks
import * as THREE from 'three';
import { Perlin } from 'perlin-noise';

class InfiniteProceduralWorld {
    constructor(config = {}) {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
        this.camera.position.set(0, 50, 0);
        
        this.chunkSize = config.chunkSize || 256;
        this.chunkSegments = config.segments || 32;
        this.perlin = new Perlin();
        this.loadedChunks = new Map(); // cache de chunks carregados
        this.chunkLoadDistance = config.loadDistance || 3; // quantos chunks ao redor do player
        
        this.terrainConfig = {
            scale: 0.01,
            heightMultiplier: 50,
            lacunarity: 2.0,
            persistance: 0.55,
            octaves: 6
        };
    }
    
    // Gerar altura em ponto X,Z usando Perlin multi-octave
    getHeightAtPoint(x, z) {
        let height = 0;
        let amplitude = 1;
        let frequency = 1;
        let maxHeight = 0;
        
        for (let i = 0; i < this.terrainConfig.octaves; i++) {
            const sampleX = (x + this.terrainConfig.scale * frequency);
            const sampleZ = (z + this.terrainConfig.scale * frequency);
            const perlinValue = this.perlin.get(sampleX, sampleZ);
            
            height += perlinValue * amplitude;
            maxHeight += amplitude;
            
            amplitude *= this.terrainConfig.persistance;
            frequency *= this.terrainConfig.lacunarity;
        }
        
        return (height / maxHeight) * this.terrainConfig.heightMultiplier;
    }
    
    // Gerar geometria de um chunk (tile do mundo)
    generateTerrainChunk(chunkX, chunkZ) {
        const key = `${chunkX},${chunkZ}`;
        if (this.loadedChunks.has(key)) return this.loadedChunks.get(key);
        
        const geometry = new THREE.PlaneGeometry(
            this.chunkSize,
            this.chunkSize,
            this.chunkSegments,
            this.chunkSegments
        );
        
        const vertices = geometry.attributes.position.array;
        const colors = [];
        
        // Preencher vértices com altura do Perlin
        for (let i = 0; i < vertices.length; i += 3) {
            const localX = vertices[i];
            const localZ = vertices[i + 2];
            const worldX = localX + chunkX * this.chunkSize;
            const worldZ = localZ + chunkZ * this.chunkSize;
            
            const height = this.getHeightAtPoint(worldX, worldZ);
            vertices[i + 1] = height; // Y = altura
            
            // Colorir por altura (verde baixo, marrom alto, neve no pico)
            const colorIndex = i / 3;
            if (height < 20) {
                colors.push(0.2, 0.5, 0.2); // verde (baixada)
            } else if (height < 35) {
                colors.push(0.6, 0.5, 0.3); // marrom (montanha)
            } else {
                colors.push(0.9, 0.9, 0.9); // branco (neve)
            }
        }
        
        geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(colors), 3));
        geometry.computeVertexNormals();
        
        const material = new THREE.MeshPhongMaterial({
            vertexColors: true,
            flatShading: false,
            wireframe: false
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(chunkX * this.chunkSize, 0, chunkZ * this.chunkSize);
        mesh.receiveShadow = true;
        
        this.loadedChunks.set(key, mesh);
        return mesh;
    }
    
    // Update: carregar/descarregar chunks próximos ao player
    updateChunksAroundPlayer(playerPosition) {
        const chunkX = Math.floor(playerPosition.x / this.chunkSize);
        const chunkZ = Math.floor(playerPosition.z / this.chunkSize);
        
        const chunksToLoad = [];
        const chunksToRemove = [];
        
        // Determinar chunks que devem estar carregados
        for (let x = chunkX - this.chunkLoadDistance; x <= chunkX + this.chunkLoadDistance; x++) {
            for (let z = chunkZ - this.chunkLoadDistance; z <= chunkZ + this.chunkLoadDistance; z++) {
                const key = `${x},${z}`;
                if (!this.loadedChunks.has(key)) {
                    chunksToLoad.push([x, z]);
                }
            }
        }
        
        // Descarregar chunks distantes
        for (const [key, mesh] of this.loadedChunks) {
            const [x, z] = key.split(',').map(Number);
            if (Math.abs(x - chunkX) > this.chunkLoadDistance || 
                Math.abs(z - chunkZ) > this.chunkLoadDistance) {
                this.scene.remove(mesh);
                this.loadedChunks.delete(key);
            }
        }
        
        // Carregar novos chunks
        for (const [x, z] of chunksToLoad) {
            const mesh = this.generateTerrainChunk(x, z);
            this.scene.add(mesh);
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        // Simular movimento do player (normalmente controlado por input)
        this.camera.position.x += 0.1;
        this.updateChunksAroundPlayer(this.camera.position);
        
        this.renderer.render(this.scene, this.camera);
    }
}

// Uso
const world = new InfiniteProceduralWorld({
    chunkSize: 256,
    segments: 32,
    loadDistance: 3
});
world.animate();
```

### Abordagem 2: IA-First com WorldGen API (Menos controle, máxima qualidade)

```python
# Pseudocódigo para chamar Meta WorldGen ou similar via API
import requests
import json

class AIWorldGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.worldgen.meta.com/v1"
    
    def generate_world(self, prompt: str, style: str = "photorealistic"):
        """
        Gerar mundo a partir de prompt de texto
        Retorna arquivo .gltf com meshes, texturas e semântica
        """
        payload = {
            "prompt": prompt,
            "style": style,  # photorealistic, stylized, cartoon, etc
            "resolution": 1080,
            "seed": None,  # None para aleatório
            "num_frames": 1  # para animação, >1
        }
        
        response = requests.post(
            f"{self.base_url}/generate",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        world_data = response.json()
        # world_data contém:
        # - gltf_url: link para download do modelo 3D
        # - objects: lista de objetos semânticos identificados
        # - layout: posições e rotações
        # - metadata: tempo de geração, tokens usados
        
        return world_data
    
    def edit_world(self, world_id: str, edit_prompt: str):
        """
        Editar mundo existente via prompt (ex: "adicionar uma ponte")
        """
        payload = {
            "world_id": world_id,
            "edit": edit_prompt,
            "preserve_existing": True
        }
        
        response = requests.post(
            f"{self.base_url}/edit",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        return response.json()

# Uso
generator = AIWorldGenerator(api_key="your-key")

# Gerar mundo a partir de descrição
world = generator.generate_world(
    prompt="Um vale montanhoso com castelo medieval no topo, rio atravessando, floresta ao fundo",
    style="photorealistic"
)

print(f"Mundo gerado: {world['gltf_url']}")
print(f"Objetos identificados: {world['objects']}")

# Editar mundo
edited = generator.edit_world(
    world_id=world['id'],
    edit_prompt="Adicionar uma aldeia com casas de pedra perto do rio"
)
```

### Abordagem 3: Hybrid (Procedural + IA para detalhe)

```python
# Combinação: gerar estrutura proceduralmente, depois usar IA para textura/detalhe
import numpy as np
from PIL import Image
import requests

class HybridWorldPipeline:
    def __init__(self):
        self.height_map = None
        self.semantic_map = None
    
    def generate_height_map(self, width=512, height=512):
        """Gerar mapa de altura proceduralmente"""
        from scipy.ndimage import gaussian_filter
        
        # Perlin noise base
        x = np.linspace(0, 4, width)
        y = np.linspace(0, 4, height)
        X, Y = np.meshgrid(x, y)
        
        # Simular Perlin com várias frequências
        height_map = np.sin(X) * np.cos(Y)
        height_map = gaussian_filter(height_map, sigma=10)
        
        # Normalizar
        self.height_map = (height_map - height_map.min()) / (height_map.max() - height_map.min())
        return self.height_map
    
    def generate_semantic_map(self, height_map):
        """Classificar regiões por tipo (água, terra, montanha, etc)"""
        semantic = np.zeros_like(height_map, dtype=int)
        semantic[height_map < 0.3] = 0  # água
        semantic[(height_map >= 0.3) & (height_map < 0.6)] = 1  # terra
        semantic[height_map >= 0.6] = 2  # montanha
        
        self.semantic_map = semantic
        return semantic
    
    def ai_texture_generation(self, region_type: int, seed=None):
        """Usar stable diffusion ou similar para gerar texturas por região"""
        prompts = {
            0: "realistic water texture, ripples, depth",
            1: "grass field texture, green, detailed",
            2: "rocky mountain texture, gray stone, snow patches"
        }
        
        # Chamar API de imagem (ex: Replicate, local Stable Diffusion)
        # Retorna tensor de textura para aplicar no mesh
        texture_prompt = prompts.get(region_type, "generic terrain")
        
        # Pseudocódigo
        texture = generate_image_from_prompt(
            prompt=texture_prompt,
            size=512,
            seed=seed
        )
        
        return texture

# Uso
pipeline = HybridWorldPipeline()
height_map = pipeline.generate_height_map(width=512, height=512)
semantic = pipeline.generate_semantic_map(height_map)

# Gerar textura IA para cada região
water_texture = pipeline.ai_texture_generation(region_type=0)
grass_texture = pipeline.ai_texture_generation(region_type=1)
mountain_texture = pipeline.ai_texture_generation(region_type=2)
```

## Stack técnico

### Renderização
- **Three.js** / **Babylon.js**: WebGL, fácil integração
- **Unreal Engine 5** / **Unity**: Para games completos com física
- **WebGPU**: Renderização de próxima geração (2026+), 10x mais rápido que WebGL

### Geração Procedural
- **Perlin Noise / Simplex Noise**: clássico para terreno
- **FastNoise2**: versão otimizada, suporta GPU
- **Grendel-GS**: distribuição multi-GPU para cenas enormes (ICLR 2025)

### IA (Text-to-World)
- **Meta WorldGen API**: end-to-end text → mundo interativo
- **Google Genie 3**: world model em tempo real (24 FPS)
- **Stable Diffusion XL** (local): texturização, detalhe visual
- **Claude API com vision**: análise de imagens, gerar layout semântico

### Infraestrutura
- **Node.js / Python**: Backend para geração e cache
- **Redis**: cache de chunks já gerados
- **WebSocket**: para streaming de mundo em multiplayer

### Hardware
- **GPU**: NVIDIA RTX 3080+ recomendado para otimização em tempo real
- **RAM**: 16GB+ para mundos grandes (1000+ chunks)

## Código prático: Sistema de Cache com LRU

```python
from collections import OrderedDict
import hashlib

class ChunkCache:
    """Cache inteligente de chunks para evitar regeneração"""
    
    def __init__(self, max_chunks=128):
        self.cache = OrderedDict()
        self.max_chunks = max_chunks
    
    def get_or_generate(self, chunk_coords, generator_func):
        """Obter chunk do cache ou gerar e cachear"""
        key = self._hash_coords(chunk_coords)
        
        if key in self.cache:
            # Mover para fim (LRU - least recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        
        # Gerar novo
        chunk = generator_func(chunk_coords)
        self.cache[key] = chunk
        
        # Remover chunk mais antigo se excedeu limite
        if len(self.cache) > self.max_chunks:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            print(f"[CACHE] Chunk {oldest_key} removido (LRU)")
        
        return chunk
    
    def _hash_coords(self, coords):
        """Hash consistente para coordenadas"""
        coord_str = f"{coords[0]},{coords[1]}"
        return hashlib.md5(coord_str.encode()).hexdigest()[:8]
    
    def stats(self):
        return {
            "cached_chunks": len(self.cache),
            "max_capacity": self.max_chunks,
            "memory_kb": sum(len(str(c)) for c in self.cache.values()) // 1024
        }

# Uso
cache = ChunkCache(max_chunks=64)

def expensive_generation(chunk_coords):
    # Simular geração cara (Perlin, IA, etc)
    import time
    time.sleep(0.5)
    return {"mesh": "geometry_data", "textures": "texture_data"}

chunk = cache.get_or_generate((10, 20), expensive_generation)
chunk = cache.get_or_generate((10, 20), expensive_generation)  # Cache hit
print(cache.stats())
```

## Armadilhas e Limitações

### 1. **Perlin Noise tem padrão visual repetitivo**
- Problema: Paisagens ficam com "azulejo" visível a distância
- Solução: Usar Simplex Noise ou combinar múltiplas oitavas com diferentes frequências (fBm - fractional Brownian motion)
- Código: Usar biblioteca `FastNoise2` que oferece falloff automático

### 2. **Overhead de geração IA é caro em latência**
- Problema: Chamar WorldGen API para cada chunk = latência 2-5s por chunk
- Solução: Gerar proceduralmente em tempo real, chamar IA apenas para áreas críticas (30m ao redor do player)
- Estratégia: Pre-compute 1-2 chunks à frente enquanto player se move

### 3. **Mudanças drásticas entre procedural e IA quebram consistência**
- Problema: Seams visíveis entre mundo procedural e mundo gerado por IA
- Solução: Manter um "mapa semântico" global que guie ambas gerações. WorldGen já faz isso; para procedural, use um segundo mapa que classifica regiões (floresta, montanha, água) e respeite essa estrutura

### 4. **Scaling infinito requer gerenciamento agressivo de memoria**
- Problema: Cache de chunks crescer indefinidamente
- Solução: LRU cache com limite hard (64-256 chunks). Chunks não usados são serializados em disco (SQLite) e recarregados on-demand

### 5. **IA pode gerar layouts não navegáveis**
- Problema: WorldGen gera uma rua que acaba em parede, ponte sem destino
- Solução: Post-process o grafo de navegação com algoritmo A*, validar conectividade antes de retornar ao player. Implementar restrições ("garanta que todas as portas são alcançáveis")

### 6. **Mudanças em tempo real quebram determinismo**
- Problema: Usuário muda seed ou parâmetros → mundo inteiro regenera, player cai pelo chão
- Solução: Versionar mundos. Guardar versão do algo de geração + seed em cada chunk. Se versão mudar, usar procedural fallback

## Conexões

- [[neural-rendering-nerf-vs-3dgs]] - Renderização neural vs splatting
- [[captura-3d-estrutura-movimento]] - Fundo: como gerar pose de câmera para IA
- [[geracao-3d-com-ia-no-browser]] - APIs de geração 3D modernas
- [[game-engine-unreal-vs-unity-2025]] - Engines para renderizar mundos
- [[Claude Code - Melhores Práticas]] - Automação com IA para worldgen
- [[agent-router-model]] - Rotear gerações simples vs complexas

## Histórico

- 2026-04-02: Nota original com exemplo Three.js básico
- 2026-04-11: Reescrita expandida com Meta WorldGen, Genie 3, hybrid pipeline, cache system, 5+ armadilhas
