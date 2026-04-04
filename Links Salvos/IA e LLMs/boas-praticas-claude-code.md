---
tags: []
source: https://x.com/techNmak/status/2037788648691884207?s=20
date: 2026-04-02
tipo: aplicacao
---
# Aplicar Boas Práticas Comprovadas no Claude Code

## O que é
Consolidação de padrões de uso eficiente do Claude Code: gestão de CLAUDE.md, plan mode, /loop, /btw, MCP debugging, review cruzada entre modelos. Aplicar reduz fricção, aumenta consistência, desbloqueia sessões longas.

## Como implementar
**1. CLAUDE.md afiado** (máx. 200 linhas):

```markdown
# Project Context

## Tech Stack
- Python 3.10, FastAPI, PostgreSQL
- Tests: pytest, coverage >80%
- CI/CD: GitHub Actions

## Code Conventions
- 4-space indentation
- Type hints mandatory
- Docstrings: Google style
- No wildcard imports

## Project-Specific Patterns
- Use dependency injection for services
- Database models in `models/`, services in `services/`
- API routes use FastAPI decorators, no manual routing

## Known Issues & Solutions
- Pattern: Async/await sometimes causes deadlock in DB queries
  → Solution: Always use `async_session.execute()`, never `.all()`
- Pattern: API rate limits from external service
  → Solution: Implement `backoff_decorator` in `utils/retry.py`

## Common Errors to Avoid
- Don't commit secrets to git (use .env)
- Don't write SQL without ORM (use SQLAlchemy)
- Don't skip type hints (ruff check enforces)

## User Preferences
- Verbose comments for non-obvious logic
- Prefer explicit over implicit
- Testing happens before merge
```

**2. Plan Mode com verificação**:

```python
# Usar em Claude Code:
# /plan "Implementar autenticação OAuth2"

# Prompt que Claude deve usar:
"""
Create a detailed plan for: Implementar autenticação OAuth2

Format:
1. Phase 1: Setup
   - Step 1.1: Create OAuth provider config
   - Step 1.2: Install `python-oauth2`

2. Phase 2: Implementation
   - Step 2.1: Create login endpoint
   - Step 2.2: Test with local provider

3. Phase 3: Testing
   - Test 1: Valid credentials → token
   - Test 2: Invalid → 401
   - Test 3: Token expiry → refresh

Before executing: user approves plan."""
```

**3. /loop para tarefas recorrentes**:

```python
# /loop "Generate database migration" --frequency hourly --max-duration 24h

# Útil para:
# - Monitorar logs e alertar
# - Rodar testes continuamente
# - Manter documentação sincronizada
```

**4. /btw para conversas paralelas**:

```
[Claude Code está rodando] $ python -m pytest --cov

[Você usa /btw]
You: Qual é o padrão comum de erro que está vendo?

Claude: Detectei 3 falhas de async/await. Enquanto tests rodam,
         posso refatorar a função `fetch_user_async` para evitar deadlock.

[Claude continua rodando testes]
[Após 30s]
You: Já corrigiu?

Claude: ✓ Refatored. Tests agora passam com 88% coverage.
```

**5. MCP + Chrome para debugging**:

```python
# Conectar Claude Code ao console do Chrome via MCP

from mcp import MCPClient

class ClaudeCodeDebugger:
    def __init__(self):
        self.mcp = MCPClient(server="chrome_devtools")

    def debug_react_component(self, component_name: str):
        """Debuga componente React vendo erros em tempo real."""
        self.mcp.connect(port=9222)  # Chrome DevTools port

        # Claude vê:
        # - Console errors
        # - Network requests
        # - React state updates
        # - Render times

        # Isso substitui cópia-cola manual de logs
```

**6. Revisão cruzada entre Claude Code + Codex** (ou outro modelo):

```python
def cross_review_implementation():
    """Implementa com Claude Code, revisa com outro modelo."""

    from anthropic import Anthropic

    client = Anthropic()

    # Fase 1: Claude Code implementa
    implementation_code = """
    def calculate_fibonacci(n: int) -> int:
        if n <= 1:
            return n
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
    """

    # Fase 2: Outro modelo revisa
    review_prompt = f"""Review this code:

{implementation_code}

Issues:
- Time complexity
- Edge cases
- Security
- Performance

Be specific and suggest fixes."""

    review = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": review_prompt}]
    )

    print("Review feedback:")
    print(review.content[0].text)

    # Fase 3: Claude Code aplica feedback
```

**7. RPI Pattern (Research-Plan-Implement)**:

```
/research "OAuth2 best practices in Python"
→ Claude busca + sintetiza

/plan "Implementar OAuth2"
→ Decompõe em steps verificáveis

/implement "OAuth2" --with-tests
→ Executa, testa, refina
```

**8. Gestão de contexto com Git Worktrees**:

```bash
# Em vez de múltiplos clones, use worktrees
git worktree add ../auth-feature auth/oauth2
cd ../auth-feature

# Agora Claude Code trabalha isoladamente
# Não interfere com branch principal
# Easy merge quando pronto
```

**9. Sub-agentes especializados por feature**:

```python
class FeatureTeam:
    def __init__(self):
        self.agents = {
            "backend": CodeAgent("FastAPI specialist"),
            "frontend": CodeAgent("React specialist"),
            "qa": CodeAgent("Testing specialist")
        }

    def implement_feature(self, requirement: str):
        """Cada agente especializado executa sua parte."""

        # Backend implementa API
        api_code = self.agents["backend"].implement(requirement)

        # Frontend implementa UI
        ui_code = self.agents["frontend"].implement(requirement)

        # QA escreve testes
        tests = self.agents["qa"].write_tests(api_code + ui_code)

        return {api_code, ui_code, tests}
```

**10. Monitorar CLAUDE.md degradation**:

```python
def monitor_claude_md_quality(claude_md_path: str):
    """Alerta quando CLAUDE.md fica > 200 linhas."""

    with open(claude_md_path) as f:
        lines = len(f.readlines())

    if lines > 200:
        print("⚠ CLAUDE.md é muito grande ({} linhas)".format(lines))
        print("Claude terá context anxiety.")
        print("Mova notas antigas para wiki/docs/.")
```

## Stack e requisitos
- **CLAUDE.md**: <200 linhas, afiado
- **Git**: worktrees para isolamento
- **MCP**: para conexão Chrome DevTools
- **Modelos**: Claude 3.5 Sonnet + GPT-4o para review cruzada
- **CLI**: git, pytest, ruff

## Armadilhas e limitações
- **CLAUDE.md bloat**: cresce rapidamente. Revisar mensalmente.
- **Context anxiety**: Sonnet tem melhor tolerância; Haiku piora após ~5k tokens
- **Token cost**: Sonnet + review cruzado = 3x custo. Compensado por qualidade

## Conexões
[[Claude Code]], [[Agent Loops]], [[Tool Use com LLMs]], [[Gestão de Contexto em Agentes]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
