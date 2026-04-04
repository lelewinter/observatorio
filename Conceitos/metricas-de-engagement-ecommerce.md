---
tags: [conceito, ecommerce, analytics, metricas, marketing, conversao]
date: 2026-04-02
tipo: conceito
aliases: [Engagement e Conversão em E-commerce, CTR CVR ROI]
---
# Métricas de Engagement e Conversão em E-commerce

## O que é

Conjunto de indicadores quantificáveis que medem eficácia de conteúdo de marketing em converter visualização em ação (click, visita, compra). Em contexto de UGC + TikTok Shop, as métricas críticas são: **Views** (alcance), **CTR** (click-through rate, qualidade de atração), **CVR** (conversion rate, qualidade de persuasão), **AOV** (average order value) e **ROAS** (return on ad spend). Cada métrica responde uma pergunta diferente.

## Como funciona

**Views (Alcance):**
Número total de vezes que vídeo foi exibido na timeline do usuário. Determinado por: algoritmo de recomendação do TikTok (engagement prévio, seguidor, tempo assistido), qualidade do hook (se usuário scrolla rápido = view conta mas não impacta algoritmo). Views = entrada do funil.

**CTR — Click-Through Rate:**
`CTR = (clicks em link → página do produto) / views × 100%`

Típico: 1-5% em ecommerce (2-3% é bom para UGC). Responde: "meu hook e copy convenceram o usuário a deixar TikTok e ir pro produto?" Alta CTR = hook forte, curiosidade gerada. Baixa CTR = hook fraco ou CTA invisível.

**CVR — Conversion Rate:**
`CVR = (compras completadas) / cliques × 100%`

Típico: 0.5-3% em ecommerce (1-2% é bom). Responde: "meu produto entregou a promessa do vídeo? Página de produto é convincente?" Alta CVR = alinhamento entre expectativa criada no vídeo e realidade do produto. Baixa CVR = bait-and-switch ou página de vendas ruim.

**AOV — Average Order Value:**
`AOV = receita total / número de compras`

Mede se cliente compra 1 unidade (AOV=R$45) ou 1 + complementos (AOV=R$120). Impactado por: recomendações "leve também", preço, bundle. Aumentar AOV em 20% = dobra lucro (margem típica ~40%).

**ROAS — Return on Ad Spend:**
`ROAS = receita atribuída / custo de publicação`

Se publica vídeo organicamente (custo ~0, apenas custo de criação), ROAS é alto (ex: R$10K receita / R$100 custo IA = ROAS 100:1). Se publica com budget pago em TikTok Ads, ROAS é menor (ex: R$10K receita / R$1K budget = ROAS 10:1). Target: ROAS ≥ 3:1 (para cada R$1 gasto, retorna R$3).

**Exemplo de cálculo integrado:**

```
Vídeo publicado (custo: R$50 de síntese IA)
1M views
CTR: 2.5% → 25K cliques
CVR: 1.2% → 300 compras
AOV: R$60
Receita: 300 × 60 = R$18K
ROAS: 18000 / 50 = 360:1 (orgânico é absurdo)

Se fosse publicado com R$500 de budget TikTok Ads:
Custo total: R$550
ROAS: 18000 / 550 = 32.7:1 (ainda excellent)
```

## Pra que serve

**Otimização de conteúdo:**
Identifique qual tipo de hook gera CTR alto (curiosidade? dor? FOMO?). Qual refina bem em CVR (honestidade? social proof?). Aloque criação pra padrões vencedores.

**Decisão de budget:**
Se CVR é 0.3% (ruim), aumentar budget de publicidade piora situação (publica mais do mesmo ruim). Primeiro fixe CVR (melhorar página, product messaging), depois escale com budget.

**Detecção de problema:**
- CTR baixo, CVR normal = problema no hook/copy/vídeo. Teste novos ângulos.
- CTR alto, CVR baixo = promessa quebrada. Vídeo exagera. Ajuste expectativa ou produto.
- Ambos baixos = produto ou público errado.

**Trade-offs e armadilhas:**

1. **Otimizar CTR pode prejudicar CVR:** Se gera clickbait extremo, CTR sobe mas CVR cai (usuário furioso, devolve). Balancear importância.

2. **Correlação vs. Causalidade:** Se vídeo A tem CTR 3% e vídeo B tem CTR 2%, não significa A é melhor — pode ser diferença de horário de publicação, audiência diferente, tamanho de account. Controlar variáveis.

3. **Atribuição é difícil:** Usuário vê vídeo 1, não compra. Vê vídeo 2, compra. Qual recebe crédito? TikTok oferece "last-click attribution" (crédito pra último vídeo), mas é enviesado. Multi-touch attribution é complexo.

4. **Métrica não é objetivo:** Otimizar ROAS é bom, mas se AOV é baixo, lucro ainda é fraco. Otimizar lucro (receita - custo - refundos) é o objetivo real.

## Exemplo prático

**Cenário:** Marca A testa UGC de esmalte Rouge Luxe em TikTok Shop. Publica 3 variações, coleta dados após 1 semana.

| Hook | Views | CTR | CVR | Compras | Receita | ROAS |
|------|-------|-----|-----|---------|---------|------|
| Dor ("descasca") | 500K | 1.8% | 0.9% | 81 | R$3,645 | 72.9:1 |
| Curiosidade ("brilha diferente") | 400K | 4.2% | 1.4% | 117 | R$5,265 | 105.3:1 |
| Prova Social ("vira fever") | 380K | 1.2% | 0.7% | 32 | R$1,440 | 28.8:1 |

**Insights:**
- Curiosidade vence em CTR (4.2% vs. 1.8%) e CVR (1.4% vs. 0.9%)
- Prova social é fraco demais
- Próxima rodada: gera 80% "curiosidade" + 20% experimental

**Decisão tática:**
Se marca tem budget pago de R$2K:
- Escala vídeo Curiosidade com R$1.5K (expected revenue: R$1.5K × 105.3 = R$157.95K — nonsense, means data é pequeno e variância alta)
- Teste experimental (novo hook) com R$500

Aprende rapidamente qual ângulo bate no mercado, escala winners.

## Aparece em
- [[producao-de-ugc-em-escala-com-ia]] — frameworks de medição e feedback
- [[producao-criativa-como-processo-estatistico]] — como métricas guiam iteração

---
*Conceito extraído em 2026-04-02*
