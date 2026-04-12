---
tags: [embeddings, multimodal, ia, rag, vetores, gemini, google, clip, imagebind, cross-modal]
source: https://www.linkedin.com/posts/fabriciocarraro_ia-inteligenciaartificial-ai-share_7441807897744785408-zau-?utm_source=social_share_send&utm_medium=android_app&rcm=ACoAAAgQrLIB4LHRfm8oNhRCsOv9i7wGJSYJXQs&utm_campaign=share_via
date: 2026-04-11
tipo: aplicacao
---
# Embeddings Multimodais: Texto, Imagem, Áudio, Vídeo em Espaço Vetorial Unificado

## O que é

Modelos de embedding **nativamente multimodais** (Gemini Embedding 2, CLIP, ImageBind, VLM2Vec-V2) mapeiam **diferentes modalidades — texto, imagem, áudio, vídeo, PDF, até IMU/depth** — em um **único espaço vetorial compartilhado**. Isso permite:

- **Buscas cross-modal:** "Encontre vídeos similares a este texto"
- **Clustering semântico:** Agrupar imagens e artigos relacionados no mesmo cluster
- **Aritmética vetorial cross-modal:** "CEO (imagem) − homem (imagem) ≈ mulher (imagem)"
- **Zero-shot classification:** Classificar áudio por similaridade com descrições em texto

**Paradigma antigo (pré-2024):** Pipeline sequencial e quebrado.
```
Áudio → Transcrição (Whisper) → Embedding Textual → Busca em DB de texts
```

**Novo (2026):** Direto, unificado.
```
Áudio → Embedding Multimodal → Busca em DB unificado (áudio + texto + imagem + vídeo)
```

Implicação: **Simplicidade arquitetural radical** e precision muito melhor em buscas cross-modal.

## Como implementar

### Opção 1: Gemini Embedding 2 (Google, Recomendado)

API cloud (pago), mas qualidade state-of-the-art em 2026. Suporta texto, imagem, áudio, vídeo.

```python
import google.generativeai as genai
from pathlib import Path

genai.configure(api_key="sua-key-aqui")

# Embeddings multimodais
def embed_multimodal_content():
    """
    Exemplo: Embeddings de texto, imagem e áudio no mesmo espaço
    """
    
    # Texto
    text_embedding = genai.embed_content(
        model="models/embedding-001",
        content="Python é uma linguagem de programação poderosa",
        task_type="SEMANTIC_SIMILARITY"
    )
    
    # Imagem (via URL ou file)
    image_embedding = genai.embed_content(
        model="models/embedding-001",
        content={
            "mime_type": "image/jpeg",
            "data": Path("programador.jpg").read_bytes()
        }
    )
    
    # Vídeo (via URL)
    video_embedding = genai.embed_content(
        model="models/embedding-001",
        content={
            "mime_type": "video/mp4",
            "data": Path("tutorial_python.mp4").read_bytes()
        }
    )
    
    return {
        "text": text_embedding["embedding"],
        "image": image_embedding["embedding"],
        "video": video_embedding["embedding"]
    }

embeddings = embed_multimodal_content()

# Vetores de diferentes modalidades estão no MESMO espaço
# Dimensão: 768 (padrão Gemini 2)
print(f"Text embedding shape: {len(embeddings['text'])}")      # 768
print(f"Image embedding shape: {len(embeddings['image'])}")    # 768
print(f"Video embedding shape: {len(embeddings['video'])}")    # 768

# Similaridade cosseno funciona direto entre modalidades
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

sim_text_image = cosine_similarity(embeddings["text"], embeddings["image"])
print(f"Similaridade texto-imagem: {sim_text_image:.3f}")
# Output esperado: ~0.65 (imagem de programador é semanticamente similar a "Python")
```

### Opção 2: OpenAI Multimodal Embeddings

Similar ao Gemini, mas API OpenAI:

```python
from openai import OpenAI
import base64

client = OpenAI(api_key="sua-key")

def embed_image(image_path):
    """Embeddings de imagem via OpenAI"""
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")
    
    # OpenAI usa modelo vision para embeddings
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=[{
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
        }]
    )
    
    return response.data[0].embedding

# Embedding de texto
text_response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Máquina de aprendizado"
)
text_embedding = text_response.data[0].embedding

# Busca cross-modal
image_embedding = embed_image("ml_diagram.jpg")
similarity = cosine_similarity(text_embedding, image_embedding)
print(f"ML text vs ML diagram similarity: {similarity:.3f}")
```

### Opção 3: CLIP + ImageBind (Open-source, Local)

Roda inteiramente offline. CLIP é especializado em texto-imagem; ImageBind estende para 6 modalidades.

```python
import torch
from PIL import Image
import clip
import numpy as np

# Baixar modelo CLIP (ViT-B/32)
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Texto
text = clip.tokenize(["um cão", "um gato", "um carro"]).to(device)
text_features = model.encode_text(text)
text_features = text_features / text_features.norm(dim=-1, keepdim=True)  # Normalizar

# Imagem
image = preprocess(Image.open("foto_de_cao.jpg")).unsqueeze(0).to(device)
image_features = model.encode_image(image)
image_features = image_features / image_features.norm(dim=-1, keepdim=True)

# Similaridade cross-modal
similarity = (image_features @ text_features.T).softmax(dim=-1)
print("Probabilidades (texto):")
print(f"  'um cão': {similarity[0, 0].item():.2%}")      # ~95%
print(f"  'um gato': {similarity[0, 1].item():.2%}")      # ~3%
print(f"  'um carro': {similarity[0, 2].item():.2%}")     # ~2%
```

**ImageBind para mais modalidades:**

```python
# Instalação requer pytorch + timm
# pip install timm

import torch
from imagebind import data
import imagebind

# Baixar modelo
device = "cuda" if torch.cuda.is_available() else "cpu"
model = imagebind.imagebind_model.imagebind_huge(pretrained=True).to(device).eval()

# Embeddings de diferentes modalidades
inputs = {
    imagebind.ModalityType.TEXT: data.load_and_transform_text(
        ["um cachorro latindo", "música clássica"],
        device
    ),
    imagebind.ModalityType.VISION: data.load_and_transform_vision_data(
        ["foto_cao.jpg"],
        device
    ),
    imagebind.ModalityType.AUDIO: data.load_and_transform_audio_data(
        ["latido_cao.wav"],
        device
    ),
}

# Forward pass — todas as modalidades no mesmo espaço (1024-dim)
embeddings = model(inputs)

# Cross-modal retrieval
text_embedding = embeddings[imagebind.ModalityType.TEXT][0]
audio_embedding = embeddings[imagebind.ModalityType.AUDIO][0]

cosine_sim = torch.nn.functional.cosine_similarity(
    text_embedding.unsqueeze(0),
    audio_embedding.unsqueeze(0)
)
print(f"Similaridade 'cachorro latindo' (texto) vs som de latido: {cosine_sim.item():.3f}")
# Output: ~0.92
```

### Aplicação Prática: Search Engine Cross-Modal

Indexar PDF (texto), imagens, vídeos, áudio em um banco vetorial unificado:

```python
from pinecone import Pinecone
import google.generativeai as genai
from pathlib import Path

# Conectar Pinecone (vector DB na cloud)
pc = Pinecone(api_key="sua-pinecone-key")
index = pc.Index("multimodal-search")

genai.configure(api_key="sua-google-key")

def index_multimodal_assets(asset_dir: str):
    """
    Index todos arquivos (PDFs, imagens, vídeos, áudio) em um diretório
    """
    
    assets_path = Path(asset_dir)
    
    for asset_file in assets_path.rglob("*"):
        if asset_file.is_dir():
            continue
        
        # Ler conteúdo conforme tipo
        mime_type = get_mime_type(asset_file)
        content = asset_file.read_bytes()
        
        # Embedar via Gemini
        embedding = genai.embed_content(
            model="models/embedding-001",
            content={"mime_type": mime_type, "data": content}
        )
        
        # Salvar em Pinecone
        metadata = {
            "filename": asset_file.name,
            "mime_type": mime_type,
            "path": str(asset_file)
        }
        
        index.upsert(
            vectors=[(
                str(asset_file),  # unique ID
                embedding["embedding"],
                metadata
            )]
        )
        
        print(f"Indexed: {asset_file.name}")

def search_multimodal(query: str, modality: str = "text"):
    """
    Buscar similar a um query (texto, imagem, etc)
    """
    
    query_embedding = genai.embed_content(
        model="models/embedding-001",
        content={
            "mime_type": f"{modality}/plain",  # text, image/jpeg, audio/mp3, etc
            "data": query.encode() if modality == "text" else query
        }
    )
    
    # Busca vetorial em Pinecone
    results = index.query(
        vector=query_embedding["embedding"],
        top_k=5,
        include_metadata=True
    )
    
    return results

# Uso
# index_multimodal_assets("/mnt/myassets")
# results = search_multimodal("tutorials sobre python", modality="text")
# for match in results["matches"]:
#     print(f"Encontrado: {match['metadata']['filename']} (score: {match['score']:.3f})")
```

## Stack e requisitos

**APIs Cloud (simplest)**
- Google Gemini Embedding 2: USD ~0.02/1000 inputs
- OpenAI Multimodal Embeddings: USD ~0.02/1000 inputs
- Anthropic: não oferece multimodal embeddings direto (2026)

**Open-source Local**
- CLIP: ~350MB download, roda em CPU (lento) ou GPU (rápido)
- ImageBind: ~1GB download, requer PyTorch + timm
- Latência local: CLIP ~100ms/imagem em RTX 4090, ~2s em CPU

**Vector Stores**
- Pinecone (cloud): USD 0.02/1M vectors/mês + USD 0.05/mês base
- FAISS (local): grátis, ~10GB RAM para 1M embeddings 768-dim
- Weaviate (cloud): USD 100+/mês
- Milvus (open-source): grátis, self-hosted

**Dimensionalidade (importante!)**
- Gemini Embedding 2: 768 dims
- OpenAI text-embedding-3: 3072 dims (pode usar `dimensions=256` para reduzir)
- CLIP ViT-B/32: 512 dims
- ImageBind: 1024 dims

⚠️ **Vetores de tamanhos diferentes (768 vs 1024) não são comparáveis diretamente.** Usar PCA ou upsampling pra alinhar dimensionalidade.

**Hardware (se self-hosted)**
- CPU: Qualquer, CLIP roda em CPU 2-core (lento)
- GPU: RTX 3060+ para processamento batch rápido
- RAM: 8GB suficiente com FAISS local (1M embeddings = 1GB)
- Storage: 50GB para ~500k PDFs + imagens + vídeos comprimidos

## Armadilhas e limitações

**1. Modality gap persiste**

Mesmo em ImageBind, existe "cone" matemático no espaço onde text embeddings agrupam separado de image embeddings. Buscas texto→imagem funcionam, mas não com 100% recall.

**Validação:** Testar embedding space em labeled dataset conhecido, medir recall@k (quantos top-10 resultados foram corretos).

**2. Quantização de embeddings degrada similaridade**

Se reduzir 768-dim pra 256-dim via PCA, precisão cai ~10-20%. Vetores comprimidos economizam RAM/storage mas perdem discriminatividade.

**Benchmark:** Medir NDCG (normalized discounted cumulative gain) antes/depois quantização.

**3. Bias em dataset de treinamento replica-se no espaço**

Imagens de pessoas tendem a cluster por raça/gênero por definiçõa do espaço de treinamento, não intenção. CLIP treinado em internet data tem bias bem documentado.

**Mitigação:** Usar modelos debiased (Gemini Embedding 2 teve esforço de debiasing), validar outputs em subgrupos sensíveis.

**4. Dimensões diferentes não são comparáveis**

CLIP (512-dim) vs Gemini (768-dim) não se comunicam. Precisa converter um dos dois via PCA/upsampling, custando precisão.

**Best practice:** Escolher um modelo e manter consistente em sistema.

**5. Similaridade cosseno não é proximidade euclidiana**

Cosseno mede ângulo, não distância absoluta. Dois embeddings podem ter cos_sim=0.9 mas estar em regiões muito diferentes do espaço se magnitudes diferem.

**Normalizá-los:** `embedding = embedding / ||embedding||` antes de armazenar em vector DB.

**6. Latência de embedding pode ser gargalo**

Gemini Embedding 2 leva ~500ms por input (IO bound). Se precisar embedar 1000 imagens, leva 8+ minutos. Batch processing ajuda (até 100 items por request), mas ainda é lento.

**Otimização:** Pre-compute embeddings offline, cache agressivamente, considerar CLIP local se latência crítica.

**7. Context window de vídeo/áudio é limitado**

Modelos não processam vídeo inteiro; pegam frames/clips. Vídeo de 1h é downsampled a ~100 frames. Podem perder informação temporal importante.

**Workaround:** Dividir vídeo em chunks (shot detection), embedar cada chunk, armazenar separado com timestamps.

## Conexões

[[democratizacao-de-modelos-de-ia|Rodando modelos multimodais localmente]]
[[construcao-de-llm-do-zero|Entender representações internas (latent space)]]
[[cursos-gratuitos-huggingface-ia|Cursos em Vision + multimodal]]
[[deepagent-gerar-app-funcional-90-segundos|Apps com busca semantic]]
[[fine-tuning-de-llms-sem-codigo|Fine-tuning de embeddings]]

## Histórico

- 2026-04-11: Nota completamente reescrita. Adicionado explicação do paradigma antigo vs novo, 3 caminhos de implementação (Gemini, OpenAI, CLIP+ImageBind), aplicação prática search engine, stack detalhado, 7 armadilhas técnicas
- 2026-04-02: Nota original criada
