---
tags: [ia-animation, text-to-animation, crowd-simulation, gamedev, procedural-animation, gltf]
source: https://x.com/MagicMotionAI/status/2037247276024758392?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Múltiplas Variações de Animação em Lote

## O que é
Pipeline que cria dezenas de variações de movimento de personagens a partir de um prompt único, empacotando tudo em um arquivo GLTF/GLB com múltiplas animation clips. Essencial para sistemas de multidão e NPC com variedade visual.

## Como implementar
**Ferramentas recomendadas**:
- **Mixamo**: interface web, geração por prompt + motion capture, export FBX/GLTF (melhor qualidade, pago)
- **Motion Labs**: specializado em crowd, desconto para batch
- **Descript Motionpipe**: local Python, open source (experimental)

**Fluxo com API (genérico)**:

1. **Preparar requisição de geração**:
```bash
curl -X POST https://api.motiongen.ai/v1/generate-batch \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "pedestrians walking in different paces and directions",
    "character_rig": "humanoid_biped",
    "num_variations": 15,
    "duration_sec": 4.0,
    "loop_friendly": true,
    "export_format": "gltf"
  }'

# Resposta: {"job_id": "xyz", "status": "queued"}
```

2. **Pooling e download**:
```python
import requests
import time

def wait_for_animations(job_id):
    while True:
        resp = requests.get(f"https://api.motiongen.ai/v1/jobs/{job_id}",
                            headers={"Authorization": f"Bearer {API_KEY}"})
        if resp.json()["status"] == "completed":
            # Download GLTF com múltiplos AnimationClips
            anim_url = resp.json()["output_url"]
            animations = requests.get(anim_url).content
            with open("crowd_animations.glb", "wb") as f:
                f.write(animations)
            return
        time.sleep(5)

wait_for_animations("xyz")
```

3. **Integrar em motores**:

**Three.js**:
```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const loader = new GLTFLoader();
loader.load('crowd_animations.glb', (gltf) => {
  const model = gltf.scene;
  const mixer = new THREE.AnimationMixer(model);

  // Lista todos os AnimationClips gerados
  console.log(gltf.animations); // [walking_1, walking_2, ..., walking_15]

  // Para cada personagem, pegar clip aleatório
  function getRandomWalkClip() {
    const clips = gltf.animations.filter(c => c.name.includes('walking'));
    return clips[Math.floor(Math.random() * clips.length)];
  }

  // Instancing com InstancedMesh + animações variadas
  const geometry = model.children[0].geometry;
  const material = model.children[0].material;
  const count = 100;
  const instanced = new THREE.InstancedMesh(geometry, material, count);

  // Cada instância tem sua própria ação (clip) via mixer
  for (let i = 0; i < count; i++) {
    const clip = getRandomWalkClip();
    const action = mixer.clipAction(clip);
    action.play();
  }
});
```

**Godot 4 GDScript**:
```gdscript
extends Node3D

func _ready():
    # Carregar GLTF com clips
    var importer = GLTFDocument.new()
    var gltf_state = GLTFState.new()
    importer.append_from_file("crowd_animations.glb", gltf_state)

    # Iterar clips
    for clip_name in gltf_state.animations.keys():
        print("Clip: ", clip_name)

    # Instanciar personagens com clips distintos
    for i in range(100):
        var npc = preload("res://npc.tscn").instantiate()
        var anim_player = npc.get_node("AnimationPlayer")

        # Selecionar clip aleatório
        var clip = choose_random_animation()
        anim_player.queue(clip)
        anim_player.play()
        add_child(npc)

func choose_random_animation():
    # Usar RNG seeded para garantir diversidade
    var clips = ["walking_1", "walking_5", "walking_12"]
    return clips[randi() % clips.size()]
```

4. **Otimização pós-geração**:
```bash
# Comprimir GLTF (reduzir tamanho 50-70%)
gltf-transform compress crowd_animations.glb crowd_animations_compressed.glb

# Bake animações em texturas (se for usar em shader)
# (avançado, raramente necessário)
```

## Stack e requisitos
- **Input**: texto descritivo (30-100 palavras)
- **Output**: GLTF/GLB com múltiplos AnimationClips (cada clip é 4-10 KB)
- **Características do personagem**: humanoid biped obrigatório (quadrúpedes, criaturas custom = experimental)
- **Duração por animação**: 2-10 segundos (maior = mais custo)
- **Variações**: 10-50 por batch (trade-off qualidade vs diversidade)
- **Custo Mixamo Pro**: $50/mês unlimited, $5 por geração sem plano
- **Tempo**: 30 sec - 5 min geração + compilação
- **Compatibilidade**: GLTF 2.0 universal — Three.js, Babylon, Godot 4, Unreal Sequencer
- **Tamanho arquivo**: 100 variações × 4 KB = 400 KB (arquivo .glb comprimido)

## Armadilhas e limitações
- **Loop continuidade**: animações podem não conectar smoothly se geradas independentemente. Exigir flag `loop_friendly` ou fazer manual blend in shader
- **Física inconsistente**: personagens podem "patinar" ou flutuar. Revisar e ajustar root motion em Blender se necessário
- **Falta de sincronização**: 100 personagens com 100 clips diferentes = carga GPU alta (considerar LOD: reduzir anims em distância > 50m)
- **Controle criativo baixo**: prompt deve ser vago o suficiente pra ser genérico, específico o suficiente pra ser útil (muito difícil achar meio-termo)
- **Caracteres humanoides only**: quadrúpedes, insetos, criaturas não-humanoides falham ou precisam rigging custom
- **Propriedade IP**: verificar ToS — Mixamo exige aceitar que podem usar suas gerações em marketing
- **Render baking obrigatório**: se quiser sombras ou materials PBR dinâmicos, precisa rebake em Blender
- **Edição pós-geração trabalhosa**: deletar/modificar um clip exige ferramentas de anim especializadas

## Conexões
- [[crowd-simulation-optimization]]
- [[instanced-mesh-rendering]]
- [[gltf-animation-clips]]
- [[motion-capture-vs-procedural-animation]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com implementação técnica + otimizações