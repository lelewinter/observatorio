---
tags: []
source: https://x.com/i/status/2040055046197674395
date: 2026-04-03
tipo: aplicacao
---
# Gerar Modelos 3D com PBR Textures a partir de Foto usando Hunyuan3D 2.1

## O que e

Hunyuan3D 2.1 e um modelo open source da Tencent que converte uma unica imagem (ou prompt de texto) em um modelo 3D completo com texturas PBR fisicamente precisas (Albedo, Normal, Roughness, Metallic), pronto para uso em Blender, Unity e Unreal Engine. Licenca Apache 2.0, pesos completos e codigo de treinamento publicamente disponíveis no Hugging Face e GitHub. O impacto e direto: o que levava de 3 a 5 dias de trabalho de um artista senior pode ser gerado em minutos, no seu proprio hardware, sem custo de licenca.

## Como implementar

**1. Clonar o repositorio e configurar o ambiente**

O primeiro passo e clonar o repositorio oficial da Tencent e instalar as dependencias. O projeto exige Python 3.10+ e CUDA 11.8 ou superior para GPU NVIDIA. Em ambientes macOS, o suporte e via Metal (MPS), sem CUDA.

```bash
git clone https://github.com/Tencent/Hunyuan3D-2
cd Hunyuan3D-2
conda create -n hunyuan3d python=3.10
conda activate hunyuan3d
pip install -r requirements.txt
```

Apos instalar as dependencias base, e necessario instalar pacotes adicionais para renderizacao e processamento de mesh. O repositorio inclui um script `install.sh` que automatiza a instalacao do `rembg` (remocao de background), `nvdiffrast` (rasterizacao diferenciavel para projecao de texturas) e `xatlas` (UV unwrapping automatico). Execute-o antes de qualquer inferencia:

```bash
bash install.sh
```

**2. Download dos pesos do modelo**

Os pesos sao hospedados no Hugging Face. O pipeline completo tem dois modulos separados: o gerador de shape (mesh) e o sintetizador de texturas PBR. Voce pode baixar ambos via `huggingface_hub` ou manualmente:

```bash
pip install huggingface_hub
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='tencent/Hunyuan3D-2.1', local_dir='./weights')"
```

O download total gira em torno de 15-25 GB dependendo dos checkpoints selecionados. Para uso minimo viavel, priorize os pesos do modelo de shape (`hunyuan3d-dit-v2-1`) e do texturizador (`hunyuan3d-paint-v2-1`).

**3. Inferencia via linha de comando — imagem para 3D**

Com o ambiente configurado, a inferencia basica a partir de uma foto e feita assim:

```bash
python infer.py \
  --image-path ./sua_imagem.png \
  --output-dir ./output \
  --steps 50 \
  --guidance-scale 7.5 \
  --seed 42
```

O pipeline interno funciona em duas etapas distintas: (a) geracao do mesh limpo via modelo de difusao multiview, e (b) projecao e sintese das texturas PBR a partir de multiplos angulos simultaneamente. Essa separacao em dois estagios e exatamente o que resolve o "Janus problem" — o modelo nao tenta gerar geometria e textura ao mesmo tempo, o que causava faces inconsistentes em geradores anteriores como Zero123 e TripoSR.

**4. Inferencia via texto (text to 3D)**

Para gerar a partir de um prompt textual, o pipeline usa um modelo de geracao de imagem intermediario (por padrao integrado ao Stable Diffusion XL ou Flux, dependendo da configuracao) para criar uma imagem de referencia antes de passar pelo Hunyuan3D. O flag muda para:

```bash
python infer.py \
  --text-prompt "a ceramic coffee mug with blue glaze, studio lighting" \
  --output-dir ./output \
  --steps 50
```

Na pratica, o resultado de text-to-3D e menos previsivel que image-to-3D. Para producao, o fluxo recomendado e: gerar a imagem de referencia com controle total (Midjourney, Flux, SDXL) → usar essa imagem como input para o Hunyuan3D. Isso maximiza a coerencia da geometria gerada.

**5. Addon para Blender**

O repositorio inclui um addon nativo para Blender 3.6+ e 4.x. Para instalar:

1. Va em `Edit > Preferences > Add-ons > Install`
2. Selecione o arquivo `hunyuan3d_blender_addon.zip` da pasta `addon/` do repositorio
3. Ative o addon e configure o caminho dos pesos no painel de preferencias
4. No viewport 3D, acesse o painel lateral (`N`) > aba `Hunyuan3D`
5. Arraste uma imagem, clique em `Generate` — o mesh e importado diretamente com materiais PBR configurados nos nos do Shader Editor

O addon cria automaticamente um material com os nodes de Albedo (Base Color), Normal Map, Roughness e Metallic conectados ao Principled BSDF, pronto para render em Cycles ou EEVEE.

**6. Integracao com ComfyUI**

Para workflows mais complexos e encadeamento com outros modelos (por exemplo, gerar a imagem de referencia com ControlNet antes de passar para o Hunyuan3D), a integracao via ComfyUI e o caminho mais produtivo. Instale o node customizado:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Tencent/Hunyuan3D-2-ComfyUI
pip install -r Hunyuan3D-2-ComfyUI/requirements.txt
```

Reinicie o ComfyUI e os nodes `Hunyuan3D Shape Generator` e `Hunyuan3D Texture Painter` aparecerao na busca. Um workflow tipico de producao: `LoadImage → RemoveBackground → Hunyuan3DShapeGen → Hunyuan3DTexturePaint → SaveGLB`.

**7. Exportacao e uso em engines**

O output padrao e `.glb` (formato GLTF binario), que e nativamente suportado por Unreal Engine 5 (via `Import Asset`), Unity (via pacote GLTF Fast ou importacao nativa no Unity 6), e Blender. Para pipelines que exigem `.fbx` ou `.obj` com textures separadas, use o Blender como intermediario: importe o `.glb`, exporte no formato desejado com `File > Export`. As texturas PBR ficam embedadas no `.glb` ou podem ser extraidas como PNGs individuais com ferramentas como `gltf-transform` (Node.js) ou `Gestaltor`.

## Stack e requisitos

- **Linguagem:** Python 3.10+
- **Framework de ML:** PyTorch 2.1+ com CUDA 11.8 ou 12.1
- **VRAM minima:** 10 GB para geracao de shape; 16 GB recomendado para shape + texturas em sequencia sem offload
- **GPU:** NVIDIA RTX 3080/4070 ou superior (testado); suporte experimental a AMD via ROCm e macOS via MPS
- **RAM do sistema:** 32 GB recomendado (o pipeline de texturizacao e intensivo em CPU durante o UV unwrapping)
- **Armazenamento:** ~25 GB para pesos completos
- **Libs principais:** `torch`, `diffusers`, `transformers`, `trimesh`, `nvdiffrast`, `xatlas`, `rembg`, `Pillow`, `einops`, `accelerate`
- **Blender:** 3.6 ou 4.x para o addon oficial
- **ComfyUI:** versao atual do branch `master` (rolling release)
- **OS:** Linux (melhor suporte), Windows 10/11 com WSL2 ou nativo, macOS 13+ (Ventura) com Apple Silicon
- **Custo de operacao:** $0 apos hardware. Sem API, sem assinatura, sem por-uso
- **Tempo de geracao:** 30-90 segundos para shape + 2-5 minutos para texturas PBR completas em RTX 4090; escala inversamente com VRAM disponivel

## Armadilhas e limitacoes

**Qualidade de mesh dependente da foto de entrada.** O modelo e excelente com objetos com geometria clara e iluminacao de estudio. Fotos em perspectiva extrema, com oclusao pesada ou fundo complexo geram meshes com artefatos. Sempre use `rembg` para remover o background antes da geracao — o pipeline ja chama isso automaticamente, mas uma remocao manual de qualidade superior (via Photoshop ou Remove.bg) melhora significativamente o resultado.

**O "Janus problem" foi reduzido, nao eliminado.** Para objetos com simetria bilateral clara (rostos humanos, animais de frente) ou objetos altamente assimetricos vistos de um unico angulo, ainda podem aparecer inconsistencias na geometria do lado oposto. O modelo infere o verso a partir da imagem frontal; se a imagem de entrada nao da pistas suficientes do verso, o modelo "alucina" a geometria traseira.

**Topologia nao e otimizada para