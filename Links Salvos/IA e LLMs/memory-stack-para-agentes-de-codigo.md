---
tags: [memoria, agentes, obsidian, rag-operacional, persistencia]
source: https://x.com/intheworldofai/status/2039481184078409769?s=20
date: 2026-04-02
tipo: aplicacao
---

# Estruturar Memory Stack de 3 Camadas com Obsidian e Claude Code

## O que e

Arquitetura que externaliza memória de agente em vault Obsidian estruturado em 3 camadas: projeto (stack, arquitetura), padrões (conventions, templates), objetivos (sprints, TODOs). Agente lê camadas antes de agir, garantindo coerência entre sessões sem dependência de prompt a cada vez.

## Como implementar

**Estrutura de pasta no Obsidian** (criar diretório `Agent-Memory`):
```
Agent-Memory/
├── 1-Projeto/
│   ├── projeto-contexto.md          # Stack, versões, dependências
│   ├── arquitetura.md               # Diagrama de componentes, fluxos
│   └── decisoes-de-design.md        # Trade-offs, rationale
├── 2-Padroes/
│   ├── conventions.md               # Nomenclatura, estrutura de pastas
│   ├── code-patterns.md             # Exemplos de código reutilizáveis
│   └── testing-strategy.md          # Framework, fixtures, coverage goals
└── 3-Objetivos/
    ├── sprint-atual.md              # Tasks, story points, dates
    ├── roadmap.md                   # Milestones 6-12 meses
    └── historico-decisoes.md        # Decisões tomadas e rationale
```

**Conteúdo estruturado** (exemplo `projeto-contexto.md`):
```markdown
---
tags: [memory-stack, project-context]
updated: 2026-04-02
---

## Stack Tecnológico
- **Linguagem**: Python 3.11
- **Framework**: FastAPI 0.104
- **Banco**: PostgreSQL 15 + Redis 7
- **Frontend**: React 18 + TypeScript 5

## Arquitetura
Microserviços com 3 camadas: API (FastAPI), Workers (Celery), Database (PostgreSQL).

## Constraints
- Latência: <200ms p95
- Uptime: 99.9%
- Max payload: 10MB

## Contatos
- Lead Dev: @alice
- DevOps: @bob
```

**Conteúdo de padrões** (`code-patterns.md`):
```markdown
## Pattern 1: Async Error Handling
Always use try-except-finally in async contexts:
\`\`\`python
async def process_data():
    try:
        result = await fetch_data()
    except TimeoutError:
        logger.error("Timeout in process_data")
        raise
    finally:
        await cleanup()
\`\`\`

## Pattern 2: Database Queries
Always use parameterized queries with SQLAlchemy ORM:
\`\`\`python
user = session.query(User).filter(User.id == user_id).first()
\`\`\`
(Never use f-strings in SQL)
```

**Setup do agente** (em Claude Code ou via script):
```python
import os
from pathlib import Path

class MemoryStack:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.memory_dir = self.vault_path / "Agent-Memory"

    def load_layer(self, layer: int) -> str:
        """Carrega uma das 3 camadas de memória"""
        layer_map = {
            1: "1-Projeto",
            2: "2-Padroes",
            3: "3-Objetivos"
        }
        layer_path = self.memory_dir / layer_map[layer]
        content = ""
        for file in sorted(layer_path.glob("*.md")):
            with open(file) as f:
                content += f.read() + "\n\n"
        return content

    def inject_context(self) -> str:
        """Retorna contexto para injetar no prompt do Claude"""
        return f"""
# MEMORY STACK (injected)

## Layer 1: Projeto
{self.load_layer(1)}

## Layer 2: Padrões
{self.load_layer(2)}

## Layer 3: Objetivos
{self.load_layer(3)}
"""

# Usar em Claude Code
memory = MemoryStack("/path/to/vault")
context = memory.inject_context()
# Adicionar context ao primeiro message de cada sessão
```

**Fluxo de integração**:
1. Usuário abre Claude Code para projeto
2. Agente executa `memory.load_layer(1)` automaticamente
3. Context é injetado no system prompt
4. Agente responde com coerência arquitetural
5. **Ao final da sessão**: usuário atualiza `3-Objetivos/sprint-atual.md` com progresso (ou agente faz automaticamente)

**Manutenção da memória** (atualizar regularmente):
- **Camada 1** (Projeto): quando stack muda ou decisões grandes são tomadas
- **Camada 2** (Padrões): quando novo padrão emerge repetidamente
- **Camada 3** (Objetivos): semanalmente ou ao completar tasks

## Stack e requisitos

- **Obsidian**: 1.3+
- **Claude Code**: qualquer versão com suporte a custom system prompts
- **Tamanho vault**: tipicamente 1-5MB para memory stack
- **Frequência de leitura**: 1x por sessão de Claude Code (no início)
- **Latência**: <100ms para carregar 3 camadas (I/O local)

## Armadilhas e limitacoes

- **Desincronização**: Se você edita camada 3 enquanto Claude trabalha, mudanças podem ser perdidas; usar versionamento git.
- **Relevância**: 3 camadas podem ser muito contexto para algumas tarefas; usar filtering (ex: carregar só camada 1 + parte de camada 2).
- **Staleness**: Memória fica desatualizada se não for mantida; implementar "last-updated" timestamps e alertas.
- **Token count**: Injetar todas 3 camadas consome ~1-2K tokens; considerar compression (CLAUDE.md) para reduzir.
- **Privacy**: Vault contém contexto sensível do projeto; não commitir em git público sem sanitização.

## Conexoes

[[Memoria Persistente em Agentes de Codigo]] [[Claude Code Melhores Praticas]] [[Obsidian com IA como Segundo Cerebro]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao