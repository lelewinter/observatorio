---
tags: [contexto, llm, configuracao, markdown, persistencia]
source: https://x.com/gregisenberg/status/2038220390665724001?s=20
date: 2026-04-02
tipo: aplicacao
---

# Configurar Contexto Persistente para LLMs com 4 Arquivos .md

## O que é

4 arquivos Markdown como instrções sistêmicas permanentes para Claude/LLM. Injection no início cada sessão. Elimina re-briefing, amplifica consistência. Funciona como "memória SLA" sem fine-tuning.

## Como implementar

**1. Estrutura de 4 arquivos**

```
.claude/
├── perfil.md         # Quem você é, contexto profissional
├── regras.md         # Tons, formatos, restrições
├── dominio.md        # Glossários, frameworks, conceitos
└── projetos.md       # Tarefas ativas, contexto temporal
```

**2. Arquivo 1: perfil.md**

```markdown
# Perfil Usuário

## Quem sou
- Cargo: Senior Product Manager, IA/Data
- Empresa: TechCorp (Series B, 50 people)
- Especialidade: LLM ops, data infrastructure
- Experiência: 8 anos em ML, 3 anos em DevOps

## Contexto
- Responsável por: Feature prioritization, roadmap decisions
- Autoridade: Decide features, não código (delegar builders)
- Time: 1 data eng, 1 ML eng, 2 backend eng

## Objetivos
- Build reliable data pipeline (100k events/day)
- Reduce latency p99 to <500ms
- Improve observability
```

**3. Arquivo 2: regras.md**

```markdown
# Regras de Comportamento

## Tom
- Pragmatic, not hype
- Direct, no filler
- Technical depth assumed

## Formatos
- Sempre estruturado (bullets, tables)
- Executive summary primeiro
- Technical details after summary
- Max 2 páginas por resposta

## Restrições
- Não: financial advice, medical claims
- Sim: technical analysis, architecture decisions
- Escopo: IA/Data/DevOps. Fora disso = rejeitar politely
```

**4. Arquivo 3: dominio.md**

```markdown
# Glossário & Frameworks

## Conceitos chave (nossa empresa)
- **EventStream**: Real-time data from users
- **DataPipeline**: Kafka → Spark → PostgreSQL
- **Throughput**: events/sec (target: 10k/s)

## Frameworks que usamos
- RICE para priorização (Reach, Impact, Confidence, Effort)
- Incident severity: P1 (no SLA met), P2 (degraded), P3 (cosmetic)
- Release process: code review + staging + canary

## Stack tech
- Language: Python 3.11+
- DataDB: PostgreSQL 14
- Stream: Apache Kafka
- Compute: Spark 3.2
- Monitor: Prometheus + Grafana
```

**5. Arquivo 4: projetos.md**

```markdown
# Projetos Ativos

## Q2 2026 OKRs
- [ ] EventStream reliability: 99.99% uptime
- [ ] Latency p99: <500ms (currently 800ms)
- [ ] Observability: 100% of critical paths traced

## Projeto 1: Latency Reduction
- Status: In progress (2 weeks in)
- Lead: John (data eng)
- Blockers: Awaiting benchmark results
- Next: Optimize Spark shuffle

## Projeto 2: Observability Revamp
- Status: Design phase
- Need: Recommend tracing tool (Jaeger vs Datadog)
- Timeline: Decision by week 15

## Current Pain Points
- Debugging is slow (no traces)
- Kafka partition balancing is manual
- No alerting on data freshness
```

**6. Injetar contexto (manual)**

Cada sessão Claude, no início:

```
[Paste content of perfil.md, regras.md, dominio.md, projetos.md]

---

Now with that context, here's my actual question:
[Your question]
```

**7. Automação (context injector)**

```python
import os

class ContextInjector:
    def __init__(self, context_dir=".claude"):
        self.context_dir = context_dir

    def load_all_contexts(self):
        """Load all .md files from context dir"""
        files = ["perfil.md", "regras.md", "dominio.md", "projetos.md"]
        contexts = []

        for f in files:
            path = os.path.join(self.context_dir, f)
            if os.path.exists(path):
                with open(path) as file:
                    contexts.append(f"## {f}\n{file.read()}")

        return "\n\n".join(contexts)

    def prepare_prompt(self, user_question):
        """Inject context + user question"""
        contexts = self.load_all_contexts()
        return f"{contexts}\n\n---\n\n{user_question}"

# Uso
injector = ContextInjector()
full_prompt = injector.prepare_prompt("What should we do about Kafka latency?")

# Pass to Claude API
response = client.messages.create(
    model="claude-opus-4-1",
    max_tokens=2000,
    messages=[{"role": "user", "content": full_prompt}]
)
```

**8. Manutenção (versioning)**

```bash
# Git track context files
git add .claude/
git commit -m "Update projetos.md: latency optimization in progress"

# Team can review changes
git log .claude/
git diff .claude/perfil.md
```

## Stack e requisitos

- 4 .md files (~1-2KB each)
- Claude API
- Copy-paste ou programmatic injection
- Optional: Git for version control

## Armadilhas e limitações

- **Context window cost**: Injecting ~5KB context = ~1300 tokens. Every request
- **Staleness**: Files must be updated regularly or become misleading
- **Not a substitute for fine-tuning**: Context is helpful but limited
- **Token budget**: If using Pro free tier, 5KB context eats quickly
- **Multi-session coordination**: If 2 people edit .claude/ simultaneously, conflicts

## Conexões

[[contexto-persistente-em-llms]]
[[CLAUDE-md-template-plan-mode-self-improvement]]
[[claude-power-user-setup]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação
