---
tags: [conceito, monitoramento, anomalia, mudanca, deteccao, alertas]
date: 2026-04-02
tipo: conceito
aliases: [Change Detection, Anomaly Detection, Trend Analysis]
---
# Detecção de Mudanças e Anomalias em Dados Contínuos

## O que é

Técnica de análise que compara estado anterior vs. estado atual de dados periódicos (snapshots a cada 15min, 1h, 1dia) e identifica: (1) mudanças estruturais (novo elemento, remoção), (2) mudanças quantitativas (crescimento percentual), (3) anomalias (valor fora do padrão histórico).

Diferencia-se de "alerta estático" (se X > 100, trigger) porque lida com mudanças contextuadas: um valor pode ser normal num contexto e anômalo noutro.

## Como funciona

**Arquitetura de três camadas:**

```
Snapshot N-1 (estado anterior)
Snapshot N (estado atual)
  ↓
Comparação estrutural (diff)
  ↓
Comparação quantitativa (delta %)
  ↓
Contexto histórico (série temporal)
  ↓
Scoring de relevância/anomalia
  ↓
Notificação (se score > threshold)
```

**1. Comparação Estrutural (Diff):**

Para dados estruturados (JSON/dicts):

```python
import json
from deepdiff import DeepDiff

snapshot_anterior = {
    "usuarios_ativos": 1000,
    "pedidos": [
        {"id": 1, "valor": 100},
        {"id": 2, "valor": 200}
    ]
}

snapshot_atual = {
    "usuarios_ativos": 950,  # -50
    "pedidos": [
        {"id": 1, "valor": 100},
        {"id": 2, "valor": 250},  # mudou de 200 → 250
        {"id": 3, "valor": 300}   # novo
    ]
}

diff = DeepDiff(snapshot_anterior, snapshot_atual, verbose_level=2)

print(diff)
# Output:
# {
#   'values_changed': {
#     "root['usuarios_ativos']": {'old_value': 1000, 'new_value': 950},
#     "root['pedidos'][1]['valor']": {'old_value': 200, 'new_value': 250}
#   },
#   'iterable_item_added': {
#     "root['pedidos'][2]": {'id': 3, 'valor': 300}
#   }
# }
```

Isso te dá **o quê mudou** (estrutura). Próximo passo: **quanto** (magnitude).

**2. Comparação Quantitativa (Magnitude):**

```python
def calculate_delta(old_val, new_val):
    """Calcular mudança percentual com casos extremos"""
    if old_val == 0:
        if new_val == 0:
            return 0
        else:
            return 100 if new_val > 0 else -100  # Mudança infinita
    return ((new_val - old_val) / abs(old_val)) * 100

# Exemplos
print(calculate_delta(1000, 950))   # -5.0%
print(calculate_delta(200, 250))    # +25.0%
print(calculate_delta(0, 100))      # +100% (começou do zero)
```

**3. Contexto Histórico (Série Temporal):**

Um valor mudou em +25%. É anômalo? Depende do histórico:

```python
import statistics

historical_values = [100, 105, 98, 102, 110, 108, 95, 112, 100]
current_value = 250

mean = statistics.mean(historical_values)      # ~103
stdev = statistics.stdev(historical_values)     # ~6

# Quantos "desvios-padrão" o valor atual está distante da média?
z_score = (current_value - mean) / stdev

print(f"Z-score: {z_score}")  # ~24 (muito anomaloso!)

# Threshold comum: z_score > 3 = anomalia (99.7% confiança em distribuição normal)
is_anomaly = abs(z_score) > 3
```

**4. Scoring de Relevância (Contextualizado):**

Nem toda anomalia é importante. Exemplo: "taxa de conversão subiu 1000%" — relevante. Mas "campo timestamp mudou 0.001ms" — não relevante.

```python
def score_change_relevance(change_dict):
    """Score 0-10 onde 10=crítico, 0=ruído"""
    score = 0

    # Fator 1: Magnitude
    if abs(change_dict["percent_change"]) > 50:
        score += 5
    elif abs(change_dict["percent_change"]) > 10:
        score += 2

    # Fator 2: Z-score (anomalia estatística)
    if change_dict["z_score"] > 3:
        score += 3

    # Fator 3: Campo importante?
    important_fields = ["revenue", "churn", "errors", "latency", "cpu"]
    if any(field in change_dict["field_name"] for field in important_fields):
        score += 2

    # Fator 4: Direção (pior é pior)
    if change_dict["field_name"] == "latency" and change_dict["percent_change"] > 0:
        score += 1
    elif change_dict["field_name"] == "revenue" and change_dict["percent_change"] < 0:
        score += 1

    return min(score, 10)  # Cap at 10

# Exemplo
change = {
    "field_name": "revenue",
    "percent_change": -30,
    "z_score": 4.5
}
score = score_change_relevance(change)
print(f"Relevance score: {score}/10")  # 10 (crítico!)
```

**5. Integração com LLM para Contexto Humano:**

Scores numéricos são úteis mas não capuram contexto. Use LLM pra "traduzir" para ação:

```python
def explain_anomaly_with_llm(change, historical_context):
    """Usar Claude pra gerar explicação em linguagem natural"""
    import anthropic

    prompt = f"""
    Anomalia detectada em monitoramento:

    Campo: {change['field_name']}
    Valor anterior: {change['old_value']}
    Valor atual: {change['new_value']}
    Mudança: {change['percent_change']}%
    Z-score: {change['z_score']}
    Histórico (últimas 10 leituras): {historical_context}

    Possíveis causas (1-3 mais prováveis):
    - [Causa 1]
    - [Causa 2]
    - [Causa 3]

    Ação recomendada (urgência: LOW/MEDIUM/HIGH):
    - [Ação]

    Retorne JSON: {{"causes": [...], "urgency": "...", "action": "...", "monitoring": "..."}}
    """

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)
```

## Pra que serve

**Monitoramento de saúde de sistema:** Detectar degradação antes que usuários reclamem. Ex: latência P95 subiu 30% → investigar antes de outage.

**Detecção de fraude:** Padrão de compra muda drasticamente (usuário normal gasta R$100/mês, de repente compra R$10K em uma transação) → flag como suspeito.

**Análise de mercado:** Preço de ativo salta 10% em 1h (fora do padrão) → notificar trader.

**Monitoramento regulatório:** Taxa de erro em processamento de transações sobe para 5% (acima de SLA de 0.1%) → trigger escalação.

**Quando NÃO usar:**
- Dados altamente sazonais sem dessazonalização (ex: tráfego web é 10x maior na sexta). Usar seasonal decomposition antes.
- Dados com tendência linear forte (ex: crescimento anual consistente). Ajustar expectativa pela tendência.
- Quando há mudanças planejadas (deployment, manutenção). Usar "maintenance windows" para suprimir alertas.

## Exemplo prático

**Cenário:** Sistema de monitoramento de 5 APIs (Stripe, Twilio, OpenAI, Anthropic, AWS) com polling a cada 30min.

**Setup:**

```python
import psycopg2
from datetime import datetime, timedelta
import json

class APIHealthMonitor:
    def __init__(self, db_conn):
        self.db = db_conn
        self.apis = ["stripe", "twilio", "openai", "anthropic", "aws"]

    def fetch_and_store_snapshot(self):
        """Fetch status de cada API e armazenar"""
        cursor = self.db.cursor()
        for api in self.apis:
            try:
                status_code, latency_ms, errors_count = self.check_api(api)
            except:
                status_code, latency_ms, errors_count = -1, 9999, 0

            cursor.execute(
                "INSERT INTO api_snapshots (api_name, status_code, latency_ms, errors_count, timestamp) VALUES (%s, %s, %s, %s, NOW())",
                (api, status_code, latency_ms, errors_count)
            )
        self.db.commit()

    def check_api(self, api_name):
        """Simpler health check (status, latency, error_count)"""
        # Implementation: call actual API, measure response time, etc.
        pass

    def detect_anomalies(self):
        """Comparar snapshots e detectar mudanças"""
        cursor = self.db.cursor()

        anomalies = []
        for api in self.apis:
            # Buscar últimas 10 leituras
            cursor.execute(
                "SELECT latency_ms, status_code, errors_count FROM api_snapshots WHERE api_name = %s ORDER BY timestamp DESC LIMIT 10",
                (api,)
            )
            readings = [dict(zip(["latency", "status", "errors"], row)) for row in cursor.fetchall()]

            if len(readings) < 2:
                continue

            current = readings[0]
            previous = readings[1]
            historical = readings[2:10]

            # Calcular deltas
            latency_delta = ((current["latency"] - previous["latency"]) / previous["latency"] * 100) if previous["latency"] > 0 else 0
            error_delta = ((current["errors"] - previous["errors"]) / max(previous["errors"], 1) * 100)

            # Z-score de latência
            latencies_historical = [r["latency"] for r in historical]
            mean_latency = sum(latencies_historical) / len(latencies_historical)
            variance = sum((x - mean_latency) ** 2 for x in latencies_historical) / len(latencies_historical)
            stdev = variance ** 0.5

            z_score_latency = (current["latency"] - mean_latency) / stdev if stdev > 0 else 0

            # Scoring
            score = 0
            if abs(latency_delta) > 30:
                score += 5
            if z_score_latency > 3:
                score += 3
            if current["status"] != 200:
                score += 10
            if error_delta > 100:
                score += 5

            if score > 3:  # Threshold
                anomalies.append({
                    "api": api,
                    "score": score,
                    "latency_delta": latency_delta,
                    "error_delta": error_delta,
                    "z_score": z_score_latency,
                    "current_latency": current["latency"]
                })

        return anomalies

    def notify_anomalies(self, anomalies):
        """Enviar notificação se score > threshold"""
        for anom in anomalies:
            if anom["score"] >= 5:  # Medium-high risk
                message = f"""
⚠️ **API ANOMALY DETECTED**
API: {anom['api']}
Latency Delta: {anom['latency_delta']:.1f}%
Current Latency: {anom['current_latency']}ms
Z-score: {anom['z_score']:.2f}
Score: {anom['score']}/10
                """
                # Send to Slack/Telegram
                self.send_alert(message)

# Uso (em scheduler)
monitor = APIHealthMonitor(db_conn)
monitor.fetch_and_store_snapshot()
anomalies = monitor.detect_anomalies()
monitor.notify_anomalies(anomalies)
```

---
*Conceito extraído em 2026-04-02*
