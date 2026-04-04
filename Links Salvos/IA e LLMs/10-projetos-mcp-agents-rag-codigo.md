---
tags: [MCP, agents, RAG, Anthropic, projetos, workflow, book writer, audio RAG, multi-agent]
source: https://x.com/_avichawla/status/1911306413932163338
date: 2025-04-13
tipo: aplicacao
---

# Implementar Sistema RAG com MCP e Agentes Multi-Step

## O que é

Sistema de busca inteligente que combina Retrieval-Augmented Generation (RAG) com Model Context Protocol (MCP) servers e múltiplos agentes especializados. Permite compor funcionalidades modulares: vector search, web fallback, transcrição de áudio, e orquestração de tarefas complexas com planeamento e revisão.

## Como implementar

### Arquitetura Base: MCP + Vector Store + LLM

MCP (Model Context Protocol) standardiza como agentes descobrem e usam ferramentas. Cada servidor MCP expõe um schema de input/output:

```json
{
  "name": "vector_search",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "top_k": {"type": "integer", "default": 5},
      "threshold": {"type": "number", "default": 0.7}
    },
    "required": ["query"]
  }
}
```

O agent descobre este schema automaticamente e invoca quando apropriado. Exemplo flow para RAG com fallback:

```python
import anthropic
import json

client = anthropic.Anthropic()

# MCP tools registradas
tools = [
    {
        "name": "vector_search",
        "description": "Busca em knowledge base vetorial. Retorna documentos com scores.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "web_search",
        "description": "Fallback para web quando vector search não encontra resultado confiável.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
]

def vector_search(query, top_k=5):
    # Conectar em vector DB (Pinecone, Milvus, FAISS)
    # Retorna [{"text": "...", "score": 0.92, "source": "doc_id"}]
    pass

def web_search(query):
    # Usar Tavily, SerpAPI, ou equivalente
    # Retorna [{"title": "...", "url": "...", "snippet": "..."}]
    pass

# Agent loop
messages = [
    {"role": "user", "content": "O que disse o CEO sobre estratégia 2025?"}
]

while True:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=tools,
        messages=messages
    )

    # Coleta tool uses
    tool_uses = [b for b in response.content if b.type == "tool_use"]

    if not tool_uses:
        # Agent retornou resposta final
        final_text = next(
            (b.text for b in response.content if hasattr(b, 'text')),
            None
        )
        print(f"Final Answer: {final_text}")
        break

    # Executa cada tool
    tool_results = []
    for tool_use in tool_uses:
        if tool_use.name == "vector_search":
            result = vector_search(**tool_use.input)
        elif tool_use.name == "web_search":
            result = web_search(**tool_use.input)

        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "content": json.dumps(result)
        })

    # Adiciona assistant response + tool results ao contexto
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})
```

### Padrão Multi-Agent: Planning + Research + Writing + Review

Para tarefas complexas (gerar 20K palavras de livro), decomponha em agentes especializados:

```python
from dataclasses import dataclass

@dataclass
class BookOutline:
    title: str
    chapters: list[dict]  # [{"title": "Cap 1", "topics": [...]}]

def planning_agent(topic: str) -> BookOutline:
    """Gera estrutura de livro."""
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Crie outline para livro sobre: {topic}

Format JSON:
{{
  "title": "...",
  "chapters": [
    {{"title": "Cap 1: ...", "topics": ["tópico 1", "tópico 2"]}},
    ...
  ]
}}"""
        }]
    )
    outline_text = response.content[0].text
    # Parse JSON
    return BookOutline(**json.loads(outline_text))

def research_agent(chapter_topics: list[str]) -> str:
    """Pesquisa tópicos de um capítulo."""
    # Use MCP web_search para cada tópico
    # Retorna markdown com fontes
    pass

def writing_agent(chapter_outline: dict, research: str) -> str:
    """Escreve capítulo em prosa."""
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""Escreva capítulo estruturado:

Título: {chapter_outline['title']}
Tópicos: {', '.join(chapter_outline['topics'])}

Pesquisa fornecida:
{research}

Requisitos:
- 600-800 palavras
- Prosa clara e envolvente
- Cite fontes quando apropriado
- Inclua exemplos concretos"""
        }]
    )
    return response.content[0].text

def review_agent(chapter_text: str) -> str:
    """Revisa prosa, fatos, coesão."""
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=3000,
        messages=[{
            "role": "user",
            "content": f"""Revise e refine este capítulo:

{chapter_text}

Checklist:
- Clareza: frases muito longas?
- Fatos: há claims não-suportadas?
- Fluxo: conexões entre parágrafos?
- Tom: mantém voz do autor?

Retorne versão melhorada."""
        }]
    )
    return response.content[0].text

# Orquestração
outline = planning_agent("Inteligência Artificial em Saúde")
full_book = []

for chapter in outline.chapters:
    research = research_agent(chapter["topics"])
    draft = writing_agent(chapter, research)
    final = review_agent(draft)
    full_book.append(final)

print("\n\n".join(full_book))
```

### RAG over Audio: Transcrição + Embedding com Timestamps

Para podcasts/palestras, transcreva, chunk, e indexe com tempo:

```python
import requests
from datetime import timedelta

def transcribe_audio(audio_url: str) -> dict:
    """AssemblyAI: transcreve com timestamps para cada palavra."""
    headers = {"Authorization": "YOUR_ASSEMBLYAI_TOKEN"}

    response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json={"audio_url": audio_url}
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

    # Retorna {"text": "...", "words": [{"text": "word", "start": 1234, "end": 5678}]}
    return result

def chunk_with_timestamps(transcript: dict, chunk_tokens=500) -> list[dict]:
    """Divide transcrição em chunks mantendo timestamps."""
    text = transcript["text"]
    words = transcript["words"]

    chunks = []
    current_chunk = []
    current_tokens = 0

    for word_data in words:
        word = word_data["text"]
        tokens = len(word) // 4 + 1  # Aprox tokenização

        if current_tokens + tokens > chunk_tokens and current_chunk:
            chunk_text = " ".join([w["text"] for w in current_chunk])
            start_time = current_chunk[0]["start"]
            end_time = current_chunk[-1]["end"]
            chunks.append({
                "text": chunk_text,
                "start_ms": start_time,
                "end_ms": end_time,
                "timestamp": format_timestamp(start_time)
            })
            current_chunk = []
            current_tokens = 0

        current_chunk.append(word_data)
        current_tokens += tokens

    return chunks

def format_timestamp(ms):
    """Converte ms em HH:MM:SS."""
    s = ms // 1000
    h, m = divmod(s, 3600)
    m, s = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def embed_and_store(chunks: list[dict]):
    """Embed cada chunk e armazena em vector DB."""
    for chunk in chunks:
        # Embed com Claude embeddings (ou OpenAI)
        embedding = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"Summarize in 1 sentence: {chunk['text'][:500]}"
            }]
        ).content[0].text

        # Store em Pinecone/Milvus com metadata
        vector_db.upsert(
            id=f"podcast_{chunk['start_ms']}",
            vector=embedding,
            metadata={
                "source": "podcast",
                "timestamp": chunk["timestamp"],
                "text_preview": chunk["text"][:200]
            }
        )

def query_with_timestamp(user_query: str):
    """Query retorna chunk + link para exato tempo."""
    results = vector_db.search(user_query, top_k=3)

    for result in results:
        metadata = result["metadata"]
        print(f"🔗 Jump to {metadata['timestamp']}")
        print(f"Snippet: {metadata['text_preview']}...")

# Pipeline completo
transcript = transcribe_audio("https://example.com/podcast.mp3")
chunks = chunk_with_timestamps(transcript, chunk_tokens=500)
embed_and_store(chunks)
query_with_timestamp("Qual framework o expert recomendou?")
```

## Stack e requisitos

**Vector DB (escolha uma):**
- Pinecone: $0.04/M vectors, managed, serverless
- Milvus: Open-source, 8GB+ RAM, self-hosted
- FAISS: CPU-only, 4GB+ RAM, embarcado

**Embedding models:**
- Claude 3.5: ~$0.02/M tokens (texto+audio)
- OpenAI text-embedding-3-large: $0.02/M tokens
- MiniLM-L6: Open-source, 384-dim, offline

**Audio transcrição:**
- AssemblyAI: $0.001/min (com timestamps)
- Whisper (OpenAI): $0.006/min ou offline com onnx
- Deepgram: $0.0043/min, streaming suportado

**MCP Servers (exemplos):**
- sqlite: built-in (Anthropic)
- web-search (Tavily): ~$10/month
- codebase-mcp: open-source
- memory-tools: context persistence

**Requisitos de hardware:**
- Local RAG: 8GB RAM + GPU (recomendado 4GB VRAM)
- Cloud RAG: serverless (não há requisitos)
- Audio processing: 2GB para Whisper

## Armadilhas e limitações

**MCP + Agent loops:**
- Sem limites explícitos de iterações, agent pode loopear indefinidamente. Sempre defina `max_tokens` e adicione contador de turns.
- Tool schemas devem ser precise; agent não interpola inputs implícitos.

**RAG:**
- Threshold muito alto (0.9+) = sem resultados úteis; muito baixo (0.5) = ruído.
- Embedding mismatch: se índice foi criado com modelo X, query deve usar mesmo modelo X.
- Contexto fragmentado: chunks de 500 tokens podem quebrar explanações cohesivas. Teste 1000-1500 também.

**Audio:**
- Transcrição pode falhar em áudio de baixa qualidade ou idiomas minoritários.
- Timestamps word-level dependem de engine. AssemblyAI é confiável; Whisper é aproximado.
- Custos crescem rápido: 100 horas de podcast = ~$6 AssemblyAI + embeddings.

**Multi-agent workflows:**
- Sem coordenação, agentes podem conflitar. Adicione validation step entre Research → Writing.
- Prompt fatigue: cada agente precisa de prompt bem-estruturado. Templates + variables reduzem erro.
- Custo: Book Writer gasta ~$2-5 USD por livro (10K tokens planning + 40K tokens escrita/review).

## Conexões

[[model-context-protocol-mcp]]
[[retrieval-augmented-generation]]
[[agentes-especializados-vs-generalistas]]
[[6-melhores-mcp-servers-assistente-ia-local]]
[[Indexacao de Codebase para Agentes IA]]
[[agentscope-framework-multi-agente]]

## Histórico

- 2025-04-13: Nota criada
- 2026-04-02: Reescrita como guia aplicação com código, configs, armadilhas
