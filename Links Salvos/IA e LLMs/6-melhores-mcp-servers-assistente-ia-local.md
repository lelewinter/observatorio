---
tags: [MCP, servers, LLM, local, assistente IA, avichawla, composable, tools]
source: https://x.com/_avichawla/status/1950443752608412090
date: 2025-07-30
tipo: aplicacao
---

# Montar Assistente IA 100% Local com 6 MCP Servers Essenciais

## O que é

Stack de 6 MCP (Model Context Protocol) servers complementares que quando compostos permitem construir assistente de IA completamente offline: navegação web, scraping, RAG multimodal, memória gráfica, execução de código, orquestração central.

## Como implementar

### 1. Setup Base: Arquitetura MCP

```
┌─────────────────────────┐
│   LLM Local (Llama 2)   │
└────────────┬────────────┘
             │
    ┌────────▼─────────────────────────┐
    │  MCP Client (Orchestrator)        │
    │  @llamafact ou custom hub         │
    └─────┬──────────────────────────┬──┘
          │                          │
    ┌─────▼──────────┐        ┌─────▼──────────┐
    │ Browser MCP    │        │ Scraping MCP   │
    │ @StagehendlerN │        │ @ffrecruit     │
    └────────────────┘        └────────────────┘
          │
    ┌─────▼──────────────────────────────┐
    │ Multimodal RAG (@rajkislal)        │
    │ Processa: texto, imagens, vídeo    │
    └──────────────────────────────────┬─┘
                                       │
    ┌──────────────────────────────────▼─┐
    │ Graph Memory (@omarayousafy)       │
    │ Armazena relacionamentos estrut.   │
    └──────────────────────────────────┬─┘
                                       │
    ┌──────────────────────────────────▼─┐
    │ Terminal MCP                       │
    │ Executa: scripts, comandos, debug  │
    └────────────────────────────────────┘
```

### 2. Instalação dos 6 Servidores

**MCP 1: @llamafact (Hub/Orchestrator)**

```bash
# Clonar e instalar
git clone https://github.com/llamafact/mcp-llamafact
cd mcp-llamafact
pip install -e .

# Config (~/.llamafactrc)
[mcp]
port = 3000
log_level = debug
```

**MCP 2: Browser (@StagehendlerN)**

```bash
pip install mcp-browser
# Registrar no hub
llamafact register --mcp mcp-browser --port 3001

# Uso: "navegue para https://example.com e extraia seções"
```

**MCP 3: Scraping (@ffrecruit)**

```bash
pip install mcp-scraper
llamafact register --mcp mcp-scraper --port 3002

# Config para estruturação
cat > scraper-config.json << 'EOF'
{
  "rules": {
    "papers": {
      "selector": "article.paper",
      "fields": {
        "title": "h1.title",
        "authors": "span.author",
        "abstract": "p.abstract",
        "url": "a.link@href"
      }
    }
  }
}
EOF
```

**MCP 4: Multimodal RAG (@rajkislal)**

```bash
pip install mcp-multimodal-rag
# Requisitos: CLIP embeddings, LLaVA para visão

llamafact register --mcp mcp-multimodal-rag --port 3003

# Config
cat > rag-config.json << 'EOF'
{
  "embedding_model": "BAAI/bge-large-en-v1.5",
  "vision_model": "llava-hf/llava-1.5-7b-hf",
  "vector_db": "faiss",
  "db_path": "./vector_index"
}
EOF
```

**MCP 5: Graph Memory (@omarayousafy)**

```bash
pip install mcp-graph-memory
# Requisitos: Neo4j ou GraphQL server local

llamafact register --mcp mcp-graph-memory --port 3004

# Iniciar GraphQL em background
docker run -d -p 7474:7474 -p 7687:7687 neo4j:5.0

# Config
cat > graph-config.json << 'EOF'
{
  "backend": "neo4j",
  "uri": "bolt://localhost:7687",
  "auth": {"user": "neo4j", "password": "password"},
  "schema": {
    "entities": ["Paper", "Author", "Topic"],
    "relations": ["AUTHORED_BY", "RELATED_TO", "CITES"]
  }
}
EOF
```

**MCP 6: Terminal MCP**

```bash
# Geralmente built-in em Anthropic SDK ou similar
# Permite execução de comandos shell seguros

cat > terminal-config.json << 'EOF'
{
  "allowed_commands": [
    "python", "bash", "npm", "git", "grep", "find"
  ],
  "sandbox": true,
  "timeout_seconds": 30
}
EOF
```

### 3. Cliente MCP: Integrar com LLM Local

```python
import asyncio
from mcp.client import MCPClient
import llama_cpp  # Para rodar Llama 2 localmente

# Inicializar LLM local
llm = llama_cpp.Llama(
    model_path="/models/llama-2-7b-chat.gguf",
    n_gpu_layers=-1,  # GPU aceleração
    n_ctx=4096,
    verbose=False
)

# Inicializar MCP client
mcp_client = MCPClient()

# Registrar todos os servidores
servers = [
    ("llamafact", "http://localhost:3000"),
    ("browser", "http://localhost:3001"),
    ("scraper", "http://localhost:3002"),
    ("rag", "http://localhost:3003"),
    ("graph", "http://localhost:3004"),
]

for name, url in servers:
    mcp_client.register_server(name, url)

# Main agent loop
async def research_agent(topic: str):
    """Pesquisa automática com composição de MCPs"""

    # Step 1: Browser + Scraper
    print(f"[1] Searching for '{topic}' papers...")
    browser_result = await mcp_client.call(
        "browser",
        "navigate",
        {
            "url": "https://scholar.google.com/scholar",
            "search_term": topic,
            "max_results": 10
        }
    )

    # Step 2: Scrape papers
    scraped_papers = await mcp_client.call(
        "scraper",
        "extract",
        {
            "html": browser_result["html"],
            "rule": "papers"
        }
    )
    # Output: [{"title": "...", "authors": [...], "abstract": "..."}]

    # Step 3: RAG index papers
    print(f"[2] Indexing {len(scraped_papers)} papers...")
    for paper in scraped_papers:
        await mcp_client.call(
            "rag",
            "upsert",
            {
                "id": paper["url"],
                "text": f"{paper['title']}\n{paper['abstract']}",
                "metadata": {"authors": paper["authors"]}
            }
        )

    # Step 4: Query RAG for insights
    insights = await mcp_client.call(
        "rag",
        "query",
        {"query": f"What are the main findings about {topic}?", "top_k": 5}
    )

    # Step 5: Store relationships in Graph Memory
    print(f"[3] Building knowledge graph...")
    for paper in scraped_papers:
        for author in paper["authors"]:
            await mcp_client.call(
                "graph",
                "create_relationship",
                {
                    "from_type": "Author",
                    "from_id": author,
                    "to_type": "Paper",
                    "to_id": paper["url"],
                    "relation": "AUTHORED_BY"
                }
            )

    # Step 6: Terminal - run analysis script
    print(f"[4] Running local analysis...")
    analysis = await mcp_client.call(
        "terminal",
        "execute",
        {
            "command": "python",
            "args": ["analyze_papers.py", "--papers", json.dumps(scraped_papers)]
        }
    )

    # Step 7: LLM synthesize everything
    context = f"""
    Papers found: {len(scraped_papers)}
    Top insights: {insights['results']}
    Analysis output: {analysis['stdout']}
    """

    response = llm.create_completion(
        prompt=f"Summarize research about {topic}:\n{context}",
        max_tokens=500
    )

    return response["choices"][0]["text"]

# Run
result = asyncio.run(research_agent("Large Language Models Safety"))
print(result)
```

## Stack e requisitos

**Hardware (mínimo):**
- CPU: 4+ cores (para parallelizar MCPs)
- RAM: 16GB (LLM 7B + embeddings + RAG index)
- GPU: 6GB VRAM (opcional, para aceleração)
- Disco: 50GB (modelos + índices)

**Modelos recomendados:**
- LLM: Llama 2 7B (13B para qualidade melhor)
- Embeddings: BAAI BGE-large (ou bge-small para RAM limitada)
- Vision: LLaVA 1.5 7B (para multimodal)

**Dependências:**
- Python 3.10+
- llama-cpp-python (inferência local)
- faiss-cpu (ou faiss-gpu)
- neo4j driver
- asyncio/uvicorn

**Custo (hardware local):**
- Zero custo operacional (vs $0.01/1K tokens com API)
- Payback em 2-3 meses vs cloud

## Armadilhas e limitações

**Performance:**
- LLM local 7B é 2-3x mais lento que Claude/GPT-4
- RAG com FAISS em CPU = latência +500ms per query
- Solução: GPU RTX 4070+ reduz a <100ms

**Qualidade:**
- Llama 2 inferior em reasoning vs Claude 3.5
- Embeddings locais (BGE) vs OpenAI (text-embedding-3) = 5-10% menos acurado
- Solução: Fine-tuning em dados próprios, ou usar Llama 3.1 70B (requer 48GB RAM)

**Orquestração:**
- 6 MCPs em paralelo = complexity. Erros em um pode quebrar pipeline
- Debugging difícil: stacktraces espalhados entre processos
- Solução: logging centralizado, timeouts explícitos, retry logic

**Manutenção:**
- Cada MCP precisa atualização independente
- Conflitos de dependências (MCP A requer lib X v1.0, MCP B requer v2.0)
- Solução: Docker containers por MCP, ou virtual envs

## Conexões

[[model-context-protocol-mcp]]
[[mcp-para-unity-editor]]
[[agentes-autonomos-multi-agente]]
[[10-projetos-mcp-agents-rag-codigo]]
[[Indexacao de Codebase para Agentes IA]]

## Histórico

- 2025-07-30: Nota criada
- 2026-04-02: Reescrita como guia prático com setup, configs, código completo
