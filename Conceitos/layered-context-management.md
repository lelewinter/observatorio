---
tags: [conceito, context-engineering, llm, arquitetura, otimizacao]
date: 2026-04-03
tipo: conceito
aliases: [Layered Context Management]
---
# Layered Context Management

## O que e

Layered Context Management é uma arquitetura de gerenciamento de contexto em múltiplas camadas hierárquicas onde diferentes tipos de informação são carregados seletivamente conforme a necessidade real de execução. Em vez de carregar toda a base de conhecimento disponível de uma só vez, o sistema decide dinamicamente o que entra na janela de contexto — e o que permanece fora dela até ser requisitado. O objetivo central é maximizar a capacidade funcional do sistema sem estourar o limite de tokens disponíveis.

## Como funciona

A arquitetura é organizada em camadas com políticas de carregamento distintas. A camada mais interna (Layer 1, ou Main Context) é sempre carregada e contém a configuração central do projeto — as instruções base, permissões globais e identidade do sistema. É o núcleo permanente e imutável do contexto em qualquer execução.

A camada intermediária (Layer 2, ou Skill Metadata) carrega apenas o frontmatter YAML de cada skill disponível — tipicamente 2 a 3 linhas por skill, com consumo inferior a 200 tokens por unidade. Isso permite que o sistema "conheça" centenas de skills simultaneamente, tendo visibilidade sobre o que existe e como acionar cada uma, sem carregar o conteúdo completo de nenhuma delas.

A camada mais externa (Layer 3, ou Active Skill Context) é carregada sob demanda: somente quando uma skill específica é ativada, seus arquivos `.md` e documentação associada são trazidos para o contexto. Arquivos de suporte como scripts e templates não são pré-carregados em nenhuma camada — eles são acessados diretamente no momento de uso, consumindo zero tokens enquanto estão ociosos.

O resultado é uma separação clara entre "saber que algo existe" (Layer 2) e "saber como fazer algo" (Layer 3), com o núcleo do sistema sempre estável (Layer 1).

## Pra que serve

A aplicação principal é viabilizar sistemas com grande número de capacidades (centenas de skills, ferramentas ou módulos) dentro de janelas de contexto fixas e limitadas — como as dos modelos de linguagem atuais. Sem essa arquitetura, carregar todas as skills simultaneamente consumiria a janela de contexto inteira antes de qualquer tarefa real começar.

**Quando usar:** sistemas com muitos módulos opcionais onde apenas uma fração é ativa em cada execução; agentes com múltiplas capacidades especializadas; pipelines que variam muito conforme o tipo de tarefa recebida.

**Quando não usar:** sistemas com pouquíssimas capacidades fixas onde o overhead de gerenciamento de camadas supera o benefício; contextos onde latência de carregamento sob demanda é inaceitável.

**Trade-offs relevantes:** o sistema ganha escala horizontal (mais skills sem custo fixo de tokens), mas introduz complexidade de resolução — é necessário um mecanismo de roteamento que interprete o metadata da Layer 2 e decida qual skill da Layer 3 ativar. Esse mecanismo de roteamento precisa ser preciso: um erro de seleção traz o conteúdo errado para o contexto e pode degradar a resposta.

Conecta diretamente com [[context-engineering|context-engineering]] como instância prática de engenharia de contexto deliberada, com [[skill-workflow-composition|skill-workflow-composition]] como o sistema que se beneficia desta arquitetura para compor workflows complexos, e com [[retrieval-augmented-generation|retrieval-augmented-generation]] como padrão conceitual análogo — ambos partem do princípio de carregar informação relevante apenas quando necessário.

## Exemplo pratico

Considere um sistema Claude com 200 skills definidas. Sem Layered Context Management, carregar todas as skills completas consumiria facilmente 200.000+ tokens — inviável. Com a arquitetura em camadas:

```
Layer 1 — Main Context (sempre presente):
  CLAUDE.md
  → configuração global, permissões, identidade do agente
  → ~500 tokens fixos

Layer 2 — Skill Metadata (sempre presente, ultra-compacto):
  200 skills × ~150 tokens de frontmatter YAML cada
  → ~30.000 tokens totais para visibilidade de TODAS as skills

  Exemplo de frontmatter de uma skill:
  ---
  name: generate-prd
  trigger: "criar PRD, documento de requisitos"
  version: 1.2
  ---

Layer 3 — Active Skill Context (sob demanda):
  Usuário pede: "crie um PRD para este projeto"
  → Sistema identifica skill generate-prd via metadata (Layer 2)
  → Carrega generate-prd.md + templates associados (~2.000 tokens)
  → Total na janela: ~500 + ~30.000 + ~2.000 = ~32.500 tokens

  Scripts e templates não usados nesta execução: 0 tokens consumidos
```

O sistema atende à tarefa com uma fração mínima do contexto que seria necessário para carregar tudo antecipadamente, mantendo capacidade de resposta para centenas de outros cenários possíveis.

## Aparece em

- [[implementar-sistema-de-3-camadas-de-context-engineering-com-claude-skills]] - O sistema de Skills utiliza exatamente 3 camadas (Main Context, Skill Metadata e Active Skill Context) para viabilizar centenas de skills sem estouro de contexto.

---
*Conceito extraido automaticamente em 2026-04-03*