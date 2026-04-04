---
tags: [3d-graphics, reconstrucao-3d, neural-rendering, open-source, performance]
source: https://x.com/tom_doerr/status/2039400710962356575?s=20
date: 2026-04-02
tipo: aplicacao
---

# Reconstruir Cenas 3D em Tempo Real com Gaussian Splatting

## O que é
Técnica de renderização volumétrica que representa cenas tridimensionais como conjunto de gaussianas posicionadas no espaço, permitindo reconstrução fotométrca a partir de fotos simples e renderização em tempo real (60-120 FPS). OpenSplat é a implementação open source em C++ para uso local.

## Como implementar
**Setup inicial (ambiente Windows/Linux)**:
```bash
git clone https://github.com/pierotofy/OpenSplat.git
cd OpenSplat
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release --parallel 8
```

**Pipeline de reconstrução em 5 passos**:

1. **Capturar imagens**: use smartphone ou câmera comum em volta de uma cena (100-200 imagens, 30° overlap entre frames). Melhor qualidade com iluminação constante.

2. **Rodar Structure-from-Motion (SfM)**: OpenSplat usa COLMAP internamente. O software gera nuvem de pontos esparsa e poses de câmera:
```bash
./OpenSplat --input ./images/ --output ./scene.ply
```

3. **Otimizar gaussianas**: o algoritmo inicializa gaussianas na nuvem de pontos e otimiza iterativamente (5-10 min para cena média em GPU):
   - Atributos por gaussiana: posição (x,y,z), covariância (3x3 matriz), opacidade (α), cor (harmônicos esféricos até ordem 3)
   - Loss fotométrico: L2 entre imagem renderizada e imagens reais
   - Pruning adaptativo: remover gaussianas redundantes em tempo de otimização

4. **Renderizar em tempo real**: export como `.splat` (formato comprimido) ou `.ply`. Visualização via [PlayCanvas Splat Viewer](https://playcanvas.com) ou integrar em Unreal/Unity via plugins.

5. **Ajustes pós-reconstrução**:
   - Se resultado está borrado: aumentar nº de imagens ou qualidade
   - Se lento: reduzir densidade de gaussianas via threshold
   - Para uso em AR/mobile: quantizar representação (reduzir precisão de números mantendo qualidade visual)

**Integração em game engine**:
- **Unreal 5**: plugin [NVIDIA Kaolin Wisp](https://github.com/NVIDIAGameWorks/kaolin-wisp) suporta 3DGS, oferece renderização em tempo real com material system
- **Unity**: use WebGL viewer ou compile splat viewer em C# via binding de C++
- **Web/Browser**: PlayCanvas ou Three.js + splat loader (20MB arquivo típico para cena média)

## Stack e requisitos
- **Hardware**: GPU NVIDIA (CUDA 12+), mínimo RTX 2060 (8GB VRAM). Sem GPU: 10x mais lento (inviável para iteração)
- **Dependências**: COLMAP (em OpenSplat), CMake 3.20+, C++17 compiler
- **Tamanho de dados**: 100-200 imagens 4K → 500MB-1GB antes da otimização → 20-50MB `.splat` comprimido
- **Tempo de otimização**: 5-15 min em RTX 3080 para cena de 10m²
- **Custo**: $0 (OpenSplat é MIT license). PlayCanvas free tier = $0 para visualização web.

## Armadilhas e limitações
- **Qualidade de imagens**: fotografias de smartphone com mudanças drásticas de iluminação fazem SfM falhar. Use lighting consistente
- **Brincos e artefatos**: reflections (espelhos, vidro) e objetos em movimento geram "fantasmas" na reconstrução
- **Limite de escala**: cenas maiores que 100m² começam a exigir RAM excessiva (~32GB para cena grande)
- **Dinâmica limitada**: gaussianas são estáticas. Para animar cena, use 4D-GS (mais novo, pesado)
- **Edição pós-reconstrução**: deletar/mover gaussianas manualmente é tedioso. Use ferramentas como [Postprocessing Kit](https://github.com/aras-p/gaussian-splatting-3d-editing) em experimento

## Conexões
- [[neural-rendering-nerf-vs-3dgs]]
- [[captura-3d-estrutura-movimento]]
- [[renderizacao-webgpu-tempo-real]]
- [[geracao-3d-com-ia-no-browser]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para guia de implementação com OpenSplat