---
tags: [prompt-engineering, llm-agents, claude, arquitetura-de-agentes, multi-agent, engenharia-de-software]
source: https://x.com/NieceOfAnton/status/2039277883127103501?s=20
date: 2026-04-01
tipo: aplicacao
---

# Arquitetura Multi-Prompt Modular para Agentes IA (Claude Code Pattern)

## O que é

Claude Code usa 26 prompts especializados em 6 camadas: sistema, ferramentas (11), agentes (5), memória (4), coordenador, utilidades. Padrão arquitetural reutilizável para agentes complexos: separar roles, não monolítico.

## Como implementar

**1. Estrutura de 6 camadas**

```
├─ Sistema (1 prompt)
│  ├─ Identidade: "você é agente X"
│  ├─ Segurança: guardrails, risco
│  └─ Roteamento: qual tool usar quando
│
├─ Ferramentas (11 prompts)
│  ├─ Shell execution
│  ├─ File manipulation
│  ├─ Web search
│  ├─ Git operations
│  ├─ Code analysis
│  └─ [outros específicos]
│
├─ Agentes (5 prompts)
│  ├─ Explorer (pesquisa/descoberta)
│  ├─ Architect (design)
│  ├─ Builder (implementação)
│  ├─ Verifier (QA/red-team)
│  └─ Documenter (docs/comunicação)
│
├─ Memória (4 prompts)
│  ├─ Session compression
│  ├─ Context retrieval
│  ├─ Summary generation
│  └─ Long-term storage
│
├─ Coordenador (1 prompt)
│  └─ Orquestra delegação entre agentes
│
└─ Utilidades (vários)
   └─ Formatter, error handler, etc
```

**2. Implementar padrão em Python**

```python
from anthropic import Anthropic

class LayeredAgent:
    def __init__(self):
        self.client = Anthropic()

        # Prompts especializados
        self.system_prompt = """
        You are a code agent with multi-layer expertise.
        Identity: Code architect and executor
        Security: Ask for confirmation on destructive ops
        Tools available: shell, file, git, web-search
        """

        self.explorer_prompt = """
        Your role: Explore codebase, find patterns,
        suggest approaches. Never execute yet.
        """

        self.verifier_prompt = """
        Your role: Red-team. Try to break code.
        Find edge cases, security issues.
        Before anything ships, test ruthlessly.
        """

        self.coordinator_prompt = """
        You coordinate multi-agent workflow.
        Route task to Explorer → Architect → Builder → Verifier
        Ensure handoffs are clean.
        """

    def explore_task(self, task):
        """Step 1: Explore"""
        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            system=self.system_prompt + self.explorer_prompt,
            messages=[{"role": "user", "content": task}]
        )
        return response.content[0].text

    def verify_code(self, code):
        """Step N: Red-team verify"""
        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            system=self.system_prompt + self.verifier_prompt,
            messages=[{"role": "user", "content": f"Break this code:\n{code}"}]
        )
        return response.content[0].text

    def coordinate(self, task):
        """Orchestrate full workflow"""
        print("1. Explorer phase...")
        exploration = self.explore_task(task)

        print("2. Architect phase...")
        # Architect reads explorer output

        print("3. Builder phase...")
        # Builder implements

        print("4. Verifier phase...")
        # Verifier breaks it

        print("5. Documenter phase...")
        # Documenter writes summary
```

**3. Especialização de prompts por role**

| Role | Responsabilidade | Anti-pattern |
|------|------------------|-------------|
| Explorer | Pesquisa, análise, não executa | "Não implemente, só estude" |
| Architect | Design, decisões estruturais | Muitos detalhes de implementação |
| Builder | Implementação, execução rápida | Sobre-engineering |
| Verifier | Testes, red-team, segurança | Roupa suja, aceitar outputs fracos |
| Documenter | Comunicação, README, explicação | Documentação de "what" sem "why" |

**4. Memória em camadas (9 seções estruturadas)**

```python
class StructuredMemory:
    def compress_session(self, messages):
        """Compress long session into 9 sections"""
        return {
            "objectives": "[distille target]",
            "constraints": "[explicit limits]",
            "decisions": "[choices made]",
            "learnings": "[what we learned]",
            "current_state": "[where we are]",
            "blockers": "[what's stuck]",
            "next_steps": "[queued tasks]",
            "user_messages": "[ALL user msg]",  # MANDATORY
            "context_metadata": "[timestamps, costs]"
        }
```

**5. Segurança contextual por risco**

```python
class RiskAwareAgent:
    def execute_task(self, task, risk_level):
        if risk_level == "low":
            # Edit files freely
            return self.builder_agent(task)
        elif risk_level == "medium":
            # Ask for confirmation
            print(f"About to {task}")
            approval = input("Approve? y/n: ")
            if approval == "y":
                return self.builder_agent(task)
        elif risk_level == "high":
            # Force-push, delete, deploy?
            print(f"DESTRUCTIVE: {task}")
            print("Require explicit approval + verification")
            return None
```

## Stack e requisitos

- Claude API (Opus 4.1+ para complexidade)
- Python 3.9+ ou Node.js
- Prompt engineering discipline (6 prompts diferentes, cada um foco)
- Logging estruturado (track qual agente fez o quê)

## Armadilhas e limitações

- **Overhead de coordenação**: 6 prompts = 6x calls. Batch quando possível
- **Context confusion**: Agente pode "esquecer" seu role se prompt não é claro
- **Cascading errors**: Se Explorer falha, Architect trabalha com base errada
- **Custo escala**: Múltiplos agentes = token usage x6
- **Debugging difícil**: Qual agente causou erro em pipeline de 5?

## Conexões

[[CLAUDE-md-template-plan-mode-self-improvement]]
[[consolidacao-de-memoria-em-agentes]]
[[empresa-virtual-de-agentes-de-ia]]

## Histórico

- 2026-04-01: Nota criada
- 2026-04-02: Reescrita como guia de arquitetura
