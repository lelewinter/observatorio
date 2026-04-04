---
tags: [memoria, agentes, consolidacao, ruido]
source: https://www.linkedin.com/posts/ant%C3%B4nio-marberger-736a441b6_o-claude-code-acabou-de-lan%C3%A7ar-silenciosamente-share-7442680422334885888-yrRT
date: 2026-04-02
tipo: aplicacao
---

# Implementar Consolidação de Memória em Agentes (Auto Dream Pattern)

## O que é

Agentes com memória persistente acumulam ruído, contradições. "Auto Dream": processo async que consolida memória (900+ sessões), remove redundâncias, normaliza datas, reorganiza em índices. Ativa a cada 24h + 5 sessões.

## Como implementar

**1. Arquivo de memória em estrutura indexada**

```json
{
  "version": 2,
  "last_consolidation": "2026-04-02T08:00:00Z",
  "session_count": 127,

  "memories": {
    "preferences": {
      "code_style": "PEP 8 + mypy strict",
      "tone": "pragmatic, no hype",
      "last_updated": "2026-03-15"
    },
    "decisions": {
      "architecture_choice_db": "PostgreSQL not MongoDB",
      "reasoning": "ACID guarantees needed",
      "date": "2026-02-20"
    },
    "patterns_learned": {
      "bug_fix_workflow": "always run full test suite",
      "refactor_approach": "small commits, one change per commit"
    }
  },

  "session_log": [
    {"date": "2026-04-02", "key_learnings": ["..."]},
    {"date": "2026-04-01", "key_learnings": ["..."]}
  ]
}
```

**2. Trigger do Auto Dream**

```python
class MemoryConsolidator:
    def should_consolidate(self):
        last_consolidation = self.memory.get("last_consolidation")
        session_count_since = self.memory.get("session_count") - \
                              self.memory.get("sessions_at_last_consolidation", 0)

        hours_since = (now() - last_consolidation).total_seconds() / 3600

        # Consolidate se: 24h passaram E 5+ sessões novas
        return hours_since >= 24 and session_count_since >= 5

    def consolidate(self):
        """Review 900+ transcripts, clean, reorganize"""
        if not self.should_consolidate():
            return

        # 1. Read all session transcripts
        transcripts = self.load_last_900_sessions()

        # 2. Filter relevance (remove obsolete info)
        relevant = [t for t in transcripts if self.is_still_relevant(t)]

        # 3. Remove contradictions
        cleaned = self.resolve_conflicts(relevant)

        # 4. Normalize temporal references
        #    "today" → "2026-04-02"
        #    "last week" → "2026-03-26"
        normalized = self.normalize_dates(cleaned)

        # 5. Rebuild indices (for fast lookup)
        self.rebuild_indexes(normalized)

        # 6. Mark consolidation complete
        self.memory["last_consolidation"] = now()
        self.memory["sessions_at_last_consolidation"] = self.memory["session_count"]
```

**3. Filtragem de relevância**

```python
def is_still_relevant(self, transcript):
    """Keep only useful info, discard noise"""

    # Discard if:
    # - Info is contradicted by newer info
    if self.is_superseded(transcript):
        return False

    # - Info is purely temporary (e.g., "bug fixed on 2026-01-15")
    if self.is_purely_temporal(transcript):
        return False

    # - Info appears in every session (likely noise)
    if self.appears_in_all_recent_sessions(transcript):
        return False

    return True
```

**4. Resolução de conflitos**

```python
def resolve_conflicts(self, transcripts):
    """If 2 rules conflict, keep latest + add context"""

    # Example: "use TypeScript" vs "use Python"
    # → Keep both, but add context:
    #   "TypeScript for frontend, Python for backend"

    conflicts = self.find_conflicts(transcripts)

    for c in conflicts:
        rule1, rule2 = c
        if rule1.date > rule2.date:
            # rule1 is newer, keep it
            # Discard rule2
            pass
        else:
            # Conflict still active, add context
            combined = f"{rule1} (legacy: also consider {rule2})"

    return combined_rules
```

**5. Normalização de datas**

```python
def normalize_dates(self, transcripts):
    """Convert relative dates to absolute"""

    # Before:
    # "I did this yesterday"
    # "Fixed last week"

    # After:
    # "I did this 2026-04-01"
    # "Fixed 2026-03-26"

    # Benefit: When you load memory 3 months later,
    # "yesterday" is meaningless, but "2026-04-01" is clear
```

**6. Sincronização segura (lock file)**

```python
import fcntl

def consolidate_safely(self):
    """Prevent race conditions with lock file"""

    lock_file = ".memory/.consolidation.lock"

    try:
        with open(lock_file, "w") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Lock acquired, safe to consolidate
            self.consolidate()
    except IOError:
        # Another process is consolidating, skip
        print("Consolidation already in progress, skipping")
        return
    finally:
        # Release lock
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
```

## Stack e requisitos

- Memory store (JSON, local file)
- Session transcript log
- Lock mechanism (fcntl ou similar)
- Scheduler (cron ou background job)

## Armadilhas e limitações

- **Aggressive cleanup breaks things**: Over-filter and lose important context
- **Consolidation is slow**: 900 transcripts = 10 min processing
- **Lock contention**: If 2+ agentes consolidate simultaneously, may deadlock
- **No versioning**: If consolidation goes wrong, hard to recover old memory

## Conexões

[[Claude Code Subconscious Letta Memory Layer]]
[[claude_mem_memoria_infinita_gratis]]
[[contexto-persistente-em-llms]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação
