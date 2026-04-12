---
tags: [agent-router, llm, complexidade, orquestração, custo, performance]
source: https://x.com/RoundtableSpace/status/2036439229748666843?s=20
date: 2026-04-02
tipo: aplicacao
---
# Implementar Roteador de Complexidade para Orquestração de Agentes

## O que é

Um componente especializado que classifica requisições de IA por complexidade e roteia automaticamente para o executor mais apropriado:
- **Tarefas simples** (Q&A, cópia, formatação): modelos locais leves 2-7B via Ollama
- **Tarefas médias** (análise, síntese): modelos híbridos 7-13B
- **Tarefas complexas** (raciocínio profundo, multi-modal, planejamento): Claude 3.5 Opus, GPT-4o na nuvem

Pesquisa recente (ACL 2025, ICLR 2025) mostra que roteadores bem treinados reduzem custos em 85% enquanto mantêm 95% da qualidade de GPT-4. O roteador funciona como middleware entre coordenador de agentes e executores.

## Por que importa agora

1. **Redução de custo radical**: Roteador inteligente ≈ 37-46% menos tokens usados na nuvem
2. **Latência minimizada**: Tarefas simples em 50-100ms (local) vs 1-2s (nuvem)
3. **Escalabilidade**: Suportar 10x mais requisições com mesmo orçamento de API
4. **Pesquisa consolidada**: RouteLLM publicado em ICLR 2025, MasRouter em ACL 2025 com benchmarks sólidos
5. **Paradigma multi-agente maduro**: LangChain 0.1+, AutoGen 0.2+ têm suporte built-in para roteamento

## Como funciona / Como implementar

### Abordagem 1: Roteador baseado em SFT (Supervised Fine-Tuning)

```python
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import Literal
import requests
from anthropic import Anthropic

class ExecutorTier(Enum):
    LOCAL = "local"           # Phi 3 2B, TinyLlama 1.1B
    HYBRID = "hybrid"         # Mistral 7B, Qwen 7B via Ollama
    CLOUD = "cloud"           # Claude Opus, GPT-4o

@dataclass
class RoutingDecision:
    executor: ExecutorTier
    confidence: float  # 0-1
    reasoning: str
    complexity_score: float  # 0-1

class ComplexityRouter:
    """
    Router treinado para classificar tarefas por complexidade.
    Baseado em critérios semânticos (não apenas token count).
    """
    
    def __init__(self, ollama_base_url="http://localhost:11434"):
        self.ollama_url = ollama_base_url
        self.router_model = "mistral"  # ou qwen:7b
        self.anthropic_client = Anthropic()
        
        # Log de roteamentos para análise
        self.routing_log = []
        
        # Critérios de classificação (ajustáveis)
        self.criteria = {
            "logical_steps": 0.2,       # quantas etapas lógicas
            "interdependencies": 0.25,  # quantas dependências entre partes
            "multimodal_required": 0.25,  # precisa processar múltiplos tipos de dado
            "context_size": 0.15,       # tamanho do contexto necessário
            "reasoning_depth": 0.15     # profundidade de raciocínio
        }
    
    def classify_task(self, task_description: str, context: str = "") -> RoutingDecision:
        """
        Classificar tarefa usando modelo local como roteador.
        """
        
        # Prompt de classificação (calibrado empiricamente)
        classification_prompt = f"""Analise esta tarefa e classifique por complexidade de 0 a 1.

TAREFA:
{task_description}

{f"CONTEXTO: {context}" if context else ""}

Responda em JSON com:
{{
    "complexity_score": <float 0-1>,
    "logical_steps": <int estimado>,
    "needs_multimodal": <bool>,
    "reasoning_depth": <str 'shallow'|'medium'|'deep'>,
    "recommended_executor": <str 'local'|'hybrid'|'cloud'>,
    "confidence": <float 0-1>,
    "reasoning": <str explicação>
}}

Critérios:
- Scores < 0.3: tarefas rotineiras (formatação, cópia, resumo simples) → LOCAL
- Scores 0.3-0.6: análise moderada, síntese, tabelas → HYBRID
- Scores > 0.6: raciocínio complexo, planejamento, multi-step → CLOUD
"""
        
        # Chamar router modelo local para decisão rápida
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.router_model,
                "prompt": classification_prompt,
                "stream": False,
                "format": "json"
            }
        )
        
        try:
            classification = json.loads(response.json()["response"])
        except json.JSONDecodeError:
            # Fallback se resposta não for JSON válido
            return self._default_to_cloud()
        
        # Traduzir recomendação para ExecutorTier
        executor_map = {
            "local": ExecutorTier.LOCAL,
            "hybrid": ExecutorTier.HYBRID,
            "cloud": ExecutorTier.CLOUD
        }
        
        executor = executor_map.get(
            classification["recommended_executor"],
            ExecutorTier.HYBRID
        )
        
        decision = RoutingDecision(
            executor=executor,
            confidence=classification["confidence"],
            reasoning=classification["reasoning"],
            complexity_score=classification["complexity_score"]
        )
        
        # Log para análise posterior
        self.routing_log.append({
            "task_hash": hash(task_description) % 10000,
            "decision": executor.value,
            "confidence": decision.confidence,
            "complexity_score": decision.complexity_score
        })
        
        return decision
    
    def _default_to_cloud(self) -> RoutingDecision:
        """Fallback conservador para tarefa ambígua"""
        return RoutingDecision(
            executor=ExecutorTier.CLOUD,
            confidence=0.5,
            reasoning="Classificação falhou, usando fallback conservador",
            complexity_score=0.65
        )

class MultiExecutorAgent:
    """Agent orquestrador que usa router para decisões"""
    
    def __init__(self, router: ComplexityRouter):
        self.router = router
        self.local_executor = LocalExecutor()
        self.hybrid_executor = HybridExecutor()
        self.cloud_executor = CloudExecutor()
    
    def execute(self, task: str, context: str = "") -> dict:
        """
        Executar tarefa roteando automaticamente.
        """
        
        # Classificar
        decision = self.router.classify_task(task, context)
        print(f"[ROUTER] Score: {decision.complexity_score:.2f} → {decision.executor.value}")
        print(f"[ROUTER] Confiança: {decision.confidence:.2f}")
        print(f"[ROUTER] Razão: {decision.reasoning}\n")
        
        # Executar com fallback em cascata
        try:
            if decision.executor == ExecutorTier.LOCAL:
                result = self.local_executor.execute(task)
            elif decision.executor == ExecutorTier.HYBRID:
                result = self.hybrid_executor.execute(task)
            else:  # CLOUD
                result = self.cloud_executor.execute(task)
            
            result["executor"] = decision.executor.value
            result["router_score"] = decision.complexity_score
            
            return result
            
        except Exception as e:
            # Escalação: se executor primário falhar, tenta próximo tier
            print(f"[ERROR] {decision.executor.value} falhou: {e}")
            print(f"[FALLBACK] Escalando para tier superior...")
            
            if decision.executor == ExecutorTier.LOCAL:
                return self.hybrid_executor.execute(task)
            elif decision.executor == ExecutorTier.HYBRID:
                return self.cloud_executor.execute(task)
            else:
                raise

class LocalExecutor:
    """Executa em modelos locais 2-7B (Phi, Mistral)"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model = "phi"  # ~4GB VRAM
    
    def execute(self, task: str) -> dict:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": task,
                "stream": False
            }
        )
        
        return {
            "result": response.json()["response"],
            "latency_ms": 150,
            "tier": "local"
        }

class HybridExecutor:
    """Executa em SLM 7-13B ou combina chamadas local+cloud"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "mistral"  # 7B
    
    def execute(self, task: str) -> dict:
        # Opção 1: usar Mistral 7B puro
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": task,
                "stream": False
            }
        )
        
        return {
            "result": response.json()["response"],
            "latency_ms": 800,
            "tier": "hybrid"
        }

class CloudExecutor:
    """Executa em Claude ou GPT-4 via API"""
    
    def __init__(self, api_key=None):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    
    def execute(self, task: str) -> dict:
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": task}]
        )
        
        return {
            "result": response.content[0].text,
            "latency_ms": 2000,
            "tier": "cloud",
            "tokens_used": response.usage.output_tokens
        }

# Uso
router = ComplexityRouter()
agent = MultiExecutorAgent(router)

# Teste 1: Tarefa simples
result1 = agent.execute("Formatar este JSON: {a:1,b:2}")
print(f"Resultado: {result1['result']}\n")

# Teste 2: Tarefa média
result2 = agent.execute(
    "Analisar dados de vendas e gerar relatório de tendências",
    context="Dados: vendas aumentaram 15% em Q1, 10% em Q2, ..."
)
print(f"Resultado: {result2['result']}\n")

# Teste 3: Tarefa complexa
result3 = agent.execute(
    "Desenhar um plano de negócios para startup de IA educacional, incluindo go-to-market strategy"
)
print(f"Resultado: {result3['result']}\n")

# Análise
print("[STATS] Roteador:")
import json
print(json.dumps(router.routing_log, indent=2))
```

### Abordagem 2: Roteador com Feedback Loop (Melhoria Contínua)

```python
import csv
from datetime import datetime
from dataclasses import dataclass

@dataclass
class RoutingFeedback:
    task_hash: str
    decision: str
    actual_success: bool
    quality_rating: float  # 0-1 do usuário/avaliador
    latency_ms: int
    tokens_used: int
    timestamp: str

class AdaptiveRouter(ComplexityRouter):
    """Roteador que aprende com feedback dos roteamentos anteriores"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feedback_history = []
        self.executor_performance = {
            "local": {"success_rate": 0.8, "avg_quality": 0.75},
            "hybrid": {"success_rate": 0.92, "avg_quality": 0.88},
            "cloud": {"success_rate": 0.97, "avg_quality": 0.95}
        }
    
    def record_feedback(self, task_hash: str, decision: str, success: bool, quality: float):
        """Registrar resultado de um roteamento"""
        feedback = RoutingFeedback(
            task_hash=task_hash,
            decision=decision,
            actual_success=success,
            quality_rating=quality,
            latency_ms=0,
            tokens_used=0,
            timestamp=datetime.now().isoformat()
        )
        
        self.feedback_history.append(feedback)
        
        # Atualizar métricas de executor
        if success:
            self.executor_performance[decision]["success_rate"] *= 0.95
            self.executor_performance[decision]["success_rate"] += 0.05
        
        # Persist feedback em arquivo
        self._save_feedback(feedback)
    
    def _save_feedback(self, feedback: RoutingFeedback):
        """Salvar feedback em jsonl para análise"""
        with open("routing_feedback.jsonl", "a") as f:
            f.write(json.dumps(feedback.__dict__) + "\n")
    
    def get_performance_summary(self) -> dict:
        """Resumo de performance por executor"""
        return self.executor_performance
    
    def rebalance_thresholds(self):
        """Ajustar thresholds de classificação baseado em histórico"""
        # Análise: se muitos roteamentos para CLOUD falharam,
        # aumentar threshold ou reverter para HYBRID
        
        cloud_decisions = [f for f in self.feedback_history if f.decision == "cloud"]
        if not cloud_decisions:
            return
        
        cloud_success = sum(1 for f in cloud_decisions if f.actual_success) / len(cloud_decisions)
        
        print(f"[ANALYSIS] Cloud success rate: {cloud_success:.2%}")
        
        if cloud_success < 0.90:
            print("[WARN] Cloud executor performance degradado, revisar classificações")

# Uso
adaptive_router = AdaptiveRouter()
agent = MultiExecutorAgent(adaptive_router)

# Executar tarefa
result = agent.execute("Tarefa X")

# Simular feedback do usuário
adaptive_router.record_feedback(
    task_hash=hash("Tarefa X"),
    decision=result["executor"],
    success=True,
    quality=0.92  # Usuário nota 0.92/1.0 de qualidade
)

print(adaptive_router.get_performance_summary())
```

## Stack técnico

### Roteador (Classificação)
- **Modelo local**: Mistral 7B, Qwen 7B, Hermes 7B
- **Latência**: ~100-500ms em CPU, 50-100ms em GPU
- **Tamanho**: 7B models = 14-15GB VRAM comprimido

### Executores
- **Local**: Ollama (qualquer modelo 2-13B), LM Studio, vLLM
- **Hybrid**: SLM 7-13B (Mistral, Qwen, Hermes), ou chamar Anthropic API com `max_tokens` baixo
- **Cloud**: Claude Opus/Sonnet, GPT-4o, Gemini 2.0

### Frameworks
- **LangChain 0.1+**: suporte nativo para roteadores via `RouterChain`
- **AutoGen 0.2+**: `routing_strategy` parameter
- **Custom**: `requests` + `httpx` para polling

### Storage
- **Redis**: cache de decisões recentes (10k últimas queries)
- **SQLite**: feedback log para análise offline
- **JSONL**: streaming de logs de roteamento

## Código prático: Benchmark de Roteadores

```python
import time
import json
from typing import List

class RouterBenchmark:
    """Comparar performance de diferentes estratégias de roteamento"""
    
    def __init__(self):
        self.results = []
    
    def benchmark_latency(self, router, tasks: List[str], iterations=10):
        """Medir latência de classificação"""
        
        for task in tasks:
            times = []
            
            for _ in range(iterations):
                start = time.time()
                decision = router.classify_task(task)
                elapsed = (time.time() - start) * 1000  # ms
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            p95_time = sorted(times)[int(0.95 * len(times))]
            
            self.results.append({
                "task_preview": task[:50],
                "avg_latency_ms": avg_time,
                "p95_latency_ms": p95_time,
                "min_ms": min(times),
                "max_ms": max(times)
            })
            
            print(f"Task: {task[:40]}... | Avg: {avg_time:.1f}ms | P95: {p95_time:.1f}ms")
    
    def benchmark_accuracy(self, router, labeled_tasks: List[tuple]):
        """
        Medir acurácia de classificação
        labeled_tasks = [(task_str, expected_executor), ...]
        """
        
        correct = 0
        total = len(labeled_tasks)
        
        for task, expected in labeled_tasks:
            decision = router.classify_task(task)
            
            if decision.executor.value == expected:
                correct += 1
        
        accuracy = correct / total
        print(f"[ACCURACY] {correct}/{total} = {accuracy:.1%}")
        
        return accuracy
    
    def benchmark_cost_reduction(self, executor_costs: dict, 
                                  baseline_executor: str,
                                  routed_results: List[dict]):
        """
        Calcular economia de custo
        executor_costs = {"local": 0, "hybrid": 0.001, "cloud": 0.02} por token
        """
        
        baseline_cost = 0
        routed_cost = 0
        
        for result in routed_results:
            tokens = result.get("tokens_used", 100)
            executor = result.get("executor", baseline_executor)
            
            baseline_cost += executor_costs[baseline_executor] * tokens
            routed_cost += executor_costs[executor] * tokens
        
        savings = (baseline_cost - routed_cost) / baseline_cost
        
        print(f"[COST] Baseline: ${baseline_cost:.2f}")
        print(f"[COST] Routed: ${routed_cost:.2f}")
        print(f"[COST] Economia: {savings:.1%}")
        
        return savings

# Uso
benchmark = RouterBenchmark()

simple_tasks = [
    "Formatar JSON",
    "Corrigir ortografia",
    "Resumir parágrafo"
]

complex_tasks = [
    "Desenhar arquitetura de sistema",
    "Analisar competidores e gerar estratégia",
    "Implementar algoritmo complexo"
]

router = ComplexityRouter()
benchmark.benchmark_latency(router, simple_tasks + complex_tasks)

labeled = [
    ("Formatar JSON", "local"),
    ("Desenhar arquitetura", "cloud"),
    ("Análise simples", "hybrid")
]
benchmark.benchmark_accuracy(router, labeled)
```

## Armadilhas e Limitações

### 1. **Misclassificação em casos limítrofes (score 0.45-0.55)**
- **Problema**: Tarefa que poderia ser HYBRID ou CLOUD fica ambígua
- **Solução**: Usar intervalo de confiança. Se `confidence < 0.7`, escalar para tier superior ao invés de confiar
- **Código**: `if decision.confidence < 0.7: executor = next_tier_up`

### 2. **Overhead de latência do roteador**
- **Problema**: Chamar roteador = 100-500ms extra. Compensa apenas para pipelines com >10 req/hr
- **Solução**: Cache decisões por hash de task. Reutilizar para tasks idênticas
- **Implementação**: Redis com TTL de 24h para decisões

### 3. **Contexto incompleto leva a má classificação**
- **Problema**: Roteador vê `"Analisar dados"` mas não sabe se são 10 pontos ou 1M pontos
- **Solução**: Passar não só task_description mas também metadata (tamanho do contexto, tipo de dado, tempo limite)

### 4. **Escalabilidade de modelo router**
- **Problema**: Mistral 7B router pode virar bottleneck se muitas requisições
- **Solução**: Usar modelo mais leve (Phi 3 2B) para roteador, reservar 7B para hybrid
- **Alternativa**: Regras heurísticas simples (token count, regex patterns) para tarefas óbvias, só chamar modelo para casos ambíguos

### 5. **Dependência do modelo router é ponto único de falha**
- **Problema**: Se Ollama/roteador local está down, todo sistema falha
- **Solução**: Fallback para heurísticas (if task_tokens > 500: cloud), ou llamar Claude API como backup
- **Redundância**: Manter 2+ roteadores em standby

### 6. **Mudança de modelo base quebra threshold antigo**
- **Problema**: Retrainaram router de Mistral 7B para Qwen 7B, scores mudaram
- **Solução**: Versionálo router e suas thresholds. Se upgrade, validar em test set antes de deploy

### 7. **Não detecta anomalias (adversarial inputs)**
- **Problema**: Input injetado pode enganar roteador (ex: prompt injection disfarçado de tarefa simples)
- **Solução**: Sandboxing de executores. Executar código/output de local executor em environment isolado

## Conexões

- [[Claude Code - Melhores Práticas]] - Integração com Claude Code para automação
- [[Arquitetura de Agentes de Código Open-Source]] - Padrões multi-agente
- [[Arquitetura Multi-Agente com Avaliador Separado]] - Avaliação de qualidade
- [[LangChain]] - Framework principal
- [[Ollama]] - Runtime para modelos locais
- [[Mistral 7B]] - Modelo recomendado para router
- [[Orquestração de Agentes]] - Conceitos gerais

## Histórico

- 2026-04-02: Nota original com implementação básica
- 2026-04-11: Reescrita expandida com SFT classifier, feedback loop, benchmark, 7+ armadilhas, stack completo
