---
tags: [reinforcement-learning, agentes, otimizacao, microsoft, prompt-engineering]
source: https://x.com/_avichawla/status/2038143522000589241?s=20
date: 2026-04-02
tipo: aplicacao
---

# Otimizar Agentes com Agent Lightning: RL Automático para Prompts

## O que e

Agent Lightning (Microsoft): framework que aplica RL para otimizar agentes (LangChain, CrewAI, AutoGen) automaticamente. Coleta eventos (prompts, tool calls, rewards), treina otimizador, retorna prompts melhorados. Sem reescrita manual.

## Como implementar

**Instalação**:
```bash
pip install agent-lightning
```

**Setup básico com LangChain**:
```python
import agent_lightning as agl
from langchain.agents import AgentExecutor, create_react_agent
from langchain.llm import ChatAnthropic

# Criar agente normal
llm = ChatAnthropic(model="claude-opus")
tools = [...]  # suas tools
prompt = """You are a helpful assistant. Use tools when needed."""
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# Integrar Agent Lightning
agl.wrap(executor)  # Autocaptura eventos

# Usar normalmente
response = executor.invoke({"input": "What is the weather?"})

# Ao final: coleta eventos, otimiza prompts
agl.optimize()  # Retorna prompt melhorado
```

**Emissão explícita de rewards** (para feedback customizado):
```python
# Agente processa task
response = executor.invoke({"input": "classify sentiment of text"})

# Você valida resultado
if sentiment_correct:
    agl.emit(signal="success", score=1.0)
else:
    agl.emit(signal="failure", score=0.0, feedback="wrong classification")

# Agent Lightning usa sinais para otimizar
```

**Exemplo: Agente de suporte ao cliente**:
```python
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import Tool
import agent_lightning as agl

def ticket_resolver():
    """Multi-agent support system"""

    # Defina agents individuais
    triage_agent = create_agent("Triage", tools=[search_kb])
    resolution_agent = create_agent("Resolution", tools=[send_response, escalate])

    # Wrapp cada um
    agl.wrap(triage_agent)
    agl.wrap(resolution_agent)

    # Em produção
    for ticket in daily_tickets:
        # Triage
        category = triage_agent.run(ticket.description)

        # Resolution
        response = resolution_agent.run(f"{ticket.description}\nCategory: {category}")

        # Feedback
        if customer_satisfied:
            agl.emit(agent="resolution", signal="success")
        else:
            agl.emit(agent="resolution", signal="failure",
                    feedback="customer not satisfied")

    # Nightly optimization
    agl.optimize_all()
    # Prompts de ambos agents melhoram autonomamente
```

**Algoritmos de otimização** (escolher qual usar):
```python
# Opção 1: Prompt optimization (reescreve prompt)
agl.optimize(algorithm="prompt_optimizer")
# Resultado: novo prompt retornado
# Exemplo: "You are helpful assistant" → "You are a specialized support agent that..."

# Opção 2: Reinforcement Learning (ajusta pesos)
agl.optimize(algorithm="policy_gradient")
# Resultado: fine-tuned weights (para custom LLM)

# Opção 3: Few-shot examples (adiciona exemplos)
agl.optimize(algorithm="example_selector")
# Resultado: "Here are examples of good responses..."
```

**Sistema multi-agente complexo** (com Agent Lightning):
```python
# 3 agentes especializados
researcher = create_agent("Researcher", tools=[search, read_papers])
analyst = create_agent("Analyst", tools=[query_data, compute_metrics])
writer = create_agent("Writer", tools=[draft_report, format_text])

# Wrapp todos
for agent in [researcher, analyst, writer]:
    agl.wrap(agent)

# Simular workflow
task = "Analyze latest ML trends in 2026"

research = researcher.run(task)
analysis = analyst.run(f"Analyze: {research}")
report = writer.run(f"Write report: {analysis}")

# Validar output
if report_quality_good:
    agl.emit(agent="writer", signal="success")
    agl.emit(agent="analyst", signal="success")
    agl.emit(agent="researcher", signal="success")
else:
    # Specify which agent failed
    agl.emit(agent="analyst", signal="failure", feedback="analysis incomplete")

# Otimizar apenas o agente que falhou
agl.optimize(agent="analyst")
```

**Monitoramento e métricas**:
```python
import agent_lightning as agl

# Ver histórico de otimizações
history = agl.get_optimization_history()
print(f"Optimizations run: {len(history)}")

# Métrica: melhoria de performance
metrics = agl.get_metrics()
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Average response time: {metrics['avg_latency']:.2f}s")

# Exportar prompts otimizados
optimized_prompts = agl.export_prompts()
for agent_name, prompt in optimized_prompts.items():
    print(f"{agent_name}: {prompt}")
```

## Stack e requisitos

- **Agent Lightning**: 0.1.0+
- **Frameworks supported**: LangChain, CrewAI, AutoGen, OpenAI SDK, vanilla Python
- **Training data**: Mínimo 50 execuções com feedback para otimização significativa
- **Latência**: +5-10% durante collection, otimização leva 1-5 minutos
- **Armazenamento**: SQLite para eventos, configurable para PostgreSQL
- **Python**: 3.8+

## Armadilhas e limitacoes

- **Feedback quality**: Otimização é tão boa quanto sinais de recompensa. Feedback ruidoso → otimização fraca.
- **Overfitting**: Com poucos exemplos, agente pode overfitar a distribuição de treinamento.
- **Exploração vs exploitation**: Agente otimizado pode parar de explorar novas estratégias.
- **Multi-objective conflicts**: Se rewards conflitam (ex: "rápido" vs "detalhado"), otimizador pode ficar confuso.
- **Reset risk**: Otimização pode piorar performance em edgecases raros. Monitorar antes de deploy.

## Conexoes

[[Orquestracao Hibrida de LLMs]] [[Memoria Persistente em Agentes de Codigo]] [[Claude Code Melhores Praticas]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao