---
tags: []
source: https://x.com/meta_alchemist/status/2038316393201012796?s=20
date: 2026-04-02
tipo: aplicacao
---
# Implementar Auto-Evolução de Comportamento em Agentes

## O que é
Mecanismo pelo qual agente de código aprende e refina seu próprio comportamento ao longo de sessões via persistência de CLAUDE.md, memória de padrões e atualização de regras heurísticas sem retreinamento.

## Como implementar
**1. Arquivo CLAUDE.md evolutivo** (ver [[auto-melhoria-persistente-em-agentes-de-codigo]]):

```markdown
# Agent State & Evolution

## System Context
- Project style: 4-space indent, type hints mandatory
- Language: Python 3.10+
- Testing framework: pytest

## Learned Patterns
- Pattern: "API auth fails on first retry". Solution: exponential backoff 100ms-2s
- Pattern: "User prefers bullet points". Format: change all prose to lists
- Pattern: "GraphQL queries timeout at >5 nesting levels". Solution: flatten or paginate

## Error Recovery
- RecursionError usually means infinite loop in graph traversal → add visited set
- TypeError on dict.get() → check if dict exists first, use defaults

## User Preferences
- Summary length: max 200 words, focused on implementation
- Code style: docstrings with examples
- Verbosity: concise, skip obvious steps
```

**2. Mecanismo de update automático**:

```python
import yaml
from datetime import datetime
from pathlib import Path

class AgentEvolutionEngine:
    def __init__(self, claude_md_path: str):
        self.claude_path = Path(claude_md_path)
        self.state = self.load_state()

    def load_state(self) -> dict:
        """Carrega estado do CLAUDE.md."""
        if not self.claude_path.exists():
            return self.default_state()

        with open(self.claude_path) as f:
            # Parse YAML front matter
            content = f.read()
            import re
            match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if match:
                return yaml.safe_load(match.group(1))
            return self.default_state()

    def default_state(self) -> dict:
        return {
            "system_context": {},
            "learned_patterns": [],
            "error_recovery": [],
            "user_preferences": {}
        }

    def register_error(self, error_type: str, context: str, solution: str, confidence: float = 0.5):
        """Registra erro e solução potencial."""
        pattern = {
            "error": error_type,
            "context": context,
            "solution": solution,
            "confidence": confidence,
            "discovered_at": datetime.now().isoformat(),
            "times_applied": 0
        }
        self.state["error_recovery"].append(pattern)
        self.save_state()

    def register_success(self, pattern_name: str, solution: str):
        """Promove solução bem-sucedida para memória permanente."""
        # Se não existe, criar
        existing = next(
            (p for p in self.state["learned_patterns"] if p.get("pattern") == pattern_name),
            None
        )

        if existing:
            existing["confidence"] = min(existing["confidence"] + 0.1, 1.0)
            existing["times_applied"] += 1
            existing["last_applied"] = datetime.now().isoformat()
        else:
            self.state["learned_patterns"].append({
                "pattern": pattern_name,
                "solution": solution,
                "confidence": 0.9,
                "times_applied": 1,
                "created_at": datetime.now().isoformat()
            })

        self.save_state()

    def register_user_preference(self, preference_key: str, value: any):
        """Aprende preferência do usuário."""
        self.state["user_preferences"][preference_key] = value
        self.save_state()

    def save_state(self):
        """Persiste estado em CLAUDE.md."""
        yaml_content = yaml.dump(self.state, default_flow_style=False, allow_unicode=True)
        md_content = f"""---
{yaml_content}---

# Evolution Log

Auto-atualizado em {datetime.now().isoformat()}
Padrões aprendidos: {len(self.state['learned_patterns'])}
Erros registrados: {len(self.state['error_recovery'])}
"""
        self.claude_path.write_text(md_content, encoding='utf-8')

    def get_relevant_patterns(self, context: str, top_k: int = 3) -> list:
        """Recupera padrões relevantes para contexto atual."""
        # BM25 simplificado
        scores = []
        for pattern in self.state["learned_patterns"]:
            if context.lower() in pattern["pattern"].lower():
                scores.append((pattern, pattern["confidence"] * pattern["times_applied"]))

        # Sort by score
        return [p for p, _ in sorted(scores, key=lambda x: x[1], reverse=True)][:top_k]
```

**3. Integração no agent loop**:

```python
from anthropic import Anthropic

class EvolvingCodeAgent:
    def __init__(self, claude_md_path: str):
        self.client = Anthropic()
        self.evolution = AgentEvolutionEngine(claude_md_path)

    def execute_task(self, task: str):
        """Executa tarefa com auto-evolução."""
        # Injetar padrões aprendidos no prompt
        relevant_patterns = self.evolution.get_relevant_patterns(task)

        system_prompt = self._build_system_prompt(relevant_patterns)

        messages = [{"role": "user", "content": task}]

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_prompt,
                messages=messages
            )

            code = response.content[0].text

            # Executar e observar resultado
            try:
                exec(code)
                # Sucesso! Registrar se foi porque usou padrão aprendido
                for pattern in relevant_patterns:
                    self.evolution.register_success(pattern["pattern"], code)
            except Exception as e:
                # Erro! Registrar
                self.evolution.register_error(
                    error_type=type(e).__name__,
                    context=task,
                    solution=f"Revisar {type(e).__name__}",
                    confidence=0.5
                )
                raise

        except Exception as e:
            # Erro durante execução do próprio agente
            self.evolution.register_error(
                error_type=f"Agent{type(e).__name__}",
                context=task,
                solution="Repensar abordagem",
                confidence=0.3
            )

    def _build_system_prompt(self, patterns: list) -> str:
        """Constrói prompt com padrões aprendidos."""
        patterns_str = "\n".join([
            f"- {p['pattern']}: {p['solution']} (confiança: {p['confidence']:.0%})"
            for p in patterns
        ])

        return f"""Você é um agente de código que evolui.

Padrões aprendidos em sessões anteriores:
{patterns_str}

Use esses padrões se forem relevantes à tarefa atual.

Preferências do usuário:
{self.evolution.state['user_preferences']}
"""
```

**4. Feedback loop com aprovação humana**:

```python
class HumanApprovedEvolution:
    def __init__(self, evolution: AgentEvolutionEngine):
        self.evolution = evolution

    def propose_pattern(self, pattern: str, solution: str) -> bool:
        """Propõe novo padrão; requer aprovação humana."""
        print(f"Nova estratégia descrita:\nPattern: {pattern}\nSolution: {solution}")
        approval = input("Aprovar? (y/n): ")

        if approval.lower() == 'y':
            self.evolution.register_success(pattern, solution)
            return True
        else:
            print("Rejeitado. Não será adicionado à memória.")
            return False

    def review_learned_patterns(self):
        """Interface para revisar padrões aprendidos."""
        patterns = self.evolution.state["learned_patterns"]

        for i, pattern in enumerate(patterns, 1):
            print(f"\n[{i}] {pattern['pattern']}")
            print(f"    Solution: {pattern['solution']}")
            print(f"    Confiança: {pattern['confidence']:.0%}")
            print(f"    Aplicado {pattern['times_applied']} vezes")

            action = input("Keep / Delete / Edit? (k/d/e): ")
            if action == 'd':
                patterns.pop(i - 1)
            elif action == 'e':
                pattern['solution'] = input("Nova solução: ")

        self.evolution.save_state()
```

**5. Análise de eficiência de evolução**:

```python
def analyze_evolution_efficiency(evolution: AgentEvolutionEngine) -> dict:
    """Mede quanto a evolução está ajudando."""

    patterns = evolution.state["learned_patterns"]
    error_log = evolution.state["error_recovery"]

    metrics = {
        "num_patterns_learned": len(patterns),
        "avg_confidence": sum(p["confidence"] for p in patterns) / max(len(patterns), 1),
        "avg_applications_per_pattern": sum(p["times_applied"] for p in patterns) / max(len(patterns), 1),
        "error_repeatability": sum(1 for e in error_log if e["times_applied"] > 1) / max(len(error_log), 1),
    }

    return metrics

# Uso
agent = EvolvingCodeAgent(claude_md_path="./CLAUDE.md")
agent.execute_task("Write a function to fetch data from API with retry")

# Revisar
human_approved = HumanApprovedEvolution(agent.evolution)
human_approved.review_learned_patterns()

# Analisar
metrics = analyze_evolution_efficiency(agent.evolution)
print(f"Evolução efetiva: {metrics['avg_applications_per_pattern']:.1f} aplicações por padrão")
```

## Stack e requisitos
- **Persistência**: arquivo YAML (CLAUDE.md) no projeto
- **Frequência**: salvar após cada sessão ou cada tarefa bem-sucedida
- **Versionamento**: manter histórico (git commit CLAUDE.md)
- **Validade**: padrões expiram se não usados em 3 meses

## Armadilhas e limitações
- **Derivas gradativas**: padrões aprendidos podem degradar silenciosamente ao longo de 6+ meses.
- **Contexto específico**: padrão para API X não funciona para API Y. Incluir contexto na chave.
- **Conflitos**: dois padrões podem contradizer-se. Implementar detection e manual resolution.
- **Privacy**: CLAUDE.md contém preferências sensíveis. Não fazer push público.

## Conexões
[[Auto-Melhoria Persistente em Agentes de Código]], [[Agentes de IA Auto-Aperfeiçoáveis]], [[Claude Code - Melhores Práticas]], [[Memória Persistente]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
