---
tags: [conceito, startup, produto, mercado, validacao, crescimento]
date: 2026-04-02
tipo: conceito
aliases: [Product-Market Fit, PMF, Fit de Produto-Mercado]
---
# Product-Market Fit — Alinhamento de Produto e Demanda Real

## O que e

Product-Market Fit (PMF) é o estado onde produto resolve um problema tão bem, e de forma tão desejada pelo mercado, que usuários retornam continuamente, pagam pelo produto, e o recomendam espontaneamente. Não é métrica única, mas composição de sinais: retenção acima de 50% Day 7, usuários pedindo features, churn baixo, NPS > 40.

PMF é qualitativo, não quantitativo — você sente quando está lá. Usuários usam produto sem que você peça. Eles descobrem bugs e mandam relatórios, não reclamações. Ao contrário, ausência de PMF manifesta como retenção abaixo de 30% em 7 dias, usuários que não voltam, e silêncio completo (ninguém pedindo features).

## Como funciona

**Sinais Mesuráveis de PMF**

1. **Retenção D7 >= 50%**: De cada 100 novos usuários, 50+ retornam em 7 dias. Abaixo disso, produto não é sticky.

2. **Retenção D30 >= 30%**: Menos stringent, mas relevante. Se apenas 30% retornam em 30 dias, economia de unidade não funciona (CAC > LTV).

3. **NPS >= 40**: Net Promoter Score via pergunta "Quanto provável você recomendaria este produto?" (0-10 escala). Scores 9-10 são promoters, 0-6 são detractores. NPS = % promoters - % detractores. Um NPS de 40 é "bom"; acima de 50 é "excelente".

4. **Churn < 5% mensal**: Se 5%+ dos usuários cancela por mês, LTV é baixo demais. Abaixo de 5% é saudável.

5. **Feedback Espontâneo**: Usuários mandam features requests sem ser solicitados. Isso indica engagement.

6. **Viral Coefficient >= 1**: Cada usuário traz >= 1 novo usuário (referral, word-of-mouth). Abaixo disso, crescimento requer paid ads.

**O que PMF NÃO é**

- Não é "todos amam meu produto" — 50% retorno em D7 é PMF, 50% também desistiram.
- Não é "vendi X cópias" — volume sem retenção é burn, não tração.
- Não é "lancei e explodiu" — hockey stick de usuários pode ser hype vazia se D7 retention cai para 20%.
- Não é permanente — PMF pode desaparecer se competitor surge ou mercado muda.

**Progressão até PMF**

1. **Problema Real**: Usuários descrevem dor intensa ("gasto 3h semanais em tarefa X")
2. **Solução Mínima**: MVP resolve dor (não perfeita, suficiente)
3. **Retenção Cresce**: D7 sobe de 20% → 40% → 60%
4. **Expansão Natural**: Usuários usam funcionalidades adicionais, pedem mais
5. **PMF**: Retenção, churn, referral atingem níveis saudáveis

## Pra que serve

**PMF como Portão Decisório**

Ter ou não ter PMF determina estratégia completa:

✓ **Se tem PMF**:
- Escalar aquisição paga (CAC/LTV viável)
- Investir em features (retenção aguenta)
- Contratar time (estrutura vai aguentar volume)

✗ **Se não tem PMF**:
- Parar aquisição (só perde dinheiro)
- Pivotar produto ou posicionamento
- Ou encerrar

**Quando Verificar PMF**

Tipicamente, ~100 usuários iniciais. Menos que 100 é ruído estatístico. Entre 100-500 começa ser claro. Acima de 500, PMF é praticamente definitivo se retenção está saudável.

**Negócio B2B vs. B2C**

PMF é mais fácil de atingir em B2B (feature-driven, uma pessoa pode impactar decisão de empresa). B2C requer escala maior porque usuários são atomizados, comportamento mais instável.

## Exemplo pratico

**Cenário 1: Saas de Rastreamento de Tempo (Tem PMF)**

Semana 1: 100 signups
- Day 7: 62 ativos (62% retenção) ✓
- Feedback: "Finalmente consegui entender quanto tempo gasto em cada projeto"
- Espontâneo: 8 fazem referral

Decisão: Tem PMF. Escala aquisição.

**Cenário 2: App Social de Gamificação (SEM PMF)**

Semana 1: 100 signups
- Day 7: 18 ativos (18% retenção) ✗
- Feedback: "Parece legal mas não sei pra que usar"
- NPS: 12 (detractores são maioria)

Decisão: Sem PMF. Volta pra entrevistas de usuários. Problema não é "gamificação legal", é "qual problema específico resolvemos?"

**Cenário 3: Tool Corporativo de Compliance (PMF Lento mas Real)**

Semana 1: 20 signups (B2B, adoption é lenta)
- Day 7: 12 ativos (60% retention) — parece bom, mas...
- Problema: Trial é 2 semanas, decisão de compra é 6 semanas
- Métrica correta: % que entra em contrato (não D7 retention)

Em 12 semanas: 8 de 20 assinam contatos anual ($1k cada). Isso é PMF B2B. D7 retention é métrica errada para esse segmento.

## Aparece em
- [[crescimento-escalonado-de-produto]] — Framework de estágios até PMF
- [[metricas-saas-essenciais]] — LTV, CAC, churn, retenção
- [[pivot-produto-estrategia]] — O que fazer quando PMF não existe

---
*Conceito extraído em 2026-04-02 a partir de estrutura de crescimento de startups*
