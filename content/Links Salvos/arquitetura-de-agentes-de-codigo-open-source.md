---
tags: []
source: https://www.linkedin.com/posts/cristianvieira-oficial_passei-um-tempo-no-reposit%C3%B3rio-que-a-langchain-share-7439666264974716929-HstF?utm_source=social_share_send&utm_medium=android_app&rcm=ACoAAAgQrLIB4LHRfm8oNhRCsOv9i7wGJSYJXQs&utm_campaign=share_via
date: 2026-04-02
---
# Arquitetura de Agentes de Código Open-Source

## Resumo
O projeto DeepAgents, da LangChain, expõe abertamente a estrutura arquitetural de agentes de código autônomos — até então restrita a produtos proprietários como Claude Code, Cursor e Codex. É model-agnostic e licenciado sob MIT.

## Explicação
Agentes de código como Claude Code, Cursor e Codex sempre operaram como caixas-pretas: o usuário fornece uma instrução e recebe código como saída, sem visibilidade sobre o que acontece entre esses dois pontos. O DeepAgents, projeto open-source da LangChain com influência arquitetural do Claude Code, torna esse "meio" explícito e auditável.

A arquitetura exposta inclui cinco componentes centrais: (1) **planning tools** para decomposição de tarefas antes da execução, (2) **file system access** para leitura, escrita e edição de arquivos, (3) **shell execution com sandboxing** para segurança na execução de comandos, (4) **sub-agents** para paralelização de trabalho complexo, e (5) **auto-summarização de contexto** para gerenciar limitações de janela de contexto dos LLMs. Esses componentes em conjunto formam o padrão arquitetural que diferencia um agente de código de um simples pipeline de geração.

O ponto crítico é que o projeto é **model-agnostic**: qualquer LLM pode ser conectado à mesma estrutura base, o que o torna uma referência de construção, não um produto final. Isso é relevante porque separa a arquitetura do agente do modelo subjacente — algo que Claude Code, por exemplo, levou aproximadamente um ano para implementar. Vale notar que o repositório existe há cerca de 6 meses (não é novidade de 2026), e a arquitetura, embora influenciada pelo Claude Code, difere dele em pontos importantes, especialmente na compatibilidade nativa com múltiplos LLMs.

Para quem está construindo sistemas agênticos, o DeepAgents funciona como uma **referência arquitetural aberta** — equivalente a ter acesso ao blueprint de engenharia de um produto antes fechado. Não replica o treinamento ou os dados do Claude Code, portanto não replica suas capacidades de raciocínio; abre apenas a estrutura de orquestração.

## Exemplos
1. **Construção de agente próprio**: usar o DeepAgents como template base para criar um agente de código interno conectado a um LLM local via Ollama, aproveitando a estrutura de planning + shell execution sem depender de APIs proprietárias.
2. **Auditoria de decisões do agente**: ao expor o ciclo de planejamento e execução, é possível inspecionar quais sub-tasks foram geradas e em que ordem, permitindo debugging e controle que ferramentas fechadas não oferecem.
3. **Orquestração multi-agente**: a estrutura de sub-agents pode ser usada como base para sistemas com múltiplos agentes especializados rodando em paralelo, como sistemas com 20+ agentes especializados por domínio de tarefa.

## Relacionado
*(Nenhuma nota relacionada no vault disponível para linkagem.)*

## Perguntas de Revisão
1. Quais são os cinco componentes arquiteturais centrais do DeepAgents e qual o papel de cada um no ciclo de execução de um agente de código?
2. Qual a diferença prática entre um agente de código model-agnostic e um acoplado a um modelo específico — e por que isso importa para quem constrói sistemas agênticos?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram