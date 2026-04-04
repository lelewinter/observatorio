---
tags: [mcp, protocolo, padronizacao, agentes, ferramentas]
source: https://x.com/techwith_ram/status/2038288464647774638?s=20
date: 2026-04-02
tipo: aplicacao
---

# Implementar Servidor MCP para Expor Ferramentas e Recursos

## O que e

Model Context Protocol é padrão aberto (JSON-RPC) que padroniza comunicação entre LLMs e servidores que expõem tools (ações invocáveis) e resources (dados legíveis). Abstrai complexidade de integração, permitindo agentes acessarem contexto externo de forma modular e segura.

## Como implementar

**Arquitetura MCP** (3 camadas):
- **Host**: Aplicação usando LLM (IDE, chatbot, CLI)
- **Client**: Componente dentro do host que conecta ao servidor MCP via JSON-RPC
- **Server**: Processo que expõe capabilities (tools + resources) como contrato padronizado

**Diferença entre Tool e Resource**:
- **Tool** (`callTool`): Ação invocável que modifica estado ou retorna resposta computada (ex: "execute_query", "send_email")
- **Resource** (`readResource`): Dados legíveis que fornecem contexto para decisões do LLM (ex: "list_database_schemas", "file_contents")

**Construir servidor MCP simples** (Node.js):
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "example-server",
  version: "1.0.0",
});

// Definir uma Tool
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "greet") {
    return {
      content: [{ type: "text", text: `Hello, ${request.params.arguments.name}!` }],
    };
  }
  throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
});

// Definir um Resource
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "file:///data/users.json",
        name: "User Database",
        description: "List of active users",
        mimeType: "application/json",
      },
    ],
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Registrar servidor em host** (Claude Desktop, Cursor, etc):
```json
// ~/.claude/settings.json ou .cursor/config.json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/mcp-server.js"]
    }
  }
}
```

**Exposição de database via MCP**:
```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "query_users") {
    const query = request.params.arguments.sql;
    const result = await db.query(query);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }],
    };
  }
});

server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "database://schema",
        name: "Database Schema",
        mimeType: "text/plain",
      },
    ],
  };
});
```

**Validação de argumentos** (type safety):
```typescript
const toolInputSchema = {
  type: "object" as const,
  properties: {
    sql: {
      type: "string",
      description: "SQL query to execute",
    },
    limit: {
      type: "number",
      description: "Max results (default 100)",
    },
  },
  required: ["sql"],
};

server.tool("query_db", "Execute SQL query", toolInputSchema, handler);
```

**Testar servidor** (MCP Inspector):
```bash
npx @modelcontextprotocol/inspector node /path/to/server.js
# Abre UI em localhost:3000 para testar tools
```

## Stack e requisitos

- **Node.js**: 18.0+
- **Linguagens suportadas**: Python, Node.js, Go, Rust (SDKs disponíveis)
- **Transporte**: stdio, HTTP, WebSocket
- **Schema validation**: JSON Schema (obrigatório para tools)
- **Latência**: <500ms esperado por tool call (depende da implementação)

## Armadilhas e limitacoes

- **Segurança**: Tools expostas são acessíveis ao LLM; NUNCA expor queries SQL raw sem validação/sanitização.
- **Timeouts**: Tool calls com latência >30s podem causar timeout no cliente; implementar async com callbacks.
- **Discovery**: Agente precisa conhecer tools disponíveis; usar descrições detalhadas e exemplos.
- **Error handling**: Se tool falha, server deve retornar erro estruturado; LLM pode ficar confused se resposta é ambígua.
- **Rate limiting**: Servidores MCP sem rate limiting podem ser explorados; adicionar circuit breakers.
- **Versionamento**: Mudar assinatura de tool quebra compatibilidade; documentar versões claramente.

## Conexoes

[[MCP Unity Editor Automacao Cenas]] [[MCP em Jogos Compilados Unity]] [[Orquestracao Hibrida de LLMs]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao