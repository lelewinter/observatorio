---
tags: [Claude, trading, options, theta decay, prompts, quantitativo, automação, renda]
source: https://x.com/heynavtoor/status/2030242736453169380
date: 2026-03-07
tipo: aplicacao
---
# Automatizar Trading de Opções com Claude — 78% Taxa de Acerto via Theta Decay

## O que e

Sistema de automação de trading de opções usando 12 prompts especializados para Claude, replicando estratégias de traders quantitativos profissionais (Citadel, Two Sigma, D.E. Shaw, Jane Street). Cada prompt encarna um papel específico no pipeline: análise de regime de mercado, seleção de strikes, cálculo de theta decay, gestão de risco. Objetivo: 0.5-2% de retorno diário consistente focado em venda de premium (theta decay) em vez de previsão direcional.

## Como implementar

**Arquitetura do Sistema**

O pipeline é composto por 12 prompts distintos, cada um representando um especialista independente em um domínio do trading de opções. A execução ocorre em sequência determinística: (1) regime de mercado classifica as condições atuais, (2) análise pré-mercado (8 AM) identifica janelas de oportunidade, (3) detecção de skew de volatilidade mapeia ineficiências, (4) seleção de strikes usa modelos probabilísticos, (5) gestão de risco define limites de posição, (6) calendário de renda integra estratégias recorrentes, (7) cálculo de theta monitora decay hora a hora, (8) captura de fim de dia executa closes nos últimos 90 minutos.

Cada prompt deve ser implementado como um agente Claude separado, acionado via API `messages` da Anthropic. A integração entre prompts ocorre via passagem de estado estruturado (JSON): o regime de mercado classifica as condições, e seus outputs alimentam Strike Selection como restrição. Similarmente, análise pré-mercado identifica oportunidades, Risk Management define posição máxima baseado em volatilidade observada, e Real-Time Theta monitora P&L contínuo.

**Implementação Prática em Python**

```python
import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

# 1. Market Regime Classifier
def classify_market_regime(price_data: dict) -> str:
    prompt = """You are a senior quantitative strategist at Citadel who classifies
market conditions into specific regimes before placing any options trade — because
the #1 reason theta traders lose is selling premium in the wrong environment.

Dados de mercado atuais:
- VIX: {vix}
- Slope de 50/200MA: {slope}
- ATR diário: {atr}
- Skew put/call: {skew}

Classifique em: TREND (bull/bear), RANGE_BOUND, VOLATILITY_SPIKE, CRUSH_SETUP"""

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# 2. Volatility Skew Exploiter
def detect_volatility_skew(option_chain: dict) -> dict:
    prompt = """You are a senior options trader at Akuna Capital who profits from
volatility skew — analyzing the phenomenon where OTM puts are priced more expensive
than equivalent calls.

Option Chain (simplified):
{chain}

Identify: (1) skew direction, (2) magnitude (in bps), (3) strike zones to target, (4)
width of spread to recommend (5 points, 10 points, 25 points?)"""

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text)

# 3. Strike Selection via Probability
def select_strikes_probability(symbol: str, regime: str, skew: dict) -> list:
    prompt = """You are a senior quantitative researcher at Two Sigma who selects
option strikes based purely on statistical probability models — removing emotion and
replacing gut feeling with math.

Symbol: {symbol}
Market Regime: {regime}
Volatility Skew: {skew}

For a SHORT premium strategy (iron condor or credit spread):
1. Calculate delta for each strike
2. Recommend strikes with win probability >= 65% (probability of profit = 1 - (max_loss / credit_received))
3. Return: [strike_1, delta_1, prob_1], [strike_2, delta_2, prob_2]"""

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text)

# 4. Real-Time Theta Decay Calculator
def calculate_theta_decay(positions: list, hours_elapsed: float) -> dict:
    prompt = """You are a senior options market maker at Susquehanna International who
quantifies exact theta decay profits on short premium positions hour by hour throughout
the trading day.

Positions (0DTE or 1DTE):
{positions}

Hours elapsed since open: {hours_elapsed}

Calculate and return:
- Theta decay per hour ($/hour)
- Cumulative profit from theta only
- Time remaining to max decay
- Estimated final theta if held to close"""

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text)

# 5. Risk Management System
def enforce_risk_rules(portfolio: dict, market_regime: str) -> dict:
    prompt = """You are a senior risk manager at Wolverine Trading who monitors options
portfolios in real-time and enforces strict risk rules that prevent catastrophic losses
— because surviving bad days is more important than maximizing good ones.

Current Portfolio:
{portfolio}

Market Regime: {market_regime}

Define and enforce:
1. Max loss per trade (% of account)
2. Max loss per day (% of account)
3. Max Greeks exposure (delta, gamma, vega)
4. Position size formula based on volatility
5. HARD STOPS: if any rule violated, return ["REDUCE", position_id, quantity_to_close]"""

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text)

# MAIN LOOP
def daily_theta_trading_cycle(market_data: dict):
    print("[08:00] Market Regime Analysis...")
    regime = classify_market_regime(market_data)
    print(f"Regime: {regime}")

    print("[08:15] Volatility Skew Detection...")
    skew = detect_volatility_skew(market_data['options'])

    print("[08:30] Strike Selection...")
    strikes = select_strikes_probability("SPY", regime, skew)

    print("[09:30] OPEN POSITIONS")
    # Execute trades based on strikes, with risk limits

    print("[15:30] REAL-TIME MONITORING")
    # Hourly theta decay tracking
    for hour in range(7):
        theta = calculate_theta_decay(positions, hour)
        print(f"Hour {hour}: Theta P&L = ${theta['cumulative_profit']}")

    print("[15:50] RISK ENFORCEMENT")
    # 10-minute final check
    risk_check = enforce_risk_rules(portfolio, regime)
    if risk_check.get('action') == 'REDUCE':
        close_position(risk_check['position_id'], risk_check['quantity'])

    print("[15:55] END-OF-DAY CAPTURE")
    # Close all 0DTE positions in final 5 minutes
    close_all_0dte()
```

**Integração com Dados Reais**

A alimentação de dados deve vir de APIs de mercado (Interactive Brokers, Tastytrade, ou Alpha Vantage para opções). Cada prompt aguarda JSON estruturado com preços, volatilidade implícita (IV), gregos (delta, gamma, theta, vega) e histórico de regime. O ciclo completo (coleta → análise → decisão → execução → monitoramento) deve levar menos de 5 minutos no início do dia e depois rodar em background, com checkpoint a cada 30 minutos.

**Orquestração e Fila de Mensagens**

Para escalar além de protótipos, considere fila de mensagens (Redis/RabbitMQ): cada agente enfileira eventos ("regime changed", "volatility skew detected"), e listeners reagem acionando análises dependentes. Isso desacopla prompts e permite replay de histórico para backtesting.

## Stack e requisitos

- **Linguagem**: Python 3.9+
- **Bibliotecas**: anthropic (API Claude), pandas (análise), requests (APIs de mercado)
- **API de Mercado**: Interactive Brokers TWS API, Tastytrade API, ou Alpha Vantage
- **Modelo Claude**: claude-opus-4-1 ou claude-3-5-sonnet (o custo aumenta com throughput)
- **Hardware**: Nenhum especial; roda em laptop
- **Custo API Anthropic**: ~$1-10/dia dependendo de volume de tokens e frequência de chamadas
- **Custo de Dados**: Gratuito (IB) ou $20-50/mês (market data premium)
- **Capital mínimo**: Recomendado $5k-10k para 0DTE trading com risco controlado

## Armadilhas e limitacoes

**Risco de "Siren Song" da Automação**: o sistema funciona bem em mercados normais (trending, range-bound), mas falha catastróficamente em gaps pós-earnings ou volatilidade extrema. A confiança no modelo pode levar a abertura de posições oversized justo quando é mais perigoso. Sempre incluir kill-switches automáticos.

**Latência e Execution Slippage**: prompts do Claude levam 500-1500ms por chamada. Em 0DTE onde segundos contam, isso pode significar preencher strikes piores ou perder janelas de oportunidade. Adicionar latência buffer na análise pré-mercado, ou usar modelos menores/mais rápidos para decisões em tempo real.

**Viés Backtest vs. Realidade**: histórico de dados é estacionário; mercados evoluem. Estratégias com 78% de acerto em backtesting caem para 60-65% em live trading porque competidores se adaptam. Sempre trade com posição reduzida enquanto valida em produção.

**Gestão de Risco Insuficiente**: mesmo com 5 prompts de risco, surpresas acontecem (halt, circuit breaker, erro de execução). Definir stop-loss absoluto por dólar, não percentual. Cúpula semanal de ganhos esperados, não perpetual.

**Dependência de Dados Limplos**: se data feed da API ficar atrasado ou duplicado, modelo recebe garbage e faz decisões erradas. Validar cada input (preços saem de bid-ask spread?, IV é razoável?) antes de passar para Claude.

**Viés de Sobrevivência**: você só vê estratégias que funcionaram. Muitos traders experimentam 50+ estratégias; 1-2 funcionam. Não assuma que esse framework específico é especial.

## Conexoes

[[theta-decay-opcoes]] — Conceito base de decaimento temporal
[[gestao-de-risco-trading]] — Frameworks de risco sistêmico
[[Anthropic API - Melhor Uso]] — Design de prompts para agendes autônomos
[[zettelkasten-automação-negocios]]

## Historico
- 2026-03-07: Nota criada a partir de X (Nav Toor, @heynavtoor)
- 2026-04-02: Nota reescrita e enriquecida pelo pipeline de curadoria — adicionados exemplos de código Python, stack técnico, armadilhas reais
