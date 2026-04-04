---
tags: [agentes-ia, frameworks, python, multi-agent, open-source, RAG, MCP, reasoning]
source: https://x.com/hasantoxr/status/2036531659378663490?s=20
date: 2026-04-02
tipo: aplicacao
---
# Construir Sistema Multi-Agente com AgentScope

## O que é
Framework Python nativo-multi-agente do Alibaba que integra memória persistente, RAG, MCP tools e raciocínio em arquitetura coesa. Permite designer visual de pipelines antes de codificar; suporta especialização de agentes por domínio; orquestra colaboração automática.

## Como implementar
**1. Instalação e setup básico**:

```bash
pip install agentscope
pip install agentscope[openai]  # ou outro provedor

# Clonar exemplos
git clone https://github.com/modelscope/agentscope
cd agentscope/examples/multi_agent_research
```

**2. Definir agentes especializados**:

```python
from agentscope import Agent, AgentConfig
from agentscope.models import ModelConfig

# Agente Planejador
planner_config = AgentConfig(
    name="planner",
    model_config=ModelConfig(
        model_type="claude",
        model_name="claude-3-5-sonnet-20241022",
        max_tokens=2000
    ),
    sys_prompt="""Você é um planejador estratégico.
    Dado um objetivo, quebre em sub-tarefas claras.
    Output em JSON: {"tasks": [{"id": 1, "description": "...", "owner": "researcher"}]}"""
)

planner = Agent(planner_config)

# Agente Pesquisador
researcher_config = AgentConfig(
    name="researcher",
    model_config=ModelConfig(model_type="claude", model_name="claude-3-5-sonnet"),
    sys_prompt="""Você é pesquisador especialista.
    Execute buscas, raspe fontes, sintetize.
    Sempre citar fontes com URLs e datas."""
)

researcher = Agent(researcher_config)

# Agente Crítico
critic_config = AgentConfig(
    name="critic",
    model_config=ModelConfig(model_type="claude", model_name="claude-3-5-sonnet"),
    sys_prompt="""Você é revisor crítico.
    Identifique gaps, inconsistências, alternativas não exploradas.
    Retorne lista de observações com severity score (0-1)."""
)

critic = Agent(critic_config)
```

**3. Configurar persistência de memória**:

```python
from agentscope.memory import Memory

# Memória por agente
planner_memory = Memory(
    agent_name="planner",
    memory_type="sqlite",
    db_path="agent_memory.db"
)

# Memória compartilhada entre agentes
shared_memory = Memory(
    memory_type="redis",
    host="localhost",
    port=6379,
    db=0
)

# Adicionar memória aos agentes
planner.memory = planner_memory
planner.shared_memory = shared_memory
```

**4. Integrar RAG para documentos internos**:

```python
from agentscope.rag import RAG, VectorStore

# Indexar documentos internos
vector_store = VectorStore(
    store_type="milvus",  # ou faiss, chromadb
    collection_name="internal_docs"
)

# Carregar PDFs, docstrings, etc
vector_store.add_documents([
    "docs/api_reference.md",
    "docs/best_practices.md",
    "internal_knowledge_base/"
])

rag = RAG(vector_store=vector_store, model="claude-3-5-sonnet")

# Adicionar RAG tool ao pesquisador
researcher.add_tool(rag.retrieve)
```

**5. Conectar ferramentas via MCP**:

```python
from agentscope.mcp import MCPClient

# Conectar ferramentas externas via MCP
mcp_client = MCPClient(
    server_url="http://localhost:3001",  # MCP server
    tools=[
        "github-search",
        "slack-notify",
        "postgres-query"
    ]
)

# Registrar em agentes
researcher.add_tool(mcp_client.call_tool)
```

**6. Orquestração do pipeline**:

```python
from agentscope.orchestration import Pipeline

# Definir pipeline
pipeline = Pipeline(
    name="research_pipeline",
    agents=[planner, researcher, critic],
    initial_agent="planner",
    transitions={
        "planner": {
            "researcher": "research_tasks_generated",
            "end": "goal_complete"
        },
        "researcher": {
            "critic": "findings_ready",
            "researcher": "more_research_needed"
        },
        "critic": {
            "researcher": "gaps_found",
            "end": "quality_acceptable"
        }
    }
)

# Executar
result = pipeline.run(
    initial_input={
        "goal": "Analise o impacto de quantização em modelos 7B",
        "context": "Para uma empresa de ML"
    },
    max_iterations=10
)

print(result)
```

**7. Visual Agent Builder (opcional)**:

```python
# Usar interface web para desenhar pipeline
# http://localhost:8080/agent-builder

# Ou em código:
from agentscope.viz import AgentDAG

dag = AgentDAG(
    agents=[planner, researcher, critic],
    connections=[
        ("planner", "researcher", "tasks"),
        ("researcher", "critic", "findings"),
        ("critic", "researcher", "feedback")
    ]
)

dag.visualize("pipeline.png")
```

**8. Monitoramento e logging**:

```python
from agentscope.monitoring import Monitor

monitor = Monitor(
    log_level="INFO",
    output_dir="agent_logs/",
    track_metrics=["latency", "token_usage", "agent_transitions"]
)

# Executar com monitoramento
result = pipeline.run(
    initial_input={"goal": "..."},
    monitor=monitor
)

# Visualizar métricas
monitor.plot_agent_timeline()
monitor.plot_token_usage()
```

## Stack e requisitos
- **Python**: 3.9+
- **Modelo base**: Claude 3.5 Sonnet, Qwen 72B, ou similar (AgentScope otimizado para Qwen)
- **Armazenamento**: SQLite local ou Redis/Milvus para shared memory + embeddings
- **MCP Server**: opcional, para integrar ferramentas externas (GitHub, Slack, DB)
- **Memória/CPU**: 8GB RAM mínimo; GPU opcional
- **Dependências principais**: `agentscope`, `langchain` (opcional), `redis`, `milvus-client`
- **Custo**: $0 local + custos de API de modelo (~$1-10 por pipeline execução médio)

## Armadilhas e limitações
- **Transições ambíguas**: defina claramente as condições de transição entre agentes. Transições vagas levam a loops infinitos.
- **Overload de agentes**: usar muitos agentes em paralelo pode saturar cota de API. Implemente retry com backoff.
- **Qualidade de critério**: agente crítico pode ter vieses. Combine com validação humana periódica.
- **Sincronização de memória**: se múltiplas instâncias rodam em paralelo, coordenação de shared memory é crítica (use locks).
- **Custo com iterações**: pipeline com muitas iterações (>10) pode ficar caro. Configure max_iterations agressivamente.

## Conexões
[[Arquitetura Multi-Agente com Avaliador Separado]], [[RAG com LLMs]], [[Tool Use com LLMs]], [[MCP - Model Context Protocol]], [[LangChain]], [[Qwen Models]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação