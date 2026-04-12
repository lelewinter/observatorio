---
tags: [machine-learning, time-series, foundation-models, forecasting, google, zero-shot, timesfm, quantile]
source: https://github.com/google-research/timesfm | https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/ | https://cloud.google.com/blog/products/data-analytics/timesfm-models-in-bigquery-and-alloydb
date: 2026-04-02
tipo: aplicacao
---

# TimesFM: Foundation Model para Previsão de Séries Temporais (Google 2026)

## O que é

TimesFM (Time Series Foundation Model) é um modelo pré-treinado do Google Research para previsão de séries temporais em modo **zero-shot**. Treinado em 100 bilhões de pontos temporais reais (cobrindo múltiplos domínios: clima, tráfego, energia, economia), consegue fazer previsões diretas sem fine-tuning.

**Versões atuais (2026)**:
- **TimesFM 1.0-200m**: 200 milhões parâmetros, contexto até 512 pontos
- **TimesFM 2.0-500m**: 500M parâmetros, contexto até 2048, 25% melhor accuracy
- **TimesFM 2.5** (março 2026): 200M parâmetros, contexto 16.000, quantiles para incerteza

Diferencial: Funciona direto; não precisa tuning, nem conhecimento de ARIMA/Prophet, nem hiper-parâmetros.

## Por que importa agora

1. **Democratização de forecasting**: Historicamente, previsões acuradas exigiam especialista tuning modelos (ARIMA, Prophet, LSTM). Agora, qualquer pessoa roda `timesfm.predict()` e obtém resultado competitivo.

2. **Generalização além domínios**: Modelos antigos (ARIMA) eram específicos de série. TimesFM viu padrões similares em bilhões de séries; generaliza para dados nunca vistos.

3. **Incerteza quantificada**: TimesFM 2.5 retorna quantiles (95%, 5%) junto com previsão, não apenas ponto estimado. Crítico para decisões.

4. **Speed**: GPU inference em ~10ms por previsão, viável em real-time (streaming).

Leticia estuda negócios/startups; previsões de demanda, receita, churn ajudam a entender métricas de negócio.

## Como implementar

### 1. Setup Básico

```bash
# Instalar
pip install timesfm google-cloud-bigquery  # BigQuery integration
# ou: pip install git+https://github.com/google-research/timesfm.git

# Opcional: GPU (CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Previsão Simples (Local)

```python
import numpy as np
import pandas as pd
from timesfm import TimeSeriesFoundationModel

# Carregar modelo (primeira execução: download ~500MB)
model = TimeSeriesFoundationModel(
    context_len=512,
    prediction_len=96,  # horizonte de previsão
    use_gpu=True  # ou False se CPU
)

# Dados de exemplo: 365 dias de tráfego web
dates = pd.date_range('2025-01-01', periods=365, freq='D')
traffic = np.array([1000 + 200*np.sin(2*np.pi*i/7) + np.random.normal(0, 50) 
                    for i in range(365)])

# Fazer previsão para próximos 96 dias
forecast = model.predict(
    context=traffic[-512:],  # últimos 512 pontos
    prediction_length=96
)

print("Previsão (próximos 96 dias):")
for i, value in enumerate(forecast[:10]):
    print(f"  Dia {i+1}: {value:.0f}")

# Visualizar
import matplotlib.pyplot as plt

plt.figure(figsize=(14, 6))
plt.plot(dates, traffic, label='Histórico')
plt.plot(pd.date_range(dates[-1], periods=97, freq='D')[1:], 
         forecast, label='Previsão TimesFM', linestyle='--')
plt.legend()
plt.xlabel('Data')
plt.ylabel('Tráfego (requisições)')
plt.title('Previsão de Tráfego Web com TimesFM')
plt.grid(alpha=0.3)
plt.show()
```

### 3. Uso Real: Previsão de Receita + Incerteza (TimesFM 2.5)

```python
import numpy as np
import pandas as pd
from timesfm import TimeSeriesFoundationModel

# Dados: receita mensal de startup (últimos 24 meses)
dates = pd.date_range('2024-01-01', periods=24, freq='M')
revenue = np.array([
    10000, 12000, 15000, 18000, 22000, 25000,
    28000, 32000, 35000, 38000, 42000, 45000,
    48000, 51000, 55000, 58000, 62000, 65000,
    68000, 72000, 75000, 80000, 83000, 85000
])  # crescimento de 8x em 2 anos

class ForecastingPipeline:
    def __init__(self):
        self.model = TimeSeriesFoundationModel(
            context_len=512,
            prediction_len=12,  # próximos 12 meses
            use_gpu=True
        )
    
    def forecast_with_intervals(self, values: np.array, confidence=0.95):
        """Previsão com intervalo de confiança."""
        
        # Previsão ponto
        forecast = self.model.predict(context=values[-512:], prediction_length=12)
        
        # Estimar intervalo (assumes normalidade; TimesFM 2.5 retorna quantiles direto)
        # Para demo, usar bootstrap simples
        n_bootstrap = 100
        bootstrap_preds = []
        
        for _ in range(n_bootstrap):
            # Adicionar ruído (simulating uncertainty)
            noisy_context = values[-512:] + np.random.normal(0, values.std() * 0.05, size=512)
            pred = self.model.predict(context=noisy_context, prediction_length=12)
            bootstrap_preds.append(pred)
        
        bootstrap_preds = np.array(bootstrap_preds)
        lower_bound = np.percentile(bootstrap_preds, (1-confidence)/2*100, axis=0)
        upper_bound = np.percentile(bootstrap_preds, (1+confidence)/2*100, axis=0)
        
        return {
            'point_forecast': forecast,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence': confidence
        }
    
    def generate_report(self, values: np.array, dates: pd.DatetimeIndex):
        """Relatório de previsão para stakeholders."""
        
        forecast_data = self.forecast_with_intervals(values, confidence=0.95)
        forecast = forecast_data['point_forecast']
        lower = forecast_data['lower_bound']
        upper = forecast_data['upper_bound']
        
        # Extrapolação para próximos 12 meses
        future_dates = pd.date_range(dates[-1], periods=13, freq='M')[1:]
        
        # Calcular CAGR histórico (crescimento anual)
        initial_revenue = values[0]
        final_revenue = values[-1]
        months = len(values)
        cagr = (final_revenue / initial_revenue) ** (12 / months) - 1
        
        report = f"""
# Previsão de Receita (TimesFM, Abril 2026)

## Resumo Executivo
- **Receita atual**: ${values[-1]:,.0f}
- **CAGR histórico**: {cagr:.1%}
- **Previsão 12 meses**: ${forecast[-1]:,.0f}
- **Crescimento esperado**: {(forecast[-1] / values[-1] - 1):.1%}

## Previsão Detalhada (com intervalo 95%)

| Mês | Ponto | Mín (5%) | Máx (95%) |
|-----|-------|----------|-----------|
"""
        
        for i, date in enumerate(future_dates):
            report += f"| {date.strftime('%b %Y')} | ${forecast[i]:,.0f} | ${lower[i]:,.0f} | ${upper[i]:,.0f} |\n"
        
        report += f"""

## Análise
- Confiança: 95%
- Modelo: TimesFM 2.5 (Google Research)
- Contexto histórico: {len(values)} meses
- Horizonte de previsão: 12 meses

## Recomendações
1. **Planejamento de recursos**: Orçamentar para crescimento de {(forecast[-1] / values[-1] - 1):.0%}
2. **Análise de sensibilidade**: Cenário pessimista (5º percentil) = ${lower[-1]:,.0f}
3. **Monitoramento**: Re-rodar modelo mensalmente; se receita desviar >15% da previsão, investigar causa.
"""
        
        return report

# Usar
pipeline = ForecastingPipeline()
report = pipeline.generate_report(revenue, dates)
print(report)
```

### 4. BigQuery Integration (Production)

Google integrou TimesFM nativamente em BigQuery (2026):

```sql
-- Previsão de séries temporais em BigQuery ML
CREATE OR REPLACE MODEL `project.dataset.revenue_forecast_model`
OPTIONS(
    model_type='LINEAR_REG',
    model_registry='vertex_ai',
    -- Use TimesFM foundation model
    time_series_model_type='TIMESFM'
) AS
SELECT
    DATE(date) as date,
    revenue as time_series_value,
    product_category as series_id
FROM `project.dataset.daily_revenue`
WHERE date >= '2024-01-01'
GROUP BY date, revenue, product_category;

-- Fazer previsão
SELECT
    forecast_timestamp,
    forecast_value,
    confidence_interval_lower_bound,
    confidence_interval_upper_bound,
    product_category
FROM ML.FORECAST(
    MODEL `project.dataset.revenue_forecast_model`,
    STRUCT(
        12 as horizon,         -- próximos 12 períodos
        0.95 as confidence_level
    )
);
```

### 5. Comparação: TimesFM vs Alternativas (2026)

| Modelo | Tipo | Zero-shot | Contexto | Incerteza | Velocidade | Código |
|--------|------|-----------|----------|-----------|-----------|--------|
| **TimesFM 2.5** | Foundation | ✓ | 16k | Quantiles | ~10ms | Open |
| **Kronos** | Foundation | ✓ | 4k | Não | ~50ms | Open |
| **ARIMA** | Classical | ✗ | N/A | IC (analítico) | Fast | Classic |
| **Prophet** | Hybrid | Parcial | ~100 | IC (bootstrap) | ~1s | Open |
| **LSTM/GRU** | Deep Learning | ✗ | 100-1k | Custom | ~100ms | Custom |

**Recomendação**:
- **Rápido + fácil**: TimesFM (qualquer série, sem tuning)
- **Interpretabilidade**: Prophet (decompõe trend/seasonality)
- **Máxima acurácia**: Ensemble (TimesFM + Prophet)

### 6. Detecção de Anomalias + Previsão

```python
class AnomalyDetectionPipeline:
    def __init__(self):
        self.model = TimeSeriesFoundationModel(context_len=512, prediction_len=1)
    
    def detect_anomalies(self, values: np.array, threshold_std=2.5):
        """Detectar outliers usando erro de previsão."""
        
        anomalies = []
        
        for i in range(512, len(values)):
            context = values[i-512:i]
            actual = values[i]
            
            # Prever próximo ponto
            predicted = self.model.predict(context=context, prediction_length=1)[0]
            
            # Erro: quantos desvios padrão?
            residual_std = np.std(context - np.mean(context))
            error_zscore = abs(actual - predicted) / residual_std if residual_std > 0 else 0
            
            if error_zscore > threshold_std:
                anomalies.append({
                    'index': i,
                    'actual': actual,
                    'predicted': predicted,
                    'error_zscore': error_zscore,
                    'severity': 'high' if error_zscore > 3.5 else 'medium'
                })
        
        return anomalies

# Usar
pipeline = AnomalyDetectionPipeline()
anomalies = pipeline.detect_anomalies(revenue)

for anom in anomalies:
    print(f"Anomalia em índice {anom['index']}: {anom['actual']:.0f} vs previsão {anom['predicted']:.0f} "
          f"(z-score: {anom['error_zscore']:.2f})")
```

## Stack e requisitos

### Hardware

| Cenário | GPU | CPU | Latência | Throughput |
|---------|-----|-----|----------|-----------|
| Demo local | RTX 3060 | i7 | ~10ms | 100 pred/s |
| Batch (1k séries) | RTX 4090 | - | ~5s total | 200 pred/s |
| Real-time streaming | T4 (cloud) | - | ~50ms p95 | 20 pred/s |
| CPU-only | - | i5 | ~500ms | 2 pred/s |

**Recomendação para Leticia**: GPU local não é crítico; CPU funciona para <100 séries/dia.

### Software

```bash
pip install timesfm torch numpy pandas scikit-learn

# Optional: visualização
pip install matplotlib seaborn plotly

# Optional: BigQuery
pip install google-cloud-bigquery google-cloud-bigquery-connection
```

### Modelos

Primeira execução do TimesFM baixa ~500MB de weights (cache em `~/.cache/`). Depois, offline.

## Armadilhas e limitações

### Técnicas

1. **Non-stationary data**: TimesFM assume alguma estacionaridade. Se série tiver trend forte ou regime shifts abruptos, performance degrada. Diferenciar antes:

```python
# Diferenciação: remover trend
diff_values = np.diff(revenue)  # hoje - ontem
forecast_diff = model.predict(context=diff_values[-512:], prediction_length=12)
forecast_original = revenue[-1] + np.cumsum(forecast_diff)
```

2. **Extrapolação além horizonte**: TimesFM é bom até ~100-200 passos. Além disso, reverter para média (mean reversion).

3. **Sazonalidade complexa**: Se série tem padrão semanal + mensal + anual, contexto de 512 pode ser insuficiente. Aumentar para 2048 (TimesFM 2.0).

### Práticas

4. **Validação em teste**: Não usar dados muito recentes para "validar" modelo (data leakage). Sempre split histórico/teste rigorosamente:

```python
split_idx = int(0.8 * len(revenue))
train = revenue[:split_idx]
test = revenue[split_idx:]

# Treinar em train (se fine-tuning), validar em test
```

5. **Recalibração frequente**: Market/comportamento muda. Re-treinar modelo a cada mês com dados novos.

6. **Intervalo de confiança não é risco**: TimesFM 2.5 retorna quantiles (95%, 5%), mas isso é **range de previsão**, não risco de decisão. Para risk = multiplicar por value-at-risk (VaR).

### Conceituais

7. **Diferença entre acurácia em teste e performance em produção**: Modelo que tem 5% MAPE (Mean Absolute Percentage Error) no teste pode ter 15% em produção se regime mudou. Sempre monitorar em tempo real.

8. **Ensemble é melhor**: TimesFM sozinho é bom, mas combinar com Prophet (usando média ponderada) melhora robustez. Prophet capta seasonalidade explícita; TimesFM capta padrões sutis.

```python
# Ensemble
forecast_timesfm = timesfm_model.predict(...)
forecast_prophet = prophet_model.predict(...)
ensemble_forecast = 0.6 * forecast_timesfm + 0.4 * forecast_prophet
```

9. **Contexto = informação**: Quanto mais histórico, melhor previsão (até certo ponto). 5 anos de dados > 1 ano. Mas muito histórico (20 anos) pode introduzir regime antigos irrelevantes.

10. **Multivariate vs univariate**: TimesFM é univariate (uma série). Se receita está correlacionada com marketing spend, usar LSTM multivariado melhora. Trade-off: complexidade.

## Conexões

- [[time-series-arima-prophet|Time Series: ARIMA, Prophet, Classical]] — alternativas complementares
- [[anomaly-detection-isolation-forest|Anomaly Detection: Isolation Forest, Z-score]] — detectar outliers
- [[financial-forecasting-lstm|Financial Forecasting com LSTM]] — deep learning para séries financeiras
- [[ensemble-methods-stacking|Ensemble Methods: Stacking, Voting]] — combinar múltiplos modelos

## Histórico

- 2026-04-02: Nota criada (conceitual)
- 2026-04-11: Expansão profunda com TimesFM 2.5, code examples, BigQuery integration, ensemble patterns
