---
tags: [conceito, opcoes, trading, theta, time-decay, financa]
date: 2026-04-02
tipo: conceito
aliases: [Theta Decay, Decomposição de Tempo]
---
# Theta Decay — Decomposição Temporal em Opções

## O que e

Theta decay é a perda de valor de uma opção conforme o tempo passa, independentemente do movimento do ativo subjacente. Expressa em valor dollar por dia (ex: "-$5/dia"), representa a taxa à qual uma opção perde extrinsic value (valor de tempo) quando tudo mais se mantém constante. Para vendedores de opções (short premium), theta decay é lucro; para compradores, é custo contínuo.

Formula matemática: Θ (theta) = taxa de mudança no preço da opção / variação de 1 dia. Theta é maior (em valor absoluto) próximo ao vencimento (expiration) e aumenta exponencialmente nos últimos 7 dias — esse padrão é a base de estratégias de trading focadas em tempo.

## Como funciona

**Mecanismo Temporal**

Uma opção de call/put tem dois componentes de valor:
1. **Intrinsic Value**: max(S - K, 0) para call; max(K - S, 0) para put. Não decai com tempo.
2. **Extrinsic Value (Valor de Tempo)**: Prêmio pago pela possibilidade futura. Decai diariamente conforme ativo subjacente tem menos tempo para se mover favorabilmente.

Exemplo: Call SPY Strike 400, SPY = 405 em 30 dias antes de expiration (expiração).
- Intrinsic: $5 (já está in-the-money)
- Extrinsic: $2 (prêmio remanescente, maior tempo = mais extrinsic)

7 dias antes de expiration (mesmo preço SPY 405):
- Intrinsic: $5 (idem)
- Extrinsic: $0.30 (decaiu muito; menos tempo = menos possibilidade de movimento lucro)

**Padrão de Decay Temporal**

Theta decay é não-linear. Nos primeiros 20 dias, decay é lento; nos últimos 7 dias, acelera. Isso porque cada dia que passa remove 1 unidade de tempo, e quando há poucos dias restantes, cada dia é uma fração maior do tempo total.

Analiticamente (Black-Scholes):
```
Θ = (dPrice / dTime)
  ≈ -Vega * (σ / (2*sqrt(T))) - r * K * exp(-r*T)

Onde:
- Vega: sensibilidade à volatilidade implícita
- σ: volatilidade histórica / implícita
- T: tempo até expiration (em anos)
- r: taxa de juros
- K: strike price
```

**Dinâmica em 0DTE (Zero Days To Expiration)**

Opções que expiram hoje têm theta extremo (muitas vezes aceleração de decay de horas). Uma opção OTM (out-of-the-money) 0DTE perde 80-90% do valor restante em 90 minutos finais antes do close. Traders de 0DTE ("QDTF" — Quant Day Trading Friday) exploram isso estruturalmente, vendendo premium que vai a zero em horas.

## Pra que serve

**Estratégias de Lucro com Theta**

1. **Covered Call / Cash-Secured Put**: Vender opções OTM coletando premium decadente. Se ativo não move muito, lucra de theta. Se move adversarialmente, assignment/loss, mas capped.

2. **Iron Condor / Butterfly Spread**: Venda de duplo spread (call spread + put spread), lucra de theta em ambos lados enquanto ativo fica em range.

3. **Calendar Spread**: Venda opção curta durabilidade (perto do vencimento), compra opção longa durabilidade. Explora diferença de theta decay entre as duas.

4. **Scalar de 0DTE**: Abrir múltiplas posições OTM em mesma semana (2o e 3o strikes away), deixar theta fazer o trabalho, fechar no final do dia com lucros.

**Trade-offs e Cuando NO Usar**

✓ **Usar quando**: mercado está em range, volatilidade implícita está elevada (mais extrinsic value pra vender), dias antes de evento (earnings, FOMC) que causará IV crush.

✗ **Evitar quando**: mercado está em trend forte (ativo vai bater stops), volatilidade implícita está muito baixa (pouco prêmio pra vender), dentro de 24h de evento econômico impactante (gap risk, além do theta não compensa risco).

**Gestão de Risco**

Theta favorable mas gamma desfavorável é perigo. Gamma = taxa de mudança de delta. Próximo ao strike (at-the-money), gamma é alto; uma volta contra você pode reverter lucros de theta em minutos. Exemplo: venda 10 puts, theta ganha $50 ao dia, mas movimento de 2% no ativo piora posição $500 (gamma loss). Sempre manter gamma sob controle quando faz short theta plays.

## Exemplo pratico

**Cenário: SPY Trading 400, 7 Dias Antes de Expiration**

Setup Iron Condor:
- Vende 400 Call Spread (vende 400 call, compra 402 call)
  - Prêmio recebido: $1.00 (inteiro call custa $1.50, spread comprado sai $0.50, lucro líquido $1.00)
  - Theta do lado call: +$0.15/dia

- Vende 400 Put Spread (vende 400 put, compra 398 put)
  - Prêmio recebido: $1.00 (idem)
  - Theta do lado put: +$0.15/dia

Total crédito: $2.00 por contrato (100 ações cada contrato = $200 por contrato)
Total theta: +$0.30/dia ($30 por contrato)

**Cenário 1: Ativo fica em range (399-401)**

Dia 1: SPY 400.5, theta ganha $30. Posição agora vale $1.70 (ao invés de $2.00 recebido).
Dia 3: SPY 400.1, theta ganha $90. Posição vale $1.10.
Dia 6: SPY 399.9, theta ganha $180. Posição vale $0.20.
Dia 7: SPY 400.0, theta ganha $20. Close 99% lucro ($198 em $200).

**Cenário 2: SPY sobe a 405**

Dia 2: SPY jumps 405. Call spread é agora ITM, max loss ($200 - $200 = $200 loss imediato). Gamma (delta acelerando) comprime lucro.

Decisão: Close call spread por $1.80 (loss $0.80 = -$80), manter put spread que ainda está OTM.
Resultado: -$80 no call, +$150 de theta/movimento no put = +$70 net (ainda lucro).

## Aparece em
- [[12-prompts-options-trading-theta-decay-claude]] — Automação de estratégias de theta com Claude
- [[gestao-de-risco-trading]] — Interação gamma/theta
- [[opcoes-greeks]] — Delta, gamma, vega, rho, theta

---
*Conceito extraído em 2026-04-02 a partir de análise estruturada de materiais de trading quantitativo*
