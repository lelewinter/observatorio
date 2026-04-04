---
tags: [claude-code, configuração, autonomia, agentes, prompt-engineering]
source: https://x.com/VadimStrizheus/status/2039170968153624930?s=20
date: 2026-04-02
tipo: aplicacao
---

# Ativar "Superpowers" em Claude Code com Configurações Avançadas

## O que é

Conjunto de configurações, permissões ampliadas e prompts especializados que transformam Claude Code padrão em agente autônomo: loop fechado sem intervenção manual, acesso MCP externo, bash irrestrito.

## Como implementar

**1. Configurar CLAUDE.md customizado**

Arquivo na raiz do projeto:

```markdown
# CLAUDE.md - Project Context & Agent Configuration

## Autonomia Permitida
- Bash execution: UNRESTRICTED (no confirmação)
- File writes: UNRESTRICTED
- Force push: REQUIRE APPROVAL (risk mitigation)
- Deploy: REQUIRE APPROVAL + verification

## Project Architecture
[seu projeto estrutura]

## Code Conventions
- Language: Python 3.11+
- Framework: FastAPI
- Testing: pytest, >80% coverage
- CI/CD: GitHub Actions
- Linting: ruff + mypy strict

## Workflows Automáticos
- On save: run tests, lint, type-check
- On error: auto-debug, suggest fixes
- On completion: auto-commit with message

## Safety Rules
- No hardcoded secrets
- All data mutations logged
- Rollback on test failure
```

**2. Ativar permissões ampliadas**

Claude Code settings (se existir) ou via prompt inicial:

```
You are a full-stack development agent for [project].

Permissions granted:
✓ Execute bash commands without confirmation
✓ Read/write all files in repo
✓ Run tests, builds, linters
✓ Create commits and branches
✗ Force push to main (needs approval)
✗ Deploy to production (needs approval)

Your role: autonomous development loop
```

**3. Integrar MCP servers (external tools)**

Arquivo `mcp-servers.json`:

```json
{
  "servers": [
    {
      "name": "browser",
      "type": "puppeteer",
      "config": {
        "headless": true,
        "screenshotOnError": true
      }
    },
    {
      "name": "database",
      "type": "postgres",
      "config": {
        "host": "localhost",
        "database": "dev"
      }
    },
    {
      "name": "api",
      "type": "http",
      "config": {
        "baseUrl": "http://localhost:3000",
        "timeout": 5000
      }
    }
  ]
}
```

Agora agente pode:
- Abrir browser, testar UI interativamente
- Rodar queries database
- Chamar APIs do projeto

**4. Automação de workflows**

Arquivo `workflows.yml`:

```yaml
onFileSave:
  - run: "ruff check --fix"
  - run: "mypy . --strict"
  - run: "pytest tests/"
  - if_pass: "Auto-commit: lint + type fixes"
  - if_fail: "Stop, report error to user"

onTaskComplete:
  - run: "pytest tests/ -v"
  - run: "git diff main"
  - create: "PR with summary"
  - tag: "ready-for-review"

onError:
  - run: "Debug: print logs, traces"
  - suggest: "Fix options (3 alternatives)"
  - ask: "Approve fix? (with cost estimate)"
```

**5. Controle de riscos em camadas**

```python
class RiskMitigation:
    """Prevent catastrophic agent failures"""

    LOW_RISK = [
        "edit non-critical files",
        "create new branches",
        "run tests"
    ]

    MEDIUM_RISK = [
        "commit to develop",
        "deploy to staging",
        "run database migrations (non-prod)"
    ]

    HIGH_RISK = [
        "force push main",
        "deploy to production",
        "delete branches/data"
    ]

    def execute(self, action, risk_level):
        if risk_level in self.LOW_RISK:
            return self.do_action(action)
        elif risk_level in self.MEDIUM_RISK:
            print(f"Pending approval: {action}")
            # Wait for user confirmation
        elif risk_level in self.HIGH_RISK:
            print(f"BLOCKED: {action} requires explicit approval + verification")
```

**6. Monitoramento e logging**

```json
{
  "logging": {
    "level": "DEBUG",
    "outputs": [
      "console",
      "file: .claude-logs/agent.log",
      "webhook: https://monitoring.example.com"
    ],
    "track": [
      "actions taken",
      "files modified",
      "cost (tokens/API calls)",
      "errors and retries",
      "time per task"
    ]
  }
}
```

## Stack e requisitos

- Claude Code instalado
- CLAUDE.md customizado (projeto-específico)
- MCP servers opcional (browser, db, api)
- Bash 4.0+, git
- Logging infrastructure

## Armadilhas e limitações

- **Segurança crítica**: Bash irrestrito = risco alto. Auditar tudo
- **Runaway loops**: Agente pode entrar loop infinito. Implemente timeout/max-iterations
- **Custoso**: Autonomia = mais API calls. Monitor token usage
- **Debugging dificultoso**: Muito está happening automaticamente. Logging é obrigatório
- **Drift de comportamento**: Agente pode "esquecer" intruções após muitos steps. Inject regras periodicamente
- **Determinismo**: Mesmo task pode resultar em diferentes soluções. Add "prefer simple over clever" rule

## Conexões

[[CLAUDE-md-template-plan-mode-self-improvement]]
[[claude-code-opera-com-26-prompts-especializados-organizados-em-camadas-funcionai]]
[[consolidacao-de-memoria-em-agentes]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de configuração
