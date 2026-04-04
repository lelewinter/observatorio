---
tags: [conceito, saas, metricas, retenção, churn, produto]
date: 2026-04-02
tipo: conceito
aliases: [User Retention, Churn Rate, Cohort Retention]
---
# Retenção de Usuário — Métrica Crítica de Viabilidade de Produto

## O que e

Retenção é percentual de usuários que permanecem ativos em período pré-definido, tipicamente medido em cohorts (grupos de usuários que entraram na mesma data). Expressa como "Day 7 Retention" (D7R) ou "30-day retention" (D30R). Exemplo: 100 usuários entram no dia 1, 60 retornam no dia 7 → D7R = 60%.

O inverso é churn: taxa de saída de usuários. Se D7R = 60%, churn = 40%. Churn é melhor métrica para SaaS pois é linear: 5% churn mensal = LTV calculável de forma simples.

## Como funciona

**Cohort Analysis — Método Padrão**

1. Usuários são agrupados por data de signup
2. Para cada cohort, mede-se % ativo nos dias 1, 7, 14, 30, 60, 90, 365
3. Compara-se comportamento entre cohorts

Exemplo (Cohorte Janeiro 2026):
```
Signup Date | Day 1 | Day 7 | Day 30 | Day 60 | Day 90
2026-01-01  | 100%  | 62%   | 38%    | 28%    | 22%
2026-01-08  | 100%  | 58%   | 35%    | 25%    | 18%
2026-01-15  | 100%  | 65%   | 42%    | 31%    | 24%
2026-01-22  | 100%  | 60%   | 36%    | 26%    | 20%

Média Cohort Jan: D7R 61%, D30R 37%
```

Padrão típico: steep drop nos primeiros dias (users exploring), depois plateau. Se não plateau, produto nunca terá PMF.

**Métricas Relacionadas**

- **D7 Retention**: Mais importante. Indica "aha moment" ou "isso funciona".
- **D30 Retention**: Indica "comprometimento" de usuário. SaaS bom tem >= 30%.
- **Rolling Retention**: % usuários ativos semana T que ainda estão ativos semana T+1. Mais relevante para subscriptions.
- **Payback Period**: Quantos dias leva para LTV > CAC. Derivado de retention + pricing.

**Por Que Retenção é Mais Importante que Aquisição**

Equação de crescimento:
```
MRR = (New Signups × Conversion %) - (Existing Churn)

Se Churn = 10%, precisa 10% new signups só pra manter flat. Ilusão de crescimento.

Se Churn = 2%, precisa apenas 2% new, resto é puro growth.
```

**Diagnóstico: Por Que Usuários Saem**

Investigar churn via:
1. **Exit surveys**: Quando usuário cancela, pergunta "por quê?"
2. **Entrevistas com churned users**: 30 min call, pergunta profunda
3. **Behavioral analysis**: Que feature não usaram? Quanto tempo até churn?

Padrão comum:
- Usuários que usam Feature X regularmente: 5% churn
- Usuários que NUNCA usam Feature X: 80% churn
- Conclusão: Feature X é crítica para retenção

## Pra que serve

**Validação de PMF**

- D7R >= 50% = Provável PMF
- D7R 30-50% = Questionável, investigar
- D7R < 30% = Sem PMF, produto não é sticky

**Viabilidade Econômica**

SaaS típico com:
- MRR por usuário: $10
- CAC: $50
- Monthly churn: 5% (D30R = 95%)
- LTV = $10 / 0.05 = $200
- LTV/CAC = 200/50 = 4x ✓ (viável)

Com churn 10%:
- LTV = $10 / 0.10 = $100
- LTV/CAC = 100/50 = 2x ✗ (marginal, risky)

**Priorização de Produto**

Se D7R é 45% e você vê que "usuários que completam onboarding" têm D7R 65%, vs "que não completam" têm 20%, então:
- Prioridade #1: Onboarding
- Não: New features (não importa se usuários caem antes)

## Exemplo pratico

**Cenário: SaaS de Note-Taking**

Cohorte Março 2026, 200 signups:
- Day 0 (signup): 200/200 (100%)
- Day 1: 180/200 (90%) — 20 usuários exploram, saem
- Day 3: 140/200 (70%) — mais exploradores
- Day 7: 100/200 (50%) — D7R = 50% (limite de PMF)
- Day 30: 60/200 (30%) — D30R = 30%
- Day 90: 42/200 (21%) — steady state

Analysis:
- Drop to 50% em 7 dias é steep, mas não calamitoso
- Plateau em 21% sugere ~15-20 usuários "core" que amam produto
- Churn mensal: (100-60)/100 = 40% em primeiro mês (péssimo)
- Mas churn em mês 3: (60-42)/60 = 30% (ainda ruim)
- Steady state churn ~10-15% é quando "core users" começam a sair

Diagnóstico:
- Entrevista com 50% que churned em D7: "Parecia legal mas não entendi pra que usar"
- Core users (que permaneceram): "Uso pra organizar pesquisa; economizo 2h por semana"

Ação:
- Redesign onboarding pra destacar "valor de pesquisa" desde primeiro clique
- Teste: D7R sobe para 65% em próxima cohort
- D30R deve subir para 40-45%

## Aparece em
- [[crescimento-escalonado-de-produto]] — Retenção como gating function
- [[product-market-fit]] — PMF tem retenção alta como sinalizador
- [[metricas-saas-essenciais]] — Junto com LTV, CAC, payback

---
*Conceito extraído em 2026-04-02 a partir de análise de crescimento de SaaS*
