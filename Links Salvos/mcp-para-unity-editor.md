---
tags: [mcp, unity, ai-tools, game-dev, llm-integrations]
source: https://github.com/CoderGamester/mcp-unity
date: 2026-04-02
---
# MCP para Unity Editor

## Resumo
MCP Unity é uma implementação do Model Context Protocol que conecta assistentes de IA (como Cursor, Claude, Copilot) diretamente ao Unity Editor, permitindo que agentes de IA executem operações reais dentro do ambiente de desenvolvimento de jogos.

## Explicação
O **Model Context Protocol (MCP)** é um protocolo padronizado que define como modelos de linguagem (LLMs) se comunicam com ferramentas e ambientes externos. O MCP Unity aplica esse protocolo ao Unity Editor, criando uma ponte entre o editor e um servidor Node.js que expõe capacidades do Unity como "ferramentas" consumíveis por agentes de IA.

Na prática, o plugin permite que um assistente de IA não apenas leia e sugira código, mas **execute ações dentro do editor**: criar GameObjects, modificar componentes, rodar testes, manipular assets e executar itens de menu. Isso representa uma mudança qualitativa no uso de IA em desenvolvimento — de copiloto de código para agente com capacidade de agir no ambiente de desenvolvimento.

A arquitetura funciona em duas camadas: um pacote C# instalado no projeto Unity (que expõe uma API WebSocket para o editor) e um servidor MCP em Node.js que traduz chamadas do protocolo MCP em comandos para o Unity. IDEs compatíveis com MCP (VSCode, Cursor, Windsurf, Claude Code) se conectam ao servidor Node.js e ganham acesso às ferramentas Unity como se fossem funções nativas do assistente.

Um aspecto relevante é a integração automática com workspaces de IDEs: o plugin adiciona a pasta `Library/PackedCache` ao workspace, melhorando a inteligência de código e o autocompletion para pacotes Unity — o que beneficia tanto o desenvolvedor humano quanto o agente de IA operando no mesmo ambiente.

## Exemplos
1. **Automação de cena**: Um agente recebe o prompt "crie um inimigo com tag Enemy, desativado por padrão" e executa `update_gameobject` e `update_component` diretamente no editor, sem intervenção manual.
2. **Debugging assistido**: O assistente seleciona um GameObject específico via `select_gameobject`, inspeciona seus componentes e sugere correções contextualizadas com o estado real da cena.
3. **Pipeline de testes**: Integração com CI — um agente executa `run_tests` no Unity Test Runner e reporta resultados diretamente no chat do IDE.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Qual é a diferença arquitetural entre um LLM usado como copiloto de código e um agente LLM com acesso a ferramentas MCP no Unity?
2. Por que a padronização via Model Context Protocol é mais escalável do que integrações diretas e proprietárias entre IDEs e ferramentas externas?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram