---
tags: []
source: https://x.com/aibuilderclub_/status/2038174485053046868?s=20
date: 2026-04-02
---
# Otimização de Tokens em LLMs

## Resumo
Estratégias deliberadas de uso do contexto e estruturação de prompts podem reduzir significativamente o consumo de tokens em ferramentas como Claude Code, sem perda de produtividade.

## Explicação
O consumo de tokens em agentes de código baseados em LLMs cresce rapidamente porque cada interação carrega o histórico acumulado da conversa, arquivos abertos, outputs de ferramentas e instruções do sistema. Esse custo composto é invisível para usuários iniciantes, mas rapidamente atinge limites de assinatura ou gera custos expressivos em uso intenso.

A otimização de tokens não é apenas economia financeira — ela reflete uma compreensão mais profunda de como LLMs processam contexto. Modelos como Claude operam com janelas de contexto fixas; quanto mais "ruído" (histórico irrelevante, arquivos desnecessários, respostas verbosas) ocupa essa janela, menor é a qualidade do raciocínio útil e maior o custo por tarefa. Reduzir tokens sem reduzir resultado exige disciplina na construção do contexto.

As táticas eficazes geralmente envolvem: compressão do histórico de conversa (resumir sessões antigas em vez de arrastá-las), carregamento seletivo de arquivos (passar apenas o trecho relevante, não o arquivo inteiro), uso de prompts de sistema enxutos e reutilizáveis, e aproveitamento de comandos de "reset" de contexto para tarefas independentes. A lógica central é: **contexto mínimo suficiente** para a tarefa atual.

Essa abordagem é análoga ao conceito de atenção esparsa em arquiteturas de transformers — não é necessário que todo token "veja" todos os outros para produzir bom resultado. Na prática do usuário, isso se traduz em hábitos de uso que imitam essa eficiência estrutural.

## Exemplos
1. **Compressão de sessão**: ao iniciar uma nova subtarefa, pedir ao modelo que resuma o que foi feito antes em 3 bullets e reiniciar o contexto a partir desse resumo.
2. **Carregamento cirúrgico de arquivos**: em vez de abrir `todo o projeto`, passar apenas a função ou classe relevante para o problema em questão.
3. **Templates de prompt reutilizáveis**: criar instruções de sistema padronizadas e curtas que substituem explicações longas repetidas a cada sessão.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Por que o histórico acumulado de conversa é a principal fonte de crescimento de tokens em agentes de código?
2. Qual é a diferença entre reduzir tokens por truncamento e reduzir tokens por compressão inteligente de contexto?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram