---
date: 2026-03-15
tags: [claude, memoria, plugin, open-source, tokens, persistencia]
source: https://x.com/oliviscusAI/status/2033141414624674159?s=20
autor: "@oliviscusAI"
tipo: aplicacao
---

# Implementar Claude-Mem para Memória Persistente Entre Sessões

## O que é

Plugin open-source que persiste memória entre sessões Claude Code. Reduz tokens ~95%, suporta 20x mais tool calls, acumula conhecimento sem re-briefing. Entrada: sessões múltiplas. Saída: contexto persistente em arquivo local.

## Como implementar

**1. Instalar Claude-Mem plugin**

```bash
# Clone do repo
git clone https://github.com/oliviscus/claude-mem.git
cd claude-mem

npm install
npm run build

# Registrar com Claude Code
claude plugin register ./dist
```

Ou via marketplace (se disponível):
```
Claude Code → Settings → Plugins → Search "claude-mem" → Install
```

**2. Configurar arquivo de memória**

Criar `.claude-mem/memory.json` na raiz do projeto:

```json
{
  "enabled": true,
  "persistenceFile": ".claude-mem/session-memory.md",
  "compressionLevel": "aggressive",
  "retentionDays": 30,
  "sections": [
    "objectives",
    "architecture_decisions",
    "past_failures",
    "successful_patterns",
    "current_state",
    "next_steps",
    "api_docs",
    "tool_calls_log"
  ]
}
```

**3. Estrutura de memória (9 seções)**

Claude-Mem automatically mantém:

```markdown
# Session Memory — Project: [name]

## Objectives (persisted)
- Primary goal: [what we're solving]
- Sub-goals: [related tasks]
- Constraints: [technical limits, deadlines]

## Architecture Decisions
- Decision 1: [choice] → Reasoning: [why] → Date: [when]
- Decision 2: ...
→ Prevent rehashing same decision every session

## Past Failures & Learnings
- Failure 1: [what broke] → Root cause: [why] → How to avoid: [lesson]
- Failure 2: ...
→ Don't repeat mistakes across sessions

## Successful Patterns
- Pattern 1: [what worked] → Context: [when to use]
- Pattern 2: ...
→ Reuse proven approaches

## Current State
- Files modified: [git diff summary]
- Tests: [passing/failing count]
- Blockers: [what's stuck]
- Progress: [% complete]

## Next Steps
- Queued tasks: [ordered priority list]
- Dependencies: [what blocks what]

## API & Tool Documentation
- Cached API specs (reduce tokens re-explaining)
- Tool usage examples
- Rate limits & quotas

## Tool Calls Log
- [action: file_write path/x.py]
- [action: shell_exec npm test]
- Prevents re-running same tools, enables audit trail
```

**4. Uso prático em sessões**

**Primeira sessão:**
```
[User] "Build a Python FastAPI service for processing images"

[Claude] Lê `.claude-mem/memory.json` (vazio na primeira)
Cria estrutura base, salva decisões arquiteturais
→ Persiste em memory.json
```

**Segunda sessão (dias depois):**
```
[User] "Continue from where we left off"

[Claude] Carrega memory.json automaticamente
Sabe: arquitetura, o que foi tentado, o que falhou
Retoma do ponto exato: "Current state: 3 endpoints done, tests failing"
Economiza re-explicação = 90% menos tokens
```

**5. Compressão e limpeza**

```python
# Cleanup automático
claude_mem.cleanup(
    retention_days=30,  # Delete sessions older than 30 days
    max_memory_size_mb=100,  # Cap memory file
    compression="aggressive"  # Compress redundant entries
)
```

**6. Integração com multi-agent systems**

Se usando múltiplos agentes (Explorer, Builder, Verifier):

```python
# Cada agente compartilha memória
class Agent:
    def __init__(self, role):
        self.memory = MemoryStore(".claude-mem/memory.json")
        self.memory.load()

    def execute(self, task):
        # Agente A: lê que Agente B descobriu falha X
        past_blockers = self.memory.get("past_failures")
        if "falha_x_mitigada_por" in past_blockers:
            # Reutiliza solução
            return self.apply_solution(past_blockers["falha_x_mitigada_por"])
```

## Stack e requisitos

- Claude Code (qualquer versão recente)
- Node.js 14+ ou Python 3.9+
- Armazenamento local (100MB+ disco)
- Zero dependências externas (100% open-source)

## Armadilhas e limitações

- **Memória cresce indefinidamente**: Se não limpar, arquivo fica gigante. Configure `retentionDays`
- **Stale information**: Memória pode ficar desatualizada se projeto mudou drasticamente. Audit periodicamente
- **Multi-agent conflicts**: Se 2+ agentes escrevem memória simultaneamente, pode corromper. Use locks
- **Privacy**: Memória armazenada localmente (seguro), mas em plain text. Considere criptografia
- **Not a silver bullet**: Memória ajuda contexto, mas não substitui bom design. Sistemas mal-arquitetados continuam lentos
- **Token count não é zero**: Mesmo com 95% redução, primeiras linhas de cada sessão ainda usam tokens carregando memória

## Conexões

[[Claude Code Subconscious Letta Memory Layer]]
[[consolidacao-de-memoria-em-agentes]]
[[contexto-persistente-em-llms]]
[[CLAUDE-md-template-plan-mode-self-improvement]]

## Histórico

- 2026-03-15: Nota criada
- 2026-04-02: Reescrita como guia de implementação
