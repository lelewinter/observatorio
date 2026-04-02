---
tags: []
source: https://x.com/aaronjmars/status/2036230574822580675?s=20
date: 2026-04-02
---
# Otimização de Rate Limit por Janela Temporal

## Resumo
É possível maximizar o uso de assinaturas de LLMs com rate limit por janela temporal monitorando o endpoint de uso da API e disparando tarefas agendadas automaticamente antes do reset.

## Explicação
Serviços como Claude Pro/Max não limitam uso por dia corrido, mas por **janelas deslizantes de tempo** (no caso, 5 horas). Isso significa que o limite se reinicia após esse intervalo, e qualquer uso não consumido dentro da janela é simplesmente perdido — não acumula para o próximo ciclo.

A estratégia de otimização consiste em monitorar continuamente o quanto da janela atual já foi consumido via endpoint de uso (`GET /api/oauth/usage`, acessível com a chave de API do Claude Code). Com essa informação em mãos, um agente automatizado pode calcular quanto tempo resta na janela corrente e, se esse tempo for curto (ex: menos de 30 minutos), disparar um conjunto de tarefas agendadas — revisão de PRs, pesquisas, geração de código — até saturar o limite disponível.

Esse padrão de comportamento é essencialmente **throughput scheduling orientado a deadline de recurso**: em vez de executar tarefas em horários fixos ou sob demanda manual, o gatilho é a iminência do reset do rate limit. O agente transforma o desperdício de capacidade contratada em execução produtiva. A implementação referenciada (projeto `aeon`) expõe isso como uma "skill" — uma unidade de comportamento autônomo do agente.

Do ponto de vista de arquitetura de agentes, isso ilustra como **metadados de infraestrutura** (estado do rate limit) podem ser incorporados como sinais de controle no loop de decisão de um agente, não apenas como restrições passivas a serem respeitadas.

## Exemplos
1. **Revisão automática de PRs**: ao detectar menos de 30 min na janela, o agente envia todos os pull requests pendentes para análise pelo Claude antes do reset.
2. **Pesquisa em lote**: tarefas de summarização de artigos ou levantamento de documentação acumuladas ao longo do dia são processadas em rajada no final da janela.
3. **Geração de testes**: suítes de testes unitários para código recém-escrito são geradas automaticamente quando o agente identifica capacidade ociosa prestes a expirar.

## Relacionado
*(Nenhuma nota existente no vault para conectar no momento.)*

## Perguntas de Revisão
1. Qual a diferença entre um rate limit por janela deslizante e um rate limit por dia fixo, e por que isso muda a estratégia de otimização?
2. Como o padrão de usar metadados de infraestrutura como sinal de controle de agente se diferencia de um simples cron job agendado?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram