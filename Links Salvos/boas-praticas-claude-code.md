---
tags: []
source: https://x.com/techNmak/status/2037788648691884207?s=20
date: 2026-04-02
---
# Boas Práticas Claude Code

## Resumo
Conjunto de práticas documentadas pela equipe do Anthropic e pela comunidade para uso eficiente do Claude Code em desenvolvimento de software, cobrindo desde estrutura de arquivos de configuração até workflows paralelos e revisão cruzada entre modelos.

## Explicação
O Claude Code é um agente de codificação baseado em LLM que opera diretamente no terminal. Sem boas práticas, o agente tende a ignorar instruções, acumular contexto desnecessário e produzir código inconsistente em projetos maiores. O repositório `claude-code-best-practice`, com mais de 22K estrelas e autoria direta de Boris Cherny (Anthropic), consolidou o que realmente funciona no uso cotidiano da ferramenta.

Um princípio central é o **modo de planejamento com verificação**: antes de executar, o Claude deve criar um plano faseado com testes para cada fase, e o desenvolvedor deve fornecer mecanismos de verificação explícitos. O uso da ferramenta `AskUserQuestion` para entrevistar o usuário antes de iniciar é uma extensão desse princípio — o modelo coleta requisitos estruturados em vez de inferir. Isso reduz o fenômeno de "context drift", onde o agente perde coerência com os objetivos originais ao longo de uma sessão longa.

A gestão de contexto é outro eixo crítico. O arquivo `CLAUDE.md` deve ser mantido abaixo de 200 linhas por arquivo — arquivos maiores causam degradação na aderência às instruções, explicando por que "Claude ignora CLAUDE.md". Git Worktrees permitem desenvolvimento paralelo em múltiplos branches sem conflito de contexto. O comando `/loop` habilita tarefas recorrentes agendadas por até 3 dias, enquanto `/btw` permite conversas laterais sem interromper o fluxo principal de trabalho do agente.

A revisão cruzada entre modelos (Claude Code + Codex) representa uma prática arquitetural relevante: usar um modelo para gerar e outro para revisar aproveita diferenças de treinamento e vieses distintos, aumentando a taxa de detecção de bugs. O workflow RPI (Research-Plan-Implement) e o uso de sub-agentes específicos por feature (em vez de agentes genéricos de QA ou backend) alinham-se com a ideia de que especialização estreita melhora a qualidade da saída em sistemas multiagente.

## Exemplos
1. **Debugging com MCP + Chrome**: Conectar o Claude Code ao console do Chrome via MCP permite que o agente veja erros de runtime diretamente, sem que o desenvolvedor precise copiar e colar logs manualmente.
2. **Workflow RPI para features complexas**: Para implementar uma nova API, o agente primeiro pesquisa a documentação relevante, depois cria um plano com testes por fase, e só então implementa — reduzindo retrabalho por requisitos mal compreendidos.
3. **Revisão cruzada de plano**: Gerar o plano de implementação com Claude Code e submetê-lo ao Codex para revisão antes de executar, usando divergências entre os modelos como sinal de ambiguidade ou risco no design.

## Relacionado
*(Nenhuma nota existente no vault para conectar neste momento.)*

## Perguntas de Revisão
1. Por que manter o `CLAUDE.md` abaixo de 200 linhas melhora a aderência do agente às instruções?
2. Qual a diferença arquitetural entre usar um sub-agente específico por feature versus um agente genérico de QA, e por que isso importa em workflows multiagente?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram