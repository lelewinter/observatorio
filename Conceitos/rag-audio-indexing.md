---
tags: [conceito, RAG, audio, embedding, search, transcription]
date: 2026-04-02
tipo: conceito
aliases: [Audio RAG, Podcast Search]
---

# RAG over Audio com Timestamps

## O que é

Pipeline que transcreve áudio (podcasts, palestras, videoaulas), divide em chunks semanticamente significativos, embed cada chunk com timestamps preservados, e permite busca vetorial que retorna exato momento do áudio onde resposta está.

## Como funciona

**Passo 1: Transcrição com Metadata**
- API (AssemblyAI, Whisper, Deepgram) transcreve áudio mantendo timestamps palavra-por-palavra
- Output: `{"text": "palavra1 palavra2...", "words": [{"text": "palavra1", "start": 0ms, "end": 500ms}]}`

**Passo 2: Chunking Inteligente**
- Não divide por tokens cegos; respeita boundary de sentença
- Mantém `start_time` e `end_time` de cada chunk
- Tipicamente 500-1000 tokens por chunk

**Passo 3: Embedding + Storage**
- Embed conteúdo de cada chunk (text-embedding-3-large, MiniLM, etc.)
- Store no vector DB com metadata: timestamp, source, preview text
- Exemplos: Pinecone, Milvus, FAISS

**Passo 4: Query com Retrieval**
- User pergunta: "Qual framework foi recomendado?"
- Vector search retorna top-3 chunks
- Para cada result, retorna: snippet + tempo exato (HH:MM:SS) para "jump to"

## Pra que serve

- Permitir deep search em conteúdo longo sem ler tudo
- Link direto ao exato momento no podcast onde resposta está
- Reduz tempo de consumo: usuário pula para trecho relevante
- Escalável: indexar centenas de horas de áudio
- [[retrieval-augmented-generation]]
- [[obsidian-com-ia-como-segundo-cerebro]] - Integração com vault Obsidian

## Exemplo prático

```python
import requests
from datetime import timedelta

# Step 1: Transcrição com AssemblyAI
def transcribe_with_timestamps(audio_url: str) -> dict:
    headers = {"Authorization": f"Bearer {ASSEMBLYAI_TOKEN}"}

    # POST para processar
    response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json={"audio_url": audio_url},
        headers=headers
    )
    transcript_id = response.json()["id"]

    # Poll até completo
    while True:
        result = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers=headers
        ).json()
        if result["status"] in ["completed", "error"]:
            break
        time.sleep(2)

    # Retorna: {"text": "...", "words": [{"text": "word", "start": 0, "end": 500}]}
    return result

# Step 2: Chunk com timestamps
def chunk_audio_transcript(transcript: dict, chunk_tokens=800) -> list:
    words = transcript["words"]
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word_obj in words:
        tokens = len(word_obj["text"]) // 4 + 1  # Aprox

        # Se chunk ficou cheio e temos algo acumulado
        if current_tokens + tokens > chunk_tokens and current_chunk:
            chunk_text = " ".join([w["text"] for w in current_chunk])
            start_time = current_chunk[0]["start"]
            end_time = current_chunk[-1]["end"]

            chunks.append({
                "text": chunk_text,
                "start_ms": start_time,
                "end_ms": end_time,
                "timestamp": ms_to_hms(start_time),
                "duration_s": (end_time - start_time) / 1000
            })

            current_chunk = []
            current_tokens = 0

        current_chunk.append(word_obj)
        current_tokens += tokens

    # Flush último chunk
    if current_chunk:
        chunks.append({...})

    return chunks

def ms_to_hms(ms: int) -> str:
    """Converte millisegundos em HH:MM:SS"""
    seconds = ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# Step 3: Embed e store
def embed_and_index_chunks(chunks: list, podcast_id: str):
    for chunk in chunks:
        # Embed com modelo (OpenAI, Cohere, ou local)
        embedding = get_embedding(chunk["text"])  # 1536-dim vector

        # Store em Pinecone com metadata
        vector_db.upsert(
            id=f"{podcast_id}_chunk_{chunk['start_ms']}",
            values=embedding,
            metadata={
                "text_preview": chunk["text"][:200],
                "timestamp": chunk["timestamp"],
                "duration_s": chunk["duration_s"],
                "podcast_id": podcast_id,
                "full_text": chunk["text"]
            }
        )

# Step 4: Search + Retrieve with timestamps
def search_audio_rag(query: str, podcast_id: str, top_k: int = 3):
    # Embed query
    query_embedding = get_embedding(query)

    # Vector search
    results = vector_db.query(
        vector=query_embedding,
        top_k=top_k,
        filter={"podcast_id": {"$eq": podcast_id}}
    )

    print(f"\n📻 Resultados para: '{query}'\n")
    for rank, result in enumerate(results, 1):
        metadata = result["metadata"]
        print(f"{rank}. 🔗 Jump to {metadata['timestamp']}")
        print(f"   Snippet: {metadata['text_preview']}...")
        print(f"   Duration: {metadata['duration_s']:.0f}s\n")

    return results

# Uso completo
transcript = transcribe_with_timestamps("https://example.com/podcast.mp3")
chunks = chunk_audio_transcript(transcript, chunk_tokens=800)
embed_and_index_chunks(chunks, podcast_id="my_podcast_001")

# Query
search_audio_rag("Qual framework foi recomendado?", podcast_id="my_podcast_001")
# Output:
# 1. 🔗 Jump to 01:23:45
#    Snippet: ...the team recommends using FastAPI for REST APIs, which scales...
```

## Stack e requisitos

**Transcrição:**
- AssemblyAI: $0.001/min, com word-level timestamps, suporta 99 idiomas
- Whisper: Grátis/open-source, timestamps aproximados, melhor offline
- Deepgram: $0.0043/min, streaming suportado

**Vector DB:**
- Pinecone: $0.04/M vectors (managed), ideal para produção
- FAISS: Open-source, embarcado em Python, 8GB+ RAM
- Milvus: Docker, 4GB+ RAM, ótimo custo-benefício

**Embedding:**
- text-embedding-3-large (OpenAI): 3072-dim, $0.02/M tokens
- BGE-large (open): 1024-dim, grátis, offline
- Cohere: 1024-dim, $0.1/M tokens

**Hardware:**
- CPU: 2-4 cores suficientes para indexação
- RAM: 8GB+ para armazenar índices locais (FAISS)
- Storage: ~1GB per 100 horas de áudio (chunked + metadata)

## Armadilhas

**Transcrição:**
- Áudio baixa qualidade = transcrição imprecisa (especialmente nomes próprios)
- Word-level timestamps variam por engine; Whisper é mais aproximado que AssemblyAI
- Idiomas minoritários: apenas AssemblyAI suporta bem (Deepgram limita a ~20 idiomas)

**Chunking:**
- Chunk muito pequeno (100 tokens): perda de contexto
- Chunk muito grande (2000+ tokens): busca fica imprecisa
- Sem respeitar sentence boundary: chunk pode quebrar mid-frase

**Embedding mismatch:**
- Se indexa com `text-embedding-3-large` e query com `BGE-small`, resultados ruins
- Sempre use MESMO modelo para indexação e query

**Custos:**
- 100 horas de podcast = ~$6 transcrição (AssemblyAI) + $2 embedding
- Se reindexar, custo dobra
- Considere batch processing para economizar

## Aparece em
- [[10-projetos-mcp-agents-rag-codigo]] - Projeto RAG over Audio
- [[retrieval-augmented-generation]] - Conceito base de RAG
- [[obsidian-com-ia-como-segundo-cerebro]] - Integrar podcasts no vault

---
*Conceito extraido em 2026-04-02*
