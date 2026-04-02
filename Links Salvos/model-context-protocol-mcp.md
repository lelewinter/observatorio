---
tags: []
source: https://x.com/techwith_ram/status/2038288464647774638?s=20
date: 2026-04-02
---
# Model Context Protocol (MCP)

## Resumo
MCP (Model Context Protocol) é um protocolo padronizado que define como modelos de linguagem se comunicam com ferramentas e fontes de dados externas. Ele resolve o problema de integração fragmentada entre LLMs e sistemas externos.

## Explicação
O MCP surge da necessidade de padronizar a forma como agentes de IA e LLMs acessam contexto externo — bancos de dados, APIs, arquivos, serviços — sem que cada integração precise ser construída do zero de forma ad hoc. Antes do MCP, cada ferramenta ou plataforma criava sua própria camada de integração, gerando inconsistência e retrabalho. O protocolo define contratos claros entre o modelo (cliente) e o servidor MCP, que expõe recursos, ferramentas e prompts de forma estruturada.

Arquiteturalmente, o MCP funciona com três camadas principais: o **Host** (a aplicação que usa o LLM, como um IDE ou chatbot), o **Client** (componente que faz a ponte entre host e servidor) e o **Server** (processo leve que expõe capacidades específicas — leitura de arquivos, execução de queries, chamadas de API). A comunicação segue um protocolo baseado em JSON-RPC, permitindo descoberta dinâmica de capacidades.

O conceito é especialmente relevante no contexto de sistemas multi-agente e pipelines RAG, pois o MCP pode servir como camada de acesso padronizado a fontes de conhecimento externas. Em vez de hardcodar integrações, o agente consulta o servidor MCP, que abstrai a complexidade do sistema subjacente. Isso torna arquiteturas agênticas mais modulares, reutilizáveis e seguras.

Construir um servidor MCP próprio envolve definir quais "tools" e "resources" ele expõe, implementar os handlers correspondentes e registrá-lo no host compatível (ex: Claude Desktop, Cursor). O ecossistema ainda é jovem, mas cresce rapidamente como infraestrutura padrão para agentes com acesso a ferramentas.

## Exemplos
1. **Servidor MCP para banco de dados**: expõe uma tool `query_db` que o LLM pode invocar para buscar registros — sem que o modelo precise conhecer o schema diretamente.
2. **Servidor MCP para sistema de arquivos**: permite que um agente leia, escreva e liste arquivos locais de forma controlada e auditável.
3. **Servidor MCP para APIs externas**: encapsula chamadas a serviços como GitHub, Notion ou Jira, expondo ações como tools que o modelo pode chamar durante raciocínio.

## Relacionado
*(Nenhuma nota existente no vault para conectar no momento.)*

## Perguntas de Revisão
1. Qual é a diferença entre um "resource" e uma "tool" na arquitetura MCP, e quando usar cada um?
2. Como o MCP se diferencia de simplesmente fazer function calling direto via API do modelo (ex: OpenAI tools)?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram