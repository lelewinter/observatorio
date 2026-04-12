---
tags: [finance, ai-agents, trading, portfolio, finbert, sentiment-analysis, quantitative-analysis, llm]
source: https://tradingagents-ai.github.io/ | https://github.com/TauricResearch/TradingAgents | https://github.com/ai4finance-foundation/finrobot
date: 2026-04-02
tipo: aplicacao
---

# Skill Pack Financeiro para Agentes IA: TradingAgents, FinRobot & Análise Quantitativa (2026)

## O que é

Skill pack financeiro é um **conjunto modular de ferramentas + modelos especializados** que equipam agentes IA com capacidades de análise profissional:

- **Coleta de dados**: Bloomberg-like (preços OHLCV, notícias, earnings)
- **Análise de sentimento**: FinBERT (modelo BERT treinado em textos financeiros)
- **Modelagem temporal**: Kronos (previsão de séries temporais)
- **Síntese**: Geração automática de relatórios, gráficos, recomendações

Dois frameworks dominam 2026:
1. **TradingAgents**: Multi-agente especializados (analyst fundamental, sentiment analyst, trader)
2. **FinRobot**: RAG + LLM para análise integrada

Ambos são open-source (MIT license), sem dependência de APIs proprietárias caras.

## Por que importa agora

1. **Democratização de análise hedge fund**: Historicamente, análise quantitativa era exclusiva de instituições com orçamento para Bloomberg ($20k+/ano). Agora qualquer pessoa consegue.

2. **Custo zero vs APIs pagas**: APIs financeiras (Alpha Vantage, IEX, Alpaca) custam €50-500/mês. TradingAgents roda local, sem custo recorrente.

3. **Análise em tempo real**: Agentes monitoram múltiplos ativos paralelo, geram alertas quando sinais mudam.

4. **Auditabilidade**: Código aberto permite entender exatamente como recomendações são geradas; caixa-preta proprietary é risco.

Leticia tem curiosidade por startups e negócios; análise automática de portfólio + detecção de oportunidades acelera learning.

## Como implementar

### 1. Setup Básico: TradingAgents (v0.2.3 - March 2026)

```bash
# Instalar
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
pip install -e .

# Dependências
pip install pandas numpy yfinance  # dados
pip install transformers torch     # IA
pip install anthropic              # ou openai para LLM
```

### 2. Arquitetura: Agentes Especializados

```python
from typing import List, Dict
import json
from dataclasses import dataclass

@dataclass
class MarketSignal:
    asset: str
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0-1
    reasoning: str
    timestamp: str

class FundamentalAnalyst:
    """Analisa dados fundamentais (P/E, ROE, growth)."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze(self, ticker: str, financial_data: Dict) -> Dict:
        """Analisar fundamentals."""
        
        prompt = f"""
        Você é um analista fundamental. Analise a empresa {ticker} com dados:
        
        P/E Ratio: {financial_data['pe_ratio']}
        ROE: {financial_data['roe']}
        Debt/Equity: {financial_data['debt_to_equity']}
        Revenue Growth YoY: {financial_data['revenue_growth']}
        
        Retorne análise em JSON:
        {{
            "rating": "BUY|SELL|HOLD",
            "target_price": float,
            "key_drivers": ["...", "..."],
            "risks": ["..."],
            "confidence": 0.0-1.0
        }}
        """
        
        response = self.llm.generate(prompt)
        return json.loads(response)

class SentimentAnalyst:
    """Analisa sentimento em notícias + redes sociais."""
    
    def __init__(self, model_name="ProsusAI/finbert"):
        from transformers import pipeline
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            device=0  # GPU
        )
    
    def analyze_news(self, ticker: str, news_items: List[str]) -> Dict:
        """Analisar sentimento em notícias."""
        
        sentiments = []
        for news in news_items:
            result = self.sentiment_pipeline(news[:512])  # truncar
            sentiment = result[0]
            sentiments.append({
                'text': news[:100],
                'label': sentiment['label'],  # positive, negative, neutral
                'score': sentiment['score']
            })
        
        # Agregar: média ponderada
        weighted_score = sum(
            (1 if s['label'] == 'positive' else -1 if s['label'] == 'negative' else 0) * s['score']
            for s in sentiments
        ) / len(sentiments) if sentiments else 0
        
        return {
            'ticker': ticker,
            'overall_sentiment': weighted_score,  # -1.0 (bearish) a +1.0 (bullish)
            'news_count': len(sentiments),
            'breakdown': sentiments
        }

class TechnicalAnalyst:
    """Analisa padrões técnicos."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze(self, ticker: str, price_history: List[float], dates: List[str]) -> Dict:
        """Analisar técnico com LLM."""
        
        # Calcular indicadores básicos
        ma_20 = sum(price_history[-20:]) / 20  # média móvel 20 dias
        ma_50 = sum(price_history[-50:]) / 50  # média móvel 50 dias
        rsi = self._calculate_rsi(price_history)  # RSI (momentum)
        
        prompt = f"""
        Analise técnico para {ticker}:
        
        Preço atual: {price_history[-1]}
        MA20: {ma_20}
        MA50: {ma_50}
        RSI(14): {rsi}
        
        Retorne JSON:
        {{
            "signal": "BUY|SELL|HOLD",
            "support": float,
            "resistance": float,
            "key_levels": [float, float]
        }}
        """
        
        response = self.llm.generate(prompt)
        return json.loads(response)
    
    def _calculate_rsi(self, prices: List[float], period=14) -> float:
        """Calcular RSI (Relative Strength Index)."""
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        seed = deltas[:period]
        up = sum(x for x in seed if x > 0) / period
        down = -sum(x for x in seed if x < 0) / period
        
        rs = up / down if down != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return rsi

class Trader:
    """Agente executivo que toma decisão final baseada em análises."""
    
    def __init__(self, llm_client, risk_profile="medium"):
        self.llm = llm_client
        self.risk_profile = risk_profile  # "conservative", "medium", "aggressive"
    
    def decide(self, ticker: str, fundamental: Dict, sentiment: Dict, technical: Dict, portfolio: Dict) -> MarketSignal:
        """Consolidar análises em decisão de trade."""
        
        # Pesos baseados em risk profile
        weights = {
            "conservative": {"fundamental": 0.6, "sentiment": 0.2, "technical": 0.2},
            "medium": {"fundamental": 0.4, "sentiment": 0.35, "technical": 0.25},
            "aggressive": {"fundamental": 0.2, "sentiment": 0.3, "technical": 0.5}
        }[self.risk_profile]
        
        # Consolidar scores
        fundamental_score = 1 if fundamental['rating'] == 'BUY' else -1 if fundamental['rating'] == 'SELL' else 0
        sentiment_score = sentiment['overall_sentiment']  # -1 a +1
        technical_score = 1 if technical['signal'] == 'BUY' else -1 if technical['signal'] == 'SELL' else 0
        
        consensus = (
            weights['fundamental'] * fundamental_score +
            weights['sentiment'] * sentiment_score +
            weights['technical'] * technical_score
        )
        
        # Determinar decisão e confiança
        if consensus > 0.5:
            signal = "BUY"
            confidence = min(consensus, 1.0)
        elif consensus < -0.5:
            signal = "SELL"
            confidence = min(abs(consensus), 1.0)
        else:
            signal = "HOLD"
            confidence = 0.5
        
        reasoning = f"""
        Fundamental ({weights['fundamental']:.0%}): {fundamental['rating']} ({fundamental['confidence']:.0%})
        Sentiment ({weights['sentiment']:.0%}): {sentiment['overall_sentiment']:.2f} (bullish-bearish scale)
        Technical ({weights['technical']:.0%}): {technical['signal']}
        Consensus score: {consensus:.2f}
        """
        
        return MarketSignal(
            asset=ticker,
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=str(pd.Timestamp.now())
        )

class PortfolioMonitor:
    """Monitora portfólio em tempo real, gera alertas."""
    
    def __init__(self, fundamental_analyst, sentiment_analyst, technical_analyst, trader):
        self.fundamental = fundamental_analyst
        self.sentiment = sentiment_analyst
        self.technical = technical_analyst
        self.trader = trader
    
    def analyze_portfolio(self, portfolio: Dict[str, float]) -> List[MarketSignal]:
        """Analisar cada ativo em portfólio, retornar sinais."""
        
        signals = []
        
        for ticker, quantity in portfolio.items():
            print(f"[{ticker}] Analisando...")
            
            # Coletar dados (assumindo funções auxiliares)
            financial_data = self._fetch_financial_data(ticker)
            news = self._fetch_news(ticker)
            price_history = self._fetch_price_history(ticker, days=100)
            
            # Análises em paralelo (ideal: usar threading)
            fundamental = self.fundamental.analyze(ticker, financial_data)
            sentiment = self.sentiment.analyze_news(ticker, news)
            technical = self.technical.analyze(ticker, price_history['close'], price_history['dates'])
            
            # Decisão
            signal = self.trader.decide(
                ticker, fundamental, sentiment, technical, 
                {'holdings': {ticker: quantity}}
            )
            
            signals.append(signal)
        
        return signals
    
    def generate_report(self, signals: List[MarketSignal]) -> str:
        """Gerar relatório estruturado."""
        
        report = "# Relatório de Portfólio - " + str(pd.Timestamp.now()) + "\n\n"
        
        buys = [s for s in signals if s.signal == 'BUY']
        sells = [s for s in signals if s.signal == 'SELL']
        holds = [s for s in signals if s.signal == 'HOLD']
        
        report += f"## Resumo\n"
        report += f"- **BUY signals**: {len(buys)}\n"
        report += f"- **SELL signals**: {len(sells)}\n"
        report += f"- **HOLD**: {len(holds)}\n\n"
        
        if buys:
            report += "## Recomendações de Compra\n"
            for signal in buys:
                report += f"- **{signal.asset}** (confiança: {signal.confidence:.0%})\n"
                report += f"  {signal.reasoning}\n\n"
        
        if sells:
            report += "## Recomendações de Venda\n"
            for signal in sells:
                report += f"- **{signal.asset}** (confiança: {signal.confidence:.0%})\n"
                report += f"  {signal.reasoning}\n\n"
        
        return report
    
    # Stubs para coleta de dados (implementar com yfinance, newsapi, etc.)
    def _fetch_financial_data(self, ticker):
        return {}
    
    def _fetch_news(self, ticker):
        return []
    
    def _fetch_price_history(self, ticker, days=100):
        return {'close': [], 'dates': []}

# Usar tudo junto
from anthropic import Anthropic

client = Anthropic()

fundamental_analyst = FundamentalAnalyst(client)
sentiment_analyst = SentimentAnalyst()
technical_analyst = TechnicalAnalyst(client)
trader = Trader(client, risk_profile="medium")

monitor = PortfolioMonitor(fundamental_analyst, sentiment_analyst, technical_analyst, trader)

# Analisar portfólio
portfolio = {"AAPL": 10, "TSLA": 5, "GOOGL": 8}
signals = monitor.analyze_portfolio(portfolio)

# Gerar relatório
report = monitor.generate_report(signals)
print(report)
```

### 3. FinRobot: RAG + Análise Integrada

FinRobot combina RAG (Retrieval-Augmented Generation) com LLM para análise integrada:

```python
from finrobot import FinanceBot
from finrobot.utils import RAGRetriever

# Inicializar bot com RAG
bot = FinanceBot(
    llm_model="claude-opus-4.6",
    retriever=RAGRetriever(
        documents_path="~/docs/financial_reports/",  # earnings, 10-K, etc.
        embeddings_model="all-MiniLM-L6-v2"
    )
)

# Query: análise integrada
response = bot.query("""
    Qual é meu melhor investimento agora?
    Portfolio: AAPL 10 ações, TSLA 5, GOOGL 8.
    Risk tolerance: médio.
    Time horizon: 2 anos.
""")

print(response)
# Output: Análise integrada levando em conta documents internos, dados públicos, histórico.
```

## Stack e requisitos

### Software & Modelos

```bash
# Core
pip install tradingagents finrobot

# Dados
pip install yfinance pandas numpy  # preços

# NLP
pip install transformers torch     # FinBERT, embeddings

# LLM
pip install anthropic              # Claude API

# Utilities
pip install requests beautifulsoup4  # web scraping de notícias
pip install newsapi-python           # API de notícias (opcional)
```

### Hardware Mínimo

- **CPU**: Qualquer i5/Ryzen 5
- **GPU**: Recomendado para FinBERT (RTX 3060+); CPU funciona mas lento (30s per news batch)
- **RAM**: 8GB (FinBERT + yfinance)
- **Internet**: Conexão estável (dados em tempo real)

### Dados & APIs

| Fonte | Dados | Custo | Cobertura |
|-------|-------|-------|-----------|
| **yfinance** (Yahoo) | Preços, fundamentals | Grátis | US, HK, CN |
| **Alpha Vantage** | Preços, technical | $0 (free, rate-limited) | Global |
| **Finnhub** | Earnings, guidance | €50+/mês | Global |
| **NewsAPI** | Notícias | €0 (free, 100/dia) | Global |

**Configurar dados localmente**:

```python
import yfinance as yf
import pandas as pd

# Baixar dados (cache local)
data = yf.download(['AAPL', 'TSLA', 'GOOGL'], start='2024-01-01', progress=False)

# Salvar cache
data.to_csv('price_history.csv')

# Carregar depois
df = pd.read_csv('price_history.csv', index_col=0, parse_dates=True)
```

## Armadilhas e limitações

### Técnicas

1. **Data snooping bias**: Testar estratégia em dados históricos (backtesting) pode gerar resultados falsamente otimistas. Sempre validar em out-of-sample (dados não vistos).

2. **FinBERT não é perfeito**: Modelo foi treinado em dados específicos (até 2020ish). Linguagem financeira nova ou jargão técnico pode não ser entendido. Testar em amostra antes de usar em produção.

3. **Atualização de modelos**: Modelos de ML treinados em 2020-2022 podem degradar em performance atual (market regime change). Re-treinar periodicamente.

4. **API rate limits**: yfinance e newsapi têm limites (100 requests/dia para newsapi free). Para monitoramento real-time de 1000+ ativos, exige premium ou API própria.

### Práticas

5. **Nunca confiar 100% em sinais**: Sinais são recomendações, não comandos. Sempre revisar fundamentalmente antes de executar trade real.

6. **Risk management obrigatório**: Implementar stop-loss, take-profit, position sizing automaticamente:

```python
def execute_trade(signal: MarketSignal, account_balance: float, max_risk_pct=0.02):
    """Executar trade com risk management."""
    
    # Risco máximo: 2% do portfólio
    risk_amount = account_balance * max_risk_pct
    
    # Calcular posição (assumindo stop-loss de 5%)
    stop_loss = 0.05
    position_size = risk_amount / (signal.asset_price * stop_loss)
    
    # Executar
    if signal.signal == 'BUY':
        buy_order(signal.asset, position_size, stop_loss=signal.asset_price * (1 - stop_loss))
```

7. **Atualizar sentimento frequentemente**: Notícias mudam rápido. Analisar sentimento a cada hora em mercado de negociação, não uma vez/dia.

### Conceituais

8. **Diferença entre previsão e recomendação**: Agente pode prever preço futuro com 70% acurácia, mas recomendação de trade depende de risk/reward ratio. Separar esses conceitos.

9. **Múltiplos time frames**: Sinais diferem em 1-dia, 1-semana, 1-mês. Consolidar em "ensemble" de time frames melhora robustez.

10. **Overfitting em back-tests**: Estratégia que funciona perfeitamente em histórico (99% Sharpe) é red flag. Reality check: humano consegue explicar por quê?

## Conexões

- [[portfolio-optimization-modern-theory|Portfolio Optimization: Modern Portfolio Theory]] — Markowitz, efficient frontier
- [[time-series-forecasting-lstm-gru|Time Series Forecasting: LSTM, GRU]] — modelos avançados além Kronos
- [[risk-management-var-cvar|Risk Management: VaR, CVaR]] — quantificação de risco

## Histórico

- 2026-04-02: Nota criada (conceitual)
- 2026-04-11: Expansão profunda com TradingAgents architecture, code examples, FinRobot RAG, backtesting pitfalls
