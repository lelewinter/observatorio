---
tags: [conceito, MCP, agents, tools, schema]
date: 2026-04-02
tipo: conceito
aliases: [Model Context Protocol, MCP]
---

# MCP Tool Composition

## O que é

Model Context Protocol (MCP) é um standard aberto que define como agentes descobrem, entendem, e invocam ferramentas (tools) de forma modular. Cada servidor MCP expõe schemas JSON que descrevem inputs/outputs, permitindo composição automática sem acoplamento.

## Como funciona

Um servidor MCP implementa uma API simples: `list_resources()` e `call_tool(name, input)`. Cliente (agent) descobre todos os tools disponíveis via schema JSON:

```json
{
  "name": "vector_search",
  "description": "Busca documentos em base vetorial",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "top_k": {"type": "integer", "default": 5},
      "threshold": {"type": "number"}
    },
    "required": ["query"]
  }
}
```

Agent analisa schema, decide quando usar baseado em task, e invoca com parâmetros corretos. Orquestração é implícita e automática.

**Benefícios:**
- Desacoplamento: novo tool pode ser adicionado sem mudar agent code
- Type safety: schema força inputs corretos
- Discovery: agent descobre capabilities dinamicamente
- Composição: múltiplos MCPs podem ser chained

## Pra que serve

- Expandir capacidades de agent sem recompilação
- Integrar ferramentas externas (web, databases, APIs)
- Permitir fallbacks automáticos (vector search → web search)
- Construir agentic workflows escaláveis
- [[Indexacao de Codebase para Agentes IA]]
- [[agentes-de-ia-auto-aperfeicoaveis]]

## Exemplo prático

```python
# MCP Server expõe tools
mcp_server = {
    "tools": [
        {
            "name": "query_vector_db",
            "description": "Busca vetorial em documentos",
            "inputSchema": {...}
        },
        {
            "name": "web_search",
            "description": "Search na web via Tavily",
            "inputSchema": {...}
        }
    ]
}

# Agent descobre automaticamente
for tool in mcp_server["tools"]:
    print(f"Available: {tool['name']}")  # Available: query_vector_db, web_search

# Agent usa quando apropriado
user_query = "O que disse CEO sobre 2025?"
# Agent pensa: "Preciso buscar documentos internos"
# Agent chama: vector_search({"query": user_query})
# Se resultado fraco (score < 0.7), agent chama: web_search({"query": user_query})
```

## Aparece em
- [[10-projetos-mcp-agents-rag-codigo]] - Arquitetura base MCP + RAG
- [[agentscope-framework-multi-agente]] - Multi-agent com MCPs
- [[6-melhores-mcp-servers-assistente-ia-local]] - Servidores MCP prontos

---
*Conceito extraido em 2026-04-02*
