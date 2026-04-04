---
tags: [character-generation, auto-rigging, animation, unreal-engine-5, hunyuan-3d, character-pipeline]
source: https://x.com/BlendiByl/status/2037014285772349574?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Personagem Jogável em UE5 de Foto em <5 Minutos

## O que é
Pipeline end-to-end: imagem (foto, conceito, avatar) → modelo 3D (Hunyuan 3D) → auto-rigging (Meshy) → animações → personagem jogável em Unreal Engine 5.

## Como implementar
**Setup (via plataforma fal.ai)**:

1. **Obter credenciais**:
```bash
# Criar conta em fal.ai
# Gerar API key (usar para orchestração de modelos)
export FAL_API_KEY="xxx-yyy-zzz"
```

2. **Escrever orquestração** (Python via fal SDK):
```python
import fal
from pathlib import Path

# Step 1: Imagem → Modelo 3D com Hunyuan 3D v3.1
def image_to_3d(image_path: str):
    model = fal.Model("hunyuan-3d-v3.1", credentials=FAL_API_KEY)

    result = model.predict(
        image=open(image_path, "rb"),
        text_prompt="a detailed 3d character model",
        guidance_scale=7.5
    )

    return result["model_url"]  # GLB file

# Step 2: Modelo 3D → Auto-rigging + Animações com Meshy
def auto_rig_and_animate(model_url: str):
    model = fal.Model("meshy-auto-rig", credentials=FAL_API_KEY)

    result = model.predict(
        model_url=model_url,
        character_type="humanoid",
        animation_presets=["idle", "walk_forward", "walk_backward", "jump"]
    )

    return result["rigged_model_url"], result["animation_clips"]

# Step 3: Exportar para Unreal Engine
def export_to_ue5(rigged_model_url: str, animations):
    # Baixar GLB + animations
    rigged_glb = requests.get(rigged_model_url).content

    with open("character.glb", "wb") as f:
        f.write(rigged_glb)

    # Annotations para Unreal
    ue5_config = {
        "skeleton_type": "humanoid_skeleton_v2",
        "animation_clips": animations,
        "materials_type": "pbr_imported",
        "import_as_skeletal": True
    }

    with open("character_ue5_config.json", "w") as f:
        json.dump(ue5_config, f)

# Rodar pipeline
image_path = "character_concept.png"
model_url = image_to_3d(image_path)
rigged_url, anims = auto_rig_and_animate(model_url)
export_to_ue5(rigged_url, anims)

print("✓ character.glb pronto para importar no UE5")
```

3. **Importar em Unreal Engine 5**:
```cpp
// No editor UE5: File → Import → character.glb
// Settings automáticos (detecta skeleton, animations via JSON)
// Resultado: personagem jogável com idle/walk/jump ja compilados

// Usar em Blueprint
ACharacter* NewCharacter = GetWorld()->SpawnActor<ACharacter>();
NewCharacter->SetActorLocation(FVector(0, 0, 100));

USkeletalMeshComponent* SkeletalMesh = NewCharacter->GetMesh();
SkeletalMesh->SetSkeletalMesh(LoadObject<USkeletalMesh>(
    nullptr,
    TEXT("SkeletalMesh'/Game/Characters/character.character'")
));

// Play animation
UAnimInstance* AnimInstance = SkeletalMesh->GetAnimInstance();
AnimInstance->Montage_Play(WalkMontage, 1.0f);
```

4. **Otimizações pós-import**:
```bash
# Reduzir poly count (se necessário)
# Remesher online ou Blender
gltf-transform quantize character.glb character_quantized.glb
# Típico: 500k polys → 100k polys, mantendo qualidade 90%
```

## Stack e requisitos
- **APIs necessárias**: fal.ai (orchestration), Hunyuan 3D v3.1 (4B model), Meshy Auto-Rig
- **Input**: JPG/PNG qualquer (512x512 a 4K ideal)
- **Output**: GLB com skeleton + animations + materials PBR
- **Tempo total**: 2-5 min (Hunyuan) + 2-3 min (auto-rig) = 4-8 min total
- **VRAM requerido**: 12+ GB (não é local, roda em cloud fal.ai)
- **Custo**: $1-3 por personagem (Hunyuan) + $0.50-1 (Meshy)
- **Compatibilidade UE5**: nativa via skeletal mesh + animations
- **Suporte a plataforma**: PC, Mobile (via LOD após import)

## Armadilhas e limitações
- **Auto-rigging falha em**: quadrúpedes, estruturas não-humanoides, criaturas fantásticas (teste + fallback to manual)
- **Animações são genéricas**: idle/walk/jump básicos. Movimentos customizados (ataque, emote, dança) precisam refinamento em motionbuilder
- **Proporções podem estar erradas**: ombros muito largos, braços muito curtos. Inspecionar e ajustar skeleton em UE5
- **Topologia densa**: personagem pode ter 500k+ polys. Remesh em Instant Meshes (online) se budget for tight
- **Fidelidade fina limitada**: cabelo, pele com detalhe fotográfico perdem na conversão (tudo fica genérico)
- **Texturas são baked**: não consegue extrair normals ou roughness separados. Se quer material customizado, rebake em Substance
- **Rig pode quebrar**: auto-rig é 90% automático, 10% falha (falta de dedos, backbone partido). Review e ajuste manualmente se crítico
- **Performance**: personagem importado no UE5 por padrão está em poly-count alto. Usar LODs (auto-geradas) para personagens distantes

## Conexões
- [[auto-rigging-character-animation]]
- [[character-pipeline-game-dev]]
- [[unreal-engine-5-character-import]]
- [[IA-generativa-personagens]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com implementação via fal.ai + UE5 setup