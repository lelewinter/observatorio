---
tags: []
source: https://x.com/tom_doerr/status/2033593821385105917?s=20
date: 2026-04-02
tipo: aplicacao
---
# Workflow de Auto-Melhoria Persistente para Claude Code

## O que é
Sistema completo (runesleo/claude-code-workflow) que persiste aprendizado entre sessões: agente registra erros, absorve correções humanas, consulta memória ao iniciar nova tarefa, refina incrementalmente sem retreinamento.

## Como implementar
Veja [[auto-evolucao-em-agentes-de-codigo]] para detalhes de engine. Aqui focamos no workflow prático.

**1. Integração com Claude Code workflow**:

```yaml
# .claude-code/workflow.yaml
name: "Auto-Improvement Workflow"
version: "1.0"

phases:
  - phase: "init"
    steps:
      - action: "load-memory"
        source: "./CLAUDE.md"
        inject_into: "system_prompt"
      - action: "retrieve-relevant-patterns"
        context_var: "task"
        limit: 5

  - phase: "execute"
    steps:
      - action: "run-task"
        with_patterns: true
      - action: "log-errors"
        to: "./agent_logs/errors.jsonl"
      - action: "capture-output"
        save_path: "./last_run_context.md"

  - phase: "reflect"
    steps:
      - action: "analyze-result"
        criteria: ["success", "partial", "failure"]
      - action: "if-successful"
        then:
          - "promote-to-patterns"
          - "update-memory"
          - "increment-confidence"
      - action: "if-error"
        then:
          - "categorize-error"
          - "store-recovery-hint"
          - "suggest-correction"

post_session:
  - "save-updated-claude-md"
  - "commit-memory-to-git"
```

**2. Estrutura de diretório para persistent state**:

```
project/
├── CLAUDE.md                  # Estado evoluído do agente
├── .claude-code/
│   ├── workflow.yaml          # Workflow definition
│   └── agent_memory.db        # SQLite com patterns
├── agent_logs/
│   ├── errors.jsonl           # Todos os erros encontrados
│   ├── patterns_learned.jsonl # Padrões bem-sucedidos
│   └── sessions.log           # Log de sessões
└── memory/
    ├── api-patterns.md        # Padrões específicos de API
    ├── error-recovery.md      # Estratégias de recovery
    └── user-preferences.md    # Preferências calibradas
```

**3. Pipeline de aprendizado em 4 fases**:

```python
class PersistentImprovementWorkflow:
    def __init__(self, project_dir: str):
        self.project = Path(project_dir)
        self.claude_md = self.project / "CLAUDE.md"
        self.memory_db = self.project / ".claude-code" / "agent_memory.db"
        self.logs = self.project / "agent_logs"

    def run_full_workflow(self, task: str) -> dict:
        """Executa workflow completo com melhorias persistentes."""

        # Fase 1: Carregamento
        print("Phase 1: Loading persistent memory...")
        memory = self.load_persistent_state()

        # Fase 2: Execução com injeção de padrões
        print("Phase 2: Executing task with learned patterns...")
        result = self.execute_with_patterns(task, memory)

        # Fase 3: Captura de aprendizado
        print("Phase 3: Capturing learnings...")
        learnings = self.extract_learnings(result)

        # Fase 4: Persistência
        print("Phase 4: Persisting improvements...")
        self.persist_learnings(learnings)

        return result

    def load_persistent_state(self) -> dict:
        """Carrega estado do CLAUDE.md e agent_memory.db."""
        import yaml
        import sqlite3

        # Carregar CLAUDE.md
        if self.claude_md.exists():
            with open(self.claude_md) as f:
                state = yaml.safe_load(f)
        else:
            state = {}

        # Carregar patterns do DB
        conn = sqlite3.connect(self.memory_db)
        patterns = conn.execute(
            "SELECT pattern, solution, confidence FROM learned_patterns ORDER BY confidence DESC LIMIT 10"
        ).fetchall()
        conn.close()

        state['patterns'] = patterns
        return state

    def execute_with_patterns(self, task: str, memory: dict) -> dict:
        """Executa tarefa com padrões injetados."""
        from anthropic import Anthropic

        client = Anthropic()

        # Injetar padrões no prompt
        pattern_str = "\n".join([
            f"- {p['pattern']}: {p['solution']} (confidence: {p['confidence']:.0%})"
            for p in memory.get('patterns', [])
        ])

        system_prompt = f"""Você é Claude Code. Use esses padrões aprendidos:

{pattern_str}

Preferências do usuário:
{memory.get('user_preferences', {})}

Erros comuns a evitar:
{memory.get('common_errors', [])}
"""

        messages = [{"role": "user", "content": task}]

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            system=system_prompt,
            messages=messages
        )

        result_text = response.content[0].text

        # Executar código se houver
        try:
            exec(result_text)
            status = "success"
        except Exception as e:
            status = "error"
            error = str(e)

        return {
            "output": result_text,
            "status": status,
            "error": error if status == "error" else None
        }

    def extract_learnings(self, result: dict) -> dict:
        """Extrai padrões do resultado da execução."""
        learnings = {
            "success_pattern": None,
            "error_recovery": None,
            "user_correction": None
        }

        if result["status"] == "success":
            # Heurística: primeira 3 linhas resumem sucesso
            learnings["success_pattern"] = result["output"].split('\n')[0]
        else:
            # Error: aprender o que não fazer
            learnings["error_recovery"] = {
                "error": result["error"],
                "context": "task context here",
                "avoidance_strategy": "implement safeguard"
            }

        return learnings

    def persist_learnings(self, learnings: dict):
        """Persiste aprendizados em banco + CLAUDE.md."""
        import sqlite3

        conn = sqlite3.connect(self.memory_db)

        if learnings["success_pattern"]:
            conn.execute("""
                INSERT OR IGNORE INTO learned_patterns (pattern, solution, confidence)
                VALUES (?, ?, 0.8)
            """, (learnings["success_pattern"], "Use this pattern"))

        if learnings["error_recovery"]:
            conn.execute("""
                INSERT INTO error_recovery (error_type, strategy, frequency)
                VALUES (?, ?, 1)
            """, (learnings["error_recovery"]["error"], learnings["error_recovery"]["avoidance_strategy"]))

        conn.commit()
        conn.close()

        # Atualizar CLAUDE.md
        self.update_claude_md()

    def update_claude_md(self):
        """Reescreve CLAUDE.md com estado atualizado."""
        import yaml

        # Ler estado
        conn = sqlite3.connect(self.memory_db)
        patterns = conn.execute(
            "SELECT pattern, solution, confidence FROM learned_patterns LIMIT 20"
        ).fetchall()
        conn.close()

        state = {
            "learned_patterns": [
                {"pattern": p[0], "solution": p[1], "confidence": p[2]}
                for p in patterns
            ]
        }

        content = f"""---
{yaml.dump(state, default_flow_style=False, allow_unicode=True)}---

# Auto-Improvement Workflow Log

Padrões aprendidos: {len(patterns)}
Última atualização: {datetime.now().isoformat()}

## Padrões Ativos
{chr(10).join([f'- {p["pattern"]}' for p in state['learned_patterns']])}
"""

        self.claude_md.write_text(content, encoding='utf-8')
```

**4. Integração com git para versionamento**:

```python
def commit_improvements(project_dir: str):
    """Commit automático de melhorias ao git."""
    import subprocess

    os.chdir(project_dir)

    # Stage CLAUDE.md e logs
    subprocess.run(["git", "add", "CLAUDE.md", "agent_logs/"])

    # Commit com mensagem informativa
    num_patterns = len(open("CLAUDE.md").readlines())
    subprocess.run([
        "git", "commit", "-m",
        f"[auto] Agente evoluiu com {num_patterns} novos padrões"
    ])

    print("✓ Melhorias commetadas ao git")
```

## Stack e requisitos
- **Persistência**: CLAUDE.md + SQLite DB
- **Versioning**: git para histórico de evolução
- **Logging**: JSONL para erros e patterns
- **Integração**: com Claude Code workflow ou custom agent loop
- **Frequência**: salvar a cada sessão (15-30min trabalho)

## Armadilhas e limitações
- **Memory pollution**: padrões ruins consolidam-se rapidamente. Implementar validation rigorosa.
- **Curva de aprendizado**: primeiras sessões têm muitos padrões ruins. Fase de "queimação" necessária.
- **Stalenesss**: padrões de 6 meses atrás podem estar desatualizados. Versão e deprecate.

## Conexões
[[Auto-Evolução em Agentes de Código]], [[Agentes de IA Auto-Aperfeiçoáveis]], [[Claude Code - Melhores Práticas]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
