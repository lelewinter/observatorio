---
tags: [llm, agentes-ia, alucinacao, prompt-engineering, claude, confiabilidade]
source: https://x.com/KingBootoshi/status/2039521846773854651?s=20
date: 2026-04-02
---
# Instrução Anti-Alucinação em Agentes LLM

## Resumo
É possível instruir agentes LLM (como Claude) via arquivos de configuração (`claude.md`, `agents.md`) a nunca responderem com falsa confiança, forçando o modelo a admitir incerteza em vez de alucinar.

## Explicação
Modelos de linguagem como Claude têm uma tendência documentada de responder com alto grau de confiança mesmo quando estão errados — fenômeno conhecido como alucinação confiante. Isso é especialmente perigoso em contextos de geração e explicação de código, onde o modelo pode afirmar que um trecho funciona de determinada forma quando não funciona, ou prometer não repetir um erro e repetir.

A abordagem prática descrita no post consiste em adicionar instruções explícitas nos arquivos de contexto persistente do agente (`claude.md` ou `agents.md`). Esses arquivos funcionam como um "system prompt" de longo prazo, carregado em toda sessão. Ao inserir regras como "nunca afirme algo sobre código com certeza se não tiver verificado" ou "sempre indique o nível de confiança da sua resposta", o comportamento do modelo pode ser calibrado de forma consistente.

Esse padrão é uma forma de **prompt engineering defensivo**: ao invés de confiar no comportamento padrão do modelo, o desenvolvedor assume controle explícito sobre as heurísticas de resposta. É análogo a adicionar guardrails num pipeline de RAG ou definir temperatura baixa para tarefas que exigem precisão — uma camada de controle sobre a natureza probabilística do LLM.

O tom emocional do post ("I AM HURT CLAUDE") também revela um padrão comportamental importante: a relação de confiança entre desenvolvedor e agente de IA é frágil e assimétrica. O modelo não tem memória ou responsabilidade real; a responsabilidade de calibrar o comportamento recai inteiramente sobre quem constrói o sistema.

## Exemplos
1. **Arquivo `claude.md`** com regra: *"Se não tiver certeza sobre como uma função se comporta, diga explicitamente 'não tenho certeza' em vez de inferir."*
2. **Pipeline de código assistido por IA**: antes de confiar na explicação do agente sobre um bug, exigir via instrução que ele cite a linha exata e reconheça limitações de contexto.
3. **Agente de revisão de PRs**: instruir o agente a nunca aprovar ou reprovar código com certeza sem listar explicitamente as premissas que assumiu.

## Relacionado
*(Nenhuma nota existente no vault para linkagem direta.)*

## Perguntas de Revisão
1. Qual a diferença entre alucinação confiante e incerteza calibrada em LLMs, e como instruções no system prompt afetam esse comportamento?
2. Por que delegar a calibração de confiança ao próprio modelo via prompt é uma solução frágil, e quais alternativas arquiteturais existem?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram