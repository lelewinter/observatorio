---
date: 2026-03-24
tags: [ia, google, gemini, embeddings, multimodal, vetores, busca]
source: https://www.linkedin.com/posts/fabriciocarraro_ia-inteligenciaartificial-ai-share-7441807897744785408-zau-
autor: "@fabriciocarraro"
tipo: aplicacao
---

# Implementar Busca Multimodal com Gemini Embedding 2

## O que é

Modelo Google Gemini Embedding 2 mapeia texto, imagens, áudio, vídeo, PDFs para único espaço vetorial. Busca cross-modal nativa: image-to-audio, text-to-video, PDF-to-image, sem conversão intermediária. Operações vetoriais funcionam multimodal (ex: imagem de rei - coroa ouro = imagem homem).

## Como implementar

**1. Obter API key**

- Acesse: https://ai.google.dev
- Clique "Get API Key"
- Copie chave (gratuita para tier inicial)

**2. Setup Python com notebook**

```python
import google.generativeai as genai
from google.colab import userdata

api_key = userdata.get('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

# Modelo multimodal
model = 'models/embedding-001'
```

**3. Gerar embeddings multimodais**

```python
# Texto
text_embedding = genai.embed_content(
    model=model,
    content="foto de gato"
)['embedding']

# Imagem (URL ou base64)
image_embedding = genai.embed_content(
    model=model,
    content={'mime_type': 'image/jpeg', 'data': image_data}
)['embedding']

# Áudio
audio_embedding = genai.embed_content(
    model=model,
    content={'mime_type': 'audio/mpeg', 'data': audio_data}
)['embedding']
```

**4. Busca por similaridade**

```python
import numpy as np

# Cosseno similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Query: imagem → encontrar áudios similares
query_embedding = image_embedding
similarities = [cosine_similarity(query_embedding, audio_emb)
                for audio_emb in audio_embeddings]
top_k = np.argsort(similarities)[-5:]  # Top 5
```

**5. Pipeline RAG melhorado**

Sem Gemini 2: áudio → transcrever → embeddings → busca (3 passos, perda info)
Com Gemini 2:

```python
# Direto
document_embeddings = {
    'video.mp4': genai.embed_content(model, video_data)['embedding'],
    'doc.pdf': genai.embed_content(model, pdf_data)['embedding'],
    'image.jpg': genai.embed_content(model, image_data)['embedding'],
}

# Query com qualquer mídia
result = max(document_embeddings.items(),
             key=lambda x: cosine_similarity(query_embedding, x[1]))
```

**6. Casos de uso estruturados**

| Aplicação | Implementação |
|-----------|--|
| Catálogo multimodal | Indexar vídeos + PDFs + imagens, busca por qualquer tipo |
| Rede social inteligente | Agrupar posts texto/imagem/video similar |
| Pesquisa documentação | Buscar PDFs por imagens/áudio sem OCR prévio |
| Recuperação RAG | Chunks áudio/imagem/texto no mesmo índice vetorial |

## Stack e requisitos

- Python 3.9+
- google-generativeai library
- NumPy (similaridade cosseno)
- Google Colab ou local (gratuito tier inicial)
- Modelos suportados: embedding-001

## Armadilhas e limitações

- **Rate limits**: Tier gratuito: ~600 requests/dia. Use caching se processamento em batch
- **Tamanho máximo**: Cada entrada até ~100K tokens (texto), ~5min (áudio/vídeo)
- **Qualidade varia**: Embeddings mais precisos em sânico bem-estruturado. Ruído audio = similaridade imprecisa
- **Sem fine-tuning**: Modelo genérico. Para domínio específico, considere treinar adapter
- **Custo escala**: Após free tier, pagamento por 1M embeddings (~$0.02)

## Conexões

[[embeddings-multimodais-em-espaco-vetorial-unificado]]
[[contexto-persistente-em-llms]]
[[geracao-de-json-a-partir-de-qualquer-fonte]]

## Histórico

- 2026-03-24: Nota criada
- 2026-04-02: Reescrita como guia de implementação
