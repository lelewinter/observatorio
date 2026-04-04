---
tags: [prompts, chatgpt, consultoria, produtividade, estrategia, ia]
source: https://www.linkedin.com/feed/update/urn:li:activity:7321258972898832387/
date: 2026-03-28
autor: "Alexandre Messina"
tipo: aplicacao
---

# Usar ChatGPT/Claude como Consultor McKinsey com Prompts Estruturados

## O que é

LLM com prompt estratégico replica raciocínio estruturado de consulting (MECE, hipóteses testáveis, priorização). Entrada: contexto empresa + problema. Saída: análise profissional de nível sênior.

## Como implementar

**1. Estruturar persona + contexto**

Template base:

```
Você é um consultor sênior da [McKinsey | BCG | EY]
especializado em [ex: growth strategy, product development].

Contexto da empresa:
- Setor: [indústria]
- Tamanho: [ARR, # clientes, # funcionários]
- Mercado: [TAM, competitors, posicionamento]
- Problema central: [métrica que está piorando | oportunidade]

Tarefa: [análise específica com estrutura]
```

Exemplo concreto:

```
Você é consultor sênior de Growth Strategy na McKinsey.

Contexto:
- Produto: SaaS B2B (procurement software)
- ARR: $2M, 50 clientes, 15 pessoas
- Churn: 18% mensal (crítico)
- Mercado: Procurement $50B+ TAM, fragmentado

Problema: Entender root causes de churn e design 30-day experiment plan

Estrutura resposta:
1. Três hipóteses mutuamente exclusivas (MECE)
2. Para cada: métricas para validar, experiment design, success criteria
3. Priorização: qual testar primeiro e por quê
4. Próximos passos: recursos, timeline
```

**2. Aplicar frameworks de consultoria**

**MECE (Mutually Exclusive, Collectively Exhaustive):**

Pergunta: "Estruture em 3 hipóteses MECE para este problema: [problema]"

Saída esperada:
```
1. Deficiência de produto (funcionalidades vs. competitors)
2. Falta de fit com ICP (wrong customer selection)
3. Go-to-market fraco (adoption/education insuficiente)
```

**Árvore de Problemas:**

```
Prompt: "Crie árvore de problemas para churn de 18%:
Root: [problema central]
├─ Causa 1.1, 1.2, 1.3
├─ Causa 2.1, 2.2
└─ Causa 3.1, 3.2

Para cada causa final: como você mediria?"
```

**Priorização (RICE/Impact-Effort):**

```
Temos 12 features no backlog, 1 sprint (10 days).
Aplique RICE (Reach, Impact, Confidence, Effort).
Rankear top 3.
```

**3. Casos prático estruturados**

| Tipo | Prompt Base |
|------|------------|
| Diagnóstico | "Analise [métrica] em degradação. Hipóteses root-cause. Validação em 30 dias." |
| Priorização | "Rank [lista items]. Frameworks: RICE ou Value-vs-Effort. Justifique top 3." |
| Estratégia produto | "Produto X estagna. Market opportunity [TAM]. Recomendação strategica: grow ou pivot?" |
| Negócio | "Fundado há [tempo]. Tração: [métricas]. Próximos milestone: [objetivo]. Plano 12 meses?" |

**4. Refinement iterativo**

Primeira resposta: geral
Refinamento: "Detalhe mais a hipótese 2. Quais sinais observaríamos se fosse verdade?"

Segundo refinement: "Qual é o custo de testar cada hipótese? Trade-off de learning vs. resource?"

**5. Documentação de saída**

Exportar como:
- Slide deck (copy-paste para PowerPoint)
- Executive summary (max 2 páginas)
- 90-day roadmap (priorizado)

## Stack e requisitos

- Claude 3.5 Sonnet ou GPT-4 (o modelo importa para qualidade)
- Contexto claro da empresa (métricas, competitors, história)
- Capacidade de pensar criticamente sobre resposta (modelo não substitui julgamento)

## Armadilhas e limitações

- **Não substitui expertise**: Consultor sênior traz intuição de 10+ years e cases. LLM não tem.
- **Cegueira de dados**: Usa apenas contexto você provê. Se contexto é biased ou incomplete, output é enviesado.
- **Tendência a evitar difícil**: Às vezes LLM propõe hipótese "segura" e óbvia. Desafiue.
- **Falta de domain specificity**: Consultoria real combina horizontal (estratégia) com vertical (indústria). LLM é melhor em horizontal.
- **Comunicação executiva**: Formata bem, mas pode não "land" sem storytelling humano.

## Conexões

[[geracao-automatizada-de-prompts]]
[[configuracao-de-contexto-para-llms]]
[[CLAUDE-md-template-plan-mode-self-improvement]]

## Histórico

- 2026-03-28: Nota criada
- 2026-04-02: Reescrita como guia de implementação
