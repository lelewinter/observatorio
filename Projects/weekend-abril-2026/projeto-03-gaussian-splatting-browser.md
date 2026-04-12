---
tags: [projeto, gaussian-splatting, 3d, threejs, webgpu, fotogrametria, open-source]
date: 2026-04-11
tipo: projeto
status: pendente
prioridade: media-alta
tempo-estimado: 2-3 horas
---
# Projeto 3: 3D Gaussian Splatting no Browser

## Objetivo

Capturar uma cena real com o celular, treinar um modelo de Gaussian Splatting, e renderizar o resultado no browser em tempo real. Experiencia end-to-end de fotogrametria moderna com IA.

## Por que fazer isso agora

Khronos (o grupo por tras de glTF, Vulkan, OpenGL) lancou a extensao KHR_gaussian_splatting para glTF 2.0 em fevereiro 2026. Google, NVIDIA e Apple estao apoiando. FastGS treina 3DGS em 100 segundos. WebGPU esta em 95% dos browsers. Three.js r171+ suporta WebGPU nativamente. Superman (2026) foi o primeiro filme a usar Gaussian Splatting dinamico. A tecnologia saiu de paper para standard da industria.

## Pre-requisitos

- Celular com camera decente (qualquer smartphone moderno serve)
- GPU NVIDIA com 8GB+ VRAM (RTX 3060 minimo)
- Python 3.10+
- COLMAP instalado (Structure-from-Motion)
- Node.js (para o viewer Three.js)
- ~5GB de espaco em disco

## Passo a Passo

### Etapa 1: Capturar Fotos (20 min)

Escolher um objeto ou cena pequena (uma mesa com objetos, uma planta, uma estante). Regras:

```
CAPTURA - REGRAS DE OURO:
- 50-100 fotos (mais = melhor, ate 200)
- Circular o objeto em 360 graus
- 3 alturas: nivel do objeto, 45 graus acima, de cima pra baixo
- Overlap de 60-70% entre fotos consecutivas
- Iluminacao uniforme (evitar flash, evitar sombras duras)
- Foco fixo (nao usar autofocus entre fotos se possivel)
- Evitar superficies refletivas (espelhos, vidro, metal polido)
```

Transferir fotos para pasta no PC: `C:\Users\leeew\gaussian-splatting\input\`

### Etapa 2: Instalar Dependencias (20 min)

```powershell
# COLMAP (para Structure-from-Motion)
# Baixar installer: https://colmap.github.io/install.html
# Ou via conda:
conda install -c conda-forge colmap

# Gaussian Splatting original (Inria)
git clone https://github.com/graphdeco-inria/gaussian-splatting.git
cd gaussian-splatting
pip install -r requirements.txt --break-system-packages
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn

# OU usar OpenSplat (alternativa mais simples)
pip install opensplat --break-system-packages
```

### Etapa 3: Processar com COLMAP (15-30 min)

```powershell
# Extrair poses de camera das fotos
colmap automatic_reconstructor `
  --workspace_path C:\Users\leeew\gaussian-splatting\workspace `
  --image_path C:\Users\leeew\gaussian-splatting\input `
  --quality medium
```

COLMAP detecta features em cada foto, faz matching entre fotos, e calcula a posicao 3D de cada camera. Saida: nuvem de pontos esparsa + poses de camera.

### Etapa 4: Treinar Gaussian Splatting (10-30 min)

```powershell
# Com o repo original da Inria
python train.py -s C:\Users\leeew\gaussian-splatting\workspace --iterations 7000

# Com OpenSplat (mais simples)
opensplat C:\Users\leeew\gaussian-splatting\workspace -n 7000
```

O treino otimiza milhares de "gaussianas 3D" (elipses com cor e opacidade) para reconstruir a cena. 7000 iteracoes e um bom ponto de partida (mais = mais detalhes, mais tempo).

Saida: arquivo `.ply` ou `.splat` (~20-100MB dependendo da cena).

### Etapa 5: Visualizar no Browser (30 min)

```powershell
# Opcao 1: Viewer online (mais rapido pra testar)
# Abrir https://playcanvas.com/supersplat
# Arrastar o arquivo .ply para a janela

# Opcao 2: Viewer Three.js local
mkdir gs-viewer && cd gs-viewer
npm init -y
npm install three @mkkellogg/gaussian-splats-3d
```

Criar `index.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <style>body { margin: 0; overflow: hidden; }</style>
</head>
<body>
  <script type="importmap">
  {
    "imports": {
      "three": "https://unpkg.com/three@0.171.0/build/three.module.js"
    }
  }
  </script>
  <script type="module">
    import * as THREE from 'three';
    import * as GaussianSplats3D from 'https://unpkg.com/@mkkellogg/gaussian-splats-3d@0.4.5/build/gaussian-splats-3d.module.js';

    const viewer = new GaussianSplats3D.Viewer({
      cameraUp: [0, -1, 0],
      initialCameraPosition: [0, 0, 5],
      initialCameraLookAt: [0, 0, 0]
    });

    viewer.addSplatScene('./scene.splat')
      .then(() => viewer.start());
  </script>
</body>
</html>
```

```powershell
# Servir localmente
npx http-server -p 8080
# Abrir http://localhost:8080
```

### Etapa 6: Experimentar (30 min)

- Orbitar a cena com mouse (drag = rotacao, scroll = zoom)
- Testar em celular (acessar IP local:8080 na mesma rede)
- Medir FPS (deve ser 30-60+ dependendo da GPU)
- Tentar cenas diferentes: objeto pequeno vs ambiente

## Checklist de Conclusao

- [ ] Fotos capturadas (50-100)
- [ ] COLMAP processou poses de camera
- [ ] Treinamento completou sem erro
- [ ] Visualizou no SuperSplat ou viewer local
- [ ] Testou navegacao 3D (orbitar, zoom)
- [ ] (Opcional) Testou no celular via rede local
- [ ] Anotou qualidade, tempo de treino, tamanho do arquivo

## Troubleshooting Comum

**COLMAP nao encontra matches**: fotos com pouco overlap ou superficies sem textura. Solucao: tirar mais fotos, adicionar objetos com textura na cena.

**Treinamento out of memory**: cena muito grande ou muitas fotos. Solucao: reduzir resolucao das fotos (`--resolution 2` no train.py) ou usar menos fotos.

**Artefatos na renderizacao**: "floaters" (gaussianas soltas no ar). Normal em areas com poucas fotos. Solucao: mais fotos naquela regiao.

**Reflexos/transparencia**: gaussianas nao modelam reflexos especulares nem transparencia. Evitar vidro, espelhos, agua.

## Notas Relacionadas

- [[3d-gaussian-splatting]]
- [[geracao-3d-a-partir-de-imagem]]
- [[skywork-matrix-game-3-world-model-interativo-tempo-real]]
- [[renderizacao-de-grama-3d-com-webgpu]]
- [[mvp-3d-no-browser-com-threejs-e-cesiumjs]]

## Criterios de Sucesso

Minimo: COLMAP processou, treinamento rodou, conseguiu visualizar no SuperSplat online.
Ideal: Viewer local funcionando com Three.js, navegacao fluida, testou no celular.
Bonus: Publicou no GitHub Pages como portfolio piece.

## Historico

- 2026-04-11: Projeto criado
