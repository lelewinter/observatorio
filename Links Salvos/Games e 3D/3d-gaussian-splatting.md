---
tags: [3d-graphics, reconstrucao-3d, neural-rendering, open-source, performance, gaussianas]
source: https://x.com/tom_doerr/status/2039400710962356575?s=20
date: 2026-04-02
tipo: aplicacao
---

# Reconstruir Cenas 3D em Tempo Real com Gaussian Splatting

## O que é

Técnica revolucionária de renderização volumétrica que representa cenas 3D como conjunto de gaussianas (elipsoides 3D com cor e opacidade). Ao invés de ray-marching como NeRF, gaussianas são rasterizadas em tempo real usando projeção 2D, alcançando:

- **60-120 FPS** em 1080p (10-20x mais rápido que NeRF)
- **Reconstrução fotométrica** a partir de 100-200 fotos simples
- **Qualidade visual** comparável ou superior a NeRF
- **Edição pós-reconstrução** possível (deletar/mover gaussianas)

OpenSplat é implementação open source em C++, multi-plataforma (Windows/Mac/Linux), com suporte a CPU e GPU. Pesquisa de 2025 mostra cenas de >100m² e otimizações para mobile.

## Por que importa agora

1. **Custo de captura caiu**: Smartphone + OpenSplat = cenas 3D fotométricas sem equipamento caro
2. **Tempo de treinamento**: 5-15 min em RTX 3080 vs horas com NeRF
3. **Integração em engines**: Unreal 5.5+ tem plugin oficial, Unity tem bindings via C#
4. **Mobile pronto**: Quantização de gaussianas permite 30 FPS em dispositivos móveis (2025)
5. **Pesquisa ativa**: FlashGS (CVPR 2025) para cenas grandes, Grendel-GS para multi-GPU

## Como funciona / Como implementar

### Entender o algoritmo: 3D Gaussian Representation

Cada gaussiana é representada por:
```
Position: (x, y, z) - coordenada no espaço 3D
Covariance: Σ = RS^T SR (3x3 matriz)
  - R: rotação (quaternion de 4 parâmetros)
  - S: escala (3 valores diagonais)
Opacity: α ∈ [0, 1] - transparência
Color: SH (spherical harmonics até ordem 3) = 16 valores RGB

Total: ~170 bytes por gaussiana
```

### Pipeline de Implementação (5 passos)

#### 1. Capturar Imagens

```bash
# Requisitos:
# - Smartphone ou câmera digital
# - Scene tamanho até 10m² (limite recomendado para primeira tentativa)
# - Iluminação estável (evitar mudanças drásticas entre frames)

# Procedimento:
# 1. Escolher ponto de partida
# 2. Andar em volta do objeto em espiral (~100-200 frames)
# 3. Sobreposição de 30° entre frames (importante para SfM)
# 4. Manter câmera apontada pro objeto em ~60% das fotos
# 5. Capturar detalhes próximos e distantes

# Ferramenta: Qualquer app de captura que salve JPEG/PNG
# Dica: usar vídeo em 60fps, depois extrair frames cada 0.5s
# ffmpeg -i video.mp4 -vf fps=2 "frame_%04d.jpg"
```

#### 2. Setup OpenSplat e COLMAP

```bash
# Clone e build (5-10 min, precisa C++17 compiler)
git clone https://github.com/pierotofy/OpenSplat.git
cd OpenSplat
mkdir build && cd build

# CMake
cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_CUDA_EXTENSION=ON
cmake --build . --config Release --parallel 8

# Verificar build
./OpenSplat --help
# Saída: OpenSplat v0.2.x [CUDA/CPU]
```

#### 3. Rodar Estrutura-do-Movimento (SfM) com COLMAP Integrado

```bash
# Usar OpenSplat integrado (melhor experiência)
./OpenSplat \
  --input /path/to/images/ \
  --output scene.ply \
  --colmap ./colmap \
  --gpu

# Ou usando COLMAP standalone (para fine-tuning)
colmap automatic_reconstructor \
  --workspace_path /path/to/project \
  --image_path /path/to/images \
  --sparse_model_path sparse/0

# Output de COLMAP: cameras.bin, images.bin, points3D.bin
# Arquivo sparse: nuvem de ~10k-50k pontos esparsos

# Verificar qualidade da pose estimação:
colmap image_deleter \
  --database_path database.db \
  --min_track_len 3  # Filtra observações fracas
```

#### 4. Otimizar Gaussianas (Training)

```cpp
// pseudocódigo C++ de como OpenSplat otimiza
#include "gaussian_rasterizer.h"
#include "loss_functions.h"

class GaussianOptimizer {
public:
    std::vector<Gaussian3D> gaussians;
    std::vector<cv::Mat> images;
    std::vector<cv::Mat> depth_maps;
    std::vector<Pose> camera_poses;
    
    void optimize(int iterations = 30000) {
        // Inicializar: uma gaussiana por ponto SfM
        initialize_from_sfm();
        
        // Otimizar iterativamente
        for (int iter = 0; iter < iterations; iter++) {
            // 1. Renderizar cena com gaussianas atuais
            std::vector<cv::Mat> rendered = rasterize(gaussians);
            
            // 2. Calcular loss fotométrico L2
            float loss = 0.0f;
            for (size_t i = 0; i < images.size(); i++) {
                loss += l2_loss(rendered[i], images[i]);
            }
            
            // 3. Backprop (CUDA otimizado)
            backward_pass(loss);
            
            // 4. Densidade adaptativa (pruning)
            if (iter % 100 == 0) {
                prune_low_opacity_gaussians(0.005);  // remover opacidade < 0.5%
                split_large_gaussians();             // dividir gaussianas grandes
                clone_high_grad_gaussians();          // duplicar gradientes altos
            }
            
            // 5. Update parâmetros (Adam optimizer)
            adam_step(learning_rate);
            
            if (iter % 1000 == 0) {
                float psnr = compute_psnr(rendered, images);
                std::cout << "Iter " << iter << ": loss=" << loss 
                          << " PSNR=" << psnr << std::endl;
            }
        }
    }

private:
    void initialize_from_sfm() {
        // Ler nuvem de pontos SfM (COLMAP)
        auto sparse_points = load_colmap_points3d();
        
        gaussians.clear();
        for (const auto& point : sparse_points) {
            Gaussian3D gauss;
            gauss.position = point.xyz;
            gauss.opacity = 0.5f;
            gauss.color = point.rgb;
            gauss.covariance_scale = {0.1f, 0.1f, 0.1f};
            gaussians.push_back(gauss);
        }
    }
    
    std::vector<cv::Mat> rasterize(const std::vector<Gaussian3D>& gaussians) {
        // Renderizar gaussianas em cada vista
        // - Transformar gaussianas para coordenadas de câmera
        // - Projetar 2D (Σ_proj = JΣJ^T, onde J é jacobiano)
        // - Splat em framebuffer (rasterização rápida)
        // - Blender (front-to-back) com opacidade
        
        std::vector<cv::Mat> rendered;
        for (const auto& pose : camera_poses) {
            cv::Mat view = splat_gaussians_to_view(gaussians, pose);
            rendered.push_back(view);
        }
        return rendered;
    }
    
    void prune_low_opacity_gaussians(float threshold) {
        // Remover gaussianas contribuindo pouco
        gaussians.erase(
            std::remove_if(gaussians.begin(), gaussians.end(),
                [threshold](const Gaussian3D& g) { return g.opacity < threshold; }),
            gaussians.end()
        );
        std::cout << "[PRUNE] Gaussianas restantes: " << gaussians.size() << std::endl;
    }
};
```

#### 5. Exportar e Renderizar

```bash
# OpenSplat exporta para:
# 1. .ply (formato padrão, editável)
# 2. .splat (formato comprimido, ~20-50MB para cena típica)

# Converter .ply para .splat (compressão)
./OpenSplat --input scene.ply --output scene.splat --compress

# Visualizar localmente:
# Opção 1: PlayCanvas Splat Viewer (web)
#   - Upload scene.splat
#   - URL: playcanvas.com/viewer

# Opção 2: Local viewer (Python com Three.js via WebGL)
python -m http.server 8000
# Aceder: localhost:8000/viewer.html (HTML + JavaScript)

# Opção 3: Unreal Engine 5
#   - Plugin: NVIDIA Kaolin Wisp
#   - Importar .ply como custom asset
#   - Integração full com material system, sombras, etc
```

### Integração em Game Engines

#### Unreal Engine 5

```cpp
// Plugin NVIDIA Kaolin Wisp
#include "KaolinGaussianSplattingComponent.h"

void AMyActor::BeginPlay() {
    Super::BeginPlay();
    
    // Criar componente de splatting
    UKaolinGaussianSplattingComponent* SplattingComponent = 
        NewObject<UKaolinGaussianSplattingComponent>(this);
    
    // Carregar cena
    SplattingComponent->LoadFromFile(FString("scene.splat"));
    SplattingComponent->RegisterComponent();
    
    // Configurar renderização
    SplattingComponent->SetRenderResolution(1920, 1080);
    SplattingComponent->EnableShadows(true);
    SplattingComponent->EnableMotionBlur(true);
    
    RootComponent = SplattingComponent;
}
```

#### Unity (via C# Binding)

```csharp
using UnityEngine;
using SplattingNative; // binding para OpenSplat C++

public class GaussianSplattingRenderer : MonoBehaviour {
    private SplatRenderer renderer;
    
    void Start() {
        renderer = new SplatRenderer();
        renderer.LoadSplat("scene.splat");
        renderer.SetResolution(1920, 1080);
    }
    
    void LateUpdate() {
        // Update camera pose
        Matrix4x4 viewProj = Camera.main.projectionMatrix * 
                             Camera.main.worldToCameraMatrix;
        
        renderer.Render(viewProj, Camera.main.transform);
    }
}
```

#### Web (Three.js + WebGL)

```javascript
// Viewer web simples
import * as THREE from 'three';
import { SplatLoader } from './SplatLoader.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Carregar splat
const loader = new SplatLoader();
loader.load('scene.splat', (geometry) => {
    const material = new THREE.RawShaderMaterial({
        vertexShader: splatVertexShader,
        fragmentShader: splatFragmentShader,
        uniforms: { projection: { value: camera.projectionMatrix } }
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
});

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
```

## Stack técnico

### Captura
- **Hardware**: Smartphone (iPhone 14 Pro+) ou câmera digital (50MP+)
- **Software**: App de vídeo stock, ou [CaptureBot](https://github.com/pierotofy/CaptureBot) (Python)
- **Saída**: 100-200 imagens JPEG/PNG, ~1-2GB total

### Processamento (SfM + Training)
- **COLMAP**: structure-from-motion, estimação de pose (C++)
- **OpenSplat**: otimização de gaussianas (C++ + CUDA)
- **Hardware**: GPU NVIDIA RTX 3080+ (8GB VRAM) ou RTX 4090 (24GB, 2-3x mais rápido)
- **Tempo**: 5-15 min em RTX 3080; 2-5 min em RTX 4090

### Rendering
- **Unreal 5.5+**: Plugin KaolinWisp nativo
- **Unity 2023+**: C# binding para OpenSplat
- **Web**: Three.js + custom WebGL shader
- **Mobile**: Quantização de gaussianas (INT8 ao invés de FP32)

### Storage
- **.ply**: ~100-200MB (não comprimido, editável)
- **.splat**: ~20-50MB (comprimido, otimizado para GPU)
- **Streaming**: ~5-10MB/s via WebSocket para mobile

## Código prático: Pipeline Automatizado

```python
import subprocess
import json
import os
from pathlib import Path
from typing import Optional

class Gaussian3DPipeline:
    """Pipeline end-to-end: fotos → SfM → otimização → .splat"""
    
    def __init__(self, input_dir: str, output_dir: str, gpu: bool = True):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.gpu = gpu
        self.log_file = output_dir / "pipeline.log"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_images(self) -> int:
        """Validar imagens de entrada"""
        images = list(self.input_dir.glob("*.jpg")) + list(self.input_dir.glob("*.png"))
        print(f"[VALIDATE] {len(images)} imagens encontradas")
        
        if len(images) < 20:
            raise ValueError("Precisa no mínimo 20 imagens para SfM")
        
        # Verificar resolução
        import cv2
        for img_path in images[:5]:
            img = cv2.imread(str(img_path))
            h, w = img.shape[:2]
            print(f"  - {img_path.name}: {w}x{h}")
            if w < 1280 or h < 720:
                print(f"    [WARN] Resolução baixa")
        
        return len(images)
    
    def run_colmap(self):
        """Rodar COLMAP para pose estimação"""
        print("[COLMAP] Iniciando Structure-from-Motion...")
        
        colmap_cmd = [
            "colmap", "automatic_reconstructor",
            "--workspace_path", str(self.output_dir / "colmap"),
            "--image_path", str(self.input_dir),
            "--dense", "0",  # não rodar MVS (caro)
        ]
        
        if self.gpu:
            colmap_cmd.extend(["--gpu", "1"])
        
        result = subprocess.run(colmap_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[COLMAP] ✓ Sucesso")
            return str(self.output_dir / "colmap" / "sparse" / "0")
        else:
            print(f"[COLMAP] ✗ Erro: {result.stderr}")
            raise RuntimeError("COLMAP falhou")
    
    def run_opensplat(self, colmap_sparse_path: str):
        """Rodar OpenSplat para otimização"""
        print("[OPENSPLAT] Iniciando otimização de gaussianas...")
        
        cmd = [
            "./OpenSplat",
            "--input", str(self.input_dir),
            "--output", str(self.output_dir / "scene.ply"),
            "--colmap_model", colmap_sparse_path,
        ]
        
        if self.gpu:
            cmd.append("--gpu")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OPENSPLAT] ✓ Sucesso")
            return str(self.output_dir / "scene.ply")
        else:
            print(f"[OPENSPLAT] ✗ Erro: {result.stderr}")
            raise RuntimeError("OpenSplat falhou")
    
    def compress_to_splat(self, ply_path: str) -> str:
        """Comprimir .ply para .splat"""
        print("[COMPRESS] Comprimindo para .splat...")
        
        splat_path = str(self.output_dir / "scene.splat")
        
        cmd = [
            "./OpenSplat",
            "--input", ply_path,
            "--output", splat_path,
            "--compress"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            ply_size = os.path.getsize(ply_path) / (1024**2)
            splat_size = os.path.getsize(splat_path) / (1024**2)
            ratio = splat_size / ply_size
            
            print(f"[COMPRESS] ✓ {ply_size:.1f}MB → {splat_size:.1f}MB ({ratio:.1%})")
            return splat_path
        else:
            print(f"[COMPRESS] ✗ Erro: {result.stderr}")
            raise RuntimeError("Compressão falhou")
    
    def run_full_pipeline(self):
        """Executar pipeline completo"""
        try:
            num_images = self.validate_images()
            colmap_path = self.run_colmap()
            ply_path = self.run_opensplat(colmap_path)
            splat_path = self.compress_to_splat(ply_path)
            
            print("\n[SUCCESS] Pipeline completo!")
            print(f"  Cena: {splat_path}")
            print(f"  Próximos passos:")
            print(f"    1. Visualizar: PlayCanvas Splat Viewer")
            print(f"    2. Integrar em Unreal/Unity")
            print(f"    3. Publicar na web")
            
            return {
                "ply": ply_path,
                "splat": splat_path,
                "num_images": num_images
            }
        
        except Exception as e:
            print(f"\n[FATAL] {e}")
            return None

# Uso
pipeline = Gaussian3DPipeline(
    input_dir="/path/to/images",
    output_dir="/path/to/output",
    gpu=True
)

result = pipeline.run_full_pipeline()
```

## Armadilhas e Limitações

### 1. **Fotografias com iluminação inconsistente quebram SfM**
- **Problema**: Fotos com mudança drástica de luz (sol se movendo, sombras) → COLMAP falha a estimar poses
- **Solução**: Capturar dentro de 5 min, evitar horário com sombras compridas, usar iluminação estável
- **Teste**: Depois de COLMAP, verificar `visualize_reconstruction.py` do COLMAP

### 2. **Reflex e vidro geram "fantasmas" na reconstrução**
- **Problema**: Espelhos e vidro refletem luz de forma não-coerente → gaussianas flutuam
- **Solução**: Mapear regiões espelhadas e marcar como "não otimizar" na loss function
- **Prático**: Remover espelhos antes de capturar, ou pedir ao usuário que evite reflex

### 3. **Escala: mundos >100m² ficam inviáveis**
- **Problema**: Pouca overlap entre imagens de pontos distantes → SfM falha ou cria buracos
- **Solução**: Dividir em tiles, processar separadamente, depois stitchar
- **Pesquisa**: FlashGS (CVPR 2025) resolve parcialmente com hierarchical optimization

### 4. **Edição pós-reconstrução é tedioso**
- **Problema**: Deletar ou mover gaussianas manualmente em milhões é impraticável
- **Solução**: Usar ferramentas como [Gaussian Splatting Editor](https://github.com/yindaz/gaussian-splatting-3d-editing) com seleção via brush
- **Alternativa**: Retrair com máscara (ignore regiões no training)

### 5. **Gaussianas estáticas (sem animação)**
- **Problema**: Objetos que se movem na cena criam "borrões" nas gaussianas
- **Solução**: Usar 4D-GS (gaussianas + time dimension) — mas é 3-5x mais caro em treinamento
- **Prático**: Garantir scene estática durante captura

### 6. **Brincos e "floaters" em transições**
- **Problema**: Em bordas de objetos ou mudança de profundidade, aparecem artefatos
- **Solução**: Aumentar número de imagens (200+ ao invés de 100), refinar parâmetros de pruning
- **Implementação**: Aumentar `prune_threshold` de 0.005 para 0.01 (remove mais agressivamente)

### 7. **Custo de hardware para treinamento**
- **Problema**: RTX 2060 8GB é borderline; RTX 3080 necessário para iteração rápida
- **Solução**: Usar cloud GPU (Google Colab com A100 = 4 min de treinamento, ~$2)
- **Alternativa**: Esperar por otimizações quantizadas (INT8) em 2026

### 8. **Formato .splat não é universal**
- **Problema**: Only three.js, PlayCanvas, Unreal suportam; Unity ainda tá atrás
- **Solução**: Manter .ply como formato master, exportar para .splat quando necessário
- **Futuro**: Esperar que WebGPU padronize em 2026-2027

## Conexões

- [[neural-rendering-nerf-vs-3dgs]] - Comparação NeRF vs Gaussian Splatting
- [[captura-3d-estrutura-movimento]] - Fundo técnico de COLMAP e SfM
- [[renderizacao-webgpu-tempo-real]] - WebGPU como futuro do splatting
- [[geracao-3d-com-ia-no-browser]] - Gerar cenas 3D via IA
- [[world-model-interativo-em-tempo-real]] - Combinar com procedural generation
- [[game-engine-unreal-vs-unity-2025]] - Integração em engines

## Histórico

- 2026-04-02: Nota original com guia básico OpenSplat
- 2026-04-11: Reescrita expandida com C++ optimizer, pipeline automatizado, 8 armadilhas específicas, integração engines
